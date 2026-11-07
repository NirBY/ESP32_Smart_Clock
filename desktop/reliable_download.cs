using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Net;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Threading;

// Has no Python or other application dependencies; tested against a fault-injecting HTTP server.
public static class ReliableDownload {
    public static Action<string, int> Progress;

    static void Notify(string message, int percent) {
        if (Progress != null) Progress(message, percent);
    }

    public static bool Verified(string path, string sha256, long size) {
        if (!File.Exists(path) || new FileInfo(path).Length != size) return false;
        using (var file = File.OpenRead(path))
        using (var hash = SHA256.Create())
            return BitConverter.ToString(hash.ComputeHash(file)).Replace("-", "").Equals(sha256, StringComparison.OrdinalIgnoreCase);
    }

    static void CheckUrl(Uri uri) {
        if (uri.Scheme == Uri.UriSchemeHttps) return;
#if TEST_DOWNLOAD
        if (uri.Scheme == Uri.UriSchemeHttp && uri.IsLoopback) return;
#endif
        throw new InvalidDataException("Setup requires a secure HTTPS download.");
    }

    static HttpWebResponse Response(Uri uri, long offset, CancellationToken token, out HttpWebRequest request) {
        for (int redirect = 0; redirect < 6; redirect++) {
            token.ThrowIfCancellationRequested();
            CheckUrl(uri);
            request = (HttpWebRequest)WebRequest.Create(uri);
            request.AllowAutoRedirect = false;
            request.Timeout = 20000;
            request.ReadWriteTimeout = 15000;
            request.UserAgent = "SmartClock-Setup/1.0";
            request.AutomaticDecompression = DecompressionMethods.None;
            request.Headers[HttpRequestHeader.AcceptEncoding] = "identity";
            request.Proxy = WebRequest.GetSystemWebProxy();
            if (request.Proxy != null) request.Proxy.Credentials = CredentialCache.DefaultCredentials;
            if (offset > 0) request.AddRange(offset);
            HttpWebResponse response;
            HttpWebRequest current = request;
            using (token.Register(() => current.Abort())) response = (HttpWebResponse)request.GetResponse();
            int status = (int)response.StatusCode;
            if (status < 300 || status >= 400) return response;
            string location = response.Headers["Location"];
            response.Close();
            if (String.IsNullOrEmpty(location)) throw new InvalidDataException("Download redirect has no destination.");
            uri = new Uri(uri, location);
        }
        throw new InvalidDataException("Too many download redirects.");
    }

    static void Transfer(Uri uri, string part, long size, CancellationToken token) {
        long offset = File.Exists(part) ? new FileInfo(part).Length : 0;
        HttpWebRequest request;
        using (var response = Response(uri, offset, token, out request))
        using (token.Register(() => request.Abort())) {
            if (response.ContentType != null && response.ContentType.IndexOf("text/html", StringComparison.OrdinalIgnoreCase) >= 0)
                throw new InvalidDataException("The server returned a web page instead of the application package.");
            bool resume = response.StatusCode == HttpStatusCode.PartialContent;
            if (resume) {
                var match = Regex.Match(response.Headers["Content-Range"] ?? "", @"^bytes (\d+)-(\d+)/(\d+)$");
                long start, end, total;
                if (!match.Success || !Int64.TryParse(match.Groups[1].Value, out start) ||
                    !Int64.TryParse(match.Groups[2].Value, out end) || !Int64.TryParse(match.Groups[3].Value, out total) ||
                    start != offset || total != size || end < start || end >= total ||
                    (response.ContentLength >= 0 && response.ContentLength != end - start + 1))
                    throw new InvalidDataException("The server returned an invalid resume range.");
            } else {
                if (response.StatusCode != HttpStatusCode.OK) throw new InvalidDataException("Unexpected download response.");
                if (offset > 0) Notify("Server cannot resume this transfer; restarting the download...", 0);
                offset = 0; // A server without Range support must restart, never append.
                if (response.ContentLength >= 0 && response.ContentLength != size)
                    throw new InvalidDataException("The package size does not match this installer.");
            }
            long received = offset;
            var timer = Stopwatch.StartNew();
            using (var input = response.GetResponseStream())
            using (var output = new FileStream(part, resume ? FileMode.Append : FileMode.Create, FileAccess.Write, FileShare.Read)) {
                var buffer = new byte[65536];
                int count;
                while ((count = input.Read(buffer, 0, buffer.Length)) > 0) {
                    token.ThrowIfCancellationRequested();
                    if (received + count > size) throw new InvalidDataException("The downloaded package is larger than expected.");
                    output.Write(buffer, 0, count);
                    received += count;
                    if (timer.ElapsedMilliseconds >= 150) {
                        Notify(String.Format(CultureInfo.InvariantCulture, "Downloading application: {0}% ({1:0.0} / {2:0.0} MB)", 100 * received / size, received / 1000000.0, size / 1000000.0), (int)(100 * received / size));
                        timer.Restart();
                    }
                }
                output.Flush(true);
            }
            if (received != size) throw new IOException("The connection ended before the package finished downloading.");
        }
    }

    public static string Get(string url, string target, string sha256, long size, CancellationToken token) {
        if (size <= 0 || !Regex.IsMatch(sha256, "^[a-fA-F0-9]{64}$")) throw new InvalidDataException("Invalid package metadata.");
        Uri uri = new Uri(url);
        CheckUrl(uri);
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(target)));
        string part = target + ".part";
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
        if (Verified(target, sha256, size)) return target;
        if (File.Exists(target)) File.Delete(target); // Only this pinned download, never an installed runtime.
        if (File.Exists(part) && new FileInfo(part).Length > size) File.Delete(part);
        Exception last = null;
        for (int attempt = 1; attempt <= 3; attempt++) {
            token.ThrowIfCancellationRequested();
            try {
                if (!Verified(part, sha256, size)) {
                    if (File.Exists(part) && new FileInfo(part).Length == size) File.Delete(part);
                    Notify("Connecting to download server (attempt " + attempt + " / 3)...", -1);
                    Transfer(uri, part, size, token);
                }
                Notify("Verifying application package...", -1);
                token.ThrowIfCancellationRequested();
                if (!Verified(part, sha256, size)) {
                    File.Delete(part);
                    throw new InvalidDataException("The package failed its SHA-256 integrity check. A fresh copy will be requested.");
                }
                File.Move(part, target);
                Notify("Download verified.", 100);
                return target;
            } catch (OperationCanceledException) { throw; }
              catch (Exception error) {
                token.ThrowIfCancellationRequested();
                if (!(error is IOException) && !(error is WebException) && !(error is InvalidDataException)) throw;
                if (error is InvalidDataException && File.Exists(part)) File.Delete(part);
                if (error is IOException && ((error.HResult & 0xffff) == 112 || (error.HResult & 0xffff) == 39))
                    throw new IOException("Not enough free disk space. Free some space and run setup again; your settings were kept.", error);
                last = error;
                int retryDelay = attempt * 1000;
                var web = error as WebException;
                var response = web == null ? null : web.Response as HttpWebResponse;
                if (response != null) {
                    int status = (int)response.StatusCode;
                    int retrySeconds;
                    if ((status == 429 || status == 503) && Int32.TryParse(response.Headers["Retry-After"], out retrySeconds))
                        retryDelay = Math.Max(1000, Math.Min(30000, retrySeconds * 1000));
                    response.Close();
                    if (status == 416 && File.Exists(part)) File.Delete(part);
                    if (status == 404) throw new IOException("This release package is not available yet. Use a published release or try again later.", error);
                    if (status == 401 || status == 403 || status == 407) throw new IOException("The download was blocked by the server or network proxy. Sign in to your network or check proxy access, then retry.", error);
                }
                // A local disk failure will not be fixed by downloading again.
                if (error is UnauthorizedAccessException) throw;
                if (attempt < 3) {
                    Notify(error is InvalidDataException ? "Package validation failed. Retrying with a fresh download..." : "Download interrupted. Retrying automatically; completed data will be reused...", -1);
                    if (token.WaitHandle.WaitOne(retryDelay)) token.ThrowIfCancellationRequested();
                }
            }
        }
        throw new IOException("Could not complete setup after 3 attempts. Check your Internet connection, available disk space and proxy/firewall settings, then run this installer again. An incomplete download will resume; your existing installation and clock settings were kept.\n\n" + last.Message, last);
    }
}

using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

class SingleFileLauncher {
    // Replaced by the packager; binds the cache to this exact payload.
    const string PayloadId = "PAYLOAD_ID";
#if WEB_INSTALLER
    const string PayloadSha256 = "PAYLOAD_SHA256";
    const string PayloadUrl = "PAYLOAD_URL";
    const long PayloadSize = PAYLOAD_SIZE;
#endif
    static Form progress;
    static Label status;
    static ProgressBar bar;
    static int overallPercent;
    static bool finished;
    static CancellationTokenSource cancellation = new CancellationTokenSource();

    static string Quote(string value) { return "\"" + value + "\""; }

    static ProcessStartInfo Python(string root, bool windowed, string arguments) {
        var start = new ProcessStartInfo(Path.Combine(root, "runtime", windowed ? "pythonw.exe" : "python.exe"), "-I " + arguments);
        start.WorkingDirectory = root;
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.EnvironmentVariables.Remove("PYTHONHOME");
        start.EnvironmentVariables.Remove("PYTHONPATH");
        start.EnvironmentVariables["PYTHONNOUSERSITE"] = "1";
        return start;
    }

    static void Update(string text) { Update(text, overallPercent); }

    static void Update(string text, int percent) {
        if (progress == null) return;
        if (progress.InvokeRequired) { progress.BeginInvoke(new Action(() => Update(text, percent))); return; }
        overallPercent = Math.Max(overallPercent, Math.Max(0, Math.Min(100, percent)));
        status.Text = "Overall setup: " + overallPercent + "% (estimated)\n" + text;
        if (bar != null) {
            bar.Style = ProgressBarStyle.Continuous;
            bar.Value = overallPercent;
        }
        Application.DoEvents();
    }

    static void DownloadProgress(string text, int percent) {
        int mapped = percent < 0 ? overallPercent : 70 * percent / 100;
        if (text.StartsWith("Verifying application", StringComparison.Ordinal)) mapped = 75;
        if (text.StartsWith("Downloading application:", StringComparison.Ordinal)) {
            int bytes = text.IndexOf('(');
            text = "Downloading application components " + (bytes >= 0 ? text.Substring(bytes) : "...");
        }
        Update(text, mapped);
    }

    static Stream Payload(string root) {
#if WEB_INSTALLER
        ReliableDownload.Progress = DownloadProgress;
        string target = Path.Combine(Path.GetDirectoryName(root), "downloads", PayloadId + ".zip");
        var task = Task.Run(() => ReliableDownload.Get(PayloadUrl, target, PayloadSha256, PayloadSize, cancellation.Token));
        while (!task.IsCompleted) { Application.DoEvents(); Thread.Sleep(50); }
        string verified = task.GetAwaiter().GetResult();
        Update("Download verified; preparing application...", 80);
        return File.OpenRead(verified);
#else
        return Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip");
#endif
    }

    static bool Ready(string root) {
        string marker = Path.Combine(root, ".complete");
        return File.Exists(marker) && File.ReadAllText(marker) == PayloadId &&
               File.Exists(Path.Combine(root, "runtime", "pythonw.exe")) &&
               File.Exists(Path.Combine(root, "git", "cmd", "git.exe")) &&
               File.Exists(Path.Combine(root, "app.py"));
    }

    static void Extract(string root) {
        if (Ready(root)) return;
        string parent = Path.GetDirectoryName(root);
        Directory.CreateDirectory(parent);
        string stage = Path.Combine(parent, "p-" + Guid.NewGuid().ToString("N").Substring(0, 10));
        string cachePrefix = Path.GetFullPath(parent) + Path.DirectorySeparatorChar;
        if (!Path.GetFullPath(stage).StartsWith(cachePrefix, StringComparison.OrdinalIgnoreCase) ||
            !Path.GetFullPath(root).StartsWith(cachePrefix, StringComparison.OrdinalIgnoreCase)) throw new IOException("Invalid application cache path");
        Directory.CreateDirectory(stage);
        bool moved = false;
        try {
            Update("Preparing Smart Clock for first use...");
            using (Stream resource = Payload(root)) {
                using (var hash = SHA256.Create()) {
                    string actual = BitConverter.ToString(hash.ComputeHash(resource)).Replace("-", "").ToLowerInvariant();
                    if (!actual.StartsWith(PayloadId, StringComparison.Ordinal)) throw new IOException("The application download is damaged. Download it again.");
                }
                resource.Position = 0;
                using (var zip = new ZipArchive(resource, ZipArchiveMode.Read)) {
                int count = 0;
                string prefix = Path.GetFullPath(stage) + Path.DirectorySeparatorChar;
                foreach (var entry in zip.Entries) {
                    cancellation.Token.ThrowIfCancellationRequested();
                    string target = Path.GetFullPath(Path.Combine(stage, entry.FullName.Replace('/', Path.DirectorySeparatorChar)));
                    if (!target.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) throw new IOException("Invalid archive path");
                    Directory.CreateDirectory(Path.GetDirectoryName(target));
                    using (Stream input = entry.Open())
                    using (Stream output = File.Create(target)) input.CopyTo(output);
                    if (++count % 40 == 0) Update("Preparing application files...", 80 + 13 * count / zip.Entries.Count);
                }
                }
            }
            Update("Preparing bundled development tools (first launch only)...", 93);
            var start = Python(stage, false, Quote(Path.Combine(stage, "prepare_runtime.py")) + " " + Quote(stage));
            start.RedirectStandardError = true;
            // Drain stderr asynchronously so extraction cannot block on a full pipe.
            using (var process = new Process()) {
                process.StartInfo = start;
                string error = "";
                process.ErrorDataReceived += (s, e) => { if (e.Data != null) error += e.Data + "\n"; };
                process.Start();
                process.BeginErrorReadLine();
                while (!process.WaitForExit(100)) {
                    Application.DoEvents();
                    if (cancellation.IsCancellationRequested) { process.Kill(); process.WaitForExit(); cancellation.Token.ThrowIfCancellationRequested(); }
                }
                process.WaitForExit();
                if (process.ExitCode != 0) throw new IOException("Could not prepare bundled tools. " + error);
            }
            Update("Finishing setup...", 99);
            File.WriteAllText(Path.Combine(stage, ".complete"), PayloadId);
            // An interrupted old extraction is replaced only in our versioned cache.
            if (Directory.Exists(root)) Directory.Move(root, root + ".incomplete-" + Guid.NewGuid().ToString("N").Substring(0, 8));
            Directory.Move(stage, root);
            moved = true;
        } finally {
            if (!moved && Directory.Exists(stage)) Directory.Delete(stage, true);
        }
    }

    [STAThread] static int Main(string[] args) {
        bool extractOnly = Array.IndexOf(args, "--extract-only") >= 0;
        bool smoke = Array.IndexOf(args, "--smoke-test") >= 0;
        bool compile = Array.IndexOf(args, "--verify-compile") >= 0;
        bool silent = extractOnly || smoke || compile;
        string appData = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "SmartClock");
#if TEST_DOWNLOAD
        string testData = Environment.GetEnvironmentVariable("SMARTCLOCK_TEST_DATA");
        if (!String.IsNullOrEmpty(testData)) appData = Path.Combine(Path.GetFullPath(testData), "SmartClock");
#endif
        string root = Path.Combine(appData, "application", PayloadId);
        try {
            Application.EnableVisualStyles();
            if (!silent && !Ready(root)) {
                progress = new Form { Text = "Smart Clock Setup", Width = 510, Height = 180, StartPosition = FormStartPosition.CenterScreen, FormBorderStyle = FormBorderStyle.FixedDialog, MaximizeBox = false, MinimizeBox = false };
                status = new Label { Left = 18, Top = 16, Width = 465, Height = 38 };
                progress.Controls.Add(status);
                bar = new ProgressBar { Left = 18, Top = 60, Width = 460, Height = 18, Style = ProgressBarStyle.Marquee };
                progress.Controls.Add(bar);
                var cancel = new Button { Text = "Cancel", Left = 385, Top = 92, Width = 90 };
                cancel.Click += (s, e) => { cancellation.Cancel(); cancel.Enabled = false; Update("Cancelling setup; partial download will be kept..."); };
                progress.Controls.Add(cancel);
                progress.FormClosing += (s, e) => { if (!finished) { cancellation.Cancel(); e.Cancel = true; } };
                progress.Show();
                Update("Preparing application...");
            }
            using (var mutex = new Mutex(false, "Local\\NirBYSmartClock-" + PayloadId)) {
                bool locked = false;
                try {
                    try { while (!(locked = mutex.WaitOne(100))) { cancellation.Token.ThrowIfCancellationRequested(); Application.DoEvents(); } }
                    catch (AbandonedMutexException) { locked = true; }
                    Extract(root);
                } finally { if (locked) mutex.ReleaseMutex(); }
            }
            cancellation.Token.ThrowIfCancellationRequested();
            Update("Setup completed.", 100);
            finished = true;
            if (progress != null) progress.Close();
            if (extractOnly) return 0;
            if (smoke || compile) {
                var start = Python(root, false, Quote(Path.Combine(root, "smoke_test.py")) + " " + Quote(Path.Combine(appData, "self-test.log")) + (compile ? " --compile" : ""));
                start.EnvironmentVariables["PATH"] = Environment.GetFolderPath(Environment.SpecialFolder.System);
                using (var process = Process.Start(start)) { process.WaitForExit(); return process.ExitCode; }
            }
            Process.Start(Python(root, true, Quote(Path.Combine(root, "app.py"))));
            return 0;
        } catch (OperationCanceledException) {
            finished = true;
            if (progress != null) progress.Close();
            return 2;
        } catch (Exception error) {
            try { Directory.CreateDirectory(appData); File.WriteAllText(Path.Combine(appData, "startup-error.log"), error.ToString()); } catch { }
            finished = true;
            if (progress != null) progress.Close();
            if (!silent && MessageBox.Show("Setup did not finish. Your existing installation and settings were kept.\n\n" + error.Message + "\n\nRetry setup now?", "Smart Clock Setup", MessageBoxButtons.RetryCancel, MessageBoxIcon.Error) == DialogResult.Retry)
                Process.Start(new ProcessStartInfo(Assembly.GetExecutingAssembly().Location) { UseShellExecute = false });
            return 1;
        }
    }
}

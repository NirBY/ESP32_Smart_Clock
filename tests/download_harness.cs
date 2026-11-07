using System;
using System.Threading;
class DownloadHarness {
    static int Main(string[] args) {
        try {
            using (var cancel = new CancellationTokenSource()) {
                if (args.Length > 4) cancel.CancelAfter(Int32.Parse(args[4]));
                ReliableDownload.Progress = (message, percent) => Console.WriteLine(message);
                Console.WriteLine(ReliableDownload.Get(args[0], args[1], args[2], Int64.Parse(args[3]), cancel.Token));
            }
            return 0;
        } catch (OperationCanceledException) { return 2; }
          catch (Exception error) { Console.Error.WriteLine(error); return 1; }
    }
}

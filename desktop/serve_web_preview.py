"""Serve only local build artifacts for reviewing the Windows online installer."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18765)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parents[1] / 'outputs/desktop-release'
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(SimpleHTTPRequestHandler, directory=str(directory)))
    print(f'Local preview listening on 127.0.0.1:{args.port}', flush=True)
    server.serve_forever()

#!/bin/bash
# Uses only macOS-provided commands until the verified private runtime is installed.
set -Eeuo pipefail
ARCH='@ARCH@'
BUILD_ID='@BUILD_ID@'
CLIENT_SHA='@CLIENT_SHA@'
MAMBA_URL='@MAMBA_URL@'
MAMBA_SHA='@MAMBA_SHA@'
MAMBA_SIZE='@MAMBA_SIZE@'
MAMBA_BINARY_SHA='@MAMBA_BINARY_SHA@'
ESPHOME_PIN='@ESPHOME_PIN@'
RESOURCES="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)"
CACHE="$HOME/.local/share/smartclock"
VERSION="$CACHE/runtime/$BUILD_ID"
ENV_PREFIX="$VERSION/env"
CLIENT="$VERSION/client"
LOG_DIR="$HOME/Library/Logs/SmartClock"
LOG="$LOG_DIR/setup.log"
LOCK="$CACHE/setup-$BUILD_ID.lock"
CHILD=''
LOCKED=0
mkdir -p "$CACHE" "$LOG_DIR"
export MAMBA_ROOT_PREFIX="$CACHE/package-cache"
export MAMBA_SSL_VERIFY=true
export PYTHONNOUSERSITE=1
unset PYTHONHOME PYTHONPATH GIT_EXEC_PATH GIT_TEMPLATE_DIR || true

digest() { /usr/bin/shasum -a 256 "$1" | /usr/bin/awk '{print $1}'; }
ready() { [ -f "$VERSION/.complete" ] && [ "$(cat "$VERSION/.complete")" = "$BUILD_ID" ] && [ -x "$ENV_PREFIX/bin/python" ] && [ -x "$ENV_PREFIX/bin/git" ] && [ -f "$CLIENT/app.py" ]; }
launch() {
  export PATH="$ENV_PREFIX/bin:/usr/bin:/bin:/usr/sbin:/sbin"
  /usr/bin/nohup "$ENV_PREFIX/bin/python" -I "$CLIENT/app.py" >> "$LOG_DIR/application.log" 2>&1 </dev/null &
}
release_lock() {
  if [ "$LOCKED" = 1 ]; then /bin/rm -f "$LOCK/pid"; /bin/rmdir "$LOCK" 2>/dev/null || true; fi
}
fail() {
  trap - ERR
  printf '\nSetup did not finish. Your existing installation and clock settings were kept.\n'
  printf 'Check Internet access, available disk space, and the details in:\n%s\n' "$LOG"
  printf 'Close this window and open Smart Clock Setup again to retry.\n'
  exit 1
}
cancel() {
  trap - INT TERM ERR
  if [ -n "$CHILD" ]; then kill -TERM "$CHILD" 2>/dev/null || true; wait "$CHILD" 2>/dev/null || true; fi
  printf '\nSetup cancelled. Downloaded data and your settings were kept. Open setup again to retry.\n'
  exit 130
}
trap release_lock EXIT
trap fail ERR
trap cancel INT TERM

if [ "$(/usr/bin/uname -s)" != Darwin ] || [ "$(/usr/bin/uname -m)" != "$ARCH" ]; then
  printf 'This download requires a %s Mac. Choose the matching Apple Silicon or Intel installer.\n' "$ARCH"
  exit 1
fi
if ready; then
  case "${1:-}" in
    --extract-only) exit 0 ;;
    --smoke-test|--verify-compile) export PATH="$ENV_PREFIX/bin:/usr/bin:/bin:/usr/sbin:/sbin"; exec "$ENV_PREFIX/bin/python" -I "$CLIENT/mac_smoke_test.py" "$VERSION" "${1:-}" ;;
    *) launch; exit 0 ;;
  esac
fi
if [ "${1:-}" = --launch-only ]; then exit 3; fi
if ! /bin/mkdir "$LOCK" 2>/dev/null; then
  if [ -f "$LOCK/pid" ] && kill -0 "$(cat "$LOCK/pid")" 2>/dev/null; then
    printf 'Smart Clock setup is already running. Please use the existing setup window.\n'; exit 1
  fi
  /bin/rm -f "$LOCK/pid"; /bin/rmdir "$LOCK"; /bin/mkdir "$LOCK"
fi
LOCKED=1
printf '%s' "$$" > "$LOCK/pid"
mkdir -p "$CACHE/downloads" "$CACHE/tools" "$VERSION"
printf 'Smart Clock Setup\n\nNo Python, Java, Homebrew or Xcode installation is required.\n'
printf 'Application components are installed privately for your user account.\nPress Control-C to cancel safely.\n\n'

download() {
  local url="$1" file="$2" sha="$3" size="$4" part="$2.part" attempt rc code actual
  if [ -f "$file" ] && [ "$(/usr/bin/stat -f%z "$file")" = "$size" ] && [ "$(digest "$file")" = "$sha" ]; then return 0; fi
  /bin/rm -f "$file"
  if [ -f "$part" ] && [ "$(/usr/bin/stat -f%z "$part")" = "$size" ]; then
    if [ "$(digest "$part")" = "$sha" ]; then /bin/mv "$part" "$file"; return 0; fi
    /bin/rm -f "$part"
  fi
  if [ -f "$part" ] && [ "$(/usr/bin/stat -f%z "$part")" -gt "$size" ]; then /bin/rm -f "$part"; fi
  for attempt in 1 2 3; do
    printf 'Downloading setup components (attempt %s/3)...\n' "$attempt"
    /usr/bin/curl --disable --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 20 \
      --speed-time 30 --speed-limit 1 --max-time 1800 --max-filesize "$size" \
      --continue-at - --progress-bar --output "$part" --write-out '%{http_code}' "$url" > "$CACHE/downloads/http-status" &
    CHILD=$!; if wait "$CHILD"; then rc=0; else rc=$?; fi; CHILD=''
    if [ "$rc" = 0 ] && [ -f "$part" ]; then
      actual="$(/usr/bin/stat -f%z "$part")"
      if [ "$actual" = "$size" ] && [ "$(digest "$part")" = "$sha" ]; then /bin/mv "$part" "$file"; return 0; fi
      printf 'The download failed size/checksum validation. Requesting a fresh copy.\n'
      /bin/rm -f "$part"
    elif [ "$rc" = 33 ] || [ "$rc" = 63 ]; then
      printf 'The server could not resume safely. Restarting this download.\n'; /bin/rm -f "$part"
    else
      code="$(cat "$CACHE/downloads/http-status" 2>/dev/null || true)"
      case "$code" in
        401|403|404|407) printf 'Download unavailable (HTTP %s). Check network/proxy access or retry later.\n' "$code"; return 1 ;;
        416) printf 'Discarding a stale partial download and restarting.\n'; /bin/rm -f "$part" ;;
      esac
      printf 'Connection interrupted. Retrying; completed data will be reused where possible.\n'
    fi
    sleep "$attempt"
  done
  return 1
}

run_step() {
  local attempt rc
  for attempt in 1 2 3; do
    "$@" >> "$LOG" 2>&1 & CHILD=$!
    while kill -0 "$CHILD" 2>/dev/null; do printf '.'; sleep 2; done
    if wait "$CHILD"; then rc=0; else rc=$?; fi; CHILD=''
    printf '\n'
    if [ "$rc" = 0 ]; then return 0; fi
    printf 'This setup step was interrupted. Retrying (%s/3); details are saved in the setup log.\n' "$attempt"
    sleep "$attempt"
  done
  return 1
}

MAMBA="$CACHE/tools/micromamba-$ARCH"
if [ ! -f "$MAMBA" ] || [ "$(digest "$MAMBA")" != "$MAMBA_BINARY_SHA" ]; then
  ARCHIVE="$CACHE/downloads/micromamba-$ARCH.tar.bz2"
  download "$MAMBA_URL" "$ARCHIVE" "$MAMBA_SHA" "$MAMBA_SIZE"
  TOOL_STAGE="$(/usr/bin/mktemp -d "$CACHE/tools/prepare.XXXXXX")"
  /usr/bin/tar -xjf "$ARCHIVE" -C "$TOOL_STAGE" bin/micromamba
  [ "$(digest "$TOOL_STAGE/bin/micromamba")" = "$MAMBA_BINARY_SHA" ]
  /bin/mv "$TOOL_STAGE/bin/micromamba" "$MAMBA"; /bin/chmod 755 "$MAMBA"
  /bin/rmdir "$TOOL_STAGE/bin" "$TOOL_STAGE"
fi

# Never reuse an unvalidated prefix. Other completed runtime versions are untouched.
if [ -d "$ENV_PREFIX" ] || [ -L "$ENV_PREFIX" ]; then
  case "$ENV_PREFIX" in "$CACHE/runtime/$BUILD_ID/env") ;; *) exit 1 ;; esac
  CACHE_CANONICAL="$(CDPATH='' cd -- "$CACHE" && pwd -P)"
  VERSION_CANONICAL="$(CDPATH='' cd -- "$VERSION" && pwd -P)"
  [ "$VERSION_CANONICAL" = "$CACHE_CANONICAL/runtime/$BUILD_ID" ]
  if [ -f "$VERSION/.complete" ]; then /bin/mv "$VERSION/.complete" "$VERSION/.complete.invalid"; fi
  /bin/rm -rf -- "$ENV_PREFIX"
fi
printf '\nPreparing Python and application tools. This may take several minutes.\n'
case "$ARCH" in arm64) MAMBA_PLATFORM=osx-arm64 ;; x86_64) MAMBA_PLATFORM=osx-64 ;; esac
run_step "$MAMBA" --no-rc create --yes --prefix "$ENV_PREFIX" --platform "$MAMBA_PLATFORM" --override-channels -c https://conda.anaconda.org/conda-forge 'python=3.13' 'tk=8.6' git pip freetype 'crcmod=1.7'
printf '\nDownloading the pinned clock software...\n'
run_step /usr/bin/env CC=/usr/bin/false CXX=/usr/bin/false "$ENV_PREFIX/bin/python" -I -m pip --isolated install --disable-pip-version-check --no-cache-dir --retries 3 --timeout 30 --index-url https://pypi.org/simple "esphome==$ESPHOME_PIN"
printf '\nValidating the installed packages...\n'
"$ENV_PREFIX/bin/python" -I -m pip check >> "$LOG" 2>&1
"$ENV_PREFIX/bin/python" -I -c 'import tkinter, ssl, esphome, serial, esptool, platformio; tkinter.Tcl().eval("info patchlevel")' >> "$LOG" 2>&1
"$ENV_PREFIX/bin/git" --version >> "$LOG" 2>&1
[ "$(digest "$RESOURCES/client.zip")" = "$CLIENT_SHA" ]
mkdir -p "$CLIENT"
/usr/bin/ditto -x -k "$RESOURCES/client.zip" "$CLIENT"
[ -f "$CLIENT/app.py" ] && [ -f "$CLIENT/firmware/esphome-smart-clock.yaml" ]
printf '%s' "$BUILD_ID" > "$VERSION/.complete.pending"
/bin/mv "$VERSION/.complete.pending" "$VERSION/.complete"
printf '\nSmart Clock is ready. Your settings remain in their separate data folder.\n'
case "${1:-}" in
  --extract-only) exit 0 ;;
  --smoke-test|--verify-compile) export PATH="$ENV_PREFIX/bin:/usr/bin:/bin:/usr/sbin:/sbin"; exec "$ENV_PREFIX/bin/python" -I "$CLIENT/mac_smoke_test.py" "$VERSION" "${1:-}" ;;
  *) launch; printf 'The application is open. You can close this setup window.\n' ;;
esac

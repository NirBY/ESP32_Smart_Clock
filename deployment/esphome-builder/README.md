# Local firmware builder (Docker / Synology)

This optional service builds your clock firmware locally for HA's Install button.
It does not replace Home Assistant and does not expose a public update service.

1. Copy this directory to your server. Copy `.env.example` to `.env` and set a
   unique `ESPHOME_PASSWORD`. Keep `.env` private.
2. Create `config/`. Put your managed clock YAML (from `examples/clock.yaml`)
   and its private `secrets.yaml` there. Preserve the existing clock's device
   name and API key, plus all local overrides.
3. Start with `docker compose up -d --build`. On Synology, create a Container
   Manager Project using this directory and its `compose.yaml`.
4. The builder is at `http://SERVER_LAN_IP:6052`. Sign in with the username and
   password from `.env`, validate your YAML, then use that URL and filename in
   the ESP32 Smart Clock Updates integration in HA.

The host-network setting supports local mDNS/OTA discovery on Linux/Synology.
The builder listens on the server's LAN interfaces with authentication. Its
separate remote-build listener is restricted to loopback. Do not forward these
ports through your router. If port 6052 is occupied, set `--port` in the service
command and use that port in HA.

The first compile downloads the ESP32 toolchain and can take several minutes.
Configuration and secrets remain in `config/`; cached tools remain in the
Docker volume. Back up the private config directory separately.

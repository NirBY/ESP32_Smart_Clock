FROM ghcr.io/esphome/esphome:2026.10.0
RUN pip install --no-cache-dir esphome-device-builder==1.26.0
ENTRYPOINT ["python", "-m", "esphome_device_builder"]
CMD ["/config", "--host", "0.0.0.0", "--remote-build-host", "127.0.0.1"]

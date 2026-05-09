#pragma once

#ifdef USE_ESP32
#include "esp_sntp.h"
#include "esp_system.h"
#endif

inline bool smart_clock_restart_sntp() {
#ifdef USE_ESP32
  if (!esp_sntp_enabled()) {
    return false;
  }
  return esp_sntp_restart();
#else
  return false;
#endif
}

inline bool smart_clock_booted_from_brownout() {
#ifdef USE_ESP32
  return esp_reset_reason() == ESP_RST_BROWNOUT;
#else
  return false;
#endif
}

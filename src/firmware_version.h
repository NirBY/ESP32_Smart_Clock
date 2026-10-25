#pragma once

// HA compares project versions independently of ESPHome's availability flag.
// In particular, beta.15-dev.3 sorts incorrectly against beta.19 in HA's
// AwesomeVersion parser. Keep published/device versions in one tested format.
namespace smart_clock {
constexpr bool version_number(const char *&p) {
  if (*p < '0' || *p > '9') return false;
  if (*p == '0' && p[1] >= '0' && p[1] <= '9') return false;
  while (*p >= '0' && *p <= '9') ++p;
  return true;
}
constexpr bool valid_firmware_version(const char *p) {
  if (!version_number(p) || *p++ != '.') return false;
  if (!version_number(p) || *p++ != '.') return false;
  if (!version_number(p)) return false;
  if (!*p) return true;
  for (const char c : "-beta.") {
    if (c && *p++ != c) return false;
  }
  return version_number(p) && !*p;
}
}  // namespace smart_clock

#ifdef ESPHOME_PROJECT_VERSION
static_assert(smart_clock::valid_firmware_version(ESPHOME_PROJECT_VERSION),
              "Use X.Y.Z or X.Y.Z-beta.N for firmware_version. HA misorders "
              "development suffixes such as -dev.3; use compilation time to identify local builds.");
#endif

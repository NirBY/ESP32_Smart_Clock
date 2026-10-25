#include "../src/firmware_version.h"
using smart_clock::valid_firmware_version;
static_assert(valid_firmware_version("0.1.0-beta.19"));
static_assert(valid_firmware_version("1.0.0"));
static_assert(!valid_firmware_version("0.1.0-beta.15-dev.3"));
static_assert(!valid_firmware_version("0.1.0-beta.19.dev.1"));
static_assert(!valid_firmware_version("0.1.0-beta.019"));
static_assert(!valid_firmware_version("0.1.0-beta."));
static_assert(!valid_firmware_version("0.1.0-b"));
static_assert(!valid_firmware_version("0.1"));
static_assert(!valid_firmware_version(""));
int main() {}

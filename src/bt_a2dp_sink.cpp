#include <Arduino.h>
#include <esp_arduino_version.h>
#if ESP_ARDUINO_VERSION_MAJOR >= 3
#include <ESP_I2S.h>
#else
#include <driver/i2s.h>
#endif
#include "BluetoothA2DPSink.h"

// NS4168 I2S amplifier
#define I2S_DOUT 25
#define I2S_BCLK 26
#define I2S_LRC 27

#if ESP_ARDUINO_VERSION_MAJOR >= 3
I2SClass i2s;
BluetoothA2DPSink a2dpSink(i2s);
#else
BluetoothA2DPSink a2dpSink;
#endif

void setup() {
  Serial.begin(115200);
  delay(500);

#if ESP_ARDUINO_VERSION_MAJOR >= 3
  i2s.setPins(I2S_BCLK, I2S_LRC, I2S_DOUT);
  if (!i2s.begin(I2S_MODE_STD, 44100, I2S_DATA_BIT_WIDTH_16BIT,
                 I2S_SLOT_MODE_STEREO, I2S_STD_SLOT_BOTH)) {
    Serial.println("Failed to initialize I2S!");
  }
#else
  // PlatformIO espressif32 uses Arduino-ESP32 2.x. Let ESP32-A2DP
  // initialize its legacy I2S output (44.1 kHz, 16-bit stereo by default).
  const i2s_pin_config_t pins = {
      .mck_io_num = I2S_PIN_NO_CHANGE,
      .bck_io_num = I2S_BCLK,
      .ws_io_num = I2S_LRC,
      .data_out_num = I2S_DOUT,
      .data_in_num = I2S_PIN_NO_CHANGE,
  };
  a2dpSink.set_pin_config(pins);
#endif

  a2dpSink.start("ESP32 Smart Clock");

  Serial.println("Bluetooth speaker ready.");
  Serial.println("Pair Android, iPhone, or PC with: ESP32 Smart Clock");
}

void loop() {
  delay(1000);
}

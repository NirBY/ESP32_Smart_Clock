#include <Arduino.h>
#include <ESP_I2S.h>
#include "BluetoothA2DPSink.h"

// NS4168 I2S amplifier
#define I2S_DOUT 25
#define I2S_BCLK 26
#define I2S_LRC 27

I2SClass i2s;
BluetoothA2DPSink a2dpSink(i2s);

void setup() {
  Serial.begin(115200);
  delay(500);

  i2s.setPins(I2S_BCLK, I2S_LRC, I2S_DOUT);
  if (!i2s.begin(I2S_MODE_STD, 44100, I2S_DATA_BIT_WIDTH_16BIT,
                 I2S_SLOT_MODE_STEREO, I2S_STD_SLOT_BOTH)) {
    Serial.println("Failed to initialize I2S!");
  }

  a2dpSink.start("ESP32 Smart Clock");

  Serial.println("Bluetooth speaker ready.");
  Serial.println("Pair Android, iPhone, or PC with: ESP32 Smart Clock");
}

void loop() {
  delay(1000);
}

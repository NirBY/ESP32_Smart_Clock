#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>
#include <MD_MAX72xx.h>
#include <driver/i2s.h>
#include <math.h>

// =========================
// Pin map - ESP32 30 pin
// =========================
// AHT20 + BMP280 I2C
#define I2C_SDA 21
#define I2C_SCL 22

// MAX7219 LED matrix
#define MAX7219_DIN 23
#define MAX7219_CLK 18
#define MAX7219_CS  5

// NS4168 I2S amplifier
#define I2S_DOUT 25
#define I2S_BCLK 26
#define I2S_LRC  27

// =========================
// MAX7219 settings
// =========================
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4  // 4 modules = 8x32 display. Change to 1 for one 8x8 module.

MD_MAX72XX mx = MD_MAX72XX(HARDWARE_TYPE, MAX7219_DIN, MAX7219_CLK, MAX7219_CS, MAX_DEVICES);

// =========================
// Sensors
// =========================
Adafruit_AHTX0 aht;
Adafruit_BMP280 bmp(&Wire);

bool ahtOk = false;
bool bmpOk = false;

// =========================
// I2S audio
// =========================
#define I2S_PORT I2S_NUM_0
#define SAMPLE_RATE 16000

void initI2S() {
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = false,
    .tx_desc_auto_clear = true,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_BCLK,
    .ws_io_num = I2S_LRC,
    .data_out_num = I2S_DOUT,
    .data_in_num = I2S_PIN_NO_CHANGE
  };

  esp_err_t err = i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  if (err != ESP_OK) {
    Serial.printf("I2S driver install failed: %d\n", err);
    return;
  }

  err = i2s_set_pin(I2S_PORT, &pin_config);
  if (err != ESP_OK) {
    Serial.printf("I2S set pin failed: %d\n", err);
    return;
  }

  i2s_zero_dma_buffer(I2S_PORT);
  Serial.println("I2S OK");
}

void playTone(int freq, int durationMs, int amplitude = 2500) {
  int totalSamples = (SAMPLE_RATE * durationMs) / 1000;
  int16_t sampleBuffer[256];

  for (int i = 0; i < totalSamples; i += 256) {
    int chunk = min(256, totalSamples - i);

    for (int j = 0; j < chunk; j++) {
      float t = (float)(i + j) / SAMPLE_RATE;
      sampleBuffer[j] = (int16_t)(amplitude * sinf(2.0f * PI * freq * t));
    }

    size_t bytesWritten = 0;
    i2s_write(I2S_PORT, sampleBuffer, chunk * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
  }

  i2s_zero_dma_buffer(I2S_PORT);
}

// =========================
// Display helpers
// =========================
void displayScrollText(const String &text, uint16_t speedMs = 55) {
  mx.clear();

  uint8_t charWidth;
  uint8_t cBuf[8];

  for (uint16_t i = 0; i < text.length(); i++) {
    charWidth = mx.getChar(text[i], sizeof(cBuf) / sizeof(cBuf[0]), cBuf);

    for (uint8_t col = 0; col < charWidth + 1; col++) {
      mx.transform(MD_MAX72XX::TSL);
      if (col < charWidth) {
        mx.setColumn(0, cBuf[col]);
      } else {
        mx.setColumn(0, 0);
      }
      delay(speedMs);
    }
  }

  for (uint8_t i = 0; i < mx.getColumnCount(); i++) {
    mx.transform(MD_MAX72XX::TSL);
    mx.setColumn(0, 0);
    delay(speedMs);
  }
}

void i2cScan() {
  Serial.println("I2C scan start...");
  byte count = 0;
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    if (error == 0) {
      Serial.printf("I2C device found at 0x%02X\n", address);
      count++;
    }
  }
  Serial.printf("I2C scan done. Found %d device(s).\n", count);
}

void initSensors() {
  delay(250);

  ahtOk = aht.begin(&Wire);
  Serial.println(ahtOk ? "AHT20 OK" : "AHT20 NOT FOUND");

  bmpOk = bmp.begin(0x76);
  if (!bmpOk) {
    bmpOk = bmp.begin(0x77);
  }

  if (bmpOk) {
    Serial.println("BMP280 OK");
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                    Adafruit_BMP280::SAMPLING_X2,
                    Adafruit_BMP280::SAMPLING_X16,
                    Adafruit_BMP280::FILTER_X16,
                    Adafruit_BMP280::STANDBY_MS_500);
  } else {
    Serial.println("BMP280 NOT FOUND");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println();
  Serial.println("ESP32 Smart Clock hardware test starting...");

  Wire.begin(I2C_SDA, I2C_SCL);
  i2cScan();

  mx.begin();
  mx.control(MD_MAX72XX::INTENSITY, 3); // brightness 0-15
  mx.clear();
  displayScrollText("START");

  initSensors();
  initI2S();
  playTone(1000, 150);
}

void loop() {
  float tempAht = NAN;
  float humidity = NAN;
  float tempBmp = NAN;
  float pressure = NAN;

  if (ahtOk) {
    sensors_event_t humEvent, tempEvent;
    aht.getEvent(&humEvent, &tempEvent);
    tempAht = tempEvent.temperature;
    humidity = humEvent.relative_humidity;
  }

  if (bmpOk) {
    tempBmp = bmp.readTemperature();
    pressure = bmp.readPressure() / 100.0f;
  }

  Serial.println("----------------------");
  if (ahtOk) {
    Serial.printf("AHT20 temp: %.2f C\n", tempAht);
    Serial.printf("AHT20 humidity: %.2f %%\n", humidity);
  }
  if (bmpOk) {
    Serial.printf("BMP280 temp: %.2f C\n", tempBmp);
    Serial.printf("BMP280 pressure: %.2f hPa\n", pressure);
  }

  String msg;
  if (ahtOk) {
    msg = String(tempAht, 1) + "C " + String(humidity, 0) + "%";
  } else if (bmpOk) {
    msg = String(tempBmp, 1) + "C " + String(pressure, 0) + "hPa";
  } else {
    msg = "NO SENSOR";
  }

  displayScrollText(msg);
  playTone(1200, 80);
  delay(3000);
}

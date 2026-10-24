#pragma once

#include <driver/gpio.h>

// Keep the externally powered amplifier inputs defined before I2S starts.
// The I2S driver takes ownership of these pins when playback begins.
inline void smart_clock_park_audio_pins() {
  for (gpio_num_t pin : {GPIO_NUM_25, GPIO_NUM_26, GPIO_NUM_27}) {
    gpio_set_level(pin, 0);
    gpio_set_direction(pin, GPIO_MODE_OUTPUT);
  }
}

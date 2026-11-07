#include "../src/brightness_schedule.h"
#include <cassert>
int main() {
  std::vector<smart_clock::BrightnessRange> r;
  assert(smart_clock::parse_brightness_schedule("07:00-22:00=3;22:00-07:00=0", r));
  assert(smart_clock::scheduled_brightness(r, 420, 8) == 3);
  assert(smart_clock::scheduled_brightness(r, 1320, 8) == 0);
  assert(smart_clock::scheduled_brightness(r, 0, 8) == 0);
  assert(smart_clock::scheduled_brightness(r, 419, 8) == 0);
  assert(smart_clock::parse_brightness_schedule("08:00-10:00=5;09:00-11:00=9", r));
  assert(smart_clock::scheduled_brightness(r, 570, 3) == 9);
  assert(smart_clock::scheduled_brightness(r, 660, 3) == 3);
  for (auto s : {"24:00-07:00=3", "22:60-07:00=3", "22:00-07:00=16", "07:00-07:00=3", "07:00-08:00=3;", "bad", "07:00-08:00=-1"})
    assert(!smart_clock::parse_brightness_schedule(s, r));
  assert(smart_clock::parse_brightness_schedule("", r));
  assert(smart_clock::scheduled_brightness(r, 0, 7) == 7);
}

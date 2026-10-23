#include "../src/clock_timer.h"
#include <cassert>
#include <iostream>

int main() {
  using smart_clock::Countdown;
  Countdown t;
  assert(!t.visible() && t.seconds() == 0);
  assert(!t.start(0, 0) && !t.start(86401, 0));
  assert(t.start(120, 1000));
  assert(!t.show_clock(10999));
  assert(t.show_clock(11000));
  assert(!t.show_clock(13000));
  assert(!t.show_clock(11000, 10, 0));
  assert(t.show_clock(6000, 5, 3));
  assert(!t.show_clock(9000, 5, 3));
  assert(!t.tick(1500) && t.seconds() == 120);
  assert(!t.tick(2000) && t.seconds() == 119);
  t.pause();
  assert(!t.tick(1000000) && t.seconds() == 119);
  t.resume(1000000);
  assert(!t.tick(1059000) && t.seconds() == 60);
  assert(!t.show_clock(1069000)); // Final minute never yields to clock.
  assert(t.tick(1119000) && t.seconds() == 0);
  assert(!t.tick(1120000)); // Completion fires once.
  assert(t.state() == Countdown::State::FINISHED);
  t.cancel();
  assert(t.state() == Countdown::State::IDLE);
  assert(t.start(2, 0xffffff00U));
  assert(!t.tick(0x100U) && t.seconds() == 2);
  assert(t.tick(0x6d0U)); // Deadline crosses millis rollover.
  assert(t.start(86400, 100));
  assert(t.seconds() == 86400);
  assert(t.tick(86400100));
  uint32_t deadline = 0;
  assert(!smart_clock::deadline_active(deadline, 2147483649U));
  deadline = 5000;
  assert(smart_clock::deadline_active(deadline, 4999));
  assert(!smart_clock::deadline_active(deadline, 5000) && deadline == 0);
  assert(!smart_clock::deadline_active(deadline, 2147490000U));
  deadline = 100;
  assert(smart_clock::deadline_active(deadline, 0xffffff00U));
  assert(!smart_clock::deadline_active(deadline, 100));
  std::cout << "Countdown and deadline regression tests passed\n";
}

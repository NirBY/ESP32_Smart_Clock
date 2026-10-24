#include "../src/alarm_schedule.h"
#include <cassert>
#include <iostream>

int main() {
  using smart_clock::AlarmSchedule;
  using smart_clock::alarm_date_valid;
  AlarmSchedule s{"Every day", 0, 1, 0, 0, 0, false};
  assert(s.matches(20261024, 7));
  assert(!s.matches(20260230, 2));
  assert(alarm_date_valid(20280229));
  assert(!alarm_date_valid(20270229));
  assert(!alarm_date_valid(0));
  s.mode = "Weekly";
  assert(!s.valid());
  s.weekdays = (1u << 0) | (1u << 6);
  assert(s.matches(20261024, 7));
  assert(s.matches(20261025, 1));
  assert(!s.matches(20261026, 2));
  assert(!s.matches(20261024, 0));
  assert(!s.matches(20261024, 8));
  assert(s.description() == "Weekly: Sun, Sat");
  s.mode = "Monthly";
  s.month_day = 31;
  assert(s.matches(20261031, 7));
  assert(!s.matches(20261130, 2));
  assert(!s.matches(20261131, 3));
  s.month_day = 29;
  assert(s.matches(20280229, 3));
  assert(!s.matches(20270228, 1));
  s.mode = "Specific date";
  assert(!s.valid());
  s.date = 20261024;
  assert(s.matches(20261024, 7));
  assert(!s.matches(20261025, 1));
  s.mode = "Every day";
  s.limited = true;
  assert(!s.valid());
  s.start = 20261231;
  s.end = 20270102;
  assert(!s.matches(20261230, 4));
  assert(s.matches(20261231, 5));
  assert(s.matches(20270101, 6));
  assert(s.matches(20270102, 7));
  assert(!s.matches(20270103, 1));
  s.end = s.start;
  assert(s.matches(20261231, 5));
  s.end = 20261230;
  assert(!s.valid());
  s.limited = false;
  assert(s.matches(20261231, 5));
  s.mode = "Unknown";
  assert(!s.valid());
  std::cout << "Alarm schedule tests passed\n";
}

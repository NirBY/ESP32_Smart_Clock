#pragma once
#include <cstdint>

namespace smart_clock {
// Called every display frame, including for lower-priority/hidden screens.
inline bool deadline_active(uint32_t &deadline, uint32_t now) {
  if (deadline == 0) return false;
  if (static_cast<int32_t>(deadline - now) <= 0) {
    deadline = 0;
    return false;
  }
  return true;
}

class Countdown {
 public:
  enum class State { IDLE, RUNNING, PAUSED, FINISHED };
  bool start(uint32_t seconds, uint32_t now) {
    if (seconds == 0 || seconds > 86400) return false;
    remaining_ms_ = seconds * 1000;
    last_ms_ = cycle_ms_ = now;
    state_ = State::RUNNING;
    return true;
  }
  // Unsigned elapsed time survives millis rollover; no wall clock required.
  bool tick(uint32_t now) {
    if (state_ != State::RUNNING) return false;
    const uint32_t elapsed = now - last_ms_;
    last_ms_ = now;
    if (elapsed >= remaining_ms_) {
      remaining_ms_ = 0;
      state_ = State::FINISHED;
      return true;
    }
    remaining_ms_ -= elapsed;
    return false;
  }
  void pause() { if (state_ == State::RUNNING) state_ = State::PAUSED; }
  void resume(uint32_t now) {
    if (state_ == State::PAUSED) {
      last_ms_ = cycle_ms_ = now;
      state_ = State::RUNNING;
    }
  }
  void cancel() { state_ = State::IDLE; remaining_ms_ = 0; }
  uint32_t seconds() const { return (remaining_ms_ + 999) / 1000; }
  State state() const { return state_; }
  const char *state_name() const {
    switch (state_) {
      case State::RUNNING: return "running";
      case State::PAUSED: return "paused";
      case State::FINISHED: return "finished";
      default: return "idle";
    }
  }
  bool visible() const { return state_ == State::RUNNING || state_ == State::PAUSED; }
  bool show_clock(uint32_t now, uint32_t timer_seconds = 10, uint32_t clock_seconds = 2) const {
    if (timer_seconds < 1) timer_seconds = 1;
    if (clock_seconds == 0 || !visible() || seconds() <= 60) return false;
    const uint32_t timer_ms = timer_seconds * 1000;
    return (now - cycle_ms_) % (timer_ms + clock_seconds * 1000) >= timer_ms;
  }
 private:
  State state_{State::IDLE};
  uint32_t remaining_ms_{0}, last_ms_{0}, cycle_ms_{0};
};
// Function-local instance avoids dependence on ESPHome's generated global
// declaration order (custom includes are emitted after component globals).
inline Countdown &timer() {
  static Countdown instance;
  return instance;
}
}  // namespace smart_clock

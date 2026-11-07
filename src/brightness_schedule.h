#pragma once
#include <string>
#include <vector>

namespace smart_clock {
struct BrightnessRange { int start, end, level; };
// Compact persisted format: HH:MM-HH:MM=0..15;... (last match wins).
inline bool parse_brightness_schedule(const std::string &text, std::vector<BrightnessRange> &out) {
  out.clear();
  if (text.empty()) return true;
  size_t pos = 0;
  while (pos < text.size()) {
    const size_t end = text.find(';', pos);
    const std::string row = text.substr(pos, end == std::string::npos ? end : end - pos);
    if (row.size() < 13 || row.size() > 14 || row[2] != ':' || row[5] != '-' || row[8] != ':' || row[11] != '=') return false;
    for (size_t i = 0; i < row.size(); ++i) {
      if (i == 2 || i == 5 || i == 8 || i == 11) continue;
      if (row[i] < '0' || row[i] > '9') return false;
    }
    const auto pair = [&row](size_t i) { return (row[i] - '0') * 10 + row[i + 1] - '0'; };
    const int sh = pair(0), sm = pair(3);
    const int eh = pair(6), em = pair(9);
    const int level = row.size() == 13 ? row[12] - '0' : pair(12);
    if (sh > 23 || eh > 23 || sm > 59 || em > 59 || level > 15 || (sh == eh && sm == em)) return false;
    out.push_back({sh * 60 + sm, eh * 60 + em, level});
    if (end == std::string::npos) return true;
    pos = end + 1;
    if (pos == text.size()) return false;
  }
  return true;
}
inline int scheduled_brightness(const std::vector<BrightnessRange> &ranges, int minute, int fallback) {
  int result = fallback;
  for (const auto &r : ranges) {
    if (r.start < r.end ? minute >= r.start && minute < r.end : minute >= r.start || minute < r.end) result = r.level;
  }
  return result;
}
}  // namespace smart_clock

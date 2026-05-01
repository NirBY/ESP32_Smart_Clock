#pragma once
#include <Arduino.h>
#include <MD_MAX72xx.h>
#include <vector>

struct Glyph {
  uint16_t code;
  uint8_t width;
  uint8_t columns[8];
};

const Glyph HEBREW_FONT[] = {
  {0x05D0,8,{0x00,0x00,0x00,0x3a,0x04,0x08,0x18,0x26}}, // א
  {0x05D1,8,{0x00,0x00,0x00,0x22,0x22,0x22,0x3e,0x20}}, // ב
  {0x05D2,8,{0x00,0x00,0x00,0x00,0x00,0x32,0x0a,0x3e}}, // ג
  {0x05D3,8,{0x00,0x00,0x00,0x00,0x02,0x02,0x3e,0x02}}, // ד
  {0x05D4,8,{0x00,0x00,0x00,0x00,0x3a,0x02,0x02,0x3e}}, // ה
  {0x05D5,8,{0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x3e}}, // ו
  {0x05D6,8,{0x00,0x00,0x00,0x00,0x02,0x3a,0x06,0x02}}, // ז
  {0x05D7,8,{0x00,0x00,0x00,0x00,0x3e,0x02,0x02,0x3e}}, // ח
  {0x05D8,8,{0x00,0x00,0x00,0x00,0x3e,0x20,0x22,0x3e}}, // ט
  {0x05D9,8,{0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x06}}, // י
  {0x05DA,8,{0x00,0x00,0x00,0x00,0x00,0x02,0x02,0x7e}}, // ך
  {0x05DB,8,{0x00,0x00,0x00,0x00,0x00,0x22,0x22,0x3e}}, // כ
  {0x05DC,8,{0x00,0x00,0x00,0x00,0x03,0x22,0x12,0x0e}}, // ל
  {0x05DD,8,{0x00,0x00,0x00,0x00,0x3e,0x22,0x22,0x3e}}, // ם
  {0x05DE,8,{0x00,0x00,0x00,0x00,0x3e,0x04,0x22,0x3e}}, // מ
  {0x05DF,8,{0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x7e}}, // ן
  {0x05E0,8,{0x00,0x00,0x00,0x00,0x00,0x20,0x22,0x3e}}, // נ
  {0x05E1,8,{0x00,0x00,0x00,0x00,0x1e,0x22,0x22,0x1e}}, // ס
  {0x05E2,8,{0x00,0x00,0x00,0x00,0x4e,0x50,0x22,0x1e}}, // ע
  {0x05E3,8,{0x00,0x00,0x00,0x00,0x02,0x06,0x02,0x7e}}, // ף
  {0x05E4,8,{0x00,0x00,0x00,0x00,0x00,0x22,0x22,0x3e}}, // פ
  {0x05E5,8,{0x00,0x00,0x00,0x00,0x06,0x18,0x2a,0x46}}, // ץ
  {0x05E6,8,{0x00,0x00,0x00,0x00,0x22,0x24,0x28,0x36}}, // צ
  {0x05E7,8,{0x00,0x00,0x00,0x00,0x72,0x02,0x22,0x1e}}, // ק
  {0x05E8,8,{0x00,0x00,0x00,0x00,0x02,0x02,0x02,0x3e}}, // ר
  {0x05E9,8,{0x00,0x00,0x00,0x3e,0x28,0x2e,0x20,0x3e}}, // ש
  {0x05EA,8,{0x00,0x00,0x00,0x00,0x20,0x3e,0x02,0x3e}}, // ת
};

const int HEBREW_FONT_COUNT = sizeof(HEBREW_FONT) / sizeof(HEBREW_FONT[0]);

bool isHebrew(uint16_t ch) {
  return ch >= 0x05D0 && ch <= 0x05EA;
}

const Glyph* getHebrewGlyph(uint16_t code) {
  for (int i = 0; i < HEBREW_FONT_COUNT; i++) {
    if (HEBREW_FONT[i].code == code) return &HEBREW_FONT[i];
  }
  return nullptr;
}

uint16_t readUtf8Char(const char* s, int& i) {
  uint8_t c = (uint8_t)s[i];

  if (c < 0x80) {
    i++;
    return c;
  }

  // Hebrew: D7 90..AA
  if (c == 0xD7) {
    uint8_t c2 = (uint8_t)s[i + 1];
    i += 2;
    return 0x05D0 + (c2 - 0x90);
  }

  i++;
  return '?';
}

std::vector<uint16_t> utf8ToCodepoints(const String& text) {
  std::vector<uint16_t> out;
  const char* s = text.c_str();

  for (int i = 0; s[i] != 0;) {
    out.push_back(readUtf8Char(s, i));
  }

  return out;
}

// Simple BiDi:
// Hebrew is reversed for RTL.
// English/numbers are kept in normal order.
std::vector<uint16_t> visualOrderRTL(const std::vector<uint16_t>& in) {
  std::vector<uint16_t> out;

  for (int i = in.size() - 1; i >= 0;) {
    uint16_t ch = in[i];

    // Keep English/numbers runs normal
    if (ch < 128 && ch != ' ') {
      int end = i;
      int start = i;

      while (start >= 0 && in[start] < 128 && in[start] != ' ') {
        start--;
      }

      for (int j = start + 1; j <= end; j++) {
        out.push_back(in[j]);
      }

      i = start;
    } else {
      out.push_back(ch);
      i--;
    }
  }

  return out;
}

void appendSpace(std::vector<uint8_t>& cols, uint8_t count = 1) {
  for (uint8_t i = 0; i < count; i++) cols.push_back(0x00);
}

void appendCharColumns(MD_MAX72XX& mx, std::vector<uint8_t>& cols, uint16_t ch) {
  if (ch == ' ') {
    appendSpace(cols, 3);
    return;
  }

  if (isHebrew(ch)) {
    const Glyph* g = getHebrewGlyph(ch);
    if (!g) return;

    int first = 0;
    while (first < g->width && g->columns[first] == 0) first++;

    int last = g->width - 1;
    while (last >= first && g->columns[last] == 0) last--;

    for (int i = first; i <= last; i++) {
      cols.push_back(g->columns[i]);
    }

    appendSpace(cols, 1);
    return;
  }

  // ASCII from MD_MAX72XX built-in font
  if (ch < 128) {
    uint8_t buffer[8];
    uint8_t width = mx.getChar((char)ch, sizeof(buffer), buffer);

    for (int i = 0; i < width; i++) {
      cols.push_back(buffer[i]);
    }

    appendSpace(cols, 1);
  }
}

std::vector<uint8_t> renderMixedTextToColumns(MD_MAX72XX& mx, const String& text) {
  std::vector<uint16_t> logical = utf8ToCodepoints(text);
  std::vector<uint16_t> visual = visualOrderRTL(logical);

  std::vector<uint8_t> cols;

  for (uint16_t ch : visual) {
    appendCharColumns(mx, cols, ch);
  }

  return cols;
}

void drawColumnsWindow(MD_MAX72XX& mx, const std::vector<uint8_t>& cols, int offset) {
  mx.clear();

  int screenCols = mx.getColumnCount();

  for (int x = 0; x < screenCols; x++) {
    int src = offset + x;

    if (src >= 0 && src < (int)cols.size()) {
      mx.setColumn(x, cols[src]);
    } else {
      mx.setColumn(x, 0x00);
    }
  }

  mx.update();
}

void scrollMixedTextRTL(MD_MAX72XX& mx, const String& text, uint16_t speedMs = 45) {
  std::vector<uint8_t> cols = renderMixedTextToColumns(mx, text);
  int screenCols = mx.getColumnCount();

  if ((int)cols.size() <= screenCols) {
    drawColumnsWindow(mx, cols, -1 * (screenCols - (int)cols.size()));
    delay(1000);
    return;
  }

  for (int offset = (int)cols.size() - screenCols; offset >= 0; offset--) {
    drawColumnsWindow(mx, cols, offset);
    delay(speedMs);
  }
}

void showMixedTextStaticRTL(MD_MAX72XX& mx, const String& text) {
  std::vector<uint8_t> cols = renderMixedTextToColumns(mx, text);
  int screenCols = mx.getColumnCount();

  drawColumnsWindow(mx, cols, -1 * max(0, screenCols - (int)cols.size()));
}

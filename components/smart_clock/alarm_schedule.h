#pragma once
#include <string>
#include <cstdio>
namespace smart_clock {
inline bool alarm_date_valid(int d) {
  int y=d/10000,m=d/100%100,day=d%100;
  if(y<1970 || y>2099 || m<1 || m>12 || day<1) return false;
  const int days[]={31,28,31,30,31,30,31,31,30,31,30,31};
  return day<=days[m-1]+(m==2 && y%4==0 && (y%100!=0 || y%400==0));
}
inline std::string alarm_date_label(int d) {
  char b[16]; snprintf(b,sizeof(b),"%04d-%02d-%02d",d/10000,d/100%100,d%100); return b;
}
struct AlarmSchedule {
  std::string mode;
  unsigned weekdays;
  int month_day, date, start, end;
  bool limited;
  bool valid() const {
    if(limited && (!alarm_date_valid(start)||!alarm_date_valid(end)||start>end)) return false;
    if(mode=="Weekly") return weekdays!=0;
    if(mode=="Monthly") return month_day>=1 && month_day<=31;
    if(mode=="Specific date") return alarm_date_valid(date);
    return mode=="Every day";
  }
  bool matches(int today,int weekday) const {
    if(!valid() || !alarm_date_valid(today)) return false;
    if(limited && (today<start || today>end)) return false;
    if(mode=="Weekly") return weekday>=1 && weekday<=7 && (weekdays & (1u<<(weekday-1)));
    if(mode=="Monthly") return today%100==month_day;
    if(mode=="Specific date") return today==date;
    return true;
  }
  std::string description() const {
    if(!valid()) return "Needs setup: choose days/dates and check date range";
    std::string result=mode;
    if(mode=="Weekly") {
      result+=": "; const char* names[]={"Sun","Mon","Tue","Wed","Thu","Fri","Sat"};
      bool first=true;
      for(int i=0;i<7;i++) if(weekdays&(1u<<i)){if(!first)result+=", ";result+=names[i];first=false;}
    }
    if(mode=="Monthly") result+=": day "+std::to_string(month_day)+" (skip shorter months)";
    if(mode=="Specific date") result+=": "+alarm_date_label(date);
    if(limited) result+=" | "+alarm_date_label(start)+" to "+alarm_date_label(end)+" inclusive";
    return result;
  }
};
}

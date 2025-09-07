import time
from datetime import datetime, timedelta
from typing import Dict, Any


class DatetimeHelper:
    """日期时间工具类，提供各种日期时间操作方法"""

    @staticmethod
    def get_timestamp10() -> int:
        """获取当前时间长度为10位长度的时间戳"""
        return int(time.time())

    @staticmethod
    def parse_datetime(date_string: str, date_format: str = "%Y-%m-%d") -> datetime:
        """将字符串解析为datetime对象"""
        return datetime.strptime(date_string, date_format)

    @staticmethod
    def datetime_to_str(dt: datetime, date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """将datetime对象转换为字符串"""
        return dt.strftime(date_format)

    @staticmethod
    def get_current_date() -> str:
        """获取当前日期字符串"""
        return time.strftime('%Y-%m-%d', time.localtime(time.time()))

    @staticmethod
    def get_current_datetime() -> str:
        """获取当前日期时间字符串"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    @staticmethod
    def string_to_datetime(date_string: str, date_format: str = "%Y-%m-%d") -> datetime:
        """将日期字符串转换为datetime对象"""
        return datetime.strptime(date_string, date_format)

    @staticmethod
    def datetime_to_string(dt: datetime, date_format: str = "%Y-%m-%d") -> str:
        """将datetime对象转换为指定格式的字符串"""
        return dt.strftime(date_format)

    @staticmethod
    def days_difference_from_now(date_string: str) -> int:
        """计算传入日期与当前日期的天数差"""
        target_date = datetime.strptime(date_string, "%Y-%m-%d")
        today = datetime.combine(datetime.now().date(), datetime.min.time())
        return (target_date - today).days

    @staticmethod
    def is_time_valid(appointment_time: str) -> bool:
        """检查预约时间是否有效（未过期）"""
        current_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time())).replace("-", "")
        current_datetime = datetime.strptime(current_time, "%Y%m%d %H:%M")
        
        appointment_clean = appointment_time.replace("-", "")
        appointment_datetime = datetime.strptime(appointment_clean, "%Y%m%d %H:%M:%S")
        
        return current_datetime < appointment_datetime

    @staticmethod
    def add_days_to_date(base_date: datetime, days: int) -> datetime:
        """根据给定日期，获取前n天或后n天的日期"""
        if days < 0:
            return base_date - timedelta(days=abs(days))
        else:
            return base_date + timedelta(days=days)

    @staticmethod
    def weekday_to_chinese(weekday_num: int) -> str:
        """将星期数字转换为中文"""
        weekday_map = {
            7: "周日",
            1: "周一", 
            2: "周二",
            3: "周三",
            4: "周四",
            5: "周五",
            6: "周六"
        }
        return weekday_map.get(weekday_num, "")

    @staticmethod
    def get_week_info_list(days: int = 6) -> Dict[str, Dict[str, Any]]:
        """获取从今天开始的连续几天信息列表"""
        today = DatetimeHelper.get_current_date()
        today_datetime = DatetimeHelper.string_to_datetime(today)
        
        result = {}
        for i in range(days + 1):
            target_date = DatetimeHelper.add_days_to_date(today_datetime, i)
            date_str = target_date.strftime('%Y-%m-%d')
            result[date_str] = {
                'weekday': DatetimeHelper.weekday_to_chinese(target_date.isoweekday()),
                'date': date_str
            }
        return result

    @staticmethod
    def get_week_dates_only(days: int = 6) -> Dict[str, Dict[str, Any]]:
        """获取从今天开始的连续几天日期列表（仅包含日期）"""
        today = DatetimeHelper.get_current_date()
        today_datetime = DatetimeHelper.string_to_datetime(today)
        
        result = {}
        for i in range(days + 1):
            target_date = DatetimeHelper.add_days_to_date(today_datetime, i)
            date_str = target_date.strftime('%Y-%m-%d')
            result[date_str] = {}
        return result

    @staticmethod
    def get_one_day_start_and_end_time(date_string: str) -> tuple[datetime, datetime]:
        """获取指定日期的一天的开始和结束时间"""
        if not date_string:
            start_time = datetime.now()
        else:
            start_time = DatetimeHelper.string_to_datetime(date_string)
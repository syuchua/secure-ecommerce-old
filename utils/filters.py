from flask import Flask
from datetime import datetime
import locale


def register_filters(app: Flask):
    """注册自定义模板过滤器"""

    @app.template_filter('datetime_format')
    def datetime_format(value, format='%Y-%m-%d %H:%M:%S'):
        """格式化datetime对象为字符串"""
        if value is None:
            return ""
        return value.strftime(format)

    @app.template_filter('currency')
    def currency_format(value):
        """格式化货币"""
        if value is None:
            return "¥0.00"
        return f"¥{float(value):.2f}"

    @app.template_filter('status_text')
    def status_text(value):
        """将订单状态代码转换为易读文本"""
        status_map = {
            'pending': '待处理',
            'processing': '处理中',
            'shipped': '已发货',
            'completed': '已完成',
            'cancelled': '已取消',
            'refunded': '已退款'
        }
        return status_map.get(value, value)

    @app.template_filter('truncate_text')
    def truncate_text(text, length=100, suffix='...'):
        """截断文本至指定长度"""
        if text is None:
            return ""
        if len(text) <= length:
            return text
        return text[:length].rstrip() + suffix

    @app.template_filter('time_ago')
    def time_ago(dt):
        """将datetime对象转换为"xx时间前"格式"""
        if not dt:
            return ""

        now = datetime.utcnow()
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}分钟前"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}小时前"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}天前"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks}周前"
        else:
            return dt.strftime('%Y-%m-%d')
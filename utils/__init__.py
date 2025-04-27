# 工具函数包初始化文件
from flask import Flask

def register_utils(app: Flask):
    """注册所有工具函数到Flask应用"""
    from utils.filters import register_filters
    register_filters(app)

    # 导入安全相关功能，确保它们被初始化
    import utils.security
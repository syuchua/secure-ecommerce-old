import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    WTF_CSRF_ENABLED = True

    # 数据库配置 - 修改这里使用文件数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'ecommerce.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 最大上传限制

    # Flask-Login配置
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

    # 应用配置
    ITEMS_PER_PAGE = 12
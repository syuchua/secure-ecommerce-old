from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 创建实例
db = SQLAlchemy()

# 配置登录管理器
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'info'
from flask_login import LoginManager
from models.user import User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录才能访问此页面。'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login用户加载函数"""
    return User.query.get(int(user_id))
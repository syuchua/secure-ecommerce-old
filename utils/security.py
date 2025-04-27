from flask import request, abort, current_app, redirect, url_for, flash
import re
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from functools import wraps
from flask_login import current_user


def require_admin(f):
    """验证当前用户是否是管理员的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# 为了保持兼容性，也可以添加admin_required作为别名
admin_required = require_admin


def generate_token(length=32):
    """生成安全的随机令牌"""
    return secrets.token_hex(length)


def secure_filename(filename):
    """创建安全的文件名，移除潜在的危险字符"""
    if filename is None:
        return None

    # 移除路径信息
    filename = filename.split('/')[-1].split('\\')[-1]

    # 移除所有非字母数字字符，保留扩展名
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    name = re.sub(r'[^\w\.]', '_', name)
    ext = re.sub(r'[^\w\.]', '', ext)

    if ext:
        return f"{name}.{ext}"
    return name


def hash_password(password):
    """对密码进行哈希处理"""
    if not password:
        raise ValueError("密码不能为空")

    return generate_password_hash(password, method='pbkdf2:sha256:150000')


def check_password(password_hash, password):
    """验证密码是否匹配哈希值

    参数:
      password_hash: 数据库中存储的密码哈希值
      password: 用户输入的明文密码
    """
    if not password_hash or not password:
        return False

    # 添加调试输出
    print(f"Checking password: hash={password_hash[:20]}..., plain_text_len={len(password)}")
    result = check_password_hash(password_hash, password)
    print(f"Password check result: {result}")
    return result


def is_strong_password(password):
    """
    检查密码强度
    要求：
    - 至少8个字符
    - 至少包含一个大写字母
    - 至少包含一个小写字母
    - 至少包含一个数字
    - 至少包含一个特殊字符
    """
    if not password or len(password) < 8:
        return False

    has_upper = re.search(r'[A-Z]', password) is not None
    has_lower = re.search(r'[a-z]', password) is not None
    has_digit = re.search(r'[0-9]', password) is not None
    has_special = re.search(r'[^A-Za-z0-9]', password) is not None

    return has_upper and has_lower and has_digit and has_special


def sanitize_input(text):
    """清理用户输入以防止XSS攻击"""
    if not text:
        return ""

    # 基本HTML实体替换
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def require_csrf_token():
    """
    检查CSRF令牌是否有效
    需要Flask-WTF提供的CSRFProtect扩展支持
    """
    if current_app.config.get('WTF_CSRF_ENABLED', True):
        from flask_wtf.csrf import validate_csrf
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            abort(403, description="CSRF验证失败")


def require_secure_connection():
    """确保连接使用HTTPS"""
    if not request.is_secure and not current_app.debug:
        abort(403, description="需要安全连接")
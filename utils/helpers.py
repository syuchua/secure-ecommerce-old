from flask import current_app, request, url_for
import os
from datetime import datetime
import re
import random
import string
from werkzeug.utils import secure_filename as werkzeug_secure_filename
import uuid


def get_page_args():
    """从请求中获取分页参数"""
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = int(request.args.get('per_page', 10))
        if per_page < 1 or per_page > 100:
            per_page = 10
    except (TypeError, ValueError):
        per_page = 10

    return page, per_page


def format_date(date, format='%Y-%m-%d'):
    """格式化日期对象为字符串"""
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return date

    if isinstance(date, datetime):
        return date.strftime(format)

    return ""


def get_unique_filename(filename):
    """生成唯一的文件名，以防止覆盖"""
    if not filename:
        return None

    # 安全处理文件名
    filename = werkzeug_secure_filename(filename)

    # 生成UUID作为前缀
    prefix = str(uuid.uuid4())[:8]

    # 添加时间戳
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # 拆分文件名和扩展名
    name, ext = os.path.splitext(filename)

    # 组合新文件名
    return f"{prefix}_{timestamp}_{name}{ext}"


def allowed_file(filename, allowed_extensions=None):
    """检查文件类型是否允许"""
    if not filename:
        return False

    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})

    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, directory=None):
    """保存上传的文件并返回保存路径"""
    if not file:
        return None

    if directory is None:
        directory = os.path.join(current_app.root_path,
                                 current_app.config.get('UPLOAD_FOLDER', 'static/uploads'))

    # 确保目录存在
    os.makedirs(directory, exist_ok=True)

    # 获取安全且唯一的文件名
    filename = get_unique_filename(file.filename)

    # 保存文件
    filepath = os.path.join(directory, filename)
    file.save(filepath)

    # 返回相对路径
    return os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), filename)


def generate_random_string(length=10):
    """生成指定长度的随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def is_valid_email(email):
    """验证电子邮件地址格式"""
    if not email:
        return False

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def is_valid_phone(phone):
    """验证电话号码格式"""
    if not phone:
        return False

    # 简单验证中国大陆手机号
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
    return ip


def build_pagination_urls(endpoint, page, total_pages, **kwargs):
    """构建分页导航URL"""
    result = {
        'first': url_for(endpoint, page=1, **kwargs) if page > 1 else None,
        'prev': url_for(endpoint, page=page - 1, **kwargs) if page > 1 else None,
        'next': url_for(endpoint, page=page + 1, **kwargs) if page < total_pages else None,
        'last': url_for(endpoint, page=total_pages, **kwargs) if page < total_pages else None,
    }
    return result
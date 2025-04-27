from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db
from datetime import datetime, timedelta
from utils.security import hash_password, check_password, generate_token, is_strong_password
from forms.user import EditProfileForm, ChangePasswordForm
from utils.security import hash_password, check_password
from flask import current_app, abort


auth_bp = Blueprint('auth', __name__, url_prefix='')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form

        if not username or not password:
            flash('请输入用户名和密码', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        # 调试输出
        print(f"Login attempt: username={username}, user found={user is not None}")

        # 添加密码校验调试信息
        if user:
            # 直接验证密码
            password_correct = check_password(user.password, password)
            print(f"Password check result: {password_correct}")

            if password_correct:
                login_user(user, remember=remember)
                flash('登录成功！', 'success')

                # 获取next参数，安全地重定向
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('shop.index')

                return redirect(next_page)

        flash('用户名或密码错误', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('shop.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('shop.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # 表单验证
        if not username or not email or not password or not confirm:
            flash('请填写所有必填字段', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('两次输入的密码不匹配', 'danger')
            return render_template('auth/register.html')

        # 检查密码强度
        if not is_strong_password(password):
            flash('密码太弱。请使用包含大小写字母、数字和特殊字符的8位以上密码。', 'danger')
            return render_template('auth/register.html')

        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已被使用', 'danger')
            return render_template('auth/register.html')

        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('电子邮箱已被使用', 'danger')
            return render_template('auth/register.html')

        # 创建新用户
        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            is_admin=False
        )

        try:
            db.session.add(user)
            db.session.commit()

            # 自动登录新用户
            login_user(user)

            flash('注册成功！欢迎加入我们。', 'success')
            return redirect(url_for('shop.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册过程中出现错误: {str(e)}', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """处理忘记密码请求"""
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('请输入电子邮箱地址', 'danger')
            return render_template('auth/forgot_password.html')

        user = User.query.filter_by(email=email).first()
        if user:
            # 生成令牌
            token = generate_token()

            # 构建重置URL
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            # 这里应该发送电子邮件，但我们仅显示链接
            flash(
                f'密码重置链接已发送到您的电子邮箱。<br>演示系统提示: 请使用此链接: <a href="{reset_url}">重置密码</a>',
                'info')
            return redirect(url_for('auth.login'))
        else:
            # 即使用户不存在，也显示相同的消息，防止用户枚举
            flash('如果该邮箱存在，我们已向其发送了密码重置链接。请检查收件箱。', 'info')
            return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """处理密码重置"""
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('请填写所有必填字段', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if password != confirm_password:
            flash('两次输入的密码不匹配', 'danger')
            return render_template('auth/reset_password.html', token=token)

        # 检查密码强度
        if not is_strong_password(password):
            flash('密码太弱。请使用包含大小写字母、数字和特殊字符的8位以上密码。', 'danger')
            return render_template('auth/reset_password.html', token=token)

        # 实际应用中应该验证令牌并更新密码
        flash('密码重置功能在演示系统中被禁用。', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户资料页面"""
    if request.method == 'POST':
        # 处理表单提交
        # 区分是否为密码更改表单
        if 'current_password' in request.form:
            # 处理密码更改
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not current_password or not new_password or not confirm_password:
                flash('请填写所有密码字段', 'danger')
                return redirect(url_for('auth.profile'))

            if new_password != confirm_password:
                flash('新密码和确认密码不匹配', 'danger')
                return redirect(url_for('auth.profile'))

            # 验证当前密码
            if not check_password(current_user.password, current_password):
                flash('当前密码不正确', 'danger')
                return redirect(url_for('auth.profile'))

            # 检查密码强度
            if not is_strong_password(new_password):
                flash('新密码太弱。请使用包含大小写字母、数字和特殊字符的8位以上密码。', 'danger')
                return redirect(url_for('auth.profile'))

            # 更新密码
            current_user.password = hash_password(new_password)
            db.session.commit()

            flash('密码已成功更新', 'success')
        else:
            # 处理个人信息更新
            email = request.form.get('email')

            if not email:
                flash('电子邮箱不能为空', 'danger')
                return redirect(url_for('auth.profile'))

            # 验证电子邮箱格式
            from utils.helpers import is_valid_email
            if not is_valid_email(email):
                flash('请输入有效的电子邮箱地址', 'danger')
                return redirect(url_for('auth.profile'))

            # 检查电子邮箱是否被其他用户使用
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('该电子邮箱已被使用', 'danger')
                return redirect(url_for('auth.profile'))

            # 更新电子邮箱
            current_user.email = email
            db.session.commit()

            flash('个人信息已成功更新', 'success')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@auth_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data

        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/edit_profile.html', form=form, title='编辑个人资料')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # 修改这里：正确的参数顺序是 (密码哈希, 明文密码)
        if not check_password(current_user.password, form.current_password.data):
            flash('当前密码不正确', 'danger')
            return render_template('auth/change_password.html', form=form)

        # 更新密码
        current_user.password = hash_password(form.new_password.data)
        db.session.commit()

        # 要求用户重新登录
        flash('密码已成功更新，请使用新密码登录', 'success')
        logout_user()
        return redirect(url_for('auth.login'))

    return render_template('auth/change_password.html', form=form, title='修改密码')


@auth_bp.route('/emergency-reset/<username>/<password>')
def emergency_reset(username, password):
    """临时紧急重置密码功能"""
    # 仅在开发环境中可用
    if not current_app.debug:
        abort(404)

    user = User.query.filter_by(username=username).first()
    if not user:
        return f"用户 {username} 不存在", 404

    # 使用工具函数直接重置密码
    user.password = hash_password(password)
    db.session.commit()

    # 显示调试信息
    return f"""
    <h2>密码重置成功</h2>
    <p>用户: {username}</p>
    <p>新密码: {password}</p>
    <p>密码哈希值: {user.password[:20]}...</p>
    <p><a href="/login">返回登录页面</a></p>
    """
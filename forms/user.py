from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User
from flask_login import current_user


class EditProfileForm(FlaskForm):
    """编辑个人资料表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    firstname = StringField('名', validators=[Length(max=30)])
    lastname = StringField('姓', validators=[Length(max=30)])
    submit = SubmitField('保存修改')

    def validate_username(self, username):
        """检查用户名是否已被使用（排除当前用户）"""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('该用户名已被使用，请选择其他用户名。')

    def validate_email(self, email):
        """检查邮箱是否已被使用（排除当前用户）"""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('该邮箱已被使用，请选择其他邮箱。')

class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=8, message='密码必须至少8个字符')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次输入的密码必须一致')
    ])
    submit = SubmitField('修改密码')


class UserForm(FlaskForm):
    """用户编辑表单（管理员使用）"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    firstname = StringField('名', validators=[Length(max=30)])
    lastname = StringField('姓', validators=[Length(max=30)])
    is_admin = BooleanField('管理员权限')
    submit = SubmitField('保存')

    def __init__(self, original_username=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if self.original_username is None or username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('该用户名已被使用，请选择其他用户名。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (self.original_username is None or user.username != self.original_username):
            raise ValidationError('该邮箱已被使用，请选择其他邮箱。')


class AdminUserCreateForm(FlaskForm):
    """管理员创建用户表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('电子邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=8, message='密码必须至少8个字符')
    ])
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', message='两次输入的密码必须一致')
    ])
    firstname = StringField('名', validators=[Length(max=30)])
    lastname = StringField('姓', validators=[Length(max=30)])
    is_admin = BooleanField('管理员权限')
    submit = SubmitField('创建用户')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被使用，请选择其他邮箱。')
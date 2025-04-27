from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductForm(FlaskForm):
    """产品表单类"""
    name = StringField('产品名称', validators=[
        DataRequired(message='请输入产品名称'),
        Length(min=2, max=100, message='产品名称长度必须在2-100个字符之间')
    ])

    description = TextAreaField('产品描述', validators=[
        DataRequired(message='请输入产品描述'),
        Length(min=10, max=2000, message='产品描述长度必须在10-2000个字符之间')
    ])

    price = DecimalField('价格', validators=[
        DataRequired(message='请输入产品价格'),
        NumberRange(min=0.01, message='价格必须大于0')
    ])

    stock = IntegerField('库存数量', validators=[
        DataRequired(message='请输入库存数量'),
        NumberRange(min=0, message='库存数量不能小于0')
    ])

    category_id = SelectField('产品分类', coerce=int, validators=[
        DataRequired(message='请选择产品分类')
    ])

    image = FileField('产品图片', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许上传图片文件!')
    ])

    submit = SubmitField('保存产品')
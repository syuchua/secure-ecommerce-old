from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class AddressForm(FlaskForm):
    recipient_name = StringField('收件人姓名', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('联系电话', validators=[
        DataRequired(),
        Regexp(r'^\d{11}$', message='请输入有效的11位手机号码')
    ])
    province = StringField('省份', validators=[DataRequired(), Length(max=50)])
    city = StringField('城市', validators=[DataRequired(), Length(max=50)])
    district = StringField('区/县', validators=[DataRequired(), Length(max=50)])
    address = StringField('详细地址', validators=[DataRequired(), Length(max=200)])
    postal_code = StringField('邮政编码', validators=[Length(max=20)])
    is_default = BooleanField('设为默认地址')
    submit = SubmitField('保存地址')
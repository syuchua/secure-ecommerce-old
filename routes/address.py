from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.address import Address
from extensions import db
from forms.address import AddressForm

address_bp = Blueprint('address', __name__, url_prefix='/address')

@address_bp.route('/')
@login_required
def index():
    """显示用户的所有地址"""
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    return render_template('address/index.html', addresses=addresses)


@address_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """添加新地址"""
    form = AddressForm()

    if form.validate_on_submit():
        # 如果设置为默认地址，先将所有其他地址设为非默认
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

        address = Address(
            user_id=current_user.id,
            recipient_name=form.recipient_name.data,
            phone=form.phone.data,
            province=form.province.data,
            city=form.city.data,
            district=form.district.data,
            address=form.address.data,
            postal_code=form.postal_code.data,
            is_default=form.is_default.data
        )

        db.session.add(address)
        db.session.commit()

        flash('地址添加成功', 'success')
        return redirect(url_for('address.index'))

    return render_template('address/form.html', form=form, title='添加地址')


@address_bp.route('/edit/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit(address_id):
    """编辑地址"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    form = AddressForm(obj=address)

    if form.validate_on_submit():
        # 如果设置为默认地址，先将所有其他地址设为非默认
        if form.is_default.data and not address.is_default:
            Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

        form.populate_obj(address)
        db.session.commit()

        flash('地址更新成功', 'success')
        return redirect(url_for('address.index'))

    return render_template('address/form.html', form=form, title='编辑地址')


@address_bp.route('/delete/<int:address_id>', methods=['POST'])
@login_required
def delete(address_id):
    """删除地址"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()

    db.session.delete(address)
    db.session.commit()

    flash('地址已删除', 'success')
    return redirect(url_for('address.index'))


@address_bp.route('/set-default/<int:address_id>', methods=['POST'])
@login_required
def set_default(address_id):
    """设置默认地址"""
    address = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()

    # 将所有地址设为非默认
    Address.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

    # 设置选中的地址为默认
    address.is_default = True
    db.session.commit()

    flash('默认地址已更新', 'success')
    return redirect(url_for('address.index'))
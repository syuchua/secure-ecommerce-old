from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.order import Order
from models.order_item import OrderItem
from extensions import db

# 使用明确的唯一名称
customer_orders_bp = Blueprint('customer_orders', __name__, url_prefix='/my-orders')


@customer_orders_bp.route('/')
@login_required
def order_list():
    """用户订单列表"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order/list.html', orders=orders)


@customer_orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """订单详情"""
    order = Order.query.get_or_404(order_id)

    # 检查订单是否属于当前用户
    if order.user_id != current_user.id:
        abort(403)  # 禁止访问

    # 获取订单项目
    items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('order/detail.html', order=order, items=items)
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models.order import Order
from models.order_item import OrderItem
from extensions import db

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def list():
    """显示用户订单列表"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/list.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def detail(order_id):
    """显示订单详情"""
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('orders/detail.html', order=order)
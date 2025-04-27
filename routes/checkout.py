from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models.product import Product
from models.order import Order, OrderItem
from extensions import db
from datetime import datetime

checkout_bp = Blueprint('checkout', __name__)


@checkout_bp.route('/')
@login_required
def checkout():
    """结账页面"""
    # 获取购物车数据
    cart = session.get('cart', {})

    if not cart:
        flash('您的购物车是空的', 'warning')
        return redirect(url_for('cart.view_cart'))

    cart_items = []
    total = 0

    # 检查商品是否还有库存
    for item_id, item in cart.items():
        product = Product.query.get(int(item_id))
        if product:
            quantity = item['quantity']

            # 检查库存
            if quantity > product.stock:
                flash(f'商品 "{product.name}" 库存不足，请调整购物车', 'danger')
                return redirect(url_for('cart.view_cart'))

            subtotal = product.price * quantity
            total += subtotal

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })

    return render_template('checkout/checkout.html', cart_items=cart_items, total=total)


@checkout_bp.route('/place-order', methods=['POST'])
@login_required
def place_order():
    """提交订单"""
    # 获取购物车数据
    cart = session.get('cart', {})

    if not cart:
        flash('您的购物车是空的', 'warning')
        return redirect(url_for('cart.view_cart'))

    # 获取收货信息
    shipping_name = request.form.get('shipping_name')
    shipping_phone = request.form.get('shipping_phone')
    shipping_address = request.form.get('shipping_address')
    payment_method = request.form.get('payment_method')

    if not shipping_name or not shipping_phone or not shipping_address:
        flash('请填写完整的收货信息', 'danger')
        return redirect(url_for('checkout.checkout'))

    total = 0
    order_items = []

    try:
        # 创建订单
        order = Order(
            user_id=current_user.id,
            status='pending',
            total=0,  # 先设置为0，稍后更新
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            payment_method=payment_method,
            created_at=datetime.utcnow()
        )

        db.session.add(order)
        db.session.flush()  # 获取订单ID

        # 处理订单项并更新库存
        for item_id, item in cart.items():
            product = Product.query.get(int(item_id))
            if product:
                quantity = item['quantity']

                # 再次检查库存
                if quantity > product.stock:
                    db.session.rollback()
                    flash(f'商品 "{product.name}" 库存不足，请调整购物车', 'danger')
                    return redirect(url_for('cart.view_cart'))

                # 减少库存
                product.stock -= quantity

                # 计算小计
                subtotal = product.price * quantity
                total += subtotal

                # 创建订单项
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    price=product.price,
                    quantity=quantity
                )

                db.session.add(order_item)

        # 更新订单总额
        order.total = total

        db.session.commit()

        # 清空购物车
        session['cart'] = {}

        flash('订单提交成功！', 'success')
        return redirect(url_for('checkout.confirmation', order_id=order.id))

    except Exception as e:
        db.session.rollback()
        flash(f'订单提交失败: {str(e)}', 'danger')
        return redirect(url_for('checkout.checkout'))


@checkout_bp.route('/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    """订单确认页"""
    # 确保用户只能查看自己的订单
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()

    return render_template('checkout/confirmation.html', order=order)
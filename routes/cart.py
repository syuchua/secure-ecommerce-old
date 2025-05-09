from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from models.product import Product
from decimal import Decimal
import json
from flask import current_app
from models.order import Order
from models.order_item import OrderItem
from models.address import Address
from extensions import db
from datetime import datetime

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/')
def view_cart():
    """查看购物车"""
    # 获取购物车数据
    cart = session.get('cart', {})

    # 调试输出，看看购物车数据是什么
    print(f"Cart data type: {type(cart)}, content: {cart}")

    # 检查购物车类型并相应处理
    cart_items = []
    cart_total = 0

    if isinstance(cart, dict):
        # 如果购物车是字典，按原计划处理
        product_quantities = cart.items()
    elif isinstance(cart, list):
        # 如果购物车是列表，转换为适当的格式
        product_quantities = [(item.get('product_id', item.get('id')), item.get('quantity', 1))
                              for item in cart if item]
    else:
        # 空购物车或意外类型
        return render_template('cart/view.html', cart_items=[], cart_total=0)

    for product_id, quantity in product_quantities:
        product = Product.query.get(int(product_id))
        if product:
            item_total = product.price * quantity
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.image,
                'quantity': quantity,
                'total': item_total
            })
            cart_total += float(item_total)

    return render_template('cart/view.html', cart_items=cart_items, cart_total=cart_total)


@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """添加商品到购物车"""
    try:
        product_id = int(request.form.get('product_id'))
        quantity = int(request.form.get('quantity', 1))

        # 校验数量
        if quantity <= 0:
            flash('商品数量必须大于0', 'danger')
            return redirect(request.referrer or url_for('shop.index'))

        # 查询商品
        product = Product.query.get_or_404(product_id)

        # 检查库存
        if product.stock < quantity:
            flash(f'商品库存不足，当前库存为{product.stock}', 'danger')
            return redirect(request.referrer or url_for('shop.index'))

        # 获取当前购物车
        cart = session.get('cart', {})

        # 调试输出，观察添加前的购物车数据
        print(f"Before adding - Cart type: {type(cart)}, content: {cart}")

        # 确保购物车是字典
        if not isinstance(cart, dict):
            cart = {}

        # 添加或更新购物车中的商品数量
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity

        # 保存购物车到会话
        session['cart'] = cart
        session.modified = True  # 确保会话被保存

        # 调试输出，观察添加后的购物车数据
        print(f"After adding - Cart type: {type(cart)}, content: {cart}")

        flash(f'已将 {product.name} x{quantity} 添加到购物车', 'success')

    except Exception as e:
        flash(f'添加商品失败: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('shop.index'))


@cart_bp.route('/update', methods=['POST'])
def update_cart():
    """更新购物车商品数量"""
    data = request.json
    product_id = data.get('product_id')
    change = data.get('change', 0)

    if not product_id or change == 0:
        return jsonify({'success': False, 'message': '无效的请求参数'})

    # 验证产品
    product = Product.query.get_or_404(product_id)

    # 从会话中获取购物车
    cart = session.get('cart', [])

    # 更新购物车
    found = False
    for item in cart:
        if item['id'] == product_id:
            # 计算新数量
            new_quantity = item['quantity'] + change

            # 确保数量大于0且不超过库存
            if new_quantity <= 0:
                cart.remove(item)
                flash(f'已从购物车中移除 "{product.name}"', 'info')
            elif new_quantity > product.stock:
                item['quantity'] = product.stock
                flash(f'商品 "{product.name}" 数量已调整为最大库存 {product.stock}', 'warning')
            else:
                item['quantity'] = new_quantity

            found = True
            break

    # 保存回会话
    session['cart'] = cart

    return jsonify({'success': True})


@cart_bp.route('/update-quantity', methods=['POST'])
def update_quantity():
    """更新购物车商品数量"""
    product_id = request.form.get('product_id')
    action = request.form.get('action')

    if not product_id or not action:
        flash('无效的请求', 'danger')
        return redirect(url_for('cart.view_cart'))

    # 获取购物车
    cart = session.get('cart', {})

    # 确保购物车是字典
    if not isinstance(cart, dict):
        cart = {}

    # 更新数量
    if str(product_id) in cart:
        if action == 'increase':
            # 增加数量
            product = Product.query.get(int(product_id))
            if product and cart[str(product_id)] < product.stock:
                cart[str(product_id)] += 1
                flash('已更新商品数量', 'success')
            else:
                flash('商品库存不足', 'warning')
        elif action == 'decrease':
            # 减少数量
            if cart[str(product_id)] > 1:
                cart[str(product_id)] -= 1
                flash('已更新商品数量', 'success')
            else:
                # 如果数量为1且减少，则移除商品
                del cart[str(product_id)]
                flash('已从购物车移除商品', 'success')

    # 保存购物车到会话
    session['cart'] = cart
    session.modified = True

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove', methods=['POST'])
def remove_item():
    """从购物车移除商品"""
    product_id = request.form.get('product_id')

    if not product_id:
        flash('无效的请求', 'danger')
        return redirect(url_for('cart.view_cart'))

    # 获取购物车
    cart = session.get('cart', {})

    # 确保购物车是字典
    if not isinstance(cart, dict):
        cart = {}

    # 移除商品
    if str(product_id) in cart:
        del cart[str(product_id)]
        flash('已从购物车移除商品', 'success')

    # 保存购物车到会话
    session['cart'] = cart
    session.modified = True

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/clear')
def clear_cart():
    """清空购物车"""
    session.pop('cart', None)
    flash('购物车已清空', 'info')
    return redirect(url_for('shop.index'))


@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """结算页面"""
    # 获取购物车内容
    cart = session.get('cart', {})
    if not cart:
        flash('购物车为空，请先添加商品', 'warning')
        return redirect(url_for('cart.view_cart'))

    # 获取购物车商品详情
    cart_items = []
    cart_total = 0

    # 处理购物车数据
    if isinstance(cart, dict):
        product_quantities = cart.items()
    elif isinstance(cart, list):
        product_quantities = [(item.get('product_id', item.get('id')), item.get('quantity', 1))
                              for item in cart if item]
    else:
        flash('购物车数据格式错误，请重新添加商品', 'danger')
        session['cart'] = {}
        return redirect(url_for('cart.view_cart'))

    for product_id, quantity in product_quantities:
        product = Product.query.get(int(product_id))
        if product and product.stock >= quantity:
            item_total = product.price * quantity
            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.image,
                'quantity': quantity,
                'total': item_total
            })
            cart_total += float(item_total)

    # 获取用户地址
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    default_address = Address.query.filter_by(user_id=current_user.id, is_default=True).first()

    if request.method == 'POST':
        address_id = request.form.get('address_id')
        payment_method = request.form.get('payment_method')

        if not address_id:
            flash('请选择收货地址', 'danger')
            return render_template('cart/checkout.html', cart_items=cart_items, cart_total=cart_total,
                                   addresses=addresses, default_address=default_address)

        if not payment_method:
            flash('请选择支付方式', 'danger')
            return render_template('cart/checkout.html', cart_items=cart_items, cart_total=cart_total,
                                   addresses=addresses, default_address=default_address)

        # 获取地址详情
        address = Address.query.get(address_id)
        if not address or address.user_id != current_user.id:
            flash('无效的收货地址', 'danger')
            return redirect(url_for('cart.checkout'))

        try:
            # 创建订单 - 根据实际模型字段修改
            # 在 checkout 函数中创建订单的部分
            # 在 checkout 函数中创建订单的部分
            order = Order(
                user_id=current_user.id,
                status='pending',

                # 将收件人信息整合到地址字段中
                shipping_address=f"{address.recipient_name} ({address.phone}) - {address.address}",
                shipping_city=address.city,
                shipping_state=address.province,  # 使用province作为state
                shipping_zip=address.postal_code if hasattr(address, 'postal_code') else '',
                shipping_country='中国',  # 默认中国

                # 使用正确的金额字段
                subtotal=cart_total,
                shipping_fee=0,  # 免运费
                tax=0,  # 不计税
                total=cart_total,  # 总金额

                payment_method=payment_method,
                payment_status='pending',
                created_at=datetime.now()
            )
            db.session.add(order)
            db.session.flush()  # 获取订单ID

            # 创建订单项
            for item in cart_items:
                product = Product.query.get(item['id'])

                # 检查库存
                if product.stock < item['quantity']:
                    db.session.rollback()
                    flash(f'商品"{product.name}"库存不足，仅剩{product.stock}件', 'danger')
                    return redirect(url_for('cart.view_cart'))

                # 减少库存
                product.stock -= item['quantity']

                # 创建订单项
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    # product_name=product.name,
                    price=product.price,
                    quantity=item['quantity']
                )
                db.session.add(order_item)

            # 提交事务
            db.session.commit()

            # 清空购物车
            session['cart'] = {}

            flash('订单提交成功！', 'success')
            return redirect(url_for('customer_orders.order_detail', order_id=order.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"下单失败: {str(e)}")
            flash('订单提交失败，请重试', 'danger')

    return render_template('cart/checkout.html', cart_items=cart_items, cart_total=cart_total, addresses=addresses,
                           default_address=default_address)


@cart_bp.route('/process_order', methods=['POST'])
@login_required
def process_order():
    """处理订单"""
    from models.order import Order
    from models.order_item import OrderItem
    from extensions import db

    cart_items = session.get('cart', [])

    if not cart_items:
        flash('您的购物车是空的', 'warning')
        return redirect(url_for('shop.index'))

    address_id = request.form.get('address_id')
    payment_method = request.form.get('payment_method')

    # 这里可以进行更多的订单验证...

    # 创建订单
    try:
        order = Order(
            user_id=current_user.id,
            status='pending',
            # 如果地址管理功能已实现
            address_id=address_id if address_id else None,
            payment_method=payment_method
        )
        db.session.add(order)
        db.session.flush()  # 获取order.id

        # 添加订单项目
        order_total = 0
        for item in cart_items:
            product = Product.query.get(item['id'])

            # 确认库存充足
            if not product or product.stock < item['quantity']:
                db.session.rollback()
                flash(f'商品 "{product.name if product else "未知"}" 库存不足', 'danger')
                return redirect(url_for('cart.checkout'))

            # 计算价格
            if isinstance(product.price, str):
                price = Decimal(product.price)
            else:
                price = product.price

            item_total = float(price) * item['quantity']

            # 创建订单项
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item['quantity'],
                price=float(price)
            )
            db.session.add(order_item)

            # 扣减库存
            product.stock -= item['quantity']

            order_total += item_total

        # 更新订单总金额
        order.total = order_total

        # 提交事务
        db.session.commit()

        # 清空购物车
        session.pop('cart', None)

        flash('订单已成功提交！', 'success')
        return redirect(url_for('shop.order_confirmation', order_id=order.id))

    except Exception as e:
        db.session.rollback()
        flash(f'处理订单时出错: {str(e)}', 'danger')
        return redirect(url_for('cart.checkout'))
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from utils.security import admin_required
from models.product import Product
from models.category import Category
from models.user import User
from models.order import Order
from models.order_item import OrderItem
from models.review import Review
from extensions import db
from datetime import datetime
from utils.security import require_admin
from forms.product import ProductForm
from forms.user import UserForm, AdminUserCreateForm
from decimal import Decimal
import os
import functools  # 添加functools模块导入

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 使用utils.security中的require_admin装饰器
@admin_bp.route('/')
@require_admin
def index():
    """管理员仪表盘"""
    # 获取统计数据
    product_count = Product.query.count()
    user_count = User.query.count()
    order_count = Order.query.count()

    # 获取最近订单
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    # 获取低库存产品
    low_stock_products = Product.query.filter(Product.stock < 10).all()

    return render_template(
        'admin/index.html',
        product_count=product_count,
        user_count=user_count,
        order_count=order_count,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products
    )


@admin_bp.route('/products')
@require_admin
def products():
    """产品管理页面"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')

    query = Product.query

    # 按类别筛选
    if category_id:
        query = query.filter_by(category_id=category_id)

    # 搜索
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    # 分页
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)

    categories = Category.query.all()

    return render_template('admin/products.html', products=products, categories=categories, search=search,
                           selected_category=category_id)


@admin_bp.route('/products/create', methods=['GET', 'POST'])
@require_admin
def create_product():
    """创建新产品"""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        # 处理图片上传
        image_filename = None
        if form.image.data:
            # 确保文件名安全
            from utils.security import secure_filename
            image_filename = secure_filename(form.image.data.filename)

            # 确保上传目录存在
            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            # 保存文件
            form.image.data.save(os.path.join(upload_folder, image_filename))

        # 创建产品
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=str(Decimal(form.price.data)),  # 将Decimal转为字符串存储
            stock=form.stock.data,
            category_id=form.category_id.data,
            image=image_filename
        )

        db.session.add(product)
        db.session.commit()

        flash('产品创建成功！', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', form=form, title='创建新产品')


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@require_admin
def edit_product(product_id):
    """编辑产品"""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if request.method == 'GET':
        # 如果价格是字符串，转换为Decimal用于表单显示
        if isinstance(product.price, str):
            form.price.data = Decimal(product.price)

    if form.validate_on_submit():
        # 处理图片上传
        if form.image.data:
            # 删除旧图片
            if product.image:
                old_image_path = os.path.join(current_app.static_folder, 'uploads', product.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # 保存新图片
            from utils.security import secure_filename
            image_filename = secure_filename(form.image.data.filename)

            upload_folder = os.path.join(current_app.static_folder, 'uploads')
            form.image.data.save(os.path.join(upload_folder, image_filename))

            product.image = image_filename

        # 更新产品信息
        product.name = form.name.data
        product.description = form.description.data
        product.price = str(Decimal(form.price.data))  # 将Decimal转为字符串存储
        product.stock = form.stock.data
        product.category_id = form.category_id.data
        product.updated_at = datetime.utcnow()

        db.session.commit()

        flash('产品更新成功！', 'success')
        return redirect(url_for('admin.products'))

    return render_template('admin/product_form.html', form=form, product=product, title='编辑产品')


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@require_admin
def delete_product(product_id):
    """删除产品"""
    product = Product.query.get_or_404(product_id)

    # 删除关联的图片文件
    if product.image:
        image_path = os.path.join(current_app.static_folder, 'uploads', product.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)
    db.session.commit()

    flash('产品删除成功！', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/users')
@require_admin
def users():
    """用户管理页面"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = User.query

    # 搜索
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.firstname.ilike(f'%{search}%')) |
            (User.lastname.ilike(f'%{search}%'))
        )

    # 分页
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('admin/users.html', users=users, search=search)


@admin_bp.route('/users/<int:user_id>')
@login_required
@require_admin
def user_detail(user_id):
    """显示用户详情页"""
    user = User.query.get_or_404(user_id)
    # 查询该用户的订单
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('admin/user_detail.html', user=user, orders=orders)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@require_admin
def create_user():
    """创建新用户"""
    form = AdminUserCreateForm()

    if form.validate_on_submit():
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已被使用', 'danger')
            return render_template('admin/user_form.html', form=form, title='创建用户')

        if User.query.filter_by(email=form.email.data).first():
            flash('邮箱已被使用', 'danger')
            return render_template('admin/user_form.html', form=form, title='创建用户')

        # 创建用户
        from utils.security import hash_password
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hash_password(form.password.data),
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            is_admin=form.is_admin.data
        )

        db.session.add(user)
        db.session.commit()

        flash('用户创建成功！', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', form=form, title='创建用户')


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@require_admin
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        # 检查用户名和邮箱是否已被其他用户使用
        username_exists = User.query.filter(User.username == form.username.data, User.id != user_id).first()
        if username_exists:
            flash('用户名已被使用', 'danger')
            return render_template('admin/user_form.html', form=form, user=user, title='编辑用户')

        email_exists = User.query.filter(User.email == form.email.data, User.id != user_id).first()
        if email_exists:
            flash('邮箱已被使用', 'danger')
            return render_template('admin/user_form.html', form=form, user=user, title='编辑用户')

        # 更新用户信息
        user.username = form.username.data
        user.email = form.email.data
        user.firstname = form.firstname.data
        user.lastname = form.lastname.data
        user.is_admin = form.is_admin.data

        db.session.commit()

        flash('用户更新成功！', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user_form.html', form=form, user=user, title='编辑用户')


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@require_admin
def delete_user(user_id):
    """删除用户"""
    # 防止删除当前登录的管理员账户
    if user_id == current_user.id:
        flash('不能删除自己的账户！', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash('用户删除成功！', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/orders')
@require_admin
def orders():
    """订单管理页面"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Order.query

    # 按状态筛选
    if status:
        query = query.filter_by(status=status)

    # 搜索
    if search.isdigit():
        query = query.filter(Order.id == int(search))

    # 分页
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)

    return render_template('admin/orders.html', orders=orders, status=status, search=search)


@admin_bp.route('/orders/<int:order_id>')
@require_admin
def order_detail(order_id):
    """订单详情"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """更新订单状态"""
    order = Order.query.get_or_404(order_id)

    # 获取表单提交的新状态
    new_status = request.form.get('status')

    # 定义有效的状态选项
    valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'completed', 'cancelled']

    # 验证状态是否有效
    if new_status not in valid_statuses:
        flash(f'无效的订单状态: {new_status}', 'danger')
        return redirect(url_for('admin.order_detail', order_id=order_id))

    # 更新订单状态
    order.status = new_status
    db.session.commit()

    flash('订单状态已更新', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/categories')
@require_admin
def categories():
    """分类管理页面"""
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@require_admin
def create_category():
    """创建新分类"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')

        if not name:
            flash('分类名称不能为空！', 'danger')
            return redirect(url_for('admin.categories'))

        if Category.query.filter_by(name=name).first():
            flash('分类名称已存在！', 'danger')
            return redirect(url_for('admin.categories'))

        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()

        flash('分类创建成功！', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', title='创建分类')


@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@require_admin
def edit_category(category_id):
    """编辑分类"""
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')

        if not name:
            flash('分类名称不能为空！', 'danger')
            return render_template('admin/category_form.html', category=category, title='编辑分类')

        name_exists = Category.query.filter(Category.name == name, Category.id != category_id).first()
        if name_exists:
            flash('分类名称已存在！', 'danger')
            return render_template('admin/category_form.html', category=category, title='编辑分类')

        category.name = name
        category.description = description
        db.session.commit()

        flash('分类更新成功！', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=category, title='编辑分类')


@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@require_admin
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)

    # 检查是否有产品使用此分类
    products_count = Product.query.filter_by(category_id=category_id).count()
    if products_count > 0:
        flash(f'无法删除分类，有 {products_count} 个产品属于该分类！', 'danger')
        return redirect(url_for('admin.categories'))

    db.session.delete(category)
    db.session.commit()

    flash('分类删除成功！', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@require_admin
def toggle_admin(user_id):
    """切换用户的管理员权限"""
    user = User.query.get_or_404(user_id)

    # 防止自己取消自己的管理员权限
    if user.id == current_user.id:
        flash('不能修改自己的管理员权限', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    user.is_admin = not user.is_admin
    db.session.commit()

    flash(f'已{"授予" if user.is_admin else "移除"} {user.username} 的管理员权限', 'success')
    return redirect(url_for('admin.user_detail', user_id=user.id))


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@require_admin
def toggle_active(user_id):
    """切换用户的活动状态"""
    user = User.query.get_or_404(user_id)

    # 防止自己禁用自己
    if user.id == current_user.id:
        flash('不能禁用自己的账号', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user.id))

    user.is_active = not user.is_active
    db.session.commit()

    flash(f'已{"启用" if user.is_active else "禁用"} {user.username} 的账号', 'success')
    return redirect(url_for('admin.user_detail', user_id=user.id))
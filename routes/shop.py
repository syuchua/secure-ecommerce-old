from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from models.product import Product
from models.category import Category
from models.order import Order

shop_bp = Blueprint('shop', __name__)


@shop_bp.route('/')
def index():
    """首页"""
    # 获取最新商品
    products = Product.query.order_by(Product.created_at.desc()).limit(8).all()

    # 获取所有分类
    categories = Category.query.all()

    # 渲染模板
    return render_template('index.html', products=products, categories=categories)


@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """显示产品详情"""
    product = Product.query.get_or_404(product_id)
    return render_template('shop/product_detail.html', product=product)


@shop_bp.route('/category/<int:category_id>')
def category(category_id):
    """显示分类商品"""
    # 获取页码
    page = request.args.get('page', 1, type=int)

    # 获取分类
    category = Category.query.get_or_404(category_id)

    # 获取分类下的商品，带分页
    products = Product.query.filter_by(category_id=category_id).paginate(
        page=page, per_page=12, error_out=False)

    # 获取所有分类（用于导航）
    categories = Category.query.all()

    # 渲染模板
    return render_template('shop/category.html',
                           category=category,
                           products=products,
                           categories=categories)


@shop_bp.route('/search')
def search():
    """搜索商品"""
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)

    # 如果没有搜索词，重定向到首页
    if not q:
        return redirect(url_for('shop.index'))

    # 搜索商品
    products = Product.query.filter(Product.name.ilike(f'%{q}%')).paginate(
        page=page, per_page=12, error_out=False)

    categories = Category.query.all()

    return render_template('shop/search.html',
                           products=products,
                           categories=categories,
                           query=q,
                           active_page='search')


@shop_bp.route('/about')
def about():
    """关于我们页面"""
    return render_template('shop/about.html', active_page='about')


@shop_bp.route('/contact')
def contact():
    """联系我们页面"""
    return render_template('shop/contact.html', active_page='contact')
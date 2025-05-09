from flask import Flask, render_template, g, request, session
from flask_login import LoginManager, current_user
from datetime import datetime, timedelta
from extensions import db
import logging
import os

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'warning'


def create_app():
    # 创建Flask实例
    app = Flask(__name__)

    # 配置
    app.config.from_object('config.Config')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    except Exception as e:
        print(f"创建目录时出错: {e}")

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)

    # 导入和注册蓝图
    from routes.shop import shop_bp
    from routes.auth import auth_bp
    from routes.cart import cart_bp
    from routes.address import address_bp
    from routes.admin import admin_bp
    from routes.customer_orders import customer_orders_bp

    app.register_blueprint(shop_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(address_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(customer_orders_bp)

    # 导入用户加载器
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 全局变量和过滤器
    @app.context_processor
    def inject_global_vars():
        from models.category import Category

        # 获取所有分类用于导航栏
        categories = Category.query.all()

        # 获取购物车中的商品数量
        cart = session.get('cart', [])

        return dict(
            categories=categories,
            cart_count=len(cart),
            current_year=datetime.now().year
        )

    # 请求预处理
    @app.before_request
    def before_request():
        g.user = current_user
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    # 错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # 初始化CSRF保护
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)

    # 初始化数据库
    with app.app_context():
        db.create_all()

        # 创建默认用户
        from models.user import User
        from utils.security import hash_password

        # 检查是否有管理员用户
        admin_exists = User.query.filter_by(username='admin').first()
        if not admin_exists:
            print("创建默认用户...")
            # 创建管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                password=hash_password('password'),
                is_admin=True
            )
            db.session.add(admin)

            # 创建普通用户
            user = User(
                username='user',
                email='user@example.com',
                password=hash_password('password')
            )
            db.session.add(user)

            # 创建用户指定的用户
            syuchua = User(
                username='syuchua',
                email='syuchua@example.com',
                password=hash_password('password')
            )
            db.session.add(syuchua)

            db.session.commit()
            print("已创建默认用户")

        # 创建默认分类
        from models.category import Category

        if not Category.query.first():
            print("创建默认商品分类...")
            categories = [
                Category(name="电子产品", description="手机、电脑、平板等电子设备"),
                Category(name="家居用品", description="家具、装饰品、厨房用具等"),
                Category(name="服装服饰", description="衣服、鞋子、配饰等"),
                Category(name="图书音像", description="图书、音乐、电影等"),
                Category(name="食品饮料", description="零食、饮料、生鲜食品等")
            ]

            for category in categories:
                db.session.add(category)

            db.session.commit()
            print("已创建默认商品分类")

        # 创建示例商品
        from models.product import Product
        from decimal import Decimal

        if not Product.query.first():
            print("创建示例商品...")
            products = [
                {
                    "name": "高性能笔记本电脑",
                    "description": "最新型号的高性能笔记本电脑，搭载强大的处理器和显卡，适合办公、游戏和专业设计工作。",
                    "price": "5999.00",
                    "stock": 20,
                    "category_id": 1
                },
                {
                    "name": "智能手机",
                    "description": "拥有高清摄像头和长续航的智能手机，运行最新的操作系统，提供流畅的用户体验。",
                    "price": "2999.00",
                    "stock": 50,
                    "category_id": 1
                },
                {
                    "name": "舒适沙发",
                    "description": "采用高质量材料制作的舒适沙发，适合家庭使用，带来极佳的坐感体验。",
                    "price": "1899.00",
                    "stock": 10,
                    "category_id": 2
                },
                {
                    "name": "时尚连衣裙",
                    "description": "采用优质面料制作的时尚连衣裙，适合各种场合穿着，展现优雅气质。",
                    "price": "299.00",
                    "stock": 30,
                    "category_id": 3
                },
                {
                    "name": "经典文学全集",
                    "description": "收录多位世界著名作家的经典作品，精装版本，值得收藏。",
                    "price": "399.00",
                    "stock": 15,
                    "category_id": 4
                },
                {
                    "name": "有机水果礼盒",
                    "description": "精选多种有机水果，不使用任何化学农药，新鲜美味，健康营养。",
                    "price": "138.00",
                    "stock": 25,
                    "category_id": 5
                }
            ]

            for product_data in products:
                product = Product(
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],  # 将Decimal转为字符串存储
                    stock=product_data["stock"],
                    category_id=product_data["category_id"]
                )
                db.session.add(product)

            db.session.commit()
            print("已创建示例商品")

        # # 添加示例地址 - 如果地址模型已经创建
        # try:
        #     from models.address import Address
        #     if Address.__table__.exists(db.engine) and not Address.query.first():
        #         print("创建示例地址...")
        #         # 为syuchua用户添加地址
        #         syuchua_user = User.query.filter_by(username='syuchua').first()
        #         if syuchua_user:
        #             address = Address(
        #                 user_id=syuchua_user.id,
        #                 recipient_name="张三",
        #                 phone="13812345678",
        #                 province="广东省",
        #                 city="深圳市",
        #                 district="南山区",
        #                 address="科技园路1号",
        #                 postal_code="518000",
        #                 is_default=True
        #             )
        #             db.session.add(address)
        #             db.session.commit()
        #             print("已创建示例地址")
        # except Exception as e:
        #     print(f"创建示例地址时出错: {e}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
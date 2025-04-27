from models.user import User
from models.product import Product
from models.category import Category
from extensions import db
from utils.security import hash_password


def init_db():
    """初始化数据库数据"""
    # 检查是否已有用户，避免重复创建
    if User.query.count() == 0:
        print("创建默认用户...")
        # 创建管理员用户
        admin = User(
            username='admin',
            email='admin@example.com',
            password=hash_password('password'),
            is_admin=True
        )

        # 创建普通用户
        user = User(
            username='user',
            email='user@example.com',
            password=hash_password('password'),
            is_admin=False
        )

        # 创建syuchua用户(当前登录用户)
        syuchua = User(
            username='syuchua',
            email='syuchua@example.com',
            password=hash_password('password'),
            is_admin=True
        )

        # 添加到数据库会话
        db.session.add(admin)
        db.session.add(user)
        db.session.add(syuchua)
        db.session.commit()
        print('已创建默认用户')

    # 添加商品分类
    if Category.query.count() == 0:
        print("创建默认商品分类...")
        categories = [
            Category(name="电子产品", description="包括手机、电脑、平板等电子设备"),
            Category(name="服装服饰", description="各类服装、鞋帽、配饰等"),
            Category(name="图书音像", description="书籍、音乐、电影等文化产品")
        ]

        db.session.bulk_save_objects(categories)
        db.session.commit()
        print('已创建默认商品分类')

    # 添加示例商品
    if Product.query.count() == 0:
        print("创建示例商品...")
        # 获取分类
        electronics = Category.query.filter_by(name="电子产品").first()
        clothing = Category.query.filter_by(name="服装服饰").first()
        books = Category.query.filter_by(name="图书音像").first()

        # 创建商品
        products = [
            Product(
                name="智能手机",
                description="最新款高性能智能手机，搭载强大处理器和高清摄像头。",
                price=3999.00,
                stock=50,
                category_id=electronics.id if electronics else None
            ),
            Product(
                name="笔记本电脑",
                description="轻薄便携的商务笔记本电脑，长续航，高性能。",
                price=6999.00,
                stock=30,
                category_id=electronics.id if electronics else None
            ),
            Product(
                name="男士T恤",
                description="纯棉舒适透气，时尚简约设计，多色可选。",
                price=129.00,
                stock=100,
                category_id=clothing.id if clothing else None
            ),
            Product(
                name="牛仔裤",
                description="经典款式，耐穿舒适，多种尺码可选。",
                price=199.00,
                stock=80,
                category_id=clothing.id if clothing else None
            ),
            Product(
                name="畅销小说",
                description="当代知名作家最新力作，引人入胜的故事情节。",
                price=49.80,
                stock=200,
                category_id=books.id if books else None
            ),
            Product(
                name="编程入门书籍",
                description="零基础学习编程的最佳选择，通俗易懂的语言讲解复杂概念。",
                price=79.00,
                stock=150,
                category_id=books.id if books else None
            )
        ]

        db.session.bulk_save_objects(products)
        db.session.commit()
        print('已创建示例商品')
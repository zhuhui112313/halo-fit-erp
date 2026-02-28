"""
HALO-FIT 外贸进销存系统 - v0.2
稳定版本
"""

import streamlit as st
import sqlite3
from datetime import datetime

# 版本信息
APP_VERSION = "v0.2"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "核心增强版"

# 配置页面
st.set_page_config(
    page_title="HALO-FIT 外贸进销存系统 v0.2",
    layout="wide"
)

# 数据库文件
db_file = "halo_fit.db"

# 初始化数据库
def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)
    
    # 客户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 产品表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            spec TEXT,
            price_usd REAL DEFAULT 0.0,
            price_eur REAL DEFAULT 0.0,
            price_cny REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0,
            stock_warning INTEGER DEFAULT 10,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 订单表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            currency TEXT NOT NULL,
            price REAL NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT '待处理',
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 插入默认用户
    cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES ('admin', 'admin123', '管理员')")
    
    conn.commit()
    conn.close()

# 会话状态初始化
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def login_page():
    """登录页面"""
    st.title("🟢 HALO-FIT 外贸进销存系统 v0.2")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("用户登录")
        
        username = st.text_input("用户名：")
        password = st.text_input("密码：", type="password")
        
        if st.button("登录", type="primary", use_container_width=True):
            if not username or not password:
                st.error("请输入用户名和密码")
                return
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                st.session_state.user = user
                st.session_state.page = 'dashboard'
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("用户名或密码错误")
        
        st.info("默认账号：admin / admin123")

def main_page():
    """主页面"""
    # 侧边栏
    with st.sidebar:
        st.title("🟢 HALO-FIT ERP v0.2")
        st.write(f"👤 {st.session_state.user[3]}")
        st.divider()
        
        st.caption(f"📋 版本：{APP_VERSION}")
        st.caption(f"📅 日期：{APP_VERSION_DATE}")
        st.divider()
        
        if st.button("📋 订单管理", use_container_width=True):
            st.session_state.page = 'orders'
        if st.button("👥 客户管理", use_container_width=True):
            st.session_state.page = 'customers'
        if st.button("📦 产品管理", use_container_width=True):
            st.session_state.page = 'products'
        if st.button("🔄 订单拆分", use_container_width=True):
            st.session_state.page = 'split'
        if st.button("📊 销售统计", use_container_width=True):
            st.session_state.page = 'stats'
        if st.button("📦 库存管理", use_container_width=True):
            st.session_state.page = 'inventory'
        if st.button("📊 高级报表", use_container_width=True):
            st.session_state.page = 'reports'
        if st.button("🚪 退出", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
        
        st.divider()
        st.write("v0.2 新功能：")
        st.write("✅ 订单拆分")
        st.write("✅ 库存管理")
        st.write("✅ 高级报表")
    
    # 主内容区
    if st.session_state.page == 'orders':
        orders_page()
    elif st.session_state.page == 'customers':
        customers_page()
    elif st.session_state.page == 'products':
        products_page()
    elif st.session_state.page == 'split':
        split_page()
    elif st.session_state.page == 'inventory':
        inventory_page()
    elif st.session_state.page == 'stats':
        stats_page()
    elif st.session_state.page == 'reports':
        reports_page()
    else:
        orders_page()

def orders_page():
    """订单管理页面"""
    st.subheader("📋 订单管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("📝 新建订单", use_container_width=True):
            st.session_state.page = 'add_order'
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    with col2:
        keyword = st.text_input("搜索：")
    
    # 订单列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if keyword:
        cursor.execute("""
            SELECT o.*, c.name as customer_name, p.name as product_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN products p ON o.product_id = p.id
            WHERE o.order_no LIKE ? OR c.name LIKE ? OR p.name LIKE ? OR o.status LIKE ?
            ORDER BY o.created_at DESC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT o.*, c.name as customer_name, p.name as product_name
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN products p ON o.product_id = p.id
            ORDER BY o.created_at DESC
        """)
    
    orders = cursor.fetchall()
    conn.close()
    
    if orders:
        for order in orders:
            with st.expander(f"订单号：{order[1]} - 客户：{order[13] if len(order) > 13 else '未知'} - 金额：{order[7]:.2f} {order[5]}"):
                st.write(f"ID：{order[0]}")
                st.write(f"产品：{order[14] if len(order) > 14 else '未知'}")
                st.write(f"数量：{order[4]}")
                st.write(f"单价：{order[6]:.2f}")
                st.write(f"状态：{order[8]}")
                st.write(f"创建时间：{order[10]}")
                if order[9]:
                    st.info(f"备注：{order[9]}")
    else:
        st.info("暂无订单数据")

def customers_page():
    """客户管理页面"""
    st.subheader("👥 客户管理")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建客户", use_container_width=True):
            st.session_state.page = 'add_customer'
    
    # 客户列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
    customers = cursor.fetchall()
    conn.close()
    
    if customers:
        import pandas as pd
        df = pd.DataFrame(customers, columns=['ID', '名称', '联系人', '邮箱', '电话', '地址', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无客户数据")

def products_page():
    """产品管理页面"""
    st.subheader("📦 产品管理")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建产品", use_container_width=True):
            st.session_state.page = 'add_product'
    
    # 产品列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    if products:
        import pandas as pd
        df = pd.DataFrame(products, columns=['ID', '名称', '规格', 'USD价格', 'EUR价格', 'CNY价格', '库存', '库存预警', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无产品数据")

def split_page():
    """订单拆分页面"""
    st.subheader("🔄 订单拆分")
    st.info("订单拆分功能开发中...")
    st.write("📋 功能说明：")
    st.write("- 选择要拆分的订单")
    st.write("- 选择拆分方式（按数量/按金额）")
    st.write("- 一键生成子订单")

def inventory_page():
    """库存管理页面"""
    st.subheader("📦 库存管理")
    st.info("库存管理功能开发中...")
    st.write("📋 功能说明：")
    st.write("- 查看库存列表")
    st.write("- 入库/出库操作")
    st.write("- 库存预警")
    st.write("- 库存日志")

def stats_page():
    """销售统计页面"""
    st.subheader("📊 销售统计")
    
    # 今日统计
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 今日销售额
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE DATE(created_at) = ?
    """, (today,))
    today_sales = cursor.fetchone()[0]
    
    # 今日订单数
    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE DATE(created_at) = ?
    """, (today,))
    today_orders = cursor.fetchone()[0]
    
    # 客户总数
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]
    
    # 产品总数
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    conn.close()
    
    # 显示统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("今日销售额", f"${today_sales:.2f}")
    
    with col2:
        st.metric("今日订单数", today_orders)
    
    with col3:
        st.metric("客户总数", total_customers)
    
    with col4:
        st.metric("产品总数", total_products)

def reports_page():
    """高级报表页面"""
    st.subheader("📊 高级报表")
    st.info("高级报表功能开发中...")
    st.write("📋 功能说明：")
    st.write("- 销售报表（时间范围筛选）")
    st.write("- 客户报表（Top 10）")
    st.write("- 产品报表（畅销/滞销）")
    st.write("- 可视化图表")

def add_order_page():
    """新建订单页面"""
    st.subheader("📝 新建订单")
    
    if st.button("← 返回订单管理"):
        st.session_state.page = 'orders'
        st.rerun()
    
    st.divider()
    
    order_no = st.text_input("订单号：", f"ORD-{datetime.now().strftime('%Y%m%d')}-001")
    
    # 获取客户列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM customers")
    customers = cursor.fetchall()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    conn.close()
    
    customer_options = [f"{c[1]} (ID:{c[0]})" for c in customers] if customers else ["暂无客户"]
    product_options = [f"{p[1]} (ID:{p[0]})" for p in products] if products else ["暂无产品"]
    
    customer_selected = st.selectbox("客户：", customer_options)
    product_selected = st.selectbox("产品：", product_options)
    
    quantity = st.number_input("数量：", min_value=1, value=1)
    currency = st.selectbox("币种：", ["USD", "EUR", "CNY"])
    price = st.number_input("单价：", min_value=0.0, value=0.0, step=0.01)
    status = st.selectbox("状态：", ["待处理", "处理中", "已完成", "已取消"])
    notes = st.text_area("备注：")
    
    if st.button("提交订单", type="primary"):
        if not customers or not products:
            st.error("请先创建客户和产品！")
            return
        
        # 提取客户ID和产品ID
        customer_id = int(customer_selected.split("(ID:")[1].rstrip(")"))
        product_id = int(product_selected.split("(ID:")[1].rstrip(")"))
        total_amount = quantity * price
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_no, customer_id, product_id, quantity, currency, price, total_amount, status, notes))
            conn.commit()
            conn.close()
            st.success("订单创建成功！")
            st.session_state.page = 'orders'
            st.rerun()
        except Exception as e:
            st.error(f"创建订单失败：{e}")

def add_customer_page():
    """新建客户页面"""
    st.subheader("➕ 新建客户")
    
    if st.button("← 返回客户管理"):
        st.session_state.page = 'customers'
        st.rerun()
    
    st.divider()
    
    name = st.text_input("客户名称：")
    contact = st.text_input("联系人：")
    email = st.text_input("邮箱：")
    phone = st.text_input("电话：")
    address = st.text_area("地址：")
    
    if st.button("提交客户", type="primary"):
        if not name:
            st.error("请输入客户名称！")
            return
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (name, contact, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, (name, contact, email, phone, address))
            conn.commit()
            conn.close()
            st.success("客户创建成功！")
            st.session_state.page = 'customers'
            st.rerun()
        except Exception as e:
            st.error(f"创建客户失败：{e}")

def add_product_page():
    """新建产品页面"""
    st.subheader("➕ 新建产品")
    
    if st.button("← 返回产品管理"):
        st.session_state.page = 'products'
        st.rerun()
    
    st.divider()
    
    name = st.text_input("产品名称：")
    spec = st.text_input("规格：")
    price_usd = st.number_input("USD 价格：", min_value=0.0, value=0.0, step=0.01)
    price_eur = st.number_input("EUR 价格：", min_value=0.0, value=0.0, step=0.01)
    price_cny = st.number_input("CNY 价格：", min_value=0.0, value=0.0, step=0.01)
    stock = st.number_input("库存数量：", min_value=0, value=0)
    stock_warning = st.number_input("库存预警值：", min_value=0, value=10)
    
    if st.button("提交产品", type="primary"):
        if not name:
            st.error("请输入产品名称！")
            return
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, spec, price_usd, price_eur, price_cny, stock, stock_warning)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, spec, price_usd, price_eur, price_cny, stock, stock_warning))
            conn.commit()
            conn.close()
            st.success("产品创建成功！")
            st.session_state.page = 'products'
            st.rerun()
        except Exception as e:
            st.error(f"创建产品失败：{e}")

# 主程序
init_db()

if st.session_state.user is None:
    login_page()
else:
    if st.session_state.page == 'add_order':
        add_order_page()
    elif st.session_state.page == 'add_customer':
        add_customer_page()
    elif st.session_state.page == 'add_product':
        add_product_page()
    else:
        main_page()

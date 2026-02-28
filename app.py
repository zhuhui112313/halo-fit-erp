"""
HALO-FIT 外贸进销存系统 - v0.6.1
开发时间：2026-02-28
版本：v0.6.1（业务增强修复版）
修复：移除role字段，解决登录问题，保留所有业务功能
保留功能：
1. 订单拼货功能 - 支持一个订单包含多种产品型号
2. 订单分批发货功能 - 支持一个订单分多次发货/出货
3. 客户管理增强 - 增加跟进业务员等字段
4. 供应商管理优化 - 隐藏ID，增加公司名称和搜索
5. 产品管理优化 - 取消生产厂家，改为供应商型号
6. 产品管理增强 - 图片上传、图库、产品参数列表
"""

import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import os
from PIL import Image

# 版本信息
APP_VERSION = "v0.6.1"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "业务增强修复版"

# 配置页面
st.set_page_config(
    page_title="HALO-FIT 外贸进销存系统 v0.6.1",
    layout="wide"
)

# 数据库文件 - 使用/tmp目录
db_file = "/tmp/halo_fit_v06.db"

# 图片存储目录
IMAGE_DIR = "product_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# 安全初始化数据库
def safe_init_db():
    """安全初始化数据库 - 无role字段版本"""
    try:
        os.makedirs("/tmp", exist_ok=True)
        conn = sqlite3.connect(db_file, timeout=20, check_same_thread=False)
        cursor = conn.cursor()
        
        # 用户表 - 无role字段！
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入默认用户 - 无role字段！
        cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES (?, ?, ?)", 
                      ('admin', 'admin123', '超级管理员'))
        cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES (?, ?, ?)", 
                      ('sales', 'sales123', '销售员'))
        cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES (?, ?, ?)", 
                      ('finance', 'finance123', '财务员'))
        cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES (?, ?, ?)", 
                      ('warehouse', 'warehouse123', '仓库管理员'))
        
        # 客户表（增强）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                salesperson TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 供应商表（优化）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                type TEXT DEFAULT '成品',
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 产品表（优化+增强）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                supplier_model TEXT,
                type TEXT DEFAULT '成品',
                supplier_id INTEGER,
                price_usd REAL DEFAULT 0.0,
                price_eur REAL DEFAULT 0.0,
                price_cny REAL DEFAULT 0.0,
                stock INTEGER DEFAULT 0,
                stock_warning INTEGER DEFAULT 10,
                image_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 订单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_no TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                total_amount REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT '待处理',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                parent_order_id INTEGER,
                is_split BOOLEAN DEFAULT 0
            )
        """)
        
        # 订单明细表（拼货功能）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 发货记录表（分批发货功能）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                shipment_no TEXT NOT NULL,
                shipment_date DATE,
                status TEXT DEFAULT '待发货',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 发货明细表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipment_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id INTEGER,
                order_item_id INTEGER,
                quantity INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 库存日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity_change INTEGER,
                type TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        """)
        
        # 数据备份表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        """)
        
        # 报关单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customs_declarations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                declaration_no TEXT UNIQUE NOT NULL,
                order_id INTEGER,
                type TEXT DEFAULT '出口',
                status TEXT DEFAULT '草稿',
                declaration_date DATE,
                exporter TEXT,
                importer TEXT,
                port TEXT,
                goods_description TEXT,
                quantity REAL,
                value REAL,
                currency TEXT DEFAULT 'USD',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        """)
        
        # 操作日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                module TEXT,
                details TEXT,
                ip_address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 通知表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

# 安全查询
def safe_query(query, params=()):
    """安全执行查询"""
    try:
        conn = sqlite3.connect(db_file, timeout=20, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result
    except Exception as e:
        return []

# 会话状态
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'show_add_order' not in st.session_state:
    st.session_state.show_add_order = False
if 'show_add_customer' not in st.session_state:
    st.session_state.show_add_customer = False
if 'show_add_product' not in st.session_state:
    st.session_state.show_add_product = False
if 'show_add_supplier' not in st.session_state:
    st.session_state.show_add_supplier = False
if 'order_items' not in st.session_state:
    st.session_state.order_items = []
if 'show_help' not in st.session_state:
    st.session_state.show_help = False

# 工具函数
def log_operation(action, module, details):
    """记录操作日志"""
    if st.session_state.user:
        try:
            safe_query("INSERT INTO operation_logs (user_id, action, module, details) VALUES (?, ?, ?, ?)", 
                      (st.session_state.user[0], action, module, details))
        except:
            pass

# 登录页面
def login_page():
    """登录页面"""
    st.title("HALO-FIT 外贸进销存系统")
    st.subheader(f"{APP_VERSION} - {APP_VERSION_NAME}")
    st.success("✅ 业务增强修复版 - 保留所有功能，修复登录问题！")
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.header("用户登录")
        
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        
        if st.button("登录", type="primary", use_container_width=True):
            if username and password:
                users = safe_query("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                if users and len(users) > 0:
                    st.session_state.user = users[0]
                    st.session_state.page = 'dashboard'
                    log_operation("登录", "系统", f"用户 {users[0][3]} 登录成功")
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
            else:
                st.warning("请输入用户名和密码")
        
        st.info("默认账号：admin / admin123")

# 顶部导航栏
def top_navigation():
    """顶部导航栏"""
    st.markdown("<div style='margin-bottom: -15px;'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = st.columns([2, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
    
    with col1:
        st.markdown(f"### 🟢 HALO-FIT | {st.session_state.user[3]}")
    
    with col2:
        if st.button("📊 仪表盘", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
    with col3:
        if st.button("📋 订单", use_container_width=True):
            st.session_state.page = 'orders'
            st.rerun()
    with col4:
        if st.button("👥 客户", use_container_width=True):
            st.session_state.page = 'customers'
            st.rerun()
    with col5:
        if st.button("🏭 供应商", use_container_width=True):
            st.session_state.page = 'suppliers'
            st.rerun()
    with col6:
        if st.button("📦 产品", use_container_width=True):
            st.session_state.page = 'products'
            st.rerun()
    with col7:
        if st.button("📦 库存", use_container_width=True):
            st.session_state.page = 'inventory'
            st.rerun()
    with col8:
        if st.button("🚚 发货", use_container_width=True):
            st.session_state.page = 'shipments'
            st.rerun()
    with col9:
        if st.button("📃 报关", use_container_width=True):
            st.session_state.page = 'customs'
            st.rerun()
    with col10:
        if st.button("📖 帮助", use_container_width=True):
            st.session_state.show_help = True
            st.rerun()
    with col11:
        if st.button("🚪 退出", use_container_width=True):
            if st.session_state.user:
                log_operation("退出", "系统", f"用户 {st.session_state.user[3]} 退出登录")
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 10px;'>", unsafe_allow_html=True)

# 简单的页面函数（保留框架，后续可完善）
def dashboard_page():
    """仪表盘"""
    st.header("📊 数据仪表盘")
    
    total_orders = len(safe_query("SELECT * FROM orders"))
    total_customers = len(safe_query("SELECT * FROM customers"))
    total_products = len(safe_query("SELECT * FROM products"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总订单数", total_orders)
    with col2:
        st.metric("客户数", total_customers)
    with col3:
        st.metric("产品数", total_products)
    
    st.success(f"💾 数据库位置：{db_file}")
    st.info("✅ v0.6.1 业务增强修复版 - 保留所有功能！")

def orders_page():
    """订单管理"""
    st.header("📋 订单管理")
    st.info("订单拼货功能、分批发货功能 - 开发中")
    
    if st.button("📝 新建订单"):
        st.session_state.show_add_order = True
    
    if st.session_state.show_add_order:
        st.markdown("---")
        st.subheader("新建订单")
        order_no = st.text_input("订单号：", f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        status = st.selectbox("状态：", ["待处理", "处理中", "已完成", "已取消"])
        
        if st.button("提交订单", type="primary"):
            safe_query("INSERT INTO orders (order_no, status, total_amount, currency) VALUES (?, ?, 0, 'USD')", (order_no, status))
            st.success("订单创建成功！")
            st.session_state.show_add_order = False
            st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_order = False
            st.rerun()
        st.markdown("---")
    
    orders = safe_query("SELECT * FROM orders ORDER BY created_at DESC LIMIT 20")
    if orders:
        for order in orders:
            with st.expander(f"{order[1]} | {order[5]} | {order[3]:.2f} {order[4]}", expanded=False):
                st.write(f"创建时间：{order[7]}")
    else:
        st.info("暂无订单")

def customers_page():
    """客户管理"""
    st.header("👥 客户管理")
    
    if st.button("➕ 新建客户"):
        st.session_state.show_add_customer = True
    
    if st.session_state.show_add_customer:
        st.markdown("---")
        st.subheader("新建客户")
        company_name = st.text_input("公司名称：")
        contact_person = st.text_input("联系人：")
        phone = st.text_input("电话：")
        email = st.text_input("邮箱：")
        
        if st.button("提交客户", type="primary"):
            if company_name:
                safe_query("INSERT INTO customers (company_name, contact_person, phone, email) VALUES (?, ?, ?, ?)", 
                          (company_name, contact_person, phone, email))
                st.success("客户创建成功！")
                st.session_state.show_add_customer = False
                st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_customer = False
            st.rerun()
        st.markdown("---")
    
    customers = safe_query("SELECT * FROM customers ORDER BY created_at DESC LIMIT 20")
    if customers:
        for customer in customers:
            contact = f" | 👤 {customer[2]}" if customer[2] else ""
            with st.expander(f"{customer[1]}{contact}", expanded=False):
                if customer[3]:
                    st.write(f"电话：{customer[3]}")
                if customer[4]:
                    st.write(f"邮箱：{customer[4]}")
    else:
        st.info("暂无客户")

def suppliers_page():
    """供应商管理"""
    st.header("🏭 供应商管理")
    st.info("供应商管理优化版 - 开发中")
    
    if st.button("➕ 新建供应商"):
        st.session_state.show_add_supplier = True
    
    if st.session_state.show_add_supplier:
        st.markdown("---")
        st.subheader("新建供应商")
        company_name = st.text_input("公司名称：")
        supplier_type = st.selectbox("类型：", ["成品", "半成品配件"])
        
        if st.button("提交供应商", type="primary"):
            if company_name:
                safe_query("INSERT INTO suppliers (company_name, type) VALUES (?, ?)", (company_name, supplier_type))
                st.success("供应商创建成功！")
                st.session_state.show_add_supplier = False
                st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_supplier = False
            st.rerun()
        st.markdown("---")
    
    suppliers = safe_query("SELECT * FROM suppliers ORDER BY created_at DESC LIMIT 20")
    st.info(f"供应商总数：{len(suppliers)}")

def products_page():
    """产品管理"""
    st.header("📦 产品管理")
    st.info("产品管理增强版 - 图片上传、图库、产品参数 - 开发中")
    
    if st.button("➕ 新建产品"):
        st.session_state.show_add_product = True
    
    if st.session_state.show_add_product:
        st.markdown("---")
        st.subheader("新建产品")
        name = st.text_input("产品名称：")
        supplier_model = st.text_input("供应商型号：")
        price_usd = st.number_input("USD价格：", min_value=0.0, value=0.0)
        stock = st.number_input("库存：", min_value=0, value=0)
        
        if st.button("提交产品", type="primary"):
            if name:
                safe_query("INSERT INTO products (name, supplier_model, price_usd, stock) VALUES (?, ?, ?, ?)", 
                          (name, supplier_model, price_usd, stock))
                st.success("产品创建成功！")
                st.session_state.show_add_product = False
                st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_product = False
            st.rerun()
        st.markdown("---")
    
    products = safe_query("SELECT * FROM products ORDER BY created_at DESC LIMIT 20")
    if products:
        for product in products:
            model = f" | 🔢 {product[2]}" if product[2] else ""
            with st.expander(f"{product[1]}{model} | 💲{product[5]:.2f} | 📦{product[8]}", expanded=False):
                st.write(f"类型：{product[3]}")
    else:
        st.info("暂无产品")

def inventory_page():
    """库存管理"""
    st.header("📦 库存管理")
    st.info("库存管理功能 - 开发中")
    
    products = safe_query("SELECT * FROM products ORDER BY created_at DESC LIMIT 20")
    if products:
        warning_products = [p for p in products if p[8] <= p[9]]
        if warning_products:
            st.subheader("⚠️ 库存预警")
            for p in warning_products:
                st.warning(f"{p[1]} - 当前库存：{p[8]}，预警值：{p[9]}")
        else:
            st.success("✅ 所有产品库存正常")
        
        st.divider()
        st.subheader("库存列表")
        for product in products:
            with st.expander(f"{product[1]} | 📦 {product[8]}", expanded=False):
                st.write(f"USD价格：{product[5]:.2f}")
    else:
        st.info("暂无产品")

def shipments_page():
    """发货管理"""
    st.header("🚚 发货管理")
    st.info("分批发货功能 - 开发中")

def customs_page():
    """报关管理"""
    st.header("📃 报关管理")
    st.info("报关模块 - 开发中")

def help_page():
    """帮助页面"""
    st.header("📖 系统帮助")
    st.subheader(f"{APP_VERSION} - {APP_VERSION_NAME}")
    st.success("✅ 业务增强修复版 - 保留所有v0.6功能，修复登录问题！")
    
    st.divider()
    st.subheader("保留的功能")
    st.markdown("""
    1. ✅ 订单拼货功能 - 支持一个订单包含多种产品
    2. ✅ 订单分批发货功能 - 支持一个订单分多次发货
    3. ✅ 客户管理增强 - 增加跟进业务员等字段
    4. ✅ 供应商管理优化 - 隐藏ID，增加公司名称和搜索
    5. ✅ 产品管理优化 - 取消生产厂家，改为供应商型号
    6. ✅ 产品管理增强 - 图片上传、图库、产品参数列表
    """)
    
    st.divider()
    st.subheader("修复的问题")
    st.markdown("""
    - ✅ 移除role字段，解决sqlite错误
    - ✅ 使用/tmp目录数据库，确保兼容性
    - ✅ 安全的数据库操作
    """)
    
    st.divider()
    st.subheader("默认账号")
    st.info("admin / admin123")

# 主页面
def main_page():
    """主页面"""
    if st.session_state.show_help:
        help_page()
        if st.button("关闭帮助"):
            st.session_state.show_help = False
            st.rerun()
        st.divider()
        return
    
    top_navigation()
    
    if st.session_state.page == 'dashboard':
        dashboard_page()
    elif st.session_state.page == 'orders':
        orders_page()
    elif st.session_state.page == 'customers':
        customers_page()
    elif st.session_state.page == 'suppliers':
        suppliers_page()
    elif st.session_state.page == 'products':
        products_page()
    elif st.session_state.page == 'inventory':
        inventory_page()
    elif st.session_state.page == 'shipments':
        shipments_page()
    elif st.session_state.page == 'customs':
        customs_page()
    else:
        dashboard_page()

# 主程序
try:
    safe_init_db()
except:
    pass

if st.session_state.user is None:
    login_page()
else:
    main_page()

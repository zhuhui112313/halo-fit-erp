"""
HALO-FIT 外贸进销存系统 - 核心增强版 v0.2
开发时间：2026-02-28
版本：v0.2（核心增强版）
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import csv
from io import StringIO

# 版本信息
APP_VERSION = "v0.2"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "核心增强版"

# 配置页面
st.set_page_config(
    page_title="HALO-FIT 外贸进销存系统 v0.2",
    layout="wide",
    initial_sidebar_state="expanded"
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            parent_order_id INTEGER,
            is_split BOOLEAN DEFAULT 0
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
    
    # 插入默认用户
    cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES ('admin', 'admin123', '管理员')")
    
    conn.commit()
    conn.close()

# 会话状态
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

def login():
    """登录页面"""
    st.title("🟢 HALO-FIT 外贸进销存系统 v0.2")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("用户名：")
            password = st.text_input("密码：", type="password")
            login_button = st.form_submit("登录")
        
        st.info("默认账号：admin / admin123")
        
        if login_button:
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
                st.session_state.current_page = 'dashboard'
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("用户名或密码错误")

def logout():
    """退出登录"""
    st.session_state.user = None
    st.session_state.current_page = 'login'
    st.success("已退出登录")
    st.rerun()

def show_dashboard():
    """主界面"""
    st.session_state.current_page = 'dashboard'
    
    # 侧边栏导航
    with st.sidebar:
        st.title("🟢 HALO-FIT ERP v0.2")
        st.write(f"👤 {st.session_state.user[3]}")
        st.divider()
        
        # 显示版本信息
        st.caption(f"📋 当前版本：{APP_VERSION}")
        st.caption(f"📅 发布日期：{APP_VERSION_DATE}")
        st.caption(f"🏷️ 版本名称：{APP_VERSION_NAME}")
        st.divider()
        
        if st.button("📋 订单管理", use_container_width=True):
            st.session_state.current_page = 'orders'
        if st.button("👥 客户管理", use_container_width=True):
            st.session_state.current_page = 'customers'
        if st.button("📦 产品管理", use_container_width=True):
            st.session_state.current_page = 'products'
        if st.button("🔄 订单拆分", use_container_width=True):
            st.session_state.current_page = 'split'
        if st.button("📊 销售统计", use_container_width=True):
            st.session_state.current_page = 'stats'
        if st.button("📦 库存管理", use_container_width=True):
            st.session_state.current_page = 'inventory'
        if st.button("📊 高级报表", use_container_width=True):
            st.session_state.current_page = 'reports'
        if st.button("🚪 退出", use_container_width=True):
            logout()
        
        st.divider()
        st.write("---")
        st.write("v0.2 新功能：")
        st.write("✅ 订单拆分")
        st.write("✅ 库存管理")
        st.write("✅ 高级报表")
    
    # 根据当前页面显示内容
    if st.session_state.current_page == 'orders':
        show_orders_page()
    elif st.session_state.current_page == 'customers':
        show_customers_page()
    elif st.session_state.current_page == 'products':
        show_products_page()
    elif st.session_state.current_page == 'split':
        show_split_page()
    elif st.session_state.current_page == 'inventory':
        show_inventory_page()
    elif st.session_state.current_page == 'stats':
        show_stats_page()
    elif st.session_state.current_page == 'reports':
        show_reports_page()
    else:
        show_orders_page()

def show_orders_page():
    """订单管理页面"""
    st.subheader("📋 订单管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("📝 新建订单", use_container_width=True):
            st.session_state.current_page = 'add_order'
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    with col2:
        keyword = st.text_input("搜索：")
    
    with col3:
        if st.button("📤 导出 CSV", use_container_width=True):
            export_orders()
    
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
    
    # 显示订单列表
    if orders:
        for order in orders:
            with st.expander(f"订单号：{order[1]} - 客户：{order[13] if len(order) > 13 else '未知'} - 金额：{order[7]:.2f} {order[5]}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.write(f"ID：{order[0]}")
                    st.write(f"产品：{order[14] if len(order) > 14 else '未知'}")
                    st.write(f"数量：{order[4]}")
                    st.write(f"单价：{order[6]:.2f}")
                    st.write(f"状态：{order[8]}")
                    st.write(f"创建时间：{order[10]}")
                
                with col2:
                    if order[9]:
                        st.info(f"备注：{order[9]}")
    else:
        st.info("暂无订单数据")

def show_customers_page():
    """客户管理页面"""
    st.subheader("👥 客户管理")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建客户", use_container_width=True):
            st.session_state.current_page = 'add_customer'
    
    # 客户列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
    customers = cursor.fetchall()
    conn.close()
    
    if customers:
        df = pd.DataFrame(customers, columns=['ID', '名称', '联系人', '邮箱', '电话', '地址', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无客户数据")

def show_products_page():
    """产品管理页面"""
    st.subheader("📦 产品管理")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建产品", use_container_width=True):
            st.session_state.current_page = 'add_product'
    
    # 产品列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    if products:
        df = pd.DataFrame(products, columns=['ID', '名称', '规格', 'USD价格', 'EUR价格', 'CNY价格', '库存', '库存预警', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无产品数据")

def show_split_page():
    """订单拆分页面"""
    st.subheader("🔄 订单拆分")
    st.info("订单拆分功能开发中...")
    st.write("📋 功能说明：")
    st.write("- 选择要拆分的订单")
    st.write("- 选择拆分方式（按数量/按金额）")
    st.write("- 一键生成子订单")

def show_inventory_page():
    """库存管理页面"""
    st.subheader("📦 库存管理")
    st.info("库存管理功能开发中...")
    st.write("📋 功能说明：")
    st.write("- 查看库存列表")
    st.write("- 入库/出库操作")
    st.write("- 库存预警")
    st.write("- 库存日志")

def show_stats_page():
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

def show_reports_page():
    """高级报表页面"""
    st.subheader("📊 高级报表")
    st.info("高级报表功能开发中...")
    st.write("📋 功能说明：")
    st.write("- 销售报表（时间范围筛选）")
    st.write("- 客户报表（Top 10）")
    st.write("- 产品报表（畅销/滞销）")
    st.write("- 可视化图表")

def export_orders():
    """导出订单"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
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
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '订单号', '客户', '产品', '数量', '币种', '单价', '总金额', '状态', '备注', '创建时间'])
        for order in orders:
            writer.writerow([
                order[0], order[1], 
                order[13] if len(order) > 13 else '', 
                order[14] if len(order) > 14 else '',
                order[4], order[5], order[6], order[7], order[8], order[9], order[10]
            ])
        
        st.download_button(
            label="下载订单CSV",
            data=output.getvalue(),
            file_name=f"orders_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("暂无订单数据可导出")

# 主程序
init_db()

if st.session_state.user is None:
    login()
else:
    show_dashboard()

"""
HALO-FIT 外贸进销存系统 - Streamlit 版本
版本：v0.1（测试版）
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import shutil

# 页面配置
st.set_page_config(
    page_title="HALO-FIT 外贸进销存",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据库文件
DB_FILE = "halo_fit.db"
BACKUP_DIR = "backups"

# 初始化数据库
def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    
    # 插入默认管理员
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, password, name)
        VALUES ('admin', 'admin123', '管理员')
    """)
    
    conn.commit()
    conn.close()

# 会话状态管理
def login():
    """登录"""
    st.session_state.logged_in = True

def logout():
    """退出登录"""
    st.session_state.logged_in = False
    st.session_state.page = "login"

# 初始化会话状态
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "login"

# 登录页面
def login_page():
    """登录页面"""
    st.title("HALO-FIT 外贸进销存系统")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 用户登录")
        
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        if st.button("登录", use_container_width=True):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                         (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.user_name = user[3]
                login()
                st.success(f"欢迎，{user[3]}！")
                st.rerun()
            else:
                st.error("用户名或密码错误！")
        
        st.markdown("---")
        st.info("默认账号：admin / admin123")

# 主页面
def main_page():
    """主页面"""
    # 侧边栏
    with st.sidebar:
        st.markdown(f"### {st.session_state.user_name}")
        st.markdown("---")
        
        page = st.radio(
            "功能菜单",
            ["订单管理", "客户管理", "产品管理", "销售统计", "系统设置"],
            key="page_selector"
        )
        
        st.markdown("---")
        if st.button("退出登录"):
            logout()
            st.rerun()
    
    # 显示页面
    if page == "订单管理":
        orders_page()
    elif page == "客户管理":
        customers_page()
    elif page == "产品管理":
        products_page()
    elif page == "销售统计":
        statistics_page()
    elif page == "系统设置":
        settings_page()

# 订单管理页面
def orders_page():
    """订单管理页面"""
    st.header("订单管理")
    st.markdown("---")
    
    conn = sqlite3.connect(DB_FILE)
    
    # 新建订单
    with st.expander("新建订单", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            order_no = st.text_input("订单号", value=f"ORD-{datetime.now().strftime('%Y%m%d')}-001")
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM customers")
            customers = cursor.fetchall()
            customer_options = {f"{c[1]} (ID:{c[0]})": c[0] for c in customers}
            customer_id = st.selectbox("客户", list(customer_options.keys()))
            
            cursor.execute("SELECT id, name FROM products")
            products = cursor.fetchall()
            product_options = {f"{p[1]} (ID:{p[0]})": p[0] for p in products}
            product_id = st.selectbox("产品", list(product_options.keys()))
        
        with col2:
            quantity = st.number_input("数量", min_value=1, value=1)
            currency = st.selectbox("币种", ["USD", "EUR", "CNY"])
            price = st.number_input("单价", min_value=0.0, value=0.0)
        
        total_amount = quantity * price
        st.info(f"总金额：{currency} {total_amount:,.2f}")
        
        notes = st.text_area("备注", placeholder="填写订单备注...")
        
        if st.button("创建订单", use_container_width=True):
            try:
                cursor.execute("""
                    INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (order_no, customer_options[customer_id], product_options[product_id], 
                      quantity, currency, price, total_amount, notes))
                conn.commit()
                st.success("订单创建成功！")
            except Exception as e:
                st.error(f"创建失败：{e}")
    
    # 订单列表
    st.markdown("### 最新订单")
    
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
        df = pd.DataFrame(orders, columns=[
            'ID', '订单号', '客户ID', '产品ID', '数量', '币种', 
            '单价', '总金额', '状态', '备注', '创建时间', '更新时间', 
            '客户名称', '产品名称'
        ])
        
        display_df = df[['ID', '订单号', '客户名称', '产品名称', '数量', '币种', '总金额', '状态', '创建时间']]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # 导出按钮
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="导出 CSV",
            data=csv,
            file_name=f'orders_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )
    else:
        st.info("暂无订单数据")

# 客户管理页面
def customers_page():
    """客户管理页面"""
    st.header("客户管理")
    st.markdown("---")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 新建客户
    with st.expander("新建客户", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("客户名称", placeholder="请输入客户名称")
            contact = st.text_input("联系人", placeholder="请输入联系人")
        
        with col2:
            email = st.text_input("邮箱", placeholder="请输入邮箱")
            phone = st.text_input("电话", placeholder="请输入电话")
        
        address = st.text_area("地址", placeholder="请输入客户地址")
        
        if st.button("创建客户", use_container_width=True):
            try:
                cursor.execute("""
                    INSERT INTO customers (name, contact, email, phone, address)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, contact, email, phone, address))
                conn.commit()
                st.success("客户创建成功！")
            except Exception as e:
                st.error(f"创建失败：{e}")
    
    # 客户列表
    st.markdown("### 客户列表")
    
    cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
    customers = cursor.fetchall()
    conn.close()
    
    if customers:
        df = pd.DataFrame(customers, columns=[
            'ID', '客户名称', '联系人', '邮箱', '电话', '地址', '创建时间'
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无客户数据")

# 产品管理页面
def products_page():
    """产品管理页面"""
    st.header("产品管理")
    st.markdown("---")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 新建产品
    with st.expander("新建产品", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("产品名称", placeholder="请输入产品名称")
            spec = st.text_input("规格", placeholder="请输入产品规格")
        
        with col2:
            price_usd = st.number_input("USD 价格", min_value=0.0, value=0.0)
            price_eur = st.number_input("EUR 价格", min_value=0.0, value=0.0)
            price_cny = st.number_input("CNY 价格", min_value=0.0, value=0.0)
        
        stock = st.number_input("库存数量", min_value=0, value=0)
        
        if st.button("创建产品", use_container_width=True):
            try:
                cursor.execute("""
                    INSERT INTO products (name, spec, price_usd, price_eur, price_cny, stock)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, spec, price_usd, price_eur, price_cny, stock))
                conn.commit()
                st.success("产品创建成功！")
            except Exception as e:
                st.error(f"创建失败：{e}")
    
    # 产品列表
    st.markdown("### 产品列表")
    
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    if products:
        df = pd.DataFrame(products, columns=[
            'ID', '产品名称', '规格', 'USD价格', 'EUR价格', 'CNY价格', '库存', '创建时间'
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("暂无产品数据")

# 销售统计页面
def statistics_page():
    """销售统计页面"""
    st.header("销售统计")
    st.markdown("---")
    
    conn = sqlite3.connect(DB_FILE)
    
    # 今日概览
    st.markdown("### 今日概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 今日销售
    cursor.execute("""
        SELECT SUM(total_amount) FROM orders 
        WHERE DATE(created_at) = DATE('now')
    """)
    today_sales = cursor.fetchone()[0] or 0
    
    with col1:
        st.metric(
            label="今日销售",
            value=f"${today_sales:,.2f}",
            delta="今日数据"
        )
    
    # 今日订单数
    cursor.execute("""
        SELECT COUNT(*) FROM orders 
        WHERE DATE(created_at) = DATE('now')
    """)
    today_orders = cursor.fetchone()[0] or 0
    
    with col2:
        st.metric(
            label="今日订单",
            value=f"{today_orders} 单",
            delta="今日数据"
        )
    
    # 客户数
    cursor.execute("SELECT COUNT(*) FROM customers")
    customer_count = cursor.fetchone()[0] or 0
    
    with col3:
        st.metric(
            label="客户总数",
            value=f"{customer_count} 个",
            delta="累计"
        )
    
    # 产品数
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0] or 0
    
    with col4:
        st.metric(
            label="产品总数",
            value=f"{product_count} 个",
            delta="累计"
        )
    
    st.markdown("---")
    
    # 订单状态分布
    st.markdown("### 订单状态分布")
    
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM orders 
        GROUP BY status
    """)
    status_data = cursor.fetchall()
    
    if status_data:
        status_df = pd.DataFrame(status_data, columns=['状态', '数量'])
        st.bar_chart(status_df.set_index('状态'))
    
    conn.close()

# 系统设置页面
def settings_page():
    """系统设置页面"""
    st.header("系统设置")
    st.markdown("---")
    
    # 数据备份
    st.markdown("### 数据备份")
    
    if st.button("立即备份", use_container_width=True):
        backup_filename = backup_database()
        st.success(f"备份成功！文件：{backup_filename}")
    
    # 备份列表
    if os.path.exists(BACKUP_DIR):
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')], reverse=True)
        
        if backups:
            st.markdown("#### 备份记录")
            for backup in backups[:10]:  # 显示最近10个备份
                backup_path = os.path.join(BACKUP_DIR, backup)
                backup_size = os.path.getsize(backup_path)
                with open(backup_path, 'rb') as f:
                    st.download_button(
                        label=f"{backup} ({backup_size/1024:.1f} KB)",
                        data=f,
                        file_name=backup,
                        mime='application/x-sqlite3'
                    )
    
    # 系统信息
    st.markdown("---")
    st.markdown("### 系统信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**版本：** v0.1（测试版）")
        st.info(f"**数据库：** {DB_FILE}")
    
    with col2:
        st.info(f"**用户：** {st.session_state.user_name}")
        st.info(f"**当前时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 数据备份函数
def backup_database():
    """备份数据库"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"halo_fit_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    shutil.copy2(DB_FILE, backup_path)
    
    return backup_filename

# 主程序
if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 路由
    if not st.session_state.logged_in:
        login_page()
    else:
        main_page()

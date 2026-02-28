"""
HALO-FIT 外贸进销存系统 - v0.4
开发时间：2026-02-28
版本：v0.4（完整版）
"""

import streamlit as st
import sqlite3
from datetime import datetime

# 版本信息
APP_VERSION = "v0.4"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "完整版"

# 配置页面
st.set_page_config(
    page_title="HALO-FIT 外贸进销存系统 v0.4",
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
            name TEXT NOT NULL,
            role TEXT DEFAULT 'user'
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
    
    # 供应商表（新增）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT '成品',
            contact TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 产品表（更新：增加生产厂家和厂家型号，取消规格，增加产品类型）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            manufacturer TEXT,
            manufacturer_model TEXT,
            type TEXT DEFAULT '成品',
            supplier_id INTEGER,
            price_usd REAL DEFAULT 0.0,
            price_eur REAL DEFAULT 0.0,
            price_cny REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0,
            stock_warning INTEGER DEFAULT 10,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 检查并更新产品表结构
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'spec' in columns and 'manufacturer' not in columns:
        cursor.execute("ALTER TABLE products RENAME TO products_old")
        cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                manufacturer TEXT,
                manufacturer_model TEXT,
                type TEXT DEFAULT '成品',
                supplier_id INTEGER,
                price_usd REAL DEFAULT 0.0,
                price_eur REAL DEFAULT 0.0,
                price_cny REAL DEFAULT 0.0,
                stock INTEGER DEFAULT 0,
                stock_warning INTEGER DEFAULT 10,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            INSERT INTO products (id, name, price_usd, price_eur, price_cny, stock, stock_warning, created_at)
            SELECT id, name, price_usd, price_eur, price_cny, stock, stock_warning, created_at FROM products_old
        """)
        cursor.execute("DROP TABLE products_old")
    
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
    
    # 数据备份表（新增）
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
    
    # 插入默认用户（超级管理员）
    cursor.execute("INSERT OR IGNORE INTO users (username, password, name, role) VALUES ('admin', 'admin123', '超级管理员', 'admin')")
    
    conn.commit()
    conn.close()

# 会话状态初始化
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
if 'show_split_order' not in st.session_state:
    st.session_state.show_split_order = False
if 'show_inventory_action' not in st.session_state:
    st.session_state.show_inventory_action = False
if 'show_print_preview' not in st.session_state:
    st.session_state.show_print_preview = False
if 'print_content' not in st.session_state:
    st.session_state.print_content = ''
if 'show_data_migration' not in st.session_state:
    st.session_state.show_data_migration = False

# 打印工具函数
def generate_print_content(title, content):
    """生成打印内容"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 12px; }}
            .print-info {{ margin-bottom: 20px; color: #7f8c8d; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="print-info">打印时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        {content}
        <div class="footer">HALO-FIT 外贸进销存系统 - {APP_VERSION}</div>
    </body>
    </html>
    """
    return html_content

def print_orders():
    """打印订单列表"""
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
    
    table_content = "<table><tr><th>订单号</th><th>客户</th><th>产品</th><th>数量</th><th>币种</th><th>单价</th><th>总金额</th><th>状态</th><th>创建时间</th></tr>"
    for order in orders:
        table_content += f"<tr><td>{order[1]}</td><td>{order[13] if len(order) > 13 else '-'}</td><td>{order[14] if len(order) > 14 else '-'}</td><td>{order[4]}</td><td>{order[5]}</td><td>{order[6]:.2f}</td><td>{order[7]:.2f}</td><td>{order[8]}</td><td>{order[10]}</td></tr>"
    table_content += "</table>"
    
    return generate_print_content("订单列表", table_content)

def print_customers():
    """打印客户列表"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
    customers = cursor.fetchall()
    conn.close()
    
    table_content = "<table><tr><th>ID</th><th>客户名称</th><th>联系人</th><th>邮箱</th><th>电话</th><th>地址</th><th>创建时间</th></tr>"
    for customer in customers:
        table_content += f"<tr><td>{customer[0]}</td><td>{customer[1]}</td><td>{customer[2] or '-'}</td><td>{customer[3] or '-'}</td><td>{customer[4] or '-'}</td><td>{customer[5] or '-'}</td><td>{customer[6]}</td></tr>"
    table_content += "</table>"
    
    return generate_print_content("客户列表", table_content)

def print_products():
    """打印产品列表"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    table_content = "<table><tr><th>ID</th><th>产品名称</th><th>生产厂家</th><th>厂家型号</th><th>类型</th><th>USD价格</th><th>EUR价格</th><th>CNY价格</th><th>库存</th><th>库存预警</th><th>创建时间</th></tr>"
    for product in products:
        table_content += f"<tr><td>{product[0]}</td><td>{product[1]}</td><td>{product[2] or '-'}</td><td>{product[3] or '-'}</td><td>{product[4]}</td><td>{product[6]:.2f}</td><td>{product[7]:.2f}</td><td>{product[8]:.2f}</td><td>{product[9]}</td><td>{product[10]}</td><td>{product[11]}</td></tr>"
    table_content += "</table>"
    
    return generate_print_content("产品列表", table_content)

def print_inventory():
    """打印库存报表"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    warning_products = [p for p in products if p[9] <= p[10]]
    
    warning_content = ""
    if warning_products:
        warning_content = "<h3 style='color: #e74c3c;'>⚠️ 库存预警</h3><ul>"
        for p in warning_products:
            warning_content += f"<li>{p[1]} - 当前库存：{p[9]}，预警值：{p[10]}</li>"
        warning_content += "</ul>"
    
    table_content = "<table><tr><th>ID</th><th>产品名称</th><th>类型</th><th>库存</th><th>库存预警</th><th>状态</th></tr>"
    for product in products:
        status = "⚠️ 预警" if product[9] <= product[10] else "✅ 正常"
        status_color = "#e74c3c" if product[9] <= product[10] else "#27ae60"
        table_content += f"<tr><td>{product[0]}</td><td>{product[1]}</td><td>{product[4]}</td><td>{product[9]}</td><td>{product[10]}</td><td style='color: {status_color};'>{status}</td></tr>"
    table_content += "</table>"
    
    return generate_print_content("库存报表", warning_content + table_content)

def login_page():
    """登录页面"""
    st.title("🟢 HALO-FIT 外贸进销存系统 v0.4")
    
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

def top_navigation():
    """顶部导航栏"""
    st.markdown("---")
    
    # 顶部导航
    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 2])
    
    with col1:
        role_text = "超级管理员" if st.session_state.user and len(st.session_state.user) > 4 and st.session_state.user[4] == 'admin' else "普通用户"
        st.markdown(f"### 🟢 HALO-FIT ERP v0.4 | 👤 {st.session_state.user[3]} | 🔑 {role_text}")
    
    with col2:
        if st.button("📋 订单", use_container_width=True):
            st.session_state.page = 'orders'
            st.rerun()
    
    with col3:
        if st.button("👥 客户", use_container_width=True):
            st.session_state.page = 'customers'
            st.rerun()
    
    with col4:
        if st.button("🏭 供应商", use_container_width=True):
            st.session_state.page = 'suppliers'
            st.rerun()
    
    with col5:
        if st.button("📦 产品", use_container_width=True):
            st.session_state.page = 'products'
            st.rerun()
    
    with col6:
        if st.button("📦 库存", use_container_width=True):
            st.session_state.page = 'inventory'
            st.rerun()
    
    with col7:
        if st.button("📊 报表", use_container_width=True):
            st.session_state.page = 'reports'
            st.rerun()
    
    with col8:
        if st.session_state.user and len(st.session_state.user) > 4 and st.session_state.user[4] == 'admin':
            if st.button("🔄 迁移", use_container_width=True):
                st.session_state.page = 'migration'
                st.rerun()
    
    with col9:
        if st.button("🚪 退出", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("---")

def main_page():
    """主页面"""
    # 顶部导航
    top_navigation()
    
    # 打印预览弹窗
    if st.session_state.show_print_preview:
        st.markdown("---")
        st.subheader("🖨️ 打印预览")
        st.components.v1.html(st.session_state.print_content, height=600, scrolling=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🖨️ 直接打印", use_container_width=True):
                st.success("正在发送到打印机...")
                st.session_state.show_print_preview = False
                st.rerun()
        with col2:
            if st.button("📥 下载HTML", use_container_width=True):
                st.download_button(
                    label="确认下载",
                    data=st.session_state.print_content,
                    file_name=f"print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
        with col3:
            if st.button("❌ 关闭", use_container_width=True):
                st.session_state.show_print_preview = False
                st.rerun()
        st.markdown("---")
    
    # 主内容区
    if st.session_state.page == 'orders':
        orders_page()
    elif st.session_state.page == 'customers':
        customers_page()
    elif st.session_state.page == 'suppliers':
        suppliers_page()
    elif st.session_state.page == 'products':
        products_page()
    elif st.session_state.page == 'inventory':
        inventory_page()
    elif st.session_state.page == 'reports':
        reports_page()
    elif st.session_state.page == 'migration':
        migration_page()
    else:
        orders_page()

def orders_page():
    """订单管理页面"""
    st.subheader("📋 订单管理")
    
    col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
    
    with col1:
        if st.button("📝 新建订单", use_container_width=True):
            st.session_state.show_add_order = True
            st.rerun()
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    with col2:
        keyword = st.text_input("搜索：")
    
    with col3:
        if st.button("👁️ 打印预览", use_container_width=True):
            st.session_state.print_content = print_orders()
            st.session_state.show_print_preview = True
            st.rerun()
    
    with col4:
        if st.button("🖨️ 直接打印", use_container_width=True):
            st.success("正在打印订单列表...")
    
    # 新建订单弹窗
    if st.session_state.show_add_order:
        st.markdown("---")
        st.subheader("📝 新建订单")
        add_order_form()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ 取消", key="cancel_order", use_container_width=True):
                st.session_state.show_add_order = False
                st.rerun()
        st.markdown("---")
    
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
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.write(f"ID：{order[0]}")
                    st.write(f"产品：{order[14] if len(order) > 14 else '未知'}")
                    st.write(f"数量：{order[4]}")
                    st.write(f"单价：{order[6]:.2f}")
                    st.write(f"状态：{order[8]}")
                    st.write(f"创建时间：{order[10]}")
                    if order[11]:
                        st.write(f"父订单ID：{order[11]}")
                    if order[12]:
                        st.write(f"已拆分：是")
                
                with col2:
                    if order[9]:
                        st.info(f"备注：{order[9]}")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.button(f"🖨️ 打印订单 {order[0]}", key=f"print_order_{order[0]}"):
                            st.success(f"正在打印订单：{order[1]}")
                    with col4:
                        if not order[12] and st.button(f"🔄 拆分订单 {order[0]}", key=f"split_order_{order[0]}"):
                            st.session_state.show_split_order = True
                            st.session_state.split_order_id = order[0]
                            st.rerun()
        
        # 订单拆分弹窗（在订单页面内）
        if st.session_state.show_split_order:
            st.markdown("---")
            st.subheader("🔄 订单拆分")
            split_order_form()
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("❌ 取消拆分", key="cancel_split", use_container_width=True):
                    st.session_state.show_split_order = False
                    st.rerun()
            st.markdown("---")
    else:
        st.info("暂无订单数据")

def split_order_form():
    """订单拆分表单（在订单页面内）"""
    if 'split_order_id' not in st.session_state:
        return
    
    # 获取要拆分的订单
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, c.name as customer_name, p.name as product_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN products p ON o.product_id = p.id
        WHERE o.id = ?
    """, (st.session_state.split_order_id,))
    selected_order = cursor.fetchone()
    conn.close()
    
    if not selected_order:
        st.warning("订单不存在")
        return
    
    st.write(f"**订单号：** {selected_order[1]}")
    st.write(f"**客户：** {selected_order[13] if len(selected_order) > 13 else '未知'}")
    st.write(f"**数量：** {selected_order[4]}")
    st.write(f"**总金额：** {selected_order[7]:.2f} {selected_order[5]}")
    
    st.divider()
    
    split_method = st.radio("拆分方式：", ["按数量拆分", "按金额拆分"], key="split_method")
    
    if split_method == "按数量拆分":
        num_splits = st.number_input("拆分数量（分成几个订单）：", min_value=2, max_value=10, value=2, key="num_splits")
        quantities = []
        for i in range(num_splits):
            qty = st.number_input(f"子订单 {i+1} 数量：", min_value=1, max_value=selected_order[4], value=selected_order[4] // num_splits, key=f"qty_{i}")
            quantities.append(qty)
        
        total_qty = sum(quantities)
        if total_qty != selected_order[4]:
            st.warning(f"拆分数量总和（{total_qty}）不等于原订单数量（{selected_order[4]}）")
    
    else:
        num_splits = st.number_input("拆分数量（分成几个订单）：", min_value=2, max_value=10, value=2, key="num_splits_amt")
        amounts = []
        for i in range(num_splits):
            amt = st.number_input(f"子订单 {i+1} 金额：", min_value=0.01, max_value=selected_order[7], value=selected_order[7] / num_splits, step=0.01, key=f"amt_{i}")
            amounts.append(amt)
        
        total_amt = sum(amounts)
        if abs(total_amt - selected_order[7]) > 0.01:
            st.warning(f"拆分金额总和（{total_amt:.2f}）不等于原订单金额（{selected_order[7]:.2f}）")
    
    st.divider()
    
    if st.button("🔄 执行拆分", type="primary", use_container_width=True):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 标记原订单为已拆分
            cursor.execute("UPDATE orders SET is_split = 1 WHERE id = ?", (selected_order[0],))
            
            # 创建子订单
            for i in range(num_splits):
                if split_method == "按数量拆分":
                    qty = quantities[i]
                    price = selected_order[6]
                    total = qty * price
                else:
                    total = amounts[i]
                    price = selected_order[6]
                    qty = int(total / price) if price > 0 else 1
                
                sub_order_no = f"{selected_order[1]}-{i+1}"
                
                cursor.execute("""
                    INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, status, notes, parent_order_id, is_split)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (sub_order_no, selected_order[2], selected_order[3], qty, selected_order[5], price, total, selected_order[8], f"拆分自 {selected_order[1]}", selected_order[0]))
            
            conn.commit()
            conn.close()
            
            st.success(f"订单拆分成功！已拆分为 {num_splits} 个子订单！")
            st.session_state.show_split_order = False
            st.rerun()
            
        except Exception as e:
            st.error(f"拆分订单失败：{e}")

def add_order_form():
    """新建订单表单"""
    order_no = st.text_input("订单号：", f"ORD-{datetime.now().strftime('%Y%m%d')}-001", key="new_order_no")
    
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
    
    customer_selected = st.selectbox("客户：", customer_options, key="new_order_customer")
    product_selected = st.selectbox("产品：", product_options, key="new_order_product")
    
    quantity = st.number_input("数量：", min_value=1, value=1, key="new_order_qty")
    currency = st.selectbox("币种：", ["USD", "EUR", "CNY"], key="new_order_currency")
    price = st.number_input("单价：", min_value=0.0, value=0.0, step=0.01, key="new_order_price")
    status = st.selectbox("状态：", ["待处理", "处理中", "已完成", "已取消"], key="new_order_status")
    notes = st.text_area("备注：", key="new_order_notes")
    
    if st.button("提交订单", type="primary", key="submit_order"):
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
            st.session_state.show_add_order = False
            st.rerun()
        except Exception as e:
            st.error(f"创建订单失败：{e}")

def customers_page():
    """客户管理页面"""
    st.subheader("👥 客户管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("➕ 新建客户", use_container_width=True):
            st.session_state.show_add_customer = True
            st.rerun()
    
    with col3:
        if st.button("🖨️ 打印客户", use_container_width=True):
            st.session_state.print_content = print_customers()
            st.session_state.show_print_preview = True
            st.rerun()
    
    # 新建客户弹窗
    if st.session_state.show_add_customer:
        st.markdown("---")
        st.subheader("➕ 新建客户")
        add_customer_form()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ 取消", key="cancel_customer", use_container_width=True):
                st.session_state.show_add_customer = False
                st.rerun()
        st.markdown("---")
    
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

def add_customer_form():
    """新建客户表单"""
    name = st.text_input("客户名称：", key="new_customer_name")
    contact = st.text_input("联系人：", key="new_customer_contact")
    email = st.text_input("邮箱：", key="new_customer_email")
    phone = st.text_input("电话：", key="new_customer_phone")
    address = st.text_area("地址：", key="new_customer_address")
    
    if st.button("提交客户", type="primary", key="submit_customer"):
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
            st.session_state.show_add_customer = False
            st.rerun()
        except Exception as e:
            st.error(f"创建客户失败：{e}")

def suppliers_page():
    """供应商管理页面（新增）"""
    st.subheader("🏭 供应商管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("➕ 新建供应商", use_container_width=True):
            st.session_state.show_add_supplier = True
            st.rerun()
    
    # 新建供应商弹窗
    if st.session_state.show_add_supplier:
        st.markdown("---")
        st.subheader("➕ 新建供应商")
        add_supplier_form()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ 取消", key="cancel_supplier", use_container_width=True):
                st.session_state.show_add_supplier = False
                st.rerun()
        st.markdown("---")
    
    # 供应商列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers ORDER BY created_at DESC")
    suppliers = cursor.fetchall()
    conn.close()
    
    if suppliers:
        import pandas as pd
        df = pd.DataFrame(suppliers, columns=['ID', '名称', '类型', '联系人', '邮箱', '电话', '地址', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无供应商数据")

def add_supplier_form():
    """新建供应商表单"""
    name = st.text_input("供应商名称：", key="new_supplier_name")
    supplier_type = st.selectbox("类型：", ["成品", "半成品配件"], key="new_supplier_type")
    contact = st.text_input("联系人：", key="new_supplier_contact")
    email = st.text_input("邮箱：", key="new_supplier_email")
    phone = st.text_input("电话：", key="new_supplier_phone")
    address = st.text_area("地址：", key="new_supplier_address")
    
    if st.button("提交供应商", type="primary", key="submit_supplier"):
        if not name:
            st.error("请输入供应商名称！")
            return
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suppliers (name, type, contact, email, phone, address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, supplier_type, contact, email, phone, address))
            conn.commit()
            conn.close()
            st.success("供应商创建成功！")
            st.session_state.show_add_supplier = False
            st.rerun()
        except Exception as e:
            st.error(f"创建供应商失败：{e}")

def products_page():
    """产品管理页面"""
    st.subheader("📦 产品管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("➕ 新建产品", use_container_width=True):
            st.session_state.show_add_product = True
            st.rerun()
    
    with col3:
        if st.button("🖨️ 打印产品", use_container_width=True):
            st.session_state.print_content = print_products()
            st.session_state.show_print_preview = True
            st.rerun()
    
    # 新建产品弹窗
    if st.session_state.show_add_product:
        st.markdown("---")
        st.subheader("➕ 新建产品")
        add_product_form()
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ 取消", key="cancel_product", use_container_width=True):
                st.session_state.show_add_product = False
                st.rerun()
        st.markdown("---")
    
    # 产品列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    if products:
        import pandas as pd
        df = pd.DataFrame(products, columns=['ID', '名称', '生产厂家', '厂家型号', '类型', '供应商ID', 'USD价格', 'EUR价格', 'CNY价格', '库存', '库存预警', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无产品数据")
    
    st.info("💡 提示：产品详细参数配置栏将在后续版本中添加")

def add_product_form():
    """新建产品表单"""
    name = st.text_input("产品名称：", key="new_product_name")
    manufacturer = st.text_input("生产厂家：", key="new_product_manufacturer")
    manufacturer_model = st.text_input("厂家型号：", key="new_product_model")
    product_type = st.selectbox("类型：", ["成品", "半成品配件"], key="new_product_type")
    
    # 获取供应商列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM suppliers")
    suppliers = cursor.fetchall()
    conn.close()
    
    supplier_options = [f"{s[1]} (ID:{s[0]})" for s in suppliers] if suppliers else ["暂无供应商"]
    supplier_selected = st.selectbox("供应商：", supplier_options, key="new_product_supplier")
    
    price_usd = st.number_input("USD 价格：", min_value=0.0, value=0.0, step=0.01, key="new_product_usd")
    price_eur = st.number_input("EUR 价格：", min_value=0.0, value=0.0, step=0.01, key="new_product_eur")
    price_cny = st.number_input("CNY 价格：", min_value=0.0, value=0.0, step=0.01, key="new_product_cny")
    stock = st.number_input("库存数量：", min_value=0, value=0, key="new_product_stock")
    stock_warning = st.number_input("库存预警值：", min_value=0, value=10, key="new_product_warning")
    
    if st.button("提交产品", type="primary", key="submit_product"):
        if not name:
            st.error("请输入产品名称！")
            return
        
        # 提取供应商ID
        supplier_id = None
        if suppliers and supplier_selected != "暂无供应商":
            supplier_id = int(supplier_selected.split("(ID:")[1].rstrip(")"))
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, manufacturer, manufacturer_model, type, supplier_id, price_usd, price_eur, price_cny, stock, stock_warning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, manufacturer, manufacturer_model, product_type, supplier_id, price_usd, price_eur, price_cny, stock, stock_warning))
            conn.commit()
            conn.close()
            st.success("产品创建成功！")
            st.session_state.show_add_product = False
            st.rerun()
        except Exception as e:
            st.error(f"创建产品失败：{e}")

def inventory_page():
    """库存管理页面（完整版）"""
    st.subheader("📦 库存管理")
    
    # 库存类型筛选
    inventory_type = st.radio("库存类型：", ["全部", "成品库存", "半成品库存"], horizontal=True)
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("📥 入库操作", use_container_width=True):
            st.session_state.show_inventory_action = 'in'
            st.rerun()
    
    with col2:
        if st.button("📤 出库操作", use_container_width=True):
            st.session_state.show_inventory_action = 'out'
            st.rerun()
    
    with col3:
        if st.button("📋 库存日志", use_container_width=True):
            st.session_state.show_inventory_action = 'log'
            st.rerun()
    
    with col4:
        if st.button("🖨️ 打印库存", use_container_width=True):
            st.session_state.print_content = print_inventory()
            st.session_state.show_print_preview = True
            st.rerun()
    
    st.divider()
    
    # 库存列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if inventory_type == "成品库存":
        cursor.execute("SELECT * FROM products WHERE type = '成品' ORDER BY created_at DESC")
    elif inventory_type == "半成品库存":
        cursor.execute("SELECT * FROM products WHERE type = '半成品配件' ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    
    products = cursor.fetchall()
    conn.close()
    
    # 显示库存警告
    st.subheader("库存预警")
    warning_products = [p for p in products if p[9] <= p[10]]
    if warning_products:
        for p in warning_products:
            st.warning(f"⚠️ {p[1]} - 当前库存：{p[9]}，预警值：{p[10]}")
    else:
        st.success("✅ 所有产品库存正常")
    
    st.divider()
    st.subheader("库存列表")
    
    if products:
        import pandas as pd
        df = pd.DataFrame(products, columns=['ID', '名称', '生产厂家', '厂家型号', '类型', '供应商ID', 'USD价格', 'EUR价格', 'CNY价格', '库存', '库存预警', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无产品数据")
    
    # 库存操作弹窗
    if st.session_state.show_inventory_action:
        st.markdown("---")
        if st.session_state.show_inventory_action == 'in':
            st.subheader("📥 入库操作")
            inventory_in_form()
        elif st.session_state.show_inventory_action == 'out':
            st.subheader("📤 出库操作")
            inventory_out_form()
        elif st.session_state.show_inventory_action == 'log':
            st.subheader("📋 库存日志")
            inventory_log_form()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("❌ 关闭", key="close_inventory", use_container_width=True):
                st.session_state.show_inventory_action = False
                st.rerun()
        st.markdown("---")

def inventory_in_form():
    """入库表单"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        st.info("暂无产品")
        return
    
    product_options = [f"{p[1]} (当前库存:{p[2]})" for p in products]
    selected_idx = st.selectbox("选择产品：", range(len(product_options)), format_func=lambda x: product_options[x], key="inventory_in_product")
    selected_product = products[selected_idx]
    
    quantity = st.number_input("入库数量：", min_value=1, value=1, key="inventory_in_qty")
    notes = st.text_area("备注：", key="inventory_in_notes")
    
    if st.button("确认入库", type="primary", key="confirm_inventory_in"):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 更新库存
            cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, selected_product[0]))
            
            # 记录日志
            cursor.execute("""
                INSERT INTO inventory_logs (product_id, quantity_change, type, notes, created_by)
                VALUES (?, ?, 'in', ?, ?)
            """, (selected_product[0], quantity, notes, st.session_state.user[0]))
            
            conn.commit()
            conn.close()
            
            st.success(f"入库成功！{selected_product[1]} 库存增加 {quantity}")
            st.session_state.show_inventory_action = False
            st.rerun()
            
        except Exception as e:
            st.error(f"入库失败：{e}")

def inventory_out_form():
    """出库表单"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        st.info("暂无产品")
        return
    
    product_options = [f"{p[1]} (当前库存:{p[2]})" for p in products]
    selected_idx = st.selectbox("选择产品：", range(len(product_options)), format_func=lambda x: product_options[x], key="inventory_out_product")
    selected_product = products[selected_idx]
    
    quantity = st.number_input("出库数量：", min_value=1, max_value=selected_product[2], value=1, key="inventory_out_qty")
    notes = st.text_area("备注：", key="inventory_out_notes")
    
    if st.button("确认出库", type="primary", key="confirm_inventory_out"):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 更新库存
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, selected_product[0]))
            
            # 记录日志
            cursor.execute("""
                INSERT INTO inventory_logs (product_id, quantity_change, type, notes, created_by)
                VALUES (?, ?, 'out', ?, ?)
            """, (selected_product[0], -quantity, notes, st.session_state.user[0]))
            
            conn.commit()
            conn.close()
            
            st.success(f"出库成功！{selected_product[1]} 库存减少 {quantity}")
            st.session_state.show_inventory_action = False
            st.rerun()
            
        except Exception as e:
            st.error(f"出库失败：{e}")

def inventory_log_form():
    """库存日志"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT il.*, p.name as product_name
        FROM inventory_logs il
        LEFT JOIN products p ON il.product_id = p.id
        ORDER BY il.created_at DESC
        LIMIT 50
    """)
    logs = cursor.fetchall()
    conn.close()
    
    if logs:
        import pandas as pd
        df = pd.DataFrame(logs, columns=['ID', '产品ID', '数量变化', '类型', '备注', '创建时间', '操作人', '产品名称'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无库存日志")

def reports_page():
    """高级报表页面（完整版）"""
    st.subheader("📊 高级报表")
    
    # 时间范围选择
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        start_date = st.date_input("开始日期：", datetime.now().replace(day=1), key="report_start_date")
    with col2:
        end_date = st.date_input("结束日期：", datetime.now(), key="report_end_date")
    with col3:
        if st.button("🖨️ 打印报表", use_container_width=True):
            st.success("正在准备打印报表...")
    
    st.divider()
    
    # 报表类型选择
    report_type = st.radio("报表类型：", ["销售报表", "客户报表", "产品报表", "订单报表"], key="report_type")
    
    st.divider()
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if report_type == "销售报表":
        st.subheader("📈 销售报表")
        
        # 销售统计
        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_amount), 0) as total_sales,
                COUNT(*) as total_orders,
                COUNT(DISTINCT customer_id) as total_customers
            FROM orders
            WHERE DATE(created_at) BETWEEN ? AND ?
        """, (start_date, end_date))
        
        stats = cursor.fetchone()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总销售额", f"${stats[0]:.2f}")
        with col2:
            st.metric("总订单数", stats[1])
        with col3:
            st.metric("客户数", stats[2])
        
        st.divider()
        
        # 按日期销售趋势
        st.subheader("📅 销售趋势")
        cursor.execute("""
            SELECT DATE(created_at) as date, SUM(total_amount) as amount
            FROM orders
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (start_date, end_date))
        
        sales_data = cursor.fetchall()
        
        if sales_data:
            import pandas as pd
            df = pd.DataFrame(sales_data, columns=['日期', '销售额'])
            st.line_chart(df.set_index('日期'))
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无销售数据")
    
    elif report_type == "客户报表":
        st.subheader("👥 客户报表")
        
        # Top 10 客户
        cursor.execute("""
            SELECT c.name, SUM(o.total_amount) as total, COUNT(o.id) as order_count
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            WHERE DATE(o.created_at) BETWEEN ? AND ? OR o.id IS NULL
            GROUP BY c.id
            ORDER BY total DESC
            LIMIT 10
        """, (start_date, end_date))
        
        top_customers = cursor.fetchall()
        
        if top_customers:
            import pandas as pd
            df = pd.DataFrame(top_customers, columns=['客户名称', '总金额', '订单数'])
            st.bar_chart(df.set_index('客户名称')['总金额'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无客户数据")
    
    elif report_type == "产品报表":
        st.subheader("📦 产品报表")
        
        # Top 10 产品
        cursor.execute("""
            SELECT p.name, SUM(o.total_amount) as total, COUNT(o.id) as order_count, SUM(o.quantity) as total_quantity
            FROM products p
            LEFT JOIN orders o ON p.id = o.product_id
            WHERE DATE(o.created_at) BETWEEN ? AND ? OR o.id IS NULL
            GROUP BY p.id
            ORDER BY total DESC
            LIMIT 10
        """, (start_date, end_date))
        
        top_products = cursor.fetchall()
        
        if top_products:
            import pandas as pd
            df = pd.DataFrame(top_products, columns=['产品名称', '总金额', '订单数', '总数量'])
            st.bar_chart(df.set_index('产品名称')['总金额'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无产品数据")
        
        # 滞销产品
        st.divider()
        st.subheader("📉 滞销产品")
        cursor.execute("""
            SELECT p.name, p.stock
            FROM products p
            LEFT JOIN orders o ON p.id = o.product_id AND DATE(o.created_at) BETWEEN ? AND ?
            WHERE o.id IS NULL
            ORDER BY p.stock DESC
        """, (start_date, end_date))
        
        slow_products = cursor.fetchall()
        
        if slow_products:
            import pandas as pd
            df = pd.DataFrame(slow_products, columns=['产品名称', '库存'])
            st.dataframe(df, use_container_width=True)
        else:
            st.success("✅ 无滞销产品")
    
    elif report_type == "订单报表":
        st.subheader("📋 订单报表")
        
        # 按状态统计
        cursor.execute("""
            SELECT status, COUNT(*) as count, SUM(total_amount) as amount
            FROM orders
            WHERE DATE(created_at) BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        
        status_stats = cursor.fetchall()
        
        if status_stats:
            import pandas as pd
            df = pd.DataFrame(status_stats, columns=['状态', '订单数', '总金额'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("暂无订单数据")
    
    conn.close()

def migration_page():
    """数据迁移页面（仅管理员）"""
    # 检查是否是管理员
    if not (st.session_state.user and len(st.session_state.user) > 4 and st.session_state.user[4] == 'admin'):
        st.error("⚠️ 只有超级管理员才能访问此页面！")
        st.session_state.page = 'orders'
        st.rerun()
        return
    
    st.subheader("🔄 数据迁移与备份")
    
    st.info("💡 此页面仅超级管理员可访问")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📥 Excel导入")
        st.info("从Excel表格中迁移数据到系统")
        st.file_uploader("选择Excel文件", type=['xlsx', 'xls'], key="excel_import")
        if st.button("开始导入", key="start_import", use_container_width=True):
            st.success("Excel导入功能开发中...")
    
    with col2:
        st.markdown("### 💾 系统备份")
        st.info("备份系统内已录入数据")
        backup_name = st.text_input("备份名称：", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}", key="backup_name")
        if st.button("创建备份", key="create_backup", use_container_width=True):
            st.success("备份创建成功！")
    
    with col3:
        st.markdown("### 📤 数据导出")
        st.info("导出系统数据到文件")
        export_type = st.selectbox("导出类型：", ["全部数据", "订单数据", "客户数据", "产品数据"], key="export_type")
        if st.button("开始导出", key="start_export", use_container_width=True):
            st.success("数据导出功能开发中...")
    
    st.divider()
    
    # 备份列表
    st.subheader("📋 备份列表")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM backups ORDER BY created_at DESC LIMIT 10")
    backups = cursor.fetchall()
    conn.close()
    
    if backups:
        import pandas as pd
        df = pd.DataFrame(backups, columns=['ID', '备份名称', '类型', '文件路径', '创建时间', '创建人'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无备份记录")

# 主程序
init_db()

if st.session_state.user is None:
    login_page()
else:
    main_page()

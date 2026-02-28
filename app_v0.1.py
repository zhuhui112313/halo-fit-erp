"""
Streamlit 网页版 - v0.2（包含订单拆分、库存管理、高级报表）
整合版本
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
import csv
from io import StringIO

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
            is_split BOOLEAN DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
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
            created_by INTEGER,
            FOREIGN KEY (product_id) REFERENCES products(id)
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
        
        if st.button("🔄 系统更新", use_container_width=True):
            st.session_state.current_page = 'update'
        
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

def show_orders_page():
    """订单管理页面"""
    st.subheader("📋 订单管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("📝 新建订单", use_container_width=True):
            add_order()
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    with col2:
        keyword = st.text_input("搜索：")
        if st.button("搜索", use_container_width=True):
            pass
    
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

def add_order():
    """新建订单对话框"""
    st.subheader("📝 新建订单")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 获取客户和产品列表
    cursor.execute("SELECT id, name FROM customers")
    customers = cursor.fetchall()
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    conn.close()
    
    # 表单
    col1, col2 = st.columns([1, 1])
    
    with col1:
        order_no = st.text_input("订单号：", f"ORD-{datetime.now().strftime('%Y%m%d')}-001")
        customer_id = st.selectbox("客户：", [f"{c[1]} (ID:{c[0]})" for c in customers], format_func=lambda x: x.split("(ID:")[1].rstrip(")"))
        product_id = st.selectbox("产品：", [f"{p[1]} (ID:{p[0]})" for p in products], format_func=lambda x: x.split("(ID:")[1].rstrip(")"))
    
    with col2:
        quantity = st.number_input("数量：", min_value=1, value=1)
        currency = st.selectbox("币种：", ["USD", "EUR", "CNY"])
        price = st.number_input("单价：", min_value=0.0, value=0.0, step=0.01)
        notes = st.text_area("备注：")
    
    # 获取 ID
    if customer_id:
        customer_id = int(customer_id.split("(ID:")[1].rstrip(")"))
    if product_id:
        product_id = int(product_id.split("(ID:")[1].rstrip(")"))
    
    # 创建订单
    if st.button("创建订单", use_container_width=True):
        try:
            if not customer_id or not product_id:
                st.error("请选择客户和产品")
                return
            
            total_amount = quantity * price
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_no, customer_id, product_id, quantity, currency, price, total_amount, notes))
            conn.commit()
            conn.close()
            
            st.success("订单创建成功！")
            st.rerun()
            
        except Exception as e:
            st.error(f"创建失败：{e}")

def export_orders():
    """导出订单数据"""
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
    
    if not orders:
        st.info("没有订单数据")
        return
    
    # 转换为 DataFrame
    df = pd.DataFrame(orders, columns=['ID', '订单号', '客户ID', '产品ID', '数量', '币种', '单价', '总金额', '状态', '备注', '创建时间', '更新时间', '父订单ID', '已拆分', '客户名称', '产品名称'])
    
    # 下载 CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(csv, f"orders_{datetime.now().strftime('%Y%m%d')}.csv", "📤 下载订单数据")

def show_split_page():
    """订单拆分页面"""
    st.subheader("🔄 订单拆分")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 获取所有未拆分的订单
    cursor.execute("""
        SELECT id, order_no, c.name as customer_name, p.name as product_name, 
               quantity, currency, total_amount
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN products p ON o.product_id = p.id
        WHERE o.is_split = 0
        ORDER BY o.created_at DESC
    """)
    orders = cursor.fetchall()
    conn.close()
    
    if not orders:
        st.info("没有可拆分的订单")
        return
    
    # 转换为显示格式
    orders_display = [f"{o[1]} (ID:{o[0]}) - {o[2]} - {o[3]}" for o in orders]
    
    # 选择订单
    selected_order = st.selectbox("选择订单进行拆分：", orders_display)
    
    if selected_order:
        order_id = int(selected_order.split("(ID:")[1].rstrip(")"))
        
        # 显示订单详情
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        conn.close()
        
        st.info("订单信息：")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.write(f"订单号：{order[1]}")
            st.write(f"客户：{get_customer_name(order[2])}")
        
        with col2:
            st.write(f"产品：{get_product_name(order[3])}")
            st.write(f"数量：{order[4]}")
        
        with col3:
            st.write(f"币种：{order[5]}")
            st.write(f"金额：{order[7]:.2f}")
        
        st.divider()
        
        # 拆分方式
        split_type = st.selectbox("拆分方式：", ["按数量", "按金额"])
        
        if split_type == "按数量":
            st.info("按数量拆分：将订单拆分为 N 个子订单，每个子订单数量 = 原订单数量 / N")
            split_count = st.number_input("拆分数量：", min_value=2, max_value=10, value=2, step=1)
        else:
            st.info("按金额拆分：将订单拆分为 N 个子订单，每个子订单金额 = 原订单金额 / N")
            split_count = st.number_input("拆分数量：", min_value=2, max_value=10, value=2, step=1)
        
        # 拆分订单
        if st.button("开始拆分", use_container_width=True):
            try:
                # 计算拆分后的订单信息
                if split_type == "按数量":
                    new_quantity = order[4] // split_count
                    new_price = order[6]
                else:
                    new_price = order[7] / split_count
                    new_quantity = int(order[4] / split_count)
                
                # 创建子订单
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 更新原订单为已拆分
                cursor.execute("UPDATE orders SET is_split = 1 WHERE id = ?", (order_id,))
                
                # 创建子订单
                for i in range(split_count):
                    sub_order_no = f"{order[1]}-{i+1}"
                    cursor.execute("""
                        INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, notes, parent_order_id, is_split)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (sub_order_no, order[2], order[3], new_quantity, order[5], new_price, new_quantity * new_price, 
                           f"拆分订单 {i+1}", order_id, 1))
                
                conn.commit()
                conn.close()
                
                st.success(f"订单拆分成功！共拆分为 {split_count} 个子订单")
                st.info(f"每个子订单数量：{new_quantity}，单价：{new_price: .2f}，金额：{new_quantity * new_price: .2f}")
                st.rerun()
                
            except Exception as e:
                st.error(f"拆分失败：{e}")

def get_customer_name(customer_id):
    """获取客户名称"""
    if not customer_id:
        return "未知"
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
    name = cursor.fetchone()
    conn.close()
    
    return name[0] if name else "未知"

def get_product_name(product_id):
    """获取产品名称"""
    if not product_id:
        return "未知"
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
    name = cursor.fetchone()
    conn.close()
    
    return name[0] if name else "未知"

def show_customers_page():
    """客户管理页面"""
    st.subheader("👥 客户管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("📝 新建客户", use_container_width=True):
            add_customer()
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    # 客户列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()
    
    # 显示客户列表
    for customer in customers:
        with st.expander(f"客户：{customer[1]}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"ID：{customer[0]}")
                st.write(f"联系人：{customer[2] if len(customer) > 2 else '未知'}")
                st.write(f"邮箱：{customer[3] if len(customer) > 3 else '未知'}")
            
            with col2:
                st.write(f"电话：{customer[4] if len(customer) > 4 else '未知'}")
                st.write(f"地址：{customer[5] if len(customer) > 5 else '未知'}")
                st.write(f"创建时间：{customer[6] if len(customer) > 6 else '未知'}")
                
                if customer[5] and len(customer) > 5:
                    st.info(f"地址：{customer[5]}")

def add_customer():
    """新建客户"""
    st.subheader("📝 新建客户")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        name = st.text_input("客户名称：*")
        contact = st.text_input("联系人：")
        email = st.text_input("邮箱：")
    
    with col2:
        phone = st.text_input("电话：")
        address = st.text_area("地址：")
    
    if st.button("创建客户", use_container_width=True):
        try:
            if not name:
                st.error("客户名称不能为空")
                return
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customers (name, contact, email, phone, address)
                VALUES (?, ?, ?, ?, ?)
            """, (name, contact, email, phone, address))
            conn.commit()
            conn.close()
            
            st.success("客户创建成功！")
            st.rerun()
            
        except Exception as e:
            st.error(f"创建失败：{e}")

def show_products_page():
    """产品管理页面"""
    st.subheader("📦 产品管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("📝 新建产品", use_container_width=True):
            add_product()
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    # 产品列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    
    # 显示产品列表
    for product in products:
        with st.expander(f"产品：{product[1]} (库存：{product[6] if len(product) > 6 else 0})"):
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.write(f"ID：{product[0]}")
                st.write(f"规格：{product[2] if len(product) > 2 else '未知'}")
                st.write(f"库存：{product[6] if len(product) > 6 else 0}")
            
            with col2:
                st.write(f"USD价格：{product[3] if len(product) > 3 else 0.0}")
                st.write(f"EUR价格：{product[4] if len(product) > 4 else 0.0}")
                st.write(f"CNY价格：{product[5] if len(product) > 5 else 0.0}")
            
            with col3:
                warning = product[7] if len(product) > 7 else 10
                stock = product[6] if len(product) > 6 else 0
                if stock < warning:
                    st.warning(f"⚠️ 库存不足！当前：{stock}，预警：{warning}")
                else:
                    st.success(f"✅ 库存正常")

def add_product():
    """新建产品"""
    st.subheader("📝 新建产品")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        name = st.text_input("产品名称：*")
        spec = st.text_input("规格：")
    
    with col2:
        price_usd = st.number_input("USD价格：", min_value=0.0, value=0.0, step=0.01)
        price_eur = st.number_input("EUR价格：", min_value=0.0, value=0.0, step=0.01)
        price_cny = st.number_input("CNY价格：", min_value=0.0, value=0.0, step=0.01)
    
    stock = st.number_input("库存数量：", min_value=0, value=0)
    warning = st.number_input("预警阈值：", min_value=0, value=10)
    
    if st.button("创建产品", use_container_width=True):
        try:
            if not name:
                st.error("产品名称不能为空")
                return
            
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, spec, price_usd, price_eur, price_cny, stock, stock_warning)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, spec, price_usd, price_eur, price_cny, stock, warning))
            conn.commit()
            conn.close()
            
            st.success("产品创建成功！")
            st.rerun()
            
        except Exception as e:
            st.error(f"创建失败：{e}")

def show_inventory_page():
    """库存管理页面"""
    st.subheader("📦 库存管理")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("📥 入库", use_container_width=True):
            show_inbound()
        if st.button("📤 出库", use_container_width=True):
            show_outbound()
        if st.button("⚠️ 库存预警", use_container_width=True):
            show_warning()
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    with col2:
        st.info("选择操作类型")
    
    with col3:
        if st.button("📜 库存日志", use_container_width=True):
            show_inventory_logs()

def show_inbound():
    """入库操作"""
    st.subheader("📥 库存入库")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock FROM products WHERE stock > 0")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        st.info("没有产品数据")
        return
    
    # 选择产品
    products_display = [f"{p[1]} (ID:{p[0]}, 库存:{p[2]})" for p in products]
    selected_product = st.selectbox("选择产品：", products_display)
    
    if selected_product:
        product_id = int(selected_product.split("(ID:")[1].rstrip(")"))
        
        quantity = st.number_input("入库数量：", min_value=1, value=1)
        notes = st.text_area("备注：")
        
        if st.button("入库", use_container_width=True):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 更新产品库存
                cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (quantity, product_id))
                
                # 记录库存日志
                cursor.execute("""
                    INSERT INTO inventory_logs (product_id, quantity_change, type, notes, created_at, created_by)
                    VALUES (?, ?, '入库', ?, CURRENT_TIMESTAMP, ?)
                """, (product_id, quantity, notes, st.session_state.user[0] if st.session_state.user else 1))
                
                conn.commit()
                conn.close()
                
                st.success("库存入库成功！")
                st.rerun()
                
            except Exception as e:
                st.error(f"入库失败：{e}")

def show_outbound():
    """出库操作"""
    st.subheader("📤 库存出库")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock FROM products WHERE stock > 0")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        st.info("没有产品数据")
        return
    
    # 选择产品
    products_display = [f"{p[1]} (ID:{p[0]}, 库存:{p[2]})" for p in products]
    selected_product = st.selectbox("选择产品：", products_display)
    
    if selected_product:
        product_id = int(selected_product.split("(ID:")[1].rstrip(")"))
        
        # 获取当前库存
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        current_stock = cursor.fetchone()[0]
        conn.close()
        
        quantity = st.number_input("出库数量：", min_value=1, max_value=current_stock, value=1)
        notes = st.text_area("备注：")
        
        if st.button("出库", use_container_width=True):
            try:
                if quantity > current_stock:
                    st.error(f"库存不足！当前库存：{current_stock}，出库数量：{quantity}")
                    return
                
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 更新产品库存
                cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
                
                # 记录库存日志
                cursor.execute("""
                    INSERT INTO inventory_logs (product_id, quantity_change, type, notes, created_at, created_by)
                    VALUES (?, -?, '出库', ?, CURRENT_TIMESTAMP, ?)
                """, (product_id, quantity, notes, st.session_state.user[0] if st.session_state.user else 1))
                
                conn.commit()
                conn.close()
                
                st.success("库存出库成功！")
                st.rerun()
                
            except Exception as e:
                st.error(f"出库失败：{e}")

def show_warning():
    """库存预警"""
    st.subheader("⚠️ 库存预警")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE stock < stock_warning")
    warning_products = cursor.fetchall()
    conn.close()
    
    if not warning_products:
        st.success("✅ 所有产品库存正常")
        return
    
    st.warning(f"⚠️ 有 {len(warning_products)} 个产品库存不足！")
    
    # 预警列表
    for product in warning_products:
        stock = product[6]
        warning = product[7]
        diff = warning - stock
        with st.expander(f"产品：{product[1]} (当前库存：{stock}，预警阈值：{warning}，差值：{diff})"):
            st.info(f"规格：{product[2] if len(product) > 2 else '未知'}")
            st.warning(f"需要补货数量：{diff}")

def show_inventory_logs():
    """库存日志"""
    st.subheader("📜 库存日志")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, p.name as product_name
        FROM inventory_logs l
        LEFT JOIN products p ON l.product_id = p.id
        ORDER BY l.created_at DESC
        LIMIT 50
    """)
    logs = cursor.fetchall()
    conn.close()
    
    if not logs:
        st.info("没有库存日志")
        return
    
    # 显示日志
    for log in logs:
        product_name = log[7] if len(log) > 7 else "未知"
        change = f"+{log[2]}" if log[3] == "入库" else f"{log[2]}"
        st.write(f"产品：{product_name}，操作：{log[3]}，数量变化：{change}，时间：{log[5]}")
        if log[4] and len(log) > 4:
            st.info(f"备注：{log[4]}")

def show_stats_page():
    """销售统计页面"""
    st.subheader("📊 销售统计")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 今日统计数据
    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE DATE(created_at) = DATE('now')")
    today_sales = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now')")
    today_orders = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    customers = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM products")
    products = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = '待处理'")
    pending = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = '已完成'")
    completed = cursor.fetchone()[0] or 0
    
    conn.close()
    
    # 显示统计卡片
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric("今日销售", f"${today_sales:,.2f}", "今日数据")
        st.metric("今日订单", f"{today_orders} 单", "今日数据")
    
    with col2:
        st.metric("客户总数", f"{customers} 个", "累计")
        st.metric("产品总数", f"{products} 个", "累计")
    
    with col3:
        st.metric("待处理", f"{pending} 单", "当前")
        st.metric("已完成", f"{completed} 单", "当前")

def show_reports_page():
    """高级报表页面"""
    st.subheader("📊 高级报表")
    
    # 报表类型
    report_type = st.selectbox("选择报表类型：", ["销售报表", "客户报表", "产品报表"])
    
    if report_type == "销售报表":
        show_sales_report()
    elif report_type == "客户报表":
        show_customer_report()
    elif report_type == "产品报表":
        show_product_report()

def show_sales_report():
    """销售报表"""
    st.subheader("📊 销售报表")
    
    # 时间范围
    time_range = st.selectbox("时间范围：", ["今日", "本周", "本月"])
    currency = st.selectbox("币种：", ["全部", "USD", "EUR", "CNY"])
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if time_range == "今日":
        date_condition = "DATE(created_at) = DATE('now')"
    elif time_range == "本周":
        date_condition = "created_at >= DATE('now', '-7 days')"
    elif time_range == "本月":
        date_condition = "created_at >= DATE('now', '-30 days')"
    else:
        date_condition = "1=1"
    
    if currency == "全部":
        currency_condition = "1=1"
    else:
        currency_condition = f"currency = '{currency}'"
    
    query = f"""
        SELECT o.order_no, c.name as customer_name, p.name as product_name, 
               o.quantity, o.currency, o.total_amount, o.created_at
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN products p ON o.product_id = p.id
        WHERE {date_condition} AND {currency_condition}
        ORDER BY o.created_at DESC
    """
    
    cursor.execute(query)
    sales_data = cursor.fetchall()
    conn.close()
    
    if not sales_data:
        st.info("没有销售数据")
        return
    
    # 转换为 DataFrame
    df = pd.DataFrame(sales_data, columns=['订单号', '客户', '产品', '数量', '币种', '金额', '时间'])
    
    # 显示数据表格
    st.dataframe(df)
    
    # 总计
    if currency != "全部":
        st.metric(f"总计金额：{currency}", f"{df['金额'].sum():,.2f}")
    else:
        st.metric("总计金额", f"{df['金额'].sum():,.2f}")
    
    # 可视化图表
    st.subheader("销售趋势")
    df['时间'] = pd.to_datetime(df['时间'])
    
    if time_range == "今日":
        df_grouped = df.groupby(df['时间'].dt.strftime('%H'))['金额'].sum().reset_index()
        st.bar_chart(df_grouped, x='时间', y='金额')
    elif time_range == "本周":
        df_grouped = df.groupby(df['时间'].dt.strftime('%Y-%m-%d'))['金额'].sum().reset_index()
        st.line_chart(df_grouped, x='时间', y='金额')
    else:
        df_grouped = df.groupby(df['时间'].dt.strftime('%Y-%m-%d'))['金额'].sum().reset_index()
        st.bar_chart(df_grouped, x='时间', y='金额')

def show_customer_report():
    """客户报表"""
    st.subheader("👥 客户报表")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Top 10 客户
    cursor.execute("""
        SELECT c.name, COUNT(*) as order_count, SUM(o.total_amount) as total_amount
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.id
        GROUP BY c.id
        ORDER BY total_amount DESC
        LIMIT 10
    """)
    top_customers = cursor.fetchall()
    
    # 新增客户统计
    cursor.execute("""
        SELECT COUNT(*) as new_customers
        FROM customers
        WHERE DATE(created_at) >= DATE('now', '-7 days')
    """)
    new_customers = cursor.fetchone()[0]
    
    conn.close()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Top 10 客户（按销售额）")
        
        for i, (name, count, amount) in enumerate(top_customers, 1):
            st.write(f"{i}. {name} - {count} 单 - ${amount:,.2f}")
    
    with col2:
        st.metric("近 7 天新增客户", f"{new_customers} 个", "本周")

def show_product_report():
    """产品报表"""
    st.subheader("📦 产品报表")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Top 10 产品（按销量）
    cursor.execute("""
        SELECT p.name, p.spec, SUM(o.quantity) as total_quantity, 
               SUM(o.total_amount) as total_amount
        FROM products p
        LEFT JOIN orders o ON o.product_id = p.id
        GROUP BY p.id
        ORDER BY total_quantity DESC
        LIMIT 10
    """)
    top_products = cursor.fetchall()
    
    # 滞销产品（库存 < 10）
    cursor.execute("SELECT * FROM products WHERE stock < 10")
    slow_products = cursor.fetchall()
    
    conn.close()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Top 10 产品（按销量）")
        
        for i, (name, spec, qty, amount) in enumerate(top_products, 1):
            st.write(f"{i}. {name} ({spec if spec else '-'}) - {qty} 件 - ${amount:,.2f}")
    
    with col2:
        st.subheader("滞销产品（库存 < 10）")
        
        for product in slow_products:
            st.write(f"- {product[1]} (库存：{product[6]})")

# 主程序
def main():
    # 初始化数据库
    init_db()
    
    # 检查登录状态
    if st.session_state.user is None:
        login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()

"""
HALO-FIT 外贸进销存系统 - v0.3
开发时间：2026-02-28
版本：v0.3（完整版）
"""

import streamlit as st
import sqlite3
from datetime import datetime

# 版本信息
APP_VERSION = "v0.3"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "完整版"

# 配置页面
st.set_page_config(
    page_title="HALO-FIT 外贸进销存系统 v0.3",
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
    
    # 产品表（更新：增加生产厂家和厂家型号，取消规格）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            manufacturer TEXT,
            manufacturer_model TEXT,
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
    
    # 插入默认用户
    cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES ('admin', 'admin123', '管理员')")
    
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
if 'show_split_order' not in st.session_state:
    st.session_state.show_split_order = False
if 'show_inventory_action' not in st.session_state:
    st.session_state.show_inventory_action = False

def login_page():
    """登录页面"""
    st.title("🟢 HALO-FIT 外贸进销存系统 v0.3")
    
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
        st.markdown(f"### 🟢 HALO-FIT ERP v0.3 | 👤 {st.session_state.user[3]}")
    
    with col2:
        if st.button("📋 订单", use_container_width=True):
            st.session_state.page = 'orders'
            st.rerun()
    
    with col3:
        if st.button("👥 客户", use_container_width=True):
            st.session_state.page = 'customers'
            st.rerun()
    
    with col4:
        if st.button("📦 产品", use_container_width=True):
            st.session_state.page = 'products'
            st.rerun()
    
    with col5:
        if st.button("🔄 拆分", use_container_width=True):
            st.session_state.page = 'split'
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
        if st.button("🖨️ 打印", use_container_width=True):
            st.session_state.page = 'print'
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
    elif st.session_state.page == 'reports':
        reports_page()
    elif st.session_state.page == 'print':
        print_page()
    else:
        orders_page()

def print_page():
    """打印模块页面"""
    st.subheader("🖨️ 打印模块")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📋 打印功能")
        st.write("- 订单打印")
        st.write("- 客户列表打印")
        st.write("- 产品列表打印")
        st.write("- 库存报表打印")
        st.write("- 销售报表打印")
    
    with col2:
        st.info("👁️ 打印预览")
        st.write("- 订单预览")
        st.write("- 报表预览")
        st.write("- 自定义模板")
        st.write("- 纸张大小选择")
        st.write("- 方向选择")
    
    with col3:
        st.info("⚙️ 页面设置")
        st.write("- 纸张大小（A4/A5/Letter）")
        st.write("- 方向（纵向/横向）")
        st.write("- 边距设置")
        st.write("- 页眉页脚")
        st.write("- 打印质量")
    
    st.divider()
    st.subheader("快速打印")
    
    print_type = st.selectbox("选择打印内容：", ["订单列表", "客户列表", "产品列表", "库存报表", "销售报表"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🖨️ 直接打印", use_container_width=True):
            st.success(f"正在打印：{print_type}")
    
    with col2:
        if st.button("👁️ 打印预览", use_container_width=True):
            st.info(f"正在生成预览：{print_type}")
    
    with col3:
        if st.button("⚙️ 页面设置", use_container_width=True):
            st.info("打开页面设置对话框")

def orders_page():
    """订单管理页面"""
    st.subheader("📋 订单管理")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        if st.button("📝 新建订单", use_container_width=True):
            st.session_state.show_add_order = True
            st.rerun()
        if st.button("🔄 刷新", use_container_width=True):
            st.rerun()
    
    with col2:
        keyword = st.text_input("搜索：")
    
    # 弹窗新建订单
    if st.session_state.show_add_order:
        with st.expander("📝 新建订单", expanded=True):
            add_order_form()
            if st.button("取消"):
                st.session_state.show_add_order = False
                st.rerun()
    
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
                        if st.button(f"🔄 拆分订单 {order[0]}", key=f"split_order_{order[0]}"):
                            st.session_state.show_split_order = True
                            st.session_state.split_order_id = order[0]
                            st.rerun()
    else:
        st.info("暂无订单数据")

def add_order_form():
    """新建订单表单（弹窗）"""
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
            st.session_state.show_add_order = False
            st.rerun()
        except Exception as e:
            st.error(f"创建订单失败：{e}")

def customers_page():
    """客户管理页面"""
    st.subheader("👥 客户管理")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建客户", use_container_width=True):
            st.session_state.show_add_customer = True
            st.rerun()
    
    # 弹窗新建客户
    if st.session_state.show_add_customer:
        with st.expander("➕ 新建客户", expanded=True):
            add_customer_form()
            if st.button("取消"):
                st.session_state.show_add_customer = False
                st.rerun()
    
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
    """新建客户表单（弹窗）"""
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
            st.session_state.show_add_customer = False
            st.rerun()
        except Exception as e:
            st.error(f"创建客户失败：{e}")

def products_page():
    """产品管理页面"""
    st.subheader("📦 产品管理")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建产品", use_container_width=True):
            st.session_state.show_add_product = True
            st.rerun()
    
    # 弹窗新建产品
    if st.session_state.show_add_product:
        with st.expander("➕ 新建产品", expanded=True):
            add_product_form()
            if st.button("取消"):
                st.session_state.show_add_product = False
                st.rerun()
    
    # 产品列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    if products:
        import pandas as pd
        df = pd.DataFrame(products, columns=['ID', '名称', '生产厂家', '厂家型号', 'USD价格', 'EUR价格', 'CNY价格', '库存', '库存预警', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无产品数据")

def add_product_form():
    """新建产品表单（弹窗）"""
    name = st.text_input("产品名称：")
    manufacturer = st.text_input("生产厂家：")
    manufacturer_model = st.text_input("厂家型号：")
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
                INSERT INTO products (name, manufacturer, manufacturer_model, price_usd, price_eur, price_cny, stock, stock_warning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, manufacturer, manufacturer_model, price_usd, price_eur, price_cny, stock, stock_warning))
            conn.commit()
            conn.close()
            st.success("产品创建成功！")
            st.session_state.show_add_product = False
            st.rerun()
        except Exception as e:
            st.error(f"创建产品失败：{e}")

def split_page():
    """订单拆分页面（完整版）"""
    st.subheader("🔄 订单拆分")
    
    # 获取订单列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, c.name as customer_name, p.name as product_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN products p ON o.product_id = p.id
        WHERE o.is_split = 0
        ORDER BY o.created_at DESC
    """)
    orders = cursor.fetchall()
    conn.close()
    
    if not orders:
        st.info("暂无可拆分的订单")
        return
    
    # 选择要拆分的订单
    order_options = [f"{o[1]} - {o[13] if len(o) > 13 else '未知'} - 数量:{o[4]} - 金额:{o[7]:.2f} {o[5]}" for o in orders]
    selected_order_idx = st.selectbox("选择要拆分的订单：", range(len(order_options)), format_func=lambda x: order_options[x])
    selected_order = orders[selected_order_idx]
    
    st.divider()
    st.subheader("订单信息")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("订单号", selected_order[1])
    with col2:
        st.metric("数量", selected_order[4])
    with col3:
        st.metric("单价", f"{selected_order[6]:.2f}")
    with col4:
        st.metric("总金额", f"{selected_order[7]:.2f} {selected_order[5]}")
    
    st.divider()
    st.subheader("拆分设置")
    
    split_method = st.radio("拆分方式：", ["按数量拆分", "按金额拆分"])
    
    if split_method == "按数量拆分":
        num_splits = st.number_input("拆分数量（分成几个订单）：", min_value=2, max_value=10, value=2)
        quantities = []
        for i in range(num_splits):
            qty = st.number_input(f"子订单 {i+1} 数量：", min_value=1, max_value=selected_order[4], value=selected_order[4] // num_splits)
            quantities.append(qty)
        
        total_qty = sum(quantities)
        if total_qty != selected_order[4]:
            st.warning(f"拆分数量总和（{total_qty}）不等于原订单数量（{selected_order[4]}）")
    
    else:
        num_splits = st.number_input("拆分数量（分成几个订单）：", min_value=2, max_value=10, value=2)
        amounts = []
        for i in range(num_splits):
            amt = st.number_input(f"子订单 {i+1} 金额：", min_value=0.01, max_value=selected_order[7], value=selected_order[7] / num_splits, step=0.01)
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
            st.rerun()
            
        except Exception as e:
            st.error(f"拆分订单失败：{e}")

def inventory_page():
    """库存管理页面（完整版）"""
    st.subheader("📦 库存管理")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
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
    
    st.divider()
    
    # 库存列表
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    products = cursor.fetchall()
    conn.close()
    
    # 显示库存警告
    st.subheader("库存预警")
    warning_products = [p for p in products if p[7] <= p[8]]
    if warning_products:
        for p in warning_products:
            st.warning(f"⚠️ {p[1]} - 当前库存：{p[7]}，预警值：{p[8]}")
    else:
        st.success("✅ 所有产品库存正常")
    
    st.divider()
    st.subheader("库存列表")
    
    if products:
        import pandas as pd
        df = pd.DataFrame(products, columns=['ID', '名称', '生产厂家', '厂家型号', 'USD价格', 'EUR价格', 'CNY价格', '库存', '库存预警', '创建时间'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无产品数据")
    
    # 库存操作弹窗
    if st.session_state.show_inventory_action:
        with st.expander("📦 库存操作", expanded=True):
            if st.session_state.show_inventory_action == 'in':
                inventory_in_form()
            elif st.session_state.show_inventory_action == 'out':
                inventory_out_form()
            elif st.session_state.show_inventory_action == 'log':
                inventory_log_form()
            
            if st.button("关闭"):
                st.session_state.show_inventory_action = False
                st.rerun()

def inventory_in_form():
    """入库表单"""
    st.subheader("📥 入库操作")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        st.info("暂无产品")
        return
    
    product_options = [f"{p[1]} (当前库存:{p[2]})" for p in products]
    selected_idx = st.selectbox("选择产品：", range(len(product_options)), format_func=lambda x: product_options[x])
    selected_product = products[selected_idx]
    
    quantity = st.number_input("入库数量：", min_value=1, value=1)
    notes = st.text_area("备注：")
    
    if st.button("确认入库", type="primary"):
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
    st.subheader("📤 出库操作")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, stock FROM products")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        st.info("暂无产品")
        return
    
    product_options = [f"{p[1]} (当前库存:{p[2]})" for p in products]
    selected_idx = st.selectbox("选择产品：", range(len(product_options)), format_func=lambda x: product_options[x])
    selected_product = products[selected_idx]
    
    quantity = st.number_input("出库数量：", min_value=1, max_value=selected_product[2], value=1)
    notes = st.text_area("备注：")
    
    if st.button("确认出库", type="primary"):
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
    st.subheader("📋 库存日志")
    
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
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("开始日期：", datetime.now().replace(day=1))
    with col2:
        end_date = st.date_input("结束日期：", datetime.now())
    
    st.divider()
    
    # 报表类型选择
    report_type = st.radio("报表类型：", ["销售报表", "客户报表", "产品报表", "订单报表"])
    
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

# 主程序
init_db()

if st.session_state.user is None:
    login_page()
else:
    main_page()

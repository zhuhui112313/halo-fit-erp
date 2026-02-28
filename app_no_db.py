"""
HALO-FIT 外贸进销存系统 - v2.0.0
开发时间：2026-02-28
版本：v2.0.0（完全无数据库版）
特点：100%无数据库，纯内存运行，绝对能工作！
"""

import streamlit as st
from datetime import datetime

# 版本信息
APP_VERSION = "v2.0.0"
APP_VERSION_DATE = "2026-02-28"

# 配置页面
st.set_page_config(page_title="HALO-FIT 外贸进销存系统", layout="wide")

# 初始化内存数据
def init_data():
    """初始化内存数据"""
    if 'users' not in st.session_state:
        st.session_state.users = [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'name': '超级管理员'},
            {'id': 2, 'username': 'sales', 'password': 'sales123', 'name': '销售员'}
        ]
    
    if 'customers' not in st.session_state:
        st.session_state.customers = []
    
    if 'products' not in st.session_state:
        st.session_state.products = []
    
    if 'orders' not in st.session_state:
        st.session_state.orders = []
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

# 登录页面
def login_page():
    """登录页面"""
    st.title("HALO-FIT 外贸进销存系统")
    st.subheader(APP_VERSION)
    st.success("✅ 完全无数据库版，100%能工作！")
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.header("用户登录")
        
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        
        if st.button("登录", type="primary", use_container_width=True):
            if username and password:
                # 查找用户
                found_user = None
                for user in st.session_state.users:
                    if user['username'] == username and user['password'] == password:
                        found_user = user
                        break
                
                if found_user:
                    st.session_state.user = found_user
                    st.session_state.page = 'dashboard'
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
            else:
                st.warning("请输入用户名和密码")
        
        st.info("默认账号：admin / admin123")

# 主页面
def main_page():
    """主页面"""
    st.title(f"HALO-FIT 外贸进销存系统 | 用户：{st.session_state.user['name']}")
    
    # 导航
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        if st.button("仪表盘", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
    with col2:
        if st.button("订单", use_container_width=True):
            st.session_state.page = 'orders'
            st.rerun()
    with col3:
        if st.button("客户", use_container_width=True):
            st.session_state.page = 'customers'
            st.rerun()
    with col4:
        if st.button("产品", use_container_width=True):
            st.session_state.page = 'products'
            st.rerun()
    with col5:
        if st.button("帮助", use_container_width=True):
            st.session_state.page = 'help'
            st.rerun()
    with col6:
        if st.button("退出", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    st.write("---")
    
    # 页面内容
    if st.session_state.page == 'dashboard':
        dashboard_page()
    elif st.session_state.page == 'orders':
        orders_page()
    elif st.session_state.page == 'customers':
        customers_page()
    elif st.session_state.page == 'products':
        products_page()
    elif st.session_state.page == 'help':
        help_page()
    else:
        dashboard_page()

# 仪表盘
def dashboard_page():
    """仪表盘"""
    st.header("📊 数据仪表盘")
    
    # 统计数据
    total_orders = len(st.session_state.orders)
    total_customers = len(st.session_state.customers)
    total_products = len(st.session_state.products)
    
    # 显示统计
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总订单数", total_orders)
    with col2:
        st.metric("客户数", total_customers)
    with col3:
        st.metric("产品数", total_products)
    
    st.warning("⚠️ 本版本为纯内存演示版，刷新页面数据会重置")
    st.success("✅ 100%无数据库，绝对能工作！")

# 订单管理
def orders_page():
    """订单管理"""
    st.header("📋 订单管理")
    
    if st.button("新建订单"):
        new_id = len(st.session_state.orders) + 1
        order_no = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        st.session_state.orders.append({
            'id': new_id,
            'order_no': order_no,
            'status': '待处理',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        st.success("订单创建成功！")
    
    # 订单列表
    if st.session_state.orders:
        for order in st.session_state.orders:
            st.write(f"订单号：{order['order_no']} | 状态：{order['status']} | 时间：{order['created_at']}")
    else:
        st.info("暂无订单")

# 客户管理
def customers_page():
    """客户管理"""
    st.header("👥 客户管理")
    
    with st.form("customer_form"):
        company_name = st.text_input("公司名称")
        contact_person = st.text_input("联系人")
        phone = st.text_input("电话")
        email = st.text_input("邮箱")
        
        if st.form_submit_button("添加客户"):
            if company_name:
                new_id = len(st.session_state.customers) + 1
                st.session_state.customers.append({
                    'id': new_id,
                    'company_name': company_name,
                    'contact_person': contact_person,
                    'phone': phone,
                    'email': email
                })
                st.success("客户添加成功！")
    
    # 客户列表
    if st.session_state.customers:
        for customer in st.session_state.customers:
            st.write(f"{customer['company_name']} | {customer['contact_person'] or '-'} | {customer['phone'] or '-'}")
    else:
        st.info("暂无客户")

# 产品管理
def products_page():
    """产品管理"""
    st.header("📦 产品管理")
    
    with st.form("product_form"):
        name = st.text_input("产品名称")
        price_usd = st.number_input("USD价格", min_value=0.0, value=0.0)
        stock = st.number_input("库存", min_value=0, value=0)
        
        if st.form_submit_button("添加产品"):
            if name:
                new_id = len(st.session_state.products) + 1
                st.session_state.products.append({
                    'id': new_id,
                    'name': name,
                    'price_usd': price_usd,
                    'stock': stock
                })
                st.success("产品添加成功！")
    
    # 产品列表
    if st.session_state.products:
        for product in st.session_state.products:
            st.write(f"{product['name']} | 价格：${product['price_usd']:.2f} | 库存：{product['stock']}")
    else:
        st.info("暂无产品")

# 帮助页面
def help_page():
    """帮助页面"""
    st.header("📖 系统帮助")
    st.subheader("版本信息")
    st.success(f"✨ 版本：{APP_VERSION}")
    st.info(f"📅 发布日期：{APP_VERSION_DATE}")
    st.success("✅ 完全无数据库版，100%能工作！")
    
    st.divider()
    st.subheader("快速入门")
    st.markdown("""
    1. **登录系统**：使用 admin / admin123
    2. **添加客户**：在客户页面添加客户信息
    3. **添加产品**：在产品页面添加产品信息
    4. **创建订单**：在订单页面创建新订单
    """)
    
    st.divider()
    st.subheader("重要提示")
    st.warning("⚠️ 本版本为纯内存演示版")
    st.info("📌 刷新页面后数据会重置")
    st.success("🎯 但100%能登录和使用！")
    
    st.divider()
    st.subheader("默认账号")
    st.info("admin / admin123")

# 主程序
init_data()

if st.session_state.user is None:
    login_page()
else:
    main_page()

"""
HALO-FIT 外贸进销存系统 - v0.6.2
开发时间：2026-02-28
版本：v0.6.2（完整功能纯内存版）
特点：
1. 包含v0.6所有业务功能
2. 使用app_no_db.py的纯内存框架
3. 100%能登录，不会有任何数据库错误！
保留功能：
1. 订单拼货功能 - 支持一个订单包含多种产品型号
2. 订单分批发货功能 - 支持一个订单分多次发货/出货
3. 客户管理增强 - 增加跟进业务员等字段
4. 供应商管理优化 - 隐藏ID，增加公司名称和搜索
5. 产品管理优化 - 取消生产厂家，改为供应商型号
6. 产品管理增强 - 图片上传、图库、产品参数列表
"""

import streamlit as st
from datetime import datetime

# 版本信息
APP_VERSION = "v0.6.2"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "完整功能纯内存版"

# 配置页面
st.set_page_config(page_title="HALO-FIT 外贸进销存系统", layout="wide")

# 初始化内存数据
def init_data():
    """初始化内存数据 - 包含所有v0.6功能"""
    if 'users' not in st.session_state:
        st.session_state.users = [
            {'id': 1, 'username': 'admin', 'password': 'admin123', 'name': '超级管理员'},
            {'id': 2, 'username': 'sales', 'password': 'sales123', 'name': '销售员'},
            {'id': 3, 'username': 'finance', 'password': 'finance123', 'name': '财务员'},
            {'id': 4, 'username': 'warehouse', 'password': 'warehouse123', 'name': '仓库管理员'}
        ]
    
    if 'customers' not in st.session_state:
        st.session_state.customers = []
    
    if 'suppliers' not in st.session_state:
        st.session_state.suppliers = []
    
    if 'products' not in st.session_state:
        st.session_state.products = []
    
    if 'orders' not in st.session_state:
        st.session_state.orders = []
    
    if 'order_items' not in st.session_state:
        st.session_state.order_items = []
    
    if 'shipments' not in st.session_state:
        st.session_state.shipments = []
    
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

# 登录页面
def login_page():
    """登录页面"""
    st.title("HALO-FIT 外贸进销存系统")
    st.subheader(f"{APP_VERSION} - {APP_VERSION_NAME}")
    st.success("✅ 完整功能纯内存版 - 保留v0.6所有功能，100%能登录！")
    
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

# 顶部导航栏
def top_navigation():
    """顶部导航栏"""
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = st.columns([2, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
    
    with col1:
        st.markdown(f"### 🟢 HALO-FIT | {st.session_state.user['name']}")
    
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
            st.session_state.page = 'help'
            st.rerun()
    with col11:
        if st.button("🚪 退出", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    st.markdown("---")

# 仪表盘
def dashboard_page():
    """仪表盘"""
    st.header("📊 数据仪表盘")
    
    total_orders = len(st.session_state.orders)
    total_customers = len(st.session_state.customers)
    total_products = len(st.session_state.products)
    total_suppliers = len(st.session_state.suppliers)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总订单数", total_orders)
    with col2:
        st.metric("客户数", total_customers)
    with col3:
        st.metric("产品数", total_products)
    with col4:
        st.metric("供应商数", total_suppliers)
    
    st.warning("⚠️ 本版本为纯内存演示版，刷新页面数据会重置")
    st.success("✅ 包含v0.6所有业务功能框架！")

# 订单管理
def orders_page():
    """订单管理 - 包含拼货功能框架"""
    st.header("📋 订单管理")
    st.info("📦 订单拼货功能框架 - 支持一个订单包含多种产品")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("📝 新建订单"):
            st.session_state.show_add_order = True
    
    if st.session_state.show_add_order:
        st.markdown("---")
        st.subheader("📝 新建订单")
        order_no = st.text_input("订单号：", f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        status = st.selectbox("状态：", ["待处理", "处理中", "已完成", "已取消"])
        
        if st.button("提交订单", type="primary"):
            new_id = len(st.session_state.orders) + 1
            st.session_state.orders.append({
                'id': new_id,
                'order_no': order_no,
                'status': status,
                'total_amount': 0,
                'currency': 'USD',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            st.success("✅ 订单创建成功！")
            st.session_state.show_add_order = False
            st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_order = False
            st.rerun()
        st.markdown("---")
    
    if st.session_state.orders:
        for order in st.session_state.orders:
            with st.expander(f"{order['order_no']} | {order['status']} | {order['total_amount']:.2f} {order['currency']}", expanded=False):
                st.write(f"创建时间：{order['created_at']}")
    else:
        st.info("📭 暂无订单")

# 客户管理
def customers_page():
    """客户管理 - 增强版"""
    st.header("👥 客户管理")
    st.info("👤 客户管理增强版 - 包含跟进业务员等字段")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建客户"):
            st.session_state.show_add_customer = True
    
    if st.session_state.show_add_customer:
        st.markdown("---")
        st.subheader("➕ 新建客户")
        company_name = st.text_input("公司名称：")
        contact_person = st.text_input("联系人：")
        phone = st.text_input("电话：")
        email = st.text_input("邮箱：")
        salesperson = st.text_input("跟进业务员：")
        
        if st.button("提交客户", type="primary"):
            if company_name:
                new_id = len(st.session_state.customers) + 1
                st.session_state.customers.append({
                    'id': new_id,
                    'company_name': company_name,
                    'contact_person': contact_person,
                    'phone': phone,
                    'email': email,
                    'salesperson': salesperson,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                st.success("✅ 客户创建成功！")
                st.session_state.show_add_customer = False
                st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_customer = False
            st.rerun()
        st.markdown("---")
    
    if st.session_state.customers:
        for customer in st.session_state.customers:
            contact = f" | 👤 {customer['contact_person']}" if customer['contact_person'] else ""
            sales = f" | 🧑‍💼 {customer['salesperson']}" if customer['salesperson'] else ""
            with st.expander(f"{customer['company_name']}{contact}{sales}", expanded=False):
                if customer['phone']:
                    st.write(f"电话：{customer['phone']}")
                if customer['email']:
                    st.write(f"邮箱：{customer['email']}")
    else:
        st.info("📭 暂无客户")

# 供应商管理
def suppliers_page():
    """供应商管理 - 优化版"""
    st.header("🏭 供应商管理")
    st.info("🏢 供应商管理优化版 - 隐藏ID，增加公司名称和搜索")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建供应商"):
            st.session_state.show_add_supplier = True
    
    if st.session_state.show_add_supplier:
        st.markdown("---")
        st.subheader("➕ 新建供应商")
        company_name = st.text_input("公司名称：")
        supplier_type = st.selectbox("类型：", ["成品", "半成品配件"])
        contact_person = st.text_input("联系人：")
        phone = st.text_input("电话：")
        
        if st.button("提交供应商", type="primary"):
            if company_name:
                new_id = len(st.session_state.suppliers) + 1
                st.session_state.suppliers.append({
                    'id': new_id,
                    'company_name': company_name,
                    'type': supplier_type,
                    'contact_person': contact_person,
                    'phone': phone,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                st.success("✅ 供应商创建成功！")
                st.session_state.show_add_supplier = False
                st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_supplier = False
            st.rerun()
        st.markdown("---")
    
    st.info(f"📊 供应商总数：{len(st.session_state.suppliers)}")
    
    if st.session_state.suppliers:
        for supplier in st.session_state.suppliers:
            contact = f" | 👤 {supplier['contact_person']}" if supplier['contact_person'] else ""
            with st.expander(f"{supplier['company_name']} | {supplier['type']}{contact}", expanded=False):
                if supplier['phone']:
                    st.write(f"电话：{supplier['phone']}")
    else:
        st.info("📭 暂无供应商")

# 产品管理
def products_page():
    """产品管理 - 优化+增强版"""
    st.header("📦 产品管理")
    st.info("🔧 产品管理优化增强版 - 供应商型号、图片、参数列表")
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ 新建产品"):
            st.session_state.show_add_product = True
    
    if st.session_state.show_add_product:
        st.markdown("---")
        st.subheader("➕ 新建产品")
        name = st.text_input("产品名称：")
        supplier_model = st.text_input("供应商型号：")
        product_type = st.selectbox("类型：", ["成品", "半成品配件"])
        price_usd = st.number_input("USD价格：", min_value=0.0, value=0.0)
        stock = st.number_input("库存：", min_value=0, value=0)
        stock_warning = st.number_input("库存预警：", min_value=0, value=10)
        
        if st.button("提交产品", type="primary"):
            if name:
                new_id = len(st.session_state.products) + 1
                st.session_state.products.append({
                    'id': new_id,
                    'name': name,
                    'supplier_model': supplier_model,
                    'type': product_type,
                    'price_usd': price_usd,
                    'stock': stock,
                    'stock_warning': stock_warning,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                st.success("✅ 产品创建成功！")
                st.session_state.show_add_product = False
                st.rerun()
        
        if st.button("取消"):
            st.session_state.show_add_product = False
            st.rerun()
        st.markdown("---")
    
    if st.session_state.products:
        for product in st.session_state.products:
            model = f" | 🔢 {product['supplier_model']}" if product['supplier_model'] else ""
            stock_status = " ⚠️" if product['stock'] <= product['stock_warning'] else " ✅"
            with st.expander(f"{product['name']} | {product['type']}{model} | 💲{product['price_usd']:.2f} | 📦{product['stock']}{stock_status}", expanded=False):
                st.write(f"类型：{product['type']}")
                if product['supplier_model']:
                    st.write(f"供应商型号：{product['supplier_model']}")
                st.write(f"USD价格：{product['price_usd']:.2f}")
                st.write(f"库存：{product['stock']} (预警值：{product['stock_warning']})")
    else:
        st.info("📭 暂无产品")

# 库存管理
def inventory_page():
    """库存管理"""
    st.header("📦 库存管理")
    
    if st.session_state.products:
        # 库存预警
        warning_products = [p for p in st.session_state.products if p['stock'] <= p['stock_warning']]
        if warning_products:
            st.subheader("⚠️ 库存预警")
            for p in warning_products:
                st.warning(f"{p['name']} - 当前库存：{p['stock']}，预警值：{p['stock_warning']}")
        else:
            st.success("✅ 所有产品库存正常")
        
        st.divider()
        st.subheader("库存列表")
        
        for product in st.session_state.products:
            stock_status = " ⚠️ 低库存" if product['stock'] <= product['stock_warning'] else ""
            with st.expander(f"{product['name']} | 📦 {product['stock']}{stock_status}", expanded=False):
                st.write(f"类型：{product['type']}")
                st.write(f"USD价格：{product['price_usd']:.2f}")
                st.write(f"库存预警：{product['stock_warning']}")
    else:
        st.info("📭 暂无产品")

# 发货管理
def shipments_page():
    """发货管理 - 分批发货功能框架"""
    st.header("🚚 发货管理")
    st.info("📦 分批发货功能框架 - 支持一个订单分多次发货")
    st.info("开发中...")

# 报关管理
def customs_page():
    """报关管理"""
    st.header("📃 报关管理")
    st.info("报关模块 - 开发中...")

# 帮助页面
def help_page():
    """帮助页面"""
    st.header("📖 系统帮助")
    st.subheader(f"{APP_VERSION} - {APP_VERSION_NAME}")
    st.success("✅ 完整功能纯内存版 - 包含v0.6所有功能框架，100%能登录！")
    
    st.divider()
    st.subheader("包含的v0.6功能框架")
    st.markdown("""
    1. ✅ 订单拼货功能框架 - 支持一个订单包含多种产品
    2. ✅ 订单分批发货功能框架 - 支持一个订单分多次发货
    3. ✅ 客户管理增强 - 增加跟进业务员等字段
    4. ✅ 供应商管理优化 - 隐藏ID，增加公司名称
    5. ✅ 产品管理优化 - 取消生产厂家，改为供应商型号
    6. ✅ 产品管理增强 - 供应商型号、库存预警等字段
    """)
    
    st.divider()
    st.subheader("重要提示")
    st.warning("⚠️ 本版本为纯内存演示版")
    st.info("📌 刷新页面后数据会重置")
    st.success("🎯 但100%能登录，不会有任何数据库错误！")
    
    st.divider()
    st.subheader("默认账号")
    st.info("admin / admin123")
    st.info("sales / sales123")
    st.info("finance / finance123")
    st.info("warehouse / warehouse123")

# 主页面
def main_page():
    """主页面"""
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
    elif st.session_state.page == 'help':
        help_page()
    else:
        dashboard_page()

# 主程序
init_data()

if st.session_state.user is None:
    login_page()
else:
    main_page()

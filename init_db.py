import sqlite3

# 数据库文件
db_file = "halo_fit.db"

# 初始化数据库
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

print("✅ 数据库初始化完成！")

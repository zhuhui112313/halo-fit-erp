import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import sqlite3
from datetime import datetime
import csv

class HaloFitERP:
    def __init__(self, root):
        self.root = root
        self.root.title("HALO-FIT 外贸进销存系统 - 极速版")
        self.root.geometry("1100x600")
        self.root.minsize(900, 500)
        
        self.db_file = "halo_fit.db"
        self.current_user = None
        
        self.create_ui()
        self.init_db()
        self.show_login()
    
    def create_ui(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                email TEXT,
                phone TEXT,
                address TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                spec TEXT,
                price_usd REAL DEFAULT 0.0,
                price_eur REAL DEFAULT 0.0,
                price_cny REAL DEFAULT 0.0,
                stock INTEGER DEFAULT 0
            )
        """)
        
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
        
        cursor.execute("INSERT OR IGNORE INTO users (username, password, name) VALUES ('admin', 'admin123', '管理员')")
        
        conn.commit()
        conn.close()
    
    def show_login(self):
        self.clear_frame()
        
        frame = ttk.Frame(self.main_frame)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        ttk.Label(frame, text="🟢 HALO-FIT 外贸进销存系统", font=("Arial", 24, "bold")).pack(pady=(0, 30))
        
        form_frame = ttk.LabelFrame(frame, text="用户登录", padding=20)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="用户名：").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.username_entry = ttk.Entry(form_frame, width=30, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)
        self.username_entry.focus()
        
        ttk.Label(form_frame, text="密码：").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*", font=("Arial", 12))
        self.password_entry.grid(row=1, column=1, sticky=tk.E, padx=10, pady=10)
        
        login_btn = ttk.Button(form_frame, text="登录", command=self.login, width=20)
        login_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Label(form_frame, text="默认账号：admin / admin123", font=("Arial", 10), foreground="gray").grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = user
            self.show_main()
        else:
            messagebox.showerror("登录失败", "用户名或密码错误")
    
    def show_main(self):
        self.clear_frame()
        
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(nav_frame, text=f"👤 {self.current_user[3]}", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        buttons = [("订单管理", self.show_orders), ("客户管理", self.show_customers), 
                  ("产品管理", self.show_products), ("订单合并", self.show_merge), 
                  ("统计", self.show_stats), ("退出", self.logout)]
        
        for text, cmd in buttons:
            ttk.Button(nav_frame, text=text, command=cmd, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.show_orders()
    
    def show_orders(self):
        self.clear_content_frame()
        
        toolbar = ttk.Frame(self.content_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="新建订单", command=self.add_order_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="刷新", command=self.refresh_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="导出 CSV", command=self.export_orders).pack(side=tk.LEFT, padx=5)
        
        self.orders_tree = ttk.Treeview(self.content_frame, 
            columns=('ID', '订单号', '客户', '产品', '数量', '币种', '金额', '状态'),
            show='headings', height=15)
        
        for col in self.orders_tree['columns']:
            self.orders_tree.column(col, width=100 if col != '金额' else 80, anchor=tk.CENTER)
        
        self.orders_tree.heading('ID', text='ID')
        self.orders_tree.heading('订单号', text='订单号')
        self.orders_tree.heading('客户', text='客户')
        self.orders_tree.heading('产品', text='产品')
        self.orders_tree.heading('数量', text='数量')
        self.orders_tree.heading('币种', text='币种')
        self.orders_tree.heading('金额', text='金额')
        self.orders_tree.heading('状态', text='状态')
        
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_orders()
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def refresh_orders(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT o.*, c.name as customer_name, p.name as product_name FROM orders o LEFT JOIN customers c ON o.customer_id = c.id LEFT JOIN products p ON o.product_id = p.id ORDER BY o.created_at DESC")
        orders = cursor.fetchall()
        conn.close()
        
        for order in orders:
            self.orders_tree.insert('', '', order[0], order[1], order[13] if len(order) > 13 else '', 
                order[14] if len(order) > 14 else '', order[4], order[5], f"{order[7]:.2f}", order[8])
    
    def add_order_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建订单")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM customers")
        customers = cursor.fetchall()
        cursor.execute("SELECT id, name FROM products")
        products = cursor.fetchall()
        conn.close()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="订单号：").grid(row=0, column=0, sticky=tk.W, pady=10)
        order_no = ttk.Entry(frame, width=40)
        order_no.insert(0, f"ORD-{datetime.now().strftime('%Y%m%d')}-001")
        order_no.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="客户：").grid(row=1, column=0, sticky=tk.W, pady=10)
        customer_combo = ttk.Combobox(frame, values=[f"{c[1]} (ID:{c[0]})" for c in customers], width=35)
        customer_combo.grid(row=1, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="产品：").grid(row=2, column=0, sticky=tk.W, pady=10)
        product_combo = ttk.Combobox(frame, values=[f"{p[1]} (ID:{p[0]})" for p in products], width=35)
        product_combo.grid(row=2, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="数量：").grid(row=3, column=0, sticky=tk.W, pady=10)
        quantity = ttk.Spinbox(frame, from_=1, to=10000, width=10)
        quantity.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(frame, text="币种：").grid(row=3, column=2, sticky=tk.W, padx=(20, 0), pady=10)
        currency = ttk.Combobox(frame, values=["USD", "EUR", "CNY"], width=10)
        currency.current("USD")
        currency.grid(row=3, column=3, sticky=tk.W, padx=10, pady=10)
        
        ttk.Label(frame, text="单价：").grid(row=4, column=0, sticky=tk.W, pady=10)
        price = ttk.Entry(frame, width=20)
        price.insert(0, "0.0")
        price.grid(row=4, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="备注：").grid(row=5, column=0, sticky=tk.W, pady=10)
        notes = tk.Text(frame, width=50, height=3)
        notes.grid(row=5, column=1, columnspan=3, sticky=tk.E, padx=10, pady=10)
        
        def save_order():
            try:
                customer_id = int(customer_combo.get().split("(ID:")[1].rstrip(")"))
                product_id = int(product_combo.get().split("(ID:")[1].rstrip(")"))
                qty = int(quantity.get())
                curr = currency.get()
                prc = float(price.get())
                total = qty * prc
                note = notes.get("1.0", tk.END).strip()
                
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                            (order_no.get(), customer_id, product_id, qty, curr, prc, total, note))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("成功", "订单创建成功！")
                self.refresh_orders()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=20)
        ttk.Button(btn_frame, text="保存", command=save_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def export_orders(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT o.*, c.name as customer_name, p.name as product_name FROM orders o LEFT JOIN customers c ON o.customer_id = c.id LEFT JOIN products p ON o.product_id = p.id ORDER BY o.created_at DESC")
            orders = cursor.fetchall()
            conn.close()
            
            if not orders:
                messagebox.showinfo("提示", "没有订单数据")
                return
            
            filename = filedialog.asksaveasfilename(defaultfilename=f'orders_{datetime.now().strftime("%Y%m%d")}.csv', 
                defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', '订单号', '客户', '产品', '数量', '币种', '单价', '总金额', '状态', '备注', '创建时间'])
                    for order in orders:
                        writer.writerow([order[0], order[1], order[13] if len(order) > 13 else '', 
                            order[14] if len(order) > 14 else '', order[4], order[5], order[6], order[7], 
                            order[8] if len(order) > 8 else '', order[10]])
                messagebox.showinfo("成功", f"导出成功：{filename}")
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def show_customers(self):
        self.clear_content_frame()
        
        toolbar = ttk.Frame(self.content_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="新建客户", command=self.add_customer_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="刷新", command=self.refresh_customers).pack(side=tk.LEFT, padx=5)
        
        self.customers_tree = ttk.Treeview(self.content_frame, 
            columns=('ID', '客户名称', '联系人', '邮箱', '电话', '地址'),
            show='headings', height=15)
        
        self.customers_tree.heading('ID', text='ID')
        self.customers_tree.heading('客户名称', text='客户名称')
        self.customers_tree.heading('联系人', text='联系人')
        self.customers_tree.heading('邮箱', text='邮箱')
        self.customers_tree.heading('电话', text='电话')
        self.customers_tree.heading('地址', text='地址')
        self.customers_tree.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_customers()
    
    def refresh_customers(self):
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        conn.close()
        
        for customer in customers:
            self.customers_tree.insert('', '', *customer)
    
    def add_customer_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建客户")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="客户名称：").grid(row=0, column=0, sticky=tk.W, pady=10)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="联系人：").grid(row=1, column=0, sticky=tk.W, pady=10)
        contact_entry = ttk.Entry(frame, width=40)
        contact_entry.grid(row=1, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="邮箱：").grid(row=2, column=0, sticky=tk.W, pady=10)
        email_entry = ttk.Entry(frame, width=40)
        email_entry.grid(row=2, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="电话：").grid(row=3, column=0, sticky=tk.W, pady=10)
        phone_entry = ttk.Entry(frame, width=40)
        phone_entry.grid(row=3, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="地址：").grid(row=4, column=0, sticky=tk.W, pady=10)
        address_text = tk.Text(frame, width=40, height=3)
        address_text.grid(row=4, column=1, sticky=tk.E, padx=10, pady=10)
        
        def save_customer():
            try:
                name = name_entry.get().strip()
                contact = contact_entry.get().strip()
                email = email_entry.get().strip()
                phone = phone_entry.get().strip()
                address = address_text.get("1.0", tk.END).strip()
                
                if not name:
                    messagebox.showwarning("提示", "客户名称不能为空")
                    return
                
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO customers (name, contact, email, phone, address) VALUES (?, ?, ?, ?, ?)", 
                            (name, contact, email, phone, address))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("成功", "客户创建成功！")
                self.refresh_customers()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="保存", command=save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_products(self):
        self.clear_content_frame()
        
        toolbar = ttk.Frame(self.content_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="新建产品", command=self.add_product_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="刷新", command=self.refresh_products).pack(side=tk.LEFT, padx=5)
        
        self.products_tree = ttk.Treeview(self.content_frame, 
            columns=('ID', '产品名称', '规格', 'USD价格', 'EUR价格', 'CNY价格', '库存'),
            show='headings', height=15)
        
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('产品名称', text='产品名称')
        self.products_tree.heading('规格', text='规格')
        self.products_tree.heading('USD价格', text='USD价格')
        self.products_tree.heading('EUR价格', text='EUR价格')
        self.products_tree.heading('CNY价格', text='CNY价格')
        self.products_tree.heading('库存', text='库存')
        self.products_tree.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_products()
    
    def refresh_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        conn.close()
        
        for product in products:
            self.products_tree.insert('', '', *product)
    
    def add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("新建产品")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="产品名称：").grid(row=0, column=0, sticky=tk.W, pady=10)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Label(frame, text="规格：").grid(row=1, column=0, sticky=tk.W, pady=10)
        spec_entry = ttk.Entry(frame, width=40)
        spec_entry.grid(row=1, column=1, sticky=tk.E, padx=10, pady=10)
        
        price_frame = ttk.Frame(frame)
        price_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Label(price_frame, text="USD价格：").pack(side=tk.LEFT)
        price_usd = ttk.Entry(price_frame, width=15)
        price_usd.insert(0, "0.0")
        price_usd.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(price_frame, text="EUR价格：").pack(side=tk.LEFT)
        price_eur = ttk.Entry(price_frame, width=15)
        price_eur.insert(0, "0.0")
        price_eur.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(price_frame, text="CNY价格：").pack(side=tk.LEFT)
        price_cny = ttk.Entry(price_frame, width=15)
        price_cny.insert(0, "0.0")
        price_cny.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(frame, text="库存数量：").grid(row=3, column=0, sticky=tk.W, pady=10)
        stock = ttk.Spinbox(frame, from_=0, to=10000, width=20)
        stock.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)
        
        def save_product():
            try:
                name = name_entry.get().strip()
                spec = spec_entry.get().strip()
                p_usd = float(price_usd.get())
                p_eur = float(price_eur.get())
                p_cny = float(price_cny.get())
                stk = int(stock.get())
                
                if not name:
                    messagebox.showwarning("提示", "产品名称不能为空")
                    return
                
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, spec, price_usd, price_eur, price_cny, stock) VALUES (?, ?, ?, ?, ?, ?)", 
                            (name, spec, p_usd, p_eur, p_cny, stk))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("成功", "产品创建成功！")
                self.refresh_products()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="保存", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_merge(self):
        self.clear_content_frame()
        
        ttk.Label(self.content_frame, text="订单合并", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(self.content_frame, text="选择两个订单进行合并：", font=("Arial", 12)).pack(pady=10)
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="订单 1：").grid(row=0, column=0, pady=10)
        self.order1_combo = ttk.Combobox(frame, width=40)
        self.order1_combo.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(frame, text="订单 2：").grid(row=1, column=0, pady=10)
        self.order2_combo = ttk.Combobox(frame, width=40)
        self.order2_combo.grid(row=1, column=1, padx=10, pady=10)
        
        def refresh_orders():
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT id, order_no FROM orders")
            orders = cursor.fetchall()
            conn.close()
            
            self.order1_combo['values'] = [f"{o[1]} (ID:{o[0]})" for o in orders]
            self.order2_combo['values'] = [f"{o[1]} (ID:{o[0]})" for o in orders]
        
        refresh_orders()
        
        def merge():
            try:
                order1_text = self.order1_combo.get()
                order2_text = self.order2_combo.get()
                
                if not order1_text or not order2_text:
                    messagebox.showwarning("提示", "请选择两个订单")
                    return
                
                order1_id = int(order1_text.split("(ID:")[1].rstrip(")"))
                order2_id = int(order2_text.split("(ID:")[1].rstrip(")"))
                
                if order1_id == order2_id:
                    messagebox.showwarning("提示", "请选择两个不同的订单")
                    return
                
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM orders WHERE id = ?", (order1_id,))
                order1 = cursor.fetchone()
                cursor.execute("SELECT * FROM orders WHERE id = ?", (order2_id,))
                order2 = cursor.fetchone()
                
                total_amount = order1[7] + order2[7]
                
                new_order_no = f"MERGED-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                cursor.execute("INSERT INTO orders (order_no, customer_id, product_id, quantity, currency, price, total_amount, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (new_order_no, order1[2], order1[3], order1[4] + order2[4], order1[5], order1[6], total_amount, f"合并订单：{order1[1]} + {order2[1]}"))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("成功", f"订单合并成功！合并订单号：{new_order_no}")
                self.refresh_orders()
                self.show_orders()
            except Exception as e:
                messagebox.showerror("错误", str(e))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="合并订单", command=merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="返回", command=self.show_orders).pack(side=tk.LEFT, padx=5)
    
    def show_stats(self):
        self.clear_content_frame()
        
        ttk.Label(self.content_frame, text="今日统计", font=("Arial", 16, "bold")).pack(pady=20)
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
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
        
        frame = ttk.Frame(self.content_frame)
        frame.pack(pady=20)
        
        metrics = [("今日销售", f"${today_sales:,.2f}"), ("今日订单", f"{today_orders} 单"), 
                  ("客户总数", f"{customers} 个"), ("产品总数", f"{products} 个"), 
                  ("待处理", f"{pending} 单"), ("已完成", f"{completed} 单")]
        
        for i, (label, value) in enumerate(metrics):
            row = i // 2
            col = i % 2
            ttk.Label(frame, text=label, font=("Arial", 12)).grid(row=row, column=col*2, sticky=tk.W, padx=20, pady=10)
            ttk.Label(frame, text=value, font=("Arial", 14, "bold"), foreground="blue").grid(row=row, column=col*2+1, sticky=tk.E, padx=10, pady=10)
        
        ttk.Button(self.content_frame, text="返回", command=self.show_orders).pack(pady=20)
    
    def logout(self):
        self.current_user = None
        self.show_login()

if __name__ == "__main__":
    root = tk.Tk()
    app = HaloFitERP(root)
    root.mainloop()

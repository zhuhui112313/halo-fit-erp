# HALO-FIT 外贸进销存系统

基于 Streamlit 的外贸进销存管理系统。

## 🚀 快速开始

### 方法 1：Streamlit Community Cloud 部署（推荐）

1. 访问 https://share.streamlit.io/deploy
2. 选择仓库：`zhuhui112313/halo-fit-erp`
3. 选择分支：`main`
4. 选择主文件：`app.py`
5. 点击 **Deploy**

### 方法 2：本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 📁 文件说明

- `app.py` - Streamlit 版本主程序
- `halo-fit-erp.py` - Tkinter 版本（独立运行）
- `requirements.txt` - Python 依赖包
- `halo_fit.db` - SQLite 数据库文件

## ✨ 功能特性

- 订单管理
- 客户管理
- 产品管理
- 销售统计
- 数据导出（Excel/CSV）
- 多币种支持
- 自动备份

## 🔧 技术栈

- **Web框架**: Streamlit 1.31.0
- **数据库**: SQLite
- **数据处理**: Pandas 2.1.0
- **表格处理**: OpenPyXL 3.1.2

## 📝 默认账号

- 用户名: `admin`
- 密码: `admin123`

⚠️ 首次登录后请立即修改密码！

## 📄 License

MIT License

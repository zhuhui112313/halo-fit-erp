"""
HALO-FIT 外贸进销存系统 - 简化测试版
用于 Streamlit 部署测试
"""

import streamlit as st
import sys

# 页面配置
st.set_page_config(
    page_title="HALO-FIT 测试版",
    page_icon="✅",
    layout="wide"
)

st.title("✅ HALO-FIT 部署测试成功！")

st.markdown("""
## 🎉 恭喜！

你的 Streamlit 应用已经成功部署！

---

## 📊 系统信息
""")

# 显示 Python 版本
st.info(f"Python 版本: {sys.version}")

# 显示 Streamlit 版本
try:
    import streamlit
    st.success(f"Streamlit 版本: {streamlit.__version__}")
except Exception as e:
    st.error(f"Streamlit 导入错误: {e}")

# 测试其他依赖
st.markdown("---")
st.subheader("📦 依赖包测试")

packages = [
    ("pandas", "数据处理"),
    ("openpyxl", "Excel处理"),
    ("PIL", "图片处理"),
]

for package, description in packages:
    try:
        if package == "PIL":
            from PIL import Image
            st.success(f"✅ {package} ({description}) - 已安装")
        else:
            __import__(package)
            st.success(f"✅ {package} ({description}) - 已安装")
    except ImportError:
        st.warning(f"⚠️ {package} ({description}) - 未安装")

st.markdown("---")
st.subheader("🔧 下一步")

st.markdown("""
1. **如果这个页面能正常显示**，说明基础环境没问题
2. **接下来可以尝试完整版本** (`app.py`)
3. **查看部署日志** 了解具体错误信息

---

## 💡 常见问题

### 问题 1：部署失败
**解决方法：**
- 查看部署日志中的错误信息
- 确认 `requirements.txt` 中的包名正确
- 尝试使用更宽松的版本号（如 `>=` 而不是 `==`）

### 问题 2：应用启动后报错
**解决方法：**
- 检查数据库文件是否存在
- 确认文件路径正确
- 查看浏览器控制台的错误信息

### 问题 3：依赖包安装失败
**解决方法：**
- 检查包名拼写是否正确
- 尝试使用不同的版本
- 查看 Streamlit 社区 Cloud 的系统限制

---

**需要帮助？查看 `DEPLOYMENT.md` 获取更多详细指南！**
""")

# 添加一个交互测试
st.markdown("---")
st.subheader("🎮 交互测试")

name = st.text_input("请输入你的名字：", "测试用户")
if name:
    st.success(f"👋 你好，{name}！应用运行正常！")

# 添加一个按钮
if st.button("点击测试"):
    st.balloons()
    st.success("🎉 按钮点击成功！")

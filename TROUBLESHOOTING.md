# 安装应用出错 - 故障排除指南

## 🔍 第一步：了解具体错误

请告诉我：
1. **在哪个阶段出错？**
   - 部署阶段（点击 Deploy 按钮后）
   - 应用启动阶段
   - 使用应用时

2. **具体的错误信息是什么？**
   - 复制粘贴错误信息
   - 截图也可以

---

## 🐛 常见问题及解决方案

### 问题 1：部署时提示 "No module named 'xxx'"

**原因：** `requirements.txt` 中的包名错误或版本不兼容

**解决方案：**

1. **使用简化版本的 requirements.txt**
   ```txt
   streamlit>=1.28.0
   pandas>=2.0.0
   openpyxl>=3.1.0
   Pillow>=10.0.0
   ```

2. **或者先部署测试版本**
   - 在 Streamlit 部署页面，Main file path 选择 `app_simple.py`
   - 这个版本依赖更少，更容易部署成功

---

### 问题 2：部署超时或卡住

**原因：** 依赖包太多或下载太慢

**解决方案：**

1. **使用测试版本先验证环境**
   - 部署 `app_simple.py`
   - 确认基础环境没问题

2. **清理并重新部署**
   - 删除现有应用
   - 重新部署

---

### 问题 3：应用能打开但功能报错

**原因：** 数据库文件缺失或路径问题

**解决方案：**

1. **检查数据库文件**
   - 确认 `halo_fit.db` 在仓库中
   - 确认文件已推送到 GitHub

2. **查看浏览器控制台错误**
   - 按 F12 打开开发者工具
   - 查看 Console 标签页的错误信息

---

### 问题 4："This app has gone to sleep"

**原因：** Streamlit 免费版的休眠机制

**解决方案：**
- 这是正常现象
- 刷新页面即可重新唤醒
- 通常需要 10-30 秒启动

---

## 📋 诊断步骤

### 步骤 1：先测试简化版本

1. 访问 https://share.streamlit.io/deploy
2. **Main file path 选择：`app_simple.py`**
3. 点击 Deploy
4. 看是否能成功

**如果简化版本能成功：**
- 说明基础环境没问题
- 问题出在完整版本的依赖或代码上

**如果简化版本也失败：**
- 说明是环境或配置问题
- 继续下面的诊断

---

### 步骤 2：检查 GitHub 仓库

1. 访问：https://github.com/zhuhui112313/halo-fit-erp
2. 确认以下文件存在：
   - [ ] `app.py`
   - [ ] `app_simple.py`
   - [ ] `requirements.txt`
   - [ ] `halo_fit.db`

3. 确认仓库是 **Public**（不是 Private）

---

### 步骤 3：查看部署日志

在 Streamlit 部署页面：
1. 找到你的应用
2. 点击 "Manage app"
3. 查看 "Logs" 标签页
4. 复制错误信息

---

## 🔧 快速修复方案

### 方案 A：使用测试版本（推荐先试这个）

**修改部署配置：**
- Repository: `zhuhui112313/halo-fit-erp`
- Branch: `main`
- **Main file path: `app_simple.py`** ⚠️ 改这个

**优点：**
- 依赖少，部署快
- 能快速验证环境

---

### 方案 B：简化 requirements.txt

使用这个更宽松的版本：
```txt
streamlit
pandas
openpyxl
Pillow
```

（去掉版本号，让 Streamlit 自动选择兼容版本）

---

### 方案 C：检查文件是否完整

确认这些文件都在 GitHub 上：
- `app.py`
- `requirements.txt`
- `halo_fit.db`
- `.streamlit/config.toml`（可选但推荐）

---

## 💡 获取更多帮助

如果以上方案都不行，请提供：

1. **具体的错误信息**（复制粘贴）
2. **部署日志截图**
3. **在哪个步骤出错**（部署时/启动时/使用时）

---

**祝你好运！🍀**

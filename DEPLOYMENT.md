# Streamlit 部署完整指南

## 🚀 5 分钟快速部署

### 第一步：访问部署页面

打开浏览器，访问：
```
https://share.streamlit.io/deploy
```

### 第二步：登录 GitHub

点击 "Sign in with GitHub" 按钮，用你的 GitHub 账号登录。

### 第三步：填写部署信息（非常重要！）

在部署表单中填写：

| 字段 | 值 | 说明 |
|------|-----|------|
| **Repository** | `zhuhui112313/halo-fit-erp` | 选择这个仓库 |
| **Branch** | `main` | 选择 main 分支 |
| **Main file path** | `app.py` | ⚠️ **必须选这个！不要选 halo-fit-erp.py** |

### 第四步：点击部署

点击 **"Deploy!"** 按钮，等待 1-3 分钟。

---

## 📋 部署前检查清单

在部署前，请确认：

- [x] GitHub 仓库是 **公开的 (Public)**
- [x] 仓库中有 `app.py` 在根目录
- [x] 仓库中有 `requirements.txt`
- [x] 所有文件已推送到 `main` 分支
- [x] 你有 GitHub 仓库的访问权限

---

## 🔍 如何确认仓库是公开的

1. 访问：https://github.com/zhuhui112313/halo-fit-erp
2. 看仓库名称旁边是否有 "Public" 标签
3. 如果是 "Private"，需要改为 "Public"：
   - 点击 Settings
   - 滚动到 "Danger Zone"
   - 点击 "Change repository visibility"
   - 选择 "Change to public"

---

## 🐛 常见问题解决

### 问题 1：找不到仓库

**解决方法：**
- 确认 GitHub 账号已连接到 Streamlit
- 刷新页面
- 手动输入仓库名：`zhuhui112313/halo-fit-erp`

### 问题 2：部署失败

**常见原因：**
1. `requirements.txt` 有问题
2. `app.py` 有语法错误
3. 依赖包版本冲突

**解决方法：**
- 查看部署日志中的错误信息
- 确认 `requirements.txt` 中的包都存在

### 问题 3：应用启动后报错

**检查：**
1. 数据库文件是否存在
2. 路径是否正确
3. 依赖是否完整

---

## 📁 当前仓库文件结构

```
halo-fit-erp/
├── app.py                    ✅ Streamlit 主程序（部署用这个！）
├── halo-fit-erp.py           ✅ Tkinter 桌面版
├── requirements.txt           ✅ Python 依赖
├── README.md                 ✅ 项目说明
├── DEPLOYMENT.md             ✅ 本部署指南
├── .streamlit/
│   └── config.toml          ✅ Streamlit 配置
├── halo_fit.db              ✅ SQLite 数据库
├── .github/
│   └── workflows/
│       └── build-exe.yml     ✅ GitHub Actions 构建
└── ...
```

---

## 🎯 部署成功后的访问

部署成功后，你会获得一个类似这样的 URL：
```
https://zhuhui112313-halo-fit-erp-app-xxxxx.streamlit.app
```

**默认登录信息：**
- 用户名：`admin`
- 密码：`admin123`

---

## 💡 提示

- Streamlit 免费版有使用限制（每月一定小时数）
- 部署的应用会自动休眠，访问时会重新启动
- 可以自定义应用 URL（需要付费）
- 可以设置密码保护（需要付费）

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 Streamlit 文档：https://docs.streamlit.io/
2. 检查部署日志中的错误信息
3. 确认 GitHub 仓库设置正确

---

**祝你部署顺利！🎉**

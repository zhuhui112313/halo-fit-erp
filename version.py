# -*- coding: utf-8 -*-
"""
版本信息管理 - v0.2
"""

# 版本信息
APP_VERSION = "v0.2"
APP_VERSION_DATE = "2026-02-28"
APP_VERSION_NAME = "核心增强版"

# 版本历史
VERSION_HISTORY = [
    {
        "version": "v0.2",
        "date": "2026-02-28",
        "name": "核心增强版",
        "description": "新增核心功能：订单拆分、库存管理、高级报表",
        "features": [
            "订单拆分功能（按数量/按金额）",
            "完整库存管理（入库/出库/预警/日志）",
            "高级报表（销售/客户/产品）",
            "界面优化（导航栏/搜索框）"
        ]
    },
    {
        "version": "v0.1",
        "date": "2026-02-27",
        "name": "初始版本",
        "description": "初始发布：订单、客户、产品、合并、统计",
        "features": [
            "订单管理（增删改查 + 导出）",
            "客户管理（增删改查）",
            "产品管理（增删改查 + 多币种）",
            "订单合并（2 个订单合并）",
            "今日统计（销售/订单/客户/产品）"
        ]
    }
]

# GitHub 仓库信息（用于检查更新）
GITHUB_REPO = "zhuhui112313/halo-fit-erp-standalone"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

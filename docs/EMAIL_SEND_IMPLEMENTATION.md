# 🚀 采集完成自动发送邮件 - 实施指南

## 功能概述

✅ **采集完成后自动发送**：无需手动触发，采集分析完成立即发送
✅ **美观HTML邮件**：包含统计图表和TOP 10条目
✅ **支持多个邮箱**：QQ、Gmail、企业邮箱等
✅ **一键配置**：无需手动编辑JSON

---

## 📋 快速启用（2分钟）

### 方式1：交互式配置（推荐新手）

```bash
python setup_email_config.py
```

按照提示填写邮箱信息，系统会自动：
1. ✅ 测试SMTP连接
2. ✅ 验证邮箱密码
3. ✅ 保存配置到.env文件

### 方式2：手动编辑.env文件

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```ini
# SMTP配置（以QQ邮箱为例）
DISTRIBUTION__SMTP_SERVER=smtp.qq.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=123456789@qq.com
DISTRIBUTION__SMTP_PASSWORD=xyzabcdefghijklm  # 授权码
DISTRIBUTION__SMTP_USE_TLS=true
DISTRIBUTION__EMAIL_SENDER=123456789@qq.com
DISTRIBUTION__EMAIL_RECIPIENTS=liujianxiong@szbring.com
DISTRIBUTION__ENABLE_EMAIL=true
```

---

## 📧 邮箱配置详细说明

### QQ邮箱（最简单）

**获取授权码**：
1. 登录 https://mail.qq.com
2. 点击右上角「设置」
3. 选择「账户」标签
4. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
5. 点击「生成授权码」按钮
6. 按提示操作，复制生成的16位授权码

**配置示例**：
```ini
DISTRIBUTION__SMTP_SERVER=smtp.qq.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=12345@qq.com
DISTRIBUTION__SMTP_PASSWORD=xyzabcdefghijklm  # 16位授权码
```

### Gmail

**获取应用密码**：
1. 启用两步验证：https://myaccount.google.com/security
2. 生成应用专用密码：https://myaccount.google.com/apppasswords
3. 复制生成的密码

**配置示例**：
```ini
DISTRIBUTION__SMTP_SERVER=smtp.gmail.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=your_email@gmail.com
DISTRIBUTION__SMTP_PASSWORD=your_app_password
```

### 企业邮箱

**获取SMTP信息**：
1. 联系IT部门获取SMTP服务器地址和端口
2. 获取邮箱用户名和密码或授权码

**配置示例**：
```ini
DISTRIBUTION__SMTP_SERVER=smtp.company.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=user@company.com
DISTRIBUTION__SMTP_PASSWORD=your_password
```

---

## 🧪 测试配置

### 步骤1：检查配置是否正确

```bash
python main.py --test
```

输出应该显示：
```
分发配置:
   邮件: 已配置  ✅
   微信: 未配置
```

### 步骤2：发送测试邮件

```bash
python3 << 'EOF'
import asyncio
from reporters import EmailSender

async def test():
    sender = EmailSender()
    if sender.is_configured():
        result = await sender.send_simple(
            "🧪 测试邮件 - CT产业情报Agent",
            "这是一封测试邮件，用于验证邮箱配置。"
        )
        if result:
            print("✅ 测试邮件发送成功，请检查收件箱")
        else:
            print("❌ 测试邮件发送失败")
    else:
        print("❌ 邮件未配置")

asyncio.run(test())
EOF
```

### 步骤3：查看日志

```bash
grep -E "邮件|email|SMTP" data/telecom_intel.log | tail -10
```

---

## 🎯 使用方法

### 采集后自动发送邮件

```bash
# 运行采集命令
python main.py --collect

# 系统会自动：
# 1. 采集数据（RSS + Web + Search）
# 2. AI分析采集的数据
# 3. 生成采集结果报告
# 4. 发送HTML邮件到：liujianxiong@szbring.com
```

**预期输出**：
```
采集完成，共分析 150 条情报
✅ 采集结果已发送到邮箱
```

### 完整流程（采集+分析+周报+发送）

```bash
python main.py

# 系统会自动执行：
# 1. 采集数据
# 2. 分析数据
# 3. 生成周报
# 4. 发送邮件（采集摘要 + 周报）
```

### 定时自动执行

```bash
# 每周五9:00自动采集并发送邮件
python main.py --schedule
```

---

## 📊 邮件内容示例

收到的邮件包含：

**邮件主题**：
```
✉️ 通信设备产业情报采集结果 - 150条新情报
```

**邮件内容**：
```
📊 通信设备产业情报采集结果报告

采集概览
├─ 采集时间: 2026-03-29 15:30:45
└─ 采集条目数: 150 条

按来源分布
├─ RSS采集器: 85 条
├─ Web采集器: 50 条
└─ Search采集器: 15 条

按分类分布
├─ 关键公司动态: 60 条
├─ 新技术: 40 条
├─ 投资收购: 30 条
├─ 专利情况: 15 条
└─ 下游产业应用: 5 条

按重要性分布
├─ 5分: 20 条
├─ 4分: 45 条
├─ 3分: 60 条
├─ 2分: 20 条
└─ 1分: 5 条

TOP 10 高重要性条目
[表格显示最重要的10条条目的标题、来源、重要性、分类]
```

---

## 🔧 故障排查

### 问题1：邮件未能发送

**检查清单**：
```bash
# 1. 检查配置
cat .env | grep DISTRIBUTION__

# 2. 检查日志
grep "邮件\|SMTP\|email" data/telecom_intel.log

# 3. 测试SMTP连接
python3 -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.qq.com', 587)
    server.starttls()
    print('✅ SMTP连接成功')
except Exception as e:
    print(f'❌ 连接失败: {e}')
"
```

### 问题2：提示"身份验证失败"

**原因**：邮箱密码或授权码错误

**解决**：
1. 确认是否使用授权码（而不是邮箱密码）
2. 重新生成授权码
3. 检查授权码是否完整（无多余空格）

### 问题3：邮件进入垃圾箱

**解决**：
1. 在邮箱中将发件人加入联系人
2. 标记为非垃圾邮件
3. 在邮箱设置中调整反垃圾过滤级别

### 问题4：显示"未配置"

**原因**：.env文件中邮件配置不完整

**解决**：
```bash
# 检查必须的配置字段
grep "DISTRIBUTION__" .env

# 应该看到：
# DISTRIBUTION__SMTP_SERVER=...
# DISTRIBUTION__SMTP_PORT=...
# DISTRIBUTION__SMTP_USER=...
# DISTRIBUTION__SMTP_PASSWORD=...
# DISTRIBUTION__EMAIL_RECIPIENTS=...
# DISTRIBUTION__ENABLE_EMAIL=true
```

---

## 📁 关键文件

| 文件 | 说明 |
|------|------|
| `.env` | 邮箱配置文件（需要创建） |
| `setup_email_config.py` | 交互式配置脚本 |
| `main.py` | 主程序（已修改以支持邮件发送） |
| `reporters/distribution.py` | 邮件发送模块（已新增send_collect_summary方法） |
| `EMAIL_CONFIG_GUIDE.md` | 详细配置指南 |

---

## 🎁 实现的功能

✅ **采集完成自动发送**
- `--collect` 模式采集完成后自动发送邮件
- 无需额外操作，零配置启用（配置后）

✅ **HTML格式报告**
- 美观的表格和统计
- 响应式设计，邮箱兼容

✅ **详细统计信息**
- 按来源分布（RSS/Web/Search）
- 按分类分布（公司动态/技术/投资等）
- 按重要性分布（5分制）
- TOP 10高重要性条目

✅ **支持多邮箱**
- QQ邮箱
- Gmail
- 企业邮箱
- 任何支持SMTP的邮箱

✅ **错误处理**
- 邮件发送失败时记录日志
- 不影响采集流程
- 用户可查看详细错误信息

---

## ⏱️ 典型工作流程

```
用户执行
    ↓
python main.py --collect
    ↓
┌─────────────────────────────────────┐
│ 1️⃣  采集数据                         │
│   ├─ RSS采集器: 85条新闻            │
│   ├─ Web采集器: 50条企业新闻        │
│   └─ Search采集器: 15条搜索结果    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2️⃣  AI分析数据                       │
│   ├─ 去重                           │
│   ├─ 关键词过滤                     │
│   ├─ LLM分类和评分                  │
│   └─ 保存到数据库                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3️⃣  生成邮件报告                     │
│   ├─ 统计采集数据                   │
│   ├─ 构建HTML邮件                   │
│   └─ 发送到收件人                   │
└─────────────────────────────────────┘
    ↓
✅ 任务完成
   邮件已发送到: liujianxiong@szbring.com
```

---

## 📞 技术支持

如遇问题，请查看：
1. **配置问题** → 参考 `EMAIL_CONFIG_GUIDE.md`
2. **邮件未发送** → 运行 `setup_email_config.py` 重新配置
3. **日志分析** → `grep "email\|SMTP" data/telecom_intel.log`
4. **代码位置** → `reporters/distribution.py` 中的 `send_collect_summary()` 方法

---

## 🎯 下一步

1. **立即配置**：运行 `python setup_email_config.py`
2. **测试发送**：运行 `python main.py --test`
3. **执行采集**：运行 `python main.py --collect`
4. **检查邮箱**：查看是否收到采集结果报告

---

**预计时间**：5分钟配置 + 1分钟测试 = 6分钟完成！


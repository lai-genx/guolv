# 📧 采集完成自动发送邮件功能 - 配置指南

## 功能说明

采集完成后，系统会**自动生成HTML格式的采集结果报告**并发送到指定邮箱。

报告包含：
- ✅ 采集时间和总条目数
- ✅ 按来源分布统计（RSS、Web、Search）
- ✅ 按分类分布统计（公司动态、专利、技术等）
- ✅ 按重要性分布统计（5分制）
- ✅ TOP 10 高重要性条目详情

---

## 快速配置（3步）

### 步骤1：编辑 .env 文件

在项目根目录创建或编辑 `.env` 文件，添加SMTP邮件配置：

```bash
# 使用QQ邮箱示例
DISTRIBUTION__SMTP_SERVER=smtp.qq.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=your_qq_email@qq.com
DISTRIBUTION__SMTP_PASSWORD=your_qq_app_password
DISTRIBUTION__SMTP_USE_TLS=true
DISTRIBUTION__EMAIL_SENDER=your_qq_email@qq.com
DISTRIBUTION__EMAIL_RECIPIENTS=liujianxiong@szbring.com
DISTRIBUTION__ENABLE_EMAIL=true
```

### 步骤2：获取邮箱授权密码

**对于QQ邮箱**（推荐）：
1. 登录 https://mail.qq.com
2. 进入「设置」→「账户」
3. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
4. 点击「生成授权码」
5. 复制生成的16位授权码到 `DISTRIBUTION__SMTP_PASSWORD`

**对于Gmail**：
1. 启用 「两步验证」
2. 生成「应用专用密码」
3. 使用应用密码而不是账户密码

**对于其他邮箱**：
- 参考邮箱服务商的SMTP配置文档
- 通常需要生成「应用密码」或「授权码」

### 步骤3：测试配置

```bash
# 测试邮件配置是否正确
python main.py --test

# 输出应该显示:
# 分发配置:
#    邮件: 已配置
```

---

## 使用方法

### 方式1：采集后自动发送（推荐）

```bash
# 运行采集命令
python main.py --collect

# 采集完成后自动发送邮件到：liujianxiong@szbring.com
# 输出示例：
# 采集完成，共分析 150 条情报
# ✅ 采集结果已发送到邮箱
```

### 方式2：完整流程（采集+分析+报告+发送）

```bash
python main.py
# 会自动执行：采集→分析→生成周报→发送周报→发送采集摘要
```

### 方式3：定时自动执行

```bash
# 启用定时调度（每周五9:00执行）
python main.py --schedule
```

---

## 邮件配置示例

### QQ邮箱（最简单）

```ini
DISTRIBUTION__SMTP_SERVER=smtp.qq.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=123456789@qq.com
DISTRIBUTION__SMTP_PASSWORD=xyzabcdefghijklm  # 授权码（16位）
DISTRIBUTION__SMTP_USE_TLS=true
DISTRIBUTION__EMAIL_SENDER=123456789@qq.com
DISTRIBUTION__EMAIL_RECIPIENTS=liujianxiong@szbring.com
DISTRIBUTION__ENABLE_EMAIL=true
```

### Gmail

```ini
DISTRIBUTION__SMTP_SERVER=smtp.gmail.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=your_email@gmail.com
DISTRIBUTION__SMTP_PASSWORD=your_app_password  # 应用专用密码
DISTRIBUTION__SMTP_USE_TLS=true
DISTRIBUTION__EMAIL_SENDER=your_email@gmail.com
DISTRIBUTION__EMAIL_RECIPIENTS=liujianxiong@szbring.com
DISTRIBUTION__ENABLE_EMAIL=true
```

### 企业邮箱（通用）

```ini
DISTRIBUTION__SMTP_SERVER=smtp.your_company.com  # 企业邮箱SMTP服务器
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=your_email@company.com
DISTRIBUTION__SMTP_PASSWORD=your_password
DISTRIBUTION__SMTP_USE_TLS=true
DISTRIBUTION__EMAIL_SENDER=your_email@company.com
DISTRIBUTION__EMAIL_RECIPIENTS=liujianxiong@szbring.com
DISTRIBUTION__ENABLE_EMAIL=true
```

---

## 邮件内容示例

发送的邮件包含以下内容：

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
├─ 华为发布新一代5G芯片 [4分] [Web采集器]
├─ 中兴通讯获得专利授权 [4分] [RSS采集器]
...
```

---

## 常见问题

### Q1: 邮件未能发送，怎么办？

**检查清单**:
1. 确认 `DISTRIBUTION__ENABLE_EMAIL=true`
2. 确认 SMTP服务器地址正确
3. 确认端口号正确（587或465）
4. 确认用户名和密码正确
5. 确认收件邮箱地址格式正确

**查看日志**:
```bash
grep "邮件\|SMTP\|email" data/telecom_intel.log | tail -20
```

### Q2: 提示"SMTP服务器连接失败"

**可能原因**:
- 防火墙阻止SMTP端口
- SMTP服务器地址或端口错误
- 网络连接问题

**解决方案**:
```bash
# 测试SMTP服务器连接
python3 -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.qq.com', 587)
    server.starttls()
    print('✅ SMTP连接成功')
except Exception as e:
    print(f'❌ SMTP连接失败: {e}')
"
```

### Q3: 显示"身份验证失败"

**原因**: 邮箱密码或授权码错误

**解决方案**:
1. 重新生成授权码（QQ邮箱可能需要重新授权）
2. 检查是否复制完整（不要有多余空格）
3. 确认是授权码而不是邮箱密码

### Q4: 邮件发送成功但没有收到

**可能原因**:
1. 邮件进入垃圾箱
2. 收件邮箱地址错误
3. 邮件被收件邮箱的反垃圾系统拦截

**解决方案**:
- 检查垃圾箱/垃圾邮件文件夹
- 在QQ邮箱中设置发件邮箱为联系人（不进垃圾箱）
- 重新检查 `DISTRIBUTION__EMAIL_RECIPIENTS` 配置

---

## 故障排查脚本

创建文件 `test_email_config.py`：

```python
#!/usr/bin/env python3
"""邮件配置测试脚本"""

import asyncio
import smtplib
from config import settings
from reporters import EmailSender

async def test_email_config():
    print("=" * 60)
    print("CT产业情报Agent - 邮件配置测试")
    print("=" * 60)

    # 1. 检查配置
    print("\n1️⃣ 配置检查:")
    print(f"   SMTP服务器: {settings.distribution.smtp_server}")
    print(f"   SMTP端口: {settings.distribution.smtp_port}")
    print(f"   SMTP用户: {settings.distribution.smtp_user}")
    print(f"   发送者: {settings.distribution.email_sender}")
    print(f"   收件人: {settings.distribution.email_recipients}")
    print(f"   启用邮件: {settings.distribution.enable_email}")

    # 2. 测试SMTP连接
    print("\n2️⃣ SMTP连接测试:")
    try:
        server = smtplib.SMTP(
            settings.distribution.smtp_server,
            settings.distribution.smtp_port
        )
        print(f"   ✅ 连接成功 ({settings.distribution.smtp_server}:{settings.distribution.smtp_port})")

        if settings.distribution.smtp_use_tls:
            server.starttls()
            print(f"   ✅ TLS启用成功")

        server.quit()
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return

    # 3. 测试身份验证
    print("\n3️⃣ 身份验证测试:")
    try:
        server = smtplib.SMTP(
            settings.distribution.smtp_server,
            settings.distribution.smtp_port
        )
        if settings.distribution.smtp_use_tls:
            server.starttls()

        server.login(
            settings.distribution.smtp_user,
            settings.distribution.smtp_password
        )
        print(f"   ✅ 身份验证成功")
        server.quit()
    except Exception as e:
        print(f"   ❌ 身份验证失败: {e}")
        print(f"      请检查用户名和密码/授权码是否正确")
        return

    # 4. 测试发送邮件
    print("\n4️⃣ 测试邮件发送:")
    email_sender = EmailSender()
    if email_sender.is_configured():
        result = await email_sender.send_simple(
            "🧪 CT产业情报Agent - 测试邮件",
            "这是一封测试邮件，用于验证邮箱配置是否正确。"
        )
        if result:
            print(f"   ✅ 测试邮件发送成功")
            print(f"      请检查 {settings.distribution.email_recipients} 是否收到邮件")
        else:
            print(f"   ❌ 测试邮件发送失败")
    else:
        print(f"   ❌ 邮件未配置")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_email_config())
```

运行测试：
```bash
python test_email_config.py
```

---

## 总结

✅ **3步快速启用**:
1. 编辑 `.env` 文件添加SMTP配置
2. 获取邮箱授权密码
3. 运行 `python main.py --collect` 自动发送

✅ **功能特点**:
- 采集完成后**自动发送**
- HTML格式，美观易读
- 包含详细统计和TOP 10条目
- 支持多个收件人

✅ **支持的邮箱**:
- QQ邮箱（推荐）
- Gmail
- 企业邮箱
- 其他支持SMTP的邮箱

---

**下一步**：配置完成后，运行 `python main.py --collect` 进行测试！


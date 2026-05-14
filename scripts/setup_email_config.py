#!/usr/bin/env python3
"""
快速邮件配置脚本
用于快速配置邮箱设置并测试连接
"""

import os
import sys
from pathlib import Path
import smtplib
from getpass import getpass

def prompt_input(prompt: str, default: str = None, is_password: bool = False) -> str:
    """带默认值的输入提示"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    if is_password:
        value = getpass(prompt) if sys.stdin.isatty() else input(prompt)
    else:
        value = input(prompt)

    return value if value else default

def test_smtp_connection(smtp_server: str, smtp_port: int, smtp_user: str,
                        smtp_password: str, use_tls: bool) -> bool:
    """测试SMTP连接"""
    try:
        print(f"\n🔗 测试连接到 {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)

        if use_tls:
            server.starttls()
            print("✅ TLS连接成功")

        print(f"🔐 尝试身份验证 ({smtp_user})...")
        server.login(smtp_user, smtp_password)
        print("✅ 身份验证成功")

        server.quit()
        return True

    except smtplib.SMTPException as e:
        print(f"❌ SMTP错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def create_env_file(config: dict) -> bool:
    """创建或更新.env文件"""
    try:
        env_path = Path(".env")

        # 读取现有.env文件
        existing_content = ""
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # 要更新的配置键
        config_keys = [
            'DISTRIBUTION__SMTP_SERVER',
            'DISTRIBUTION__SMTP_PORT',
            'DISTRIBUTION__SMTP_USER',
            'DISTRIBUTION__SMTP_PASSWORD',
            'DISTRIBUTION__SMTP_USE_TLS',
            'DISTRIBUTION__EMAIL_SENDER',
            'DISTRIBUTION__EMAIL_RECIPIENTS',
            'DISTRIBUTION__ENABLE_EMAIL',
        ]

        # 移除旧的配置行
        lines = existing_content.split('\n')
        new_lines = []
        for line in lines:
            if not any(line.startswith(key) for key in config_keys):
                new_lines.append(line)

        # 添加新配置
        new_lines.append("\n# ==========================================")
        new_lines.append("# 邮件配置（已配置）")
        new_lines.append("# ==========================================")
        new_lines.append(f"DISTRIBUTION__SMTP_SERVER={config['smtp_server']}")
        new_lines.append(f"DISTRIBUTION__SMTP_PORT={config['smtp_port']}")
        new_lines.append(f"DISTRIBUTION__SMTP_USER={config['smtp_user']}")
        new_lines.append(f"DISTRIBUTION__SMTP_PASSWORD={config['smtp_password']}")
        new_lines.append(f"DISTRIBUTION__SMTP_USE_TLS={config['smtp_use_tls']}")
        new_lines.append(f"DISTRIBUTION__EMAIL_SENDER={config['email_sender']}")
        new_lines.append(f"DISTRIBUTION__EMAIL_RECIPIENTS={config['email_recipients']}")
        new_lines.append(f"DISTRIBUTION__ENABLE_EMAIL={config['enable_email']}")

        # 写入文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))

        print(f"✅ 配置已保存到 .env 文件")
        return True

    except Exception as e:
        print(f"❌ 保存配置失败: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎯 CT产业情报Agent - 邮件配置向导")
    print("="*60)

    # 1. 选择邮箱类型
    print("\n📧 选择邮箱类型:")
    print("  1. QQ邮箱（推荐）")
    print("  2. Gmail")
    print("  3. 企业邮箱（自定义）")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice == "1":
        smtp_server = "smtp.qq.com"
        smtp_port = 587
        use_tls = True
        print("\n✅ 已选择 QQ邮箱")
        print("   SMTP服务器: smtp.qq.com")
        print("   SMTP端口: 587")
        print("\n❗ 获取授权码步骤:")
        print("   1. 登录 https://mail.qq.com")
        print("   2. 进入「设置」→「账户」")
        print("   3. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」")
        print("   4. 点击「生成授权码」")
        print("   5. 复制16位授权码")

    elif choice == "2":
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        use_tls = True
        print("\n✅ 已选择 Gmail")
        print("   SMTP服务器: smtp.gmail.com")
        print("   SMTP端口: 587")
        print("\n❗ 获取应用密码步骤:")
        print("   1. 启用 Google 账户的两步验证")
        print("   2. 访问 https://myaccount.google.com/apppasswords")
        print("   3. 生成应用专用密码")

    elif choice == "3":
        smtp_server = prompt_input("\nSMTP服务器地址", "smtp.example.com")
        smtp_port = int(prompt_input("SMTP端口", "587"))
        use_tls_str = prompt_input("是否使用TLS (yes/no)", "yes").lower()
        use_tls = use_tls_str in ['yes', 'y', 'true']
        print("\n✅ 已选择企业邮箱（自定义）")

    else:
        print("❌ 无效选择")
        return

    # 2. 输入邮箱凭据
    print("\n📝 输入邮箱凭据:")
    smtp_user = prompt_input("SMTP用户名/邮箱", "user@example.com")
    smtp_password = prompt_input("SMTP密码/授权码", is_password=True)
    email_sender = prompt_input("发件人邮箱", smtp_user)

    # 3. 输入收件人
    print("\n✉️ 输入收件人邮箱:")
    email_recipients = prompt_input("收件人邮箱", "liujianxiong@szbring.com")

    # 4. 测试连接
    print("\n🔗 正在测试邮箱配置...")
    if not test_smtp_connection(smtp_server, smtp_port, smtp_user, smtp_password, use_tls):
        retry = input("\n连接失败，是否重试? (yes/no): ").lower()
        if retry in ['yes', 'y']:
            return main()
        else:
            print("⚠️ 跳过连接测试，继续保存配置")
    else:
        print("✅ 邮箱配置测试成功！")

    # 5. 保存配置
    config = {
        'smtp_server': smtp_server,
        'smtp_port': str(smtp_port),
        'smtp_user': smtp_user,
        'smtp_password': smtp_password,
        'smtp_use_tls': 'true' if use_tls else 'false',
        'email_sender': email_sender,
        'email_recipients': email_recipients,
        'enable_email': 'true',
    }

    print("\n💾 保存配置...")
    if create_env_file(config):
        print("\n" + "="*60)
        print("✅ 配置完成！")
        print("="*60)
        print("\n📝 配置摘要:")
        print(f"   SMTP服务器: {smtp_server}")
        print(f"   SMTP端口: {smtp_port}")
        print(f"   SMTP用户: {smtp_user}")
        print(f"   发件人: {email_sender}")
        print(f"   收件人: {email_recipients}")
        print(f"   启用邮件: 是")

        print("\n🚀 下一步:")
        print("   1. 运行测试: python main.py --test")
        print("   2. 执行采集: python main.py --collect")
        print("   3. 采集完成后自动发送邮件到: {email_recipients}")

    else:
        print("❌ 配置保存失败")

if __name__ == "__main__":
    main()

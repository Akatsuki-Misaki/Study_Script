import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_email(subject, message, recipient):
    sender = "syayuri@xbox.email.cn"
    password = "3NCjnCAcMJEFM7db"

    # 设置邮件内容
    email = MIMEText(message)
    email["Subject"] = subject
    email["From"] = sender
    email["To"] = recipient

    # 连接SMTP服务器
    with smtplib.SMTP_SSL("smtp.email.cn", 465) as server:
        # 登录SMTP服务器
        server.login(sender, password)

        # 发送邮件
        server.sendmail(sender, [recipient], email.as_string())

        print("邮件发送成功！")

def main():
    command = "baidu.com"  # 替换为要ping的域名或IP地址
    recipient = "mirai@lolicon.team"  # 替换为要发送邮件的邮箱地址
    subject = "UPS输入市电恢复"  # 替换为邮件主题

    # 动态生成DateTime内容
    now = datetime.now()
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
    message = f"""
    来自 USB790470F_ID；
    事件: UPS输入市电异常；
    类型: 输入事件;
    Contact: syayuri@xbox.email.cn;
    DateTime: {datetime_str}
    """  # 替换为要发送的邮件内容

    ping_result = 1
    while ping_result != 0:
        # 执行ping命令
        ping_result = os.system(f"ping -c 1 {command}")

        if ping_result == 0:
            # ping成功，发送电子邮件
            send_email(subject, message, recipient)
        else:
            print("Ping失败，正在重试...")

if __name__ == "__main__":
    main()

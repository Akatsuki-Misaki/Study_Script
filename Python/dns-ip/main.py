import requests
import time
import json

def get_current_ip():
    try:
        response = requests.get("https://archive.ovofish.com/api/center/ipsee/")
        data = response.json()
        print("API响应：", data)  # 打印完整的API响应
        return data["ip"]
    except KeyError:
        print("API返回的JSON格式不正确，未找到'ip'键。")
        return None
    except Exception as e:
        print(f"发生错误：{e}")
        return None

def perform_action(ip):
    if ip is not None:
        # 执行你的操作，访问 https://link.dns.pub/
        # 你可以使用 requests.get() 或其他适当的方法
        url = "https://link.dns.pub/"
        try:
            response = requests.get(url)
            # 在这里可以添加处理响应的代码，例如检查状态码、打印内容等
            print(f"执行操作，访问 {url}，当前IP: {ip}")
        except Exception as e:
            print(f"执行操作时发生错误：{e}")
    else:
        print("无法获取有效的IP地址，跳过执行操作。")

def main():
    current_ip = get_current_ip()
    
    # 初始操作
    perform_action(current_ip)
    
    while True:
        time.sleep(120)
        
        new_ip = get_current_ip()
        
        if new_ip is not None and new_ip != current_ip:
            print("IP 已更改，执行操作")
            
            # 执行操作
            perform_action(new_ip)
            
            current_ip = new_ip
        else:
            print("IP 未更改，继续等待")

if __name__ == "__main__":
    main()
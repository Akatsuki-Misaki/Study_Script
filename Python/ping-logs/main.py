import time
from ping3 import ping
import requests
import json
import sys
import io
# 设置标准输入输出为UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')
def load_config():
    with open("config.json", "r", encoding="utf-8") as config_file:
        config_data = json.load(config_file)
    return config_data["target_ips"]

def continuous_ping(ip_addresses):
    while True:
        for ip_address, data in ip_addresses.items():
            location = data["location"]
            threshold_ms = data["threshold_ms"]
            log_method = data["log_method"]

            delay = ping(ip_address)

            if delay is not None:
                # print(f'Ping delay to {location} ({ip_address}): {delay * 1000:.2f} ms')
                delay = int(delay * 1000)
            else:
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S")}Ping to {location} ({ip_address}) failed.')
                delay = 0  # 或者设定其他默认值
            if delay is not None and delay > threshold_ms:
                log_message = f'High latency detected for {location} ({ip_address})! Delay: {delay}ms'

                if log_method == "file":
                    try:
                        with open(f'{location}_ping_log.txt', 'a', encoding="utf-8") as log_file:
                            log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")}\t{ip_address}\t{delay}ms\n')
                    except Exception as e:
                        print(f'Error writing to file: {e}')
                elif log_method == "console":
                    print(log_message)
                elif log_method == "url":
                    target_url = "https://archive.ovofish.com/api/center/ping-logs/"

                    payload = {"location": location, "ip_address": ip_address, "delay": delay}
                    headers = {"Content-Type": "application/json"}

                    try:
                        response = requests.post(target_url, data=json.dumps(payload), headers=headers)
                        if response.status_code == 200:
                            print(f'Delay information sent to {target_url} successfully.')
                        else:
                            print(f'Failed to send delay information to {target_url}. Status code: {response.status_code}')

                            # 获取返回的 JSON 数据
                            try:
                                error_json = response.json()
                                print(f'Error JSON: {error_json}')
                            except json.JSONDecodeError:
                                print('Failed to decode error JSON.')
                    except Exception as e:
                        print(f'Error sending delay information to {target_url}: {e}')
                else:
                    pass

        time.sleep(1)

if __name__ == "__main__":
    # 判断是否有配置文件
    try:
        with open("config.json", "r") as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        print("配置文件不存在，请检查文件路径。")
        exit(1)
    print("正在运行...")
    target_ips = load_config()
    continuous_ping(target_ips)

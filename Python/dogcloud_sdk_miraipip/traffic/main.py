from hashlib import sha1
import hmac
import requests
import json
import urllib
from datetime import datetime, timedelta

def dogecloud_api(api_path, data={}, json_mode=False):
    """
    调用多吉云 API
    """
    access_key = '91fc21b83716ce4e'  # 替换为你的 AccessKey
    secret_key = 'ea944e5745a1565f979df0a5457fe6e4'  # 替换为你的 SecretKey

    body = ''
    mime = ''
    if json_mode:
        body = json.dumps(data)
        mime = 'application/json'
    else:
        body = urllib.parse.urlencode(data)
        mime = 'application/x-www-form-urlencoded'
    sign_str = api_path + "\n" + body
    signed_data = hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), sha1)
    sign = signed_data.digest().hex()
    authorization = 'TOKEN ' + access_key + ':' + sign
    response = requests.post('https://api.dogecloud.com' + api_path, data=body, headers={
        'Authorization': authorization,
        'Content-Type': mime
    })
    return response.json()

def get_traffic_data(start_date, end_date):
    """
    查询指定日期范围内的 CDN 流量数据
    """
    api_path = "/cdn/stat/traffic.json"
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "granularity": "day",  # 按天粒度查询
        "area": "china",  # 查询中国境内的流量
        "domains": "down-cdn.ovofish.com"  # 替换为你的加速域名
    }
    response = dogecloud_api(api_path, params)
    if response.get("code") == 200:
        return response["data"]
    else:
        raise Exception(f"API 错误: {response.get('msg')}")

def bytes_to_gb(bytes_value):
    """
    将字节（B）转换为千兆字节（GB）
    """
    bytes_value /= 1024 ** 3
    # 保留小数点后两位
    bytes_value = round(bytes_value, 2)
    
    return bytes_value

def calculate_traffic_stats():
    """
    计算本月流量、今日流量和昨日流量
    """
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    first_day_of_month = today.replace(day=1)

    # 查询本月流量数据
    month_data = get_traffic_data(first_day_of_month.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    this_month_traffic = sum(day["data"][0] for day in month_data["result"])  # 本月总流量

    # 查询今日和昨日流量数据
    today_data = get_traffic_data(today.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
    yesterday_data = get_traffic_data(yesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"))

    today_traffic = today_data["result"][0]["data"][0] if today_data["result"] else 0
    yesterday_traffic = yesterday_data["result"][0]["data"][0] if yesterday_data["result"] else 0

    # 将流量数据从字节转换为 GB
    return {
        "this_month_traffic_gb": bytes_to_gb(this_month_traffic),
        "today_traffic_gb": bytes_to_gb(today_traffic),
        "yesterday_traffic_gb": bytes_to_gb(yesterday_traffic)
    }

def save_to_json(data, filename="traffic_stats.json"):
    """
    将流量统计数据保存到 JSON 文件
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    try:
        # 计算流量统计数据
        stats = calculate_traffic_stats()
        print("流量统计（单位：GB）：")
        print(json.dumps(stats, indent=4))

        # 将统计数据保存到 JSON 文件
        save_to_json(stats)
        print(f"流量统计数据已保存到 traffic_stats.json")
    except Exception as e:
        print(f"错误: {e}")
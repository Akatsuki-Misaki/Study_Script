import requests
from bs4 import BeautifulSoup
import re
import json
import os
import hmac
from hashlib import sha1

# 配置选项
ENABLE_CDN_REFRESH = True  # 设置为False禁用CDN预热功能

print("Start downloading file links...")

# 发送GET请求获取页面内容
url = "https://teamspeak.com/zh-CN/downloads/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# 找到所有<a>标签并提取链接
links = soup.find_all("a", href=True)

# 匹配包含"https://files.teamspeak-services.com"的链接
file_links = [link["href"] for link in links if re.search(r"https://files.teamspeak-services.com", link["href"])]

# 按版本划分链接（新增Ver6支持）
ver3_links = [link for link in file_links if re.search(r"\/3\.\d+\.\d+\/", link)]
ver5_links = [link for link in file_links if re.search(r"\/(?:5\.\d+\.\d+|5\.\d+\.\d+\-\w+)/", link)]
ver6_links = [link for link in file_links if re.search(r"\/6\.\d+\.\d+.*\/", link)]  # 新增Ver6匹配模式

# 设置全局变量
download_file = True
file_updated = False

# 创建版本文件夹并保存链接
def save_links_to_folder(links, folder_name):
    global download_file, file_updated
    folder_path = os.path.join(os.getcwd(), "tsfile", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for link in links:
        file_name = link.split("/")[-1]
        file_path = os.path.join(folder_path, file_name)

        # 检查文件是否需要更新
        if os.path.exists(file_path):
            response = requests.head(link)
            remote_file_size = int(response.headers.get('Content-Length', 0))
            local_file_size = os.path.getsize(file_path)
            if remote_file_size == local_file_size:
                print(f"文件 {file_name} 无需更新。")
                continue
            else:
                os.remove(file_path)
                print(f"发现新版本 {file_name}，开始下载...")
                file_updated = True
        
        # 下载文件
        with open(file_path, "wb") as file:
            response = requests.get(link)
            file.write(response.content)
            print(f"文件 {file_name} 已下载到 {folder_name}")
            file_updated = True

# 保存链接到对应版本文件夹中（新增Ver6处理）
save_links_to_folder(ver3_links, "Ver3")
save_links_to_folder(ver5_links, "Ver5")
save_links_to_folder(ver6_links, "Ver6")

# 将链接存储为JSON文件（新增Ver6数据）
data = {
    "Ver3": ver3_links,
    "Ver5": ver5_links,
    "Ver6": ver6_links  # 新增Ver6数据
}

with open("file_links.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("链接已保存至file_links.json")

# 生成本地文件下载链接
base_download_url = "https://file-us.ovofish.com/tsfile/"

def generate_local_download_links(links, folder_name):
    local_download_links = [base_download_url + folder_name + "/" + link.split("/")[-1] for link in links]
    return local_download_links

ver3_local_download_links = generate_local_download_links(ver3_links, "Ver3")
ver5_local_download_links = generate_local_download_links(ver5_links, "Ver5")
ver6_local_download_links = generate_local_download_links(ver6_links, "Ver6")  # 新增Ver6链接生成

# 合并所有下载链接用于CDN预热
all_local_links = ver3_local_download_links + ver5_local_download_links + ver6_local_download_links

# 将本地文件下载链接存储为JSON文件（新增Ver6数据）
local_download_links_data = {
    "Ver3": ver3_local_download_links,
    "Ver5": ver5_local_download_links,
    "Ver6": ver6_local_download_links  # 新增Ver6数据
}

with open("local_download_links.json", "w") as local_json_file:
    json.dump(local_download_links_data, local_json_file, indent=4)

print("本地下载链接已保存至local_download_links.json")

# CDN刷新功能（新增开关控制）
def dogecloud_api(api_path, data={}, json_mode=False):
    """多吉云API接口"""
    print('正在调用多吉云API...')
    access_key = ''  # 请替换为你的Access Key
    secret_key = ''  # 请替换为你的Secret Key
    
    if not access_key or not secret_key:
        print('请填写多吉云Access Key和Secret Key。')
        return None

    body = json.dumps(data) if json_mode else urllib.parse.urlencode(data)
    mime = 'application/json' if json_mode else 'application/x-www-form-urlencoded'

    sign_str = api_path + "\n" + body
    signed_data = hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), sha1)
    sign = signed_data.digest().hex()
    authorization = 'TOKEN ' + access_key + ':' + sign

    response = requests.post(
        'https://api.dogecloud.com' + api_path,
        data=body,
        headers={'Authorization': authorization, 'Content-Type': mime}
    )
    return response.json()

# 根据配置决定是否执行CDN预热
if file_updated and ENABLE_CDN_REFRESH:
    print("文件已更新，开始预热CDN...")
    
    # 预热具体文件
    refresh_data = {
        'rtype': 'prefetch',
        'urls': json.dumps(all_local_links)
    }
    response = dogecloud_api('/cdn/refresh/add.json', refresh_data, json_mode=True)
    print("文件预热响应：", response)
    
    # 刷新目录
    path_refresh_data = {
        'rtype': 'path',
        'urls': 'https://file-us.ovofish.com/file/'
    }
    response = dogecloud_api('/cdn/refresh/add.json', path_refresh_data, json_mode=True)
    print("目录刷新响应：", response)
elif file_updated:
    print("文件已更新，但CDN刷新功能已禁用。")
else:
    print("文件未更新，无需任何操作。")
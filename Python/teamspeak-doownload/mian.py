import requests
from bs4 import BeautifulSoup
import re
import json
import os
import hmac
from hashlib import sha1


print("Start downloading file links...")

# 发送GET请求获取页面内容
url = "https://teamspeak.com/zh-CN/downloads/"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# 找到所有<a>标签并提取链接
links = soup.find_all("a", href=True)

# 匹配包含"https://files.teamspeak-services.com"的链接
file_links = [link["href"] for link in links if re.search(r"https://files.teamspeak-services.com", link["href"])]

# 按版本划分链接
ver3_links = [link for link in file_links if re.search(r"\/3\.\d+\.\d+\/", link)]
ver5_links = [link for link in file_links if re.search(r"\/(?:5\.\d+\.\d+|5\.\d+\.\d+\-\w+)/", link)]

# 设置全局变量
download_file = True
file_updated = False
# 创建版本文件夹并保存链接
def save_links_to_folder(links, folder_name):
    folder_path = os.path.join(os.getcwd(), "file", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for link in links:
        file_name = link.split("/")[-1]
        file_path = os.path.join(folder_path, file_name)

        # 检查文件是否需要更新
        global download_file
        if os.path.exists(file_path):
            response = requests.head(link)
            remote_file_size = int(response.headers.get('Content-Length', 0))
            local_file_size = os.path.getsize(file_path)
            if remote_file_size == local_file_size:
                download_file = False
                print(f"文件 {file_name} 已更新。无需下载。")
            else:
                download_file = True
                os.remove(file_path)
        
        # 如果需要下载文件
        if download_file:
            with open(file_path, "wb") as file:
                response = requests.get(link)
                file.write(response.content)
                print(f"文件 {file_name} 已下载到 {folder_name}")

# 保存链接到对应版本文件夹中
save_links_to_folder(ver3_links, "Ver3")
save_links_to_folder(ver5_links, "Ver5")

# 将链接存储为JSON文件
data = {"Ver3": ver3_links, "Ver5": ver5_links}

with open("file_links.json", "w") as json_file:
    json.dump(data, json_file, indent=4)

print("链接已保存至file_links.json")

def downloadFile():
    global file_updated
    if download_file:
        print("download_file的值为:", download_file)
        file_updated = True
    else:
        print("download_file的值为:", download_file)
        file_updated = False
downloadFile()
print("file_updated的最终值为:", file_updated)

# 生成本地文件下载链接
base_download_url = "https://file-teamspeak-download.lolicon.team/file/"

def generate_local_download_links(links, folder_name):
    local_download_links = [base_download_url + folder_name + "/" + link.split("/")[-1] for link in links]
    return local_download_links

ver3_local_download_links = generate_local_download_links(ver3_links, "Ver3")
ver5_local_download_links = generate_local_download_links(ver5_links, "Ver5")

# 将本地文件下载链接存储为JSON文件
local_download_links_data = {"Ver3": ver3_local_download_links, "Ver5": ver5_local_download_links}

with open("local_download_links.json", "w") as local_json_file:
    json.dump(local_download_links_data, local_json_file, indent=4)

print("本地下载链接已保存至local_download_links.json")

# 判断是否有文件更新
if file_updated:
    print("文件已更新，开始预热CDN...")
    # 预热 CDN
    def dogecloud_api(api_path, data={}, json_mode=False):
        print('正在调用多吉云 API...')
        access_key = ''  # 请将此处替换为你的多吉云 Access Key
        secret_key = ''  # 请将此处替换为你的多吉云 Secret Key
        # 如果没有 access_key 和 secret_key，则跳过下面所有操作
        if not access_key or not secret_key:
            print('请填写多吉云 Access Key 和 Secret Key。')
            return None

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

    api_path = '/cdn/refresh/add.json'
    data = {
        'rtype': 'prefetch',
        'urls': json.dumps(all_local_links)
    }
    response = dogecloud_api(api_path, data, json_mode=True)
    print(response)
    data = {
        'rtype': 'path',
        'urls': 'https://file-teamspeak-download.lolicon.team/file/'
    }
    response = dogecloud_api(api_path, data, json_mode=True)
    print(response)
else:
    print("文件未更新，无需预热CDN。")

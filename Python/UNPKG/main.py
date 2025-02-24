import requests
import re
import os
import shutil
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置
url = "https://unpkg.com/"
headers = {
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Content-Type': 'text/html; Charset=utf-8',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

# 输入模块名
mod = input("请输入模块名:")

# 设置重试机制
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
    proxies=None
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    if proxies:
        session.proxies.update(proxies)
    return session

# 获取HTML
def getHTML(url, encoding='utf-8', proxies=None):
    try:
        with requests_retry_session(proxies=proxies).get(url, headers=headers) as rd:
            rd.encoding = encoding
            rd.raise_for_status()
            return rd.text
    except requests.exceptions.RequestException as e:
        print(f"获取HTML时发生错误: {e}")
        return None

# 获取版本
def getVsions(m, proxies=None):
    h = getHTML(url + m + '/', proxies=proxies)
    j = re.findall(r'<select name="version"(.*?)</select>', h, re.S)[0]
    patt = re.compile(r'<option.+?>(.+?)</option>')
    option = patt.findall(j)
    return option

# 扫描目录
def getPaths(v, p='/', files=[], folders=[], proxies=None):
    h = getHTML(url + v + p, proxies=proxies)
    t = re.findall(r'<table(.*?)</table>', h, re.S)[0]
    href = re.findall('href="(.*?)"', t)
    for name in href:
        path = p + name
        if name in ['../', 'LICENSE'] or path in ['/src/', '/packages/', '/types/', '/dist/docs/', '/docs/',
                                                  '/samples/', "/test/", "/locale/"]:  # 跳过
            continue
        print(path)
        if name[-1] == '/':
            folders.append(path)
            getPaths(v, path, files, folders, proxies)
        else:
            files.append(path)
    return {"files": files, "folders": folders}

# 创建目录
def makeDirs(dirs, p):
    if p is None:
        p = './'
    for i in dirs:
        path = p + i
        if not os.path.exists(path):
            print("创建目录", path)
            os.makedirs(path)

# 下载文件
def download(url, path=None, proxies=None):
    try:
        with requests_retry_session(proxies=proxies).get(url, proxies=proxies) as r:
            r.raise_for_status()
            if not os.path.exists(path):
                print("下载:", url)
                t = str(time.time()) + '.' + str(os.getpid()) + '.tmp'
                with open(t, 'wb') as tmp_file:
                    tmp_file.write(r.content)
                os.rename(t, path)
            else:
                print("文件已存在")
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生错误: {e}")

# 获取所有版本并展示
versions = getVsions(mod)
print("所有版本:", versions)

# 选择版本
version = input("请输入版本号（留空使用最新版）:") or versions[-1]
print("选择的版本:", version)

# 构建版本路径
version_path = mod + '@' + version

# 检查当前目录是否存在该版本
if os.path.exists(version_path):
    print(f"版本 {version_path} 已存在，不再下载。")
else:
    # 使用代理
    proxies = None
    use_proxy = input("是否使用代理？（输入 'y' 或 'n'）: ").lower()
    if use_proxy == 'y':
        # 获取代理设置
        default_proxy_host = "10.10.50.65"  # 设置默认代理主机
        default_proxy_port = 7897  # 设置默认代理端口

        proxy_host = input(f"请输入代理主机 (默认为 {default_proxy_host}): ") or default_proxy_host
        proxy_port = int(input(f"请输入代理端口 (默认为 {default_proxy_port}): ") or default_proxy_port)
        proxy_username = input("请输入代理用户名（如果不需要身份验证，直接回车）: ")
        proxy_password = input("请输入代理密码（如果不需要身份验证，直接回车）: ")

        # 设置代理
        proxies = {
            'http': f'socks5://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}' if proxy_username else f'socks5://{proxy_host}:{proxy_port}',
            'https': f'socks5://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}' if proxy_username else f'socks5://{proxy_host}:{proxy_port}'
        }

    paths = getPaths(version_path, proxies=proxies)
    makeDirs(paths["folders"], version_path)
    for i in paths["files"]:
        u = url + version_path + i
        download(u, version_path + '/' + i, proxies)
    print("下载完成")
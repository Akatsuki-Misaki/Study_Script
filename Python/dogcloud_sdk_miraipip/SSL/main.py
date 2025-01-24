# 该脚本适合使用通配符进行证书绑定
# 作者：Akatsuki-Misaki
# 引入模块
import re
from hashlib import sha1
import hmac
import requests
import json
import urllib
import datetime
# 引入模块结束

# 默认数值填写

# 需要匹配的域名
defCDNdomain = 'example.com'
# 是否使用二级域名 *.example.com
UseSubDomain = True
# 是否使用三级域名 *.*.example.com
UseThirdDomain = False
# 单域名绑定
UseONEDomain = False
# 证书文件路径 绝对路径
SSLFilePath = '/1panel/SSL_Save/full_example_com/'
# 证书文件名
SSL_fullchainName = 'fullchain.pem'
# 证书密钥文件名
SSL_privName = 'privkey.pem'

#默认数值填写结束

# 获取当前日期
nowtime = datetime.datetime.now().strftime('%Y-%m-%d')

# 引入函数模块
def dogecloud_api(api_path, data={}, json_mode=False):
    # 这里替换为你的多吉云永久 AccessKey 和 SecretKey，可在用户中心 - 密钥管理中查看
    # 请勿在客户端暴露 AccessKey 和 SecretKey，否则恶意用户将获得账号完全控制权
    access_key = 'aaaaaaaaaaaaaaaaa'
    secret_key = 'aaaaaaaaaaaaaaaaa'

    body = ''
    mime = ''
    if json_mode:
        body = json.dumps(data)
        mime = 'application/json'
    else:
        body = urllib.parse.urlencode(data) # Python 2 可以直接用 urllib.urlencode
        mime = 'application/x-www-form-urlencoded'
    sign_str = api_path + "\n" + body
    signed_data = hmac.new(secret_key.encode('utf-8'), sign_str.encode('utf-8'), sha1)
    sign = signed_data.digest().hex()
    authorization = 'TOKEN ' + access_key + ':' + sign
    response = requests.post('https://api.dogecloud.com' + api_path, data=body, headers = {
        'Authorization': authorization,
        'Content-Type': mime
    })
    return response.json()

def SSL_OLD_NEW_JSON():
     # 从old_id.json中读取id并删除证书 并且确认是否删除成功
    with open('old_id.json') as f:
        old_id = json.load(f)['id']
        api = dogecloud_api('/cdn/cert/delete.json', {'id': old_id})
        if api['code'] == 200:
            print("脚本：删除证书成功"+"(证书ID: " + str(old_id)+")")
        else:
            print("脚本：删除证书失败"+"(证书ID: " + str(old_id)+")")
    
    # 删除旧ID证书后将新证书ID保存到old_id.json中 用于下次删除
    with open('old_id.json', 'w') as f:
        json.dump({'id': ssl_id}, f)
        print("证书已保存到old_id.json中")
        print("证书ID: " + str(ssl_id))

# 证书绑定域名
def SSL_BIND_DOMAIN(defCDNdomain,ssl_id):
    print("域名进行证书绑定")
    api = dogecloud_api('/cdn/domain/list.json')
    print("传递参数："+ defCDNdomain)
    print("传递参数："+ str(ssl_id))
    # 将defCDNdomain拆分为前后
    parts = defCDNdomain.split('.')
    if len(parts) == 2:  # 确保域名只包含一个点号
        defCDNprefix, defCDNsuffix = parts
        # 如果使用二级域名
        if UseSubDomain:
            print("使用二级域名匹配规则")
            pattern = r'^([^.]+\.)?' + re.escape(defCDNprefix) + '\.' + re.escape(defCDNsuffix) + '$'
            print("正则表达式1"+pattern)
        elif UseThirdDomain:
            print("使用三级域名匹配规则")
            pattern = r'^([^.]+\.){1}' + re.escape(defCDNprefix) + '\.' + re.escape(defCDNsuffix) + '$'
            print("正则表达式1"+pattern)
        elif UseONEDomain:
            print("使用单域名精准匹配规则")
            pattern = r'^' + re.escape(defCDNdomain) + '$'
            print("正则表达式1"+pattern)
        else:
            print("未启用任何域名匹配规则")
    else:
        print("域名格式不正确,创建正则表达式失败")
    try:
        for domain in api['data']['domains']:
            # 仅此匹配*.example.com不匹配*.*.example.com
            if re.match (pattern,domain['name']):
                print("正则表达式2"+pattern)
                print("找到匹配的域名:"+ domain['name'])
                cdndomain = domain['name']
                print("证书ID:"+ str(ssl_id))
                # api = dogecloud_api('/cdn/domain/config.json?domain=' + cdndomain, {'cert_id': ssl_id})
                api = dogecloud_api('/cdn/domain/config.json?domain='+ cdndomain, {'cert_id': ssl_id}, True)
                print(api)
                if api['code'] == 200:
                    print("脚本:证书绑定成功("+ domain['name']+")")
                else:
                    print("脚本:证书绑定失败("+ domain['name']+")")
            else:
                print("未匹配的域名:"+ domain['name'])
    except Exception as e:
        print("域名正则表达式创建失败")

# 引入函数模块结束

# 主程序
__name__ == '__main__'
print("开始执行证书更新")
# 下面两个函数用于读取证书文件 若要修改请到上面的默认数值修改
with open(SSLFilePath+SSL_fullchainName) as fullchain:
    full = fullchain.read()
with open(SSLFilePath+SSL_privName) as privkey:
    priv = privkey.read()
api = dogecloud_api('/cdn/cert/upload.json', {
    "note": f"自动证书"+nowtime,
    "cert": full,
    "private": priv
})


if api['code'] == 200:
    ssl_id = api['data']['id']
    print("api success: " + api['msg'])
    print("证书ID: " + str(ssl_id))
    # 域名绑定证书
    SSL_BIND_DOMAIN(defCDNdomain,ssl_id)
else:
    print("api failed: " + api['msg']) # 失敗
    # 退出脚本
    print("因为域名证书上传失败，脚本已退出")
    exit()


# 查询是否具有old_id.json
# 如果有则运行SSL_OLD_NEW_JSON
try:
    with open('old_id.json') as f:
        SSL_OLD_NEW_JSON()
        print("已执行删除操作")
except FileNotFoundError:
    print("没有找到old_id.json文件，无法执行删除操作")
    # 新增old_id.json文件
    with open('old_id.json', 'w') as f:
        json.dump({'id': ssl_id}, f)
        print("已创建新的old_id.json文件")
    exit()
    
print("证书更新已完成")
print("主程序已结束")
#!/bin/bash

# 定义用户名和密码
USERNAME="****"  
PASSWORD="****"  

# 安全入口 EntranceCode（Base64 ）
ENTRANCE_CODE="******"  

# 1Panel API 地址
LOGIN_URL="http://*******/api/v1/auth/login"  
UPLOAD_URL="http://********/api/v1/websites/ssl/upload"  

# 定义证书相关信息
PRIVATE_KEY_PATH="/data2/SSL_SAVE/ovofish/privkey.pem"  
CERTIFICATE_PATH="/data2/SSL_SAVE/ovofish/fullchain.pem"  
SSL_ID=3
DESCRIPTION="sync from certd:tx4"

# 构建登录请求的 JSON 数据
LOGIN_DATA=$(cat <<EOF
{
    "name": "$USERNAME",
    "password": "$PASSWORD",
    "language":"zh",
    "authMethod": "jwt"
}
EOF
)
# 使用 curl 发送登录请求
RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
    -H "Content-Type: application/json" \
    -H "EntranceCode: $ENTRANCE_CODE" \
    -d "$LOGIN_DATA")
# 解析返回的 token
TOKEN=$(echo $RESPONSE | grep -Po '(?<="token":")[^"]*')

# 检查是否登录成功
if [ -n "$TOKEN" ]; then
    echo "登录成功，token: $TOKEN"

    # 读取私钥和证书内容
    PRIVATE_KEY_CONTENT=$(cat "$PRIVATE_KEY_PATH" | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
    CERTIFICATE_CONTENT=$(cat "$CERTIFICATE_PATH" | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
    printf "私钥内容: $PRIVATE_KEY_CONTENT"
    printf "证书内容: $CERTIFICATE_CONTENT"
    # 构建上传证书的请求数据
    UPLOAD_DATA=$(cat <<EOF
{
    "privateKey": "$PRIVATE_KEY_CONTENT",
    "certificate": "$CERTIFICATE_CONTENT",
    "privateKeyPath": "",
    "certificatePath": "",
    "type": "paste",
    "sslID": $SSL_ID,
    "description": "$DESCRIPTION"
}
EOF
    )

    # 发送证书上传请求
    UPLOAD_RESPONSE=$(curl -s -X POST "$UPLOAD_URL" \
        -H "PanelAuthorization: $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$UPLOAD_DATA")

    # 输出上传结果
    echo "$UPLOAD_DATA"
    echo "证书上传响应: $UPLOAD_RESPONSE"
else
    echo "登录失败，请检查用户名或密码"
    echo "失败响应: $RESPONSE"
fi

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import urllib.request
import urllib.parse
import json

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')

# 获取环境变量
appid = os.environ.get('WECHAT_APPID', '')
appsecret = os.environ.get('WECHAT_APPSECRET', '')

# 获取access_token
token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"

print(f"正在获取access_token...")

req = urllib.request.Request(token_url)
with urllib.request.urlopen(req, timeout=30) as response:
    data = json.loads(response.read().decode('utf-8'))
    
    if 'access_token' in data:
        access_token = data['access_token']
        print(f"✓ 获取access_token成功\n")
        
        # 使用在线图片作为封面
        # 使用一个历史相关的图片URL
        cover_url = "https://images.unsplash.com/photo-1540979388789-6cee28a1cdc9?w=900&h=383&fit=crop"
        
        print(f"正在下载封面图片...")
        
        # 下载图片
        img_req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(img_req, timeout=30) as img_response:
            image_data = img_response.read()
            
            print(f"✓ 下载成功，图片大小: {len(image_data)} bytes\n")
            
            # 上传到微信
            upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
            
            print(f"正在上传封面到微信...")
            
            # 构建multipart请求
            import io
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            
            body = io.BytesIO()
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="media"; filename="cover.jpg"\r\n')
            body.write(b'Content-Type: image/jpeg\r\n\r\n')
            body.write(image_data)
            body.write(f'\r\n--{boundary}--\r\n'.encode())
            
            req = urllib.request.Request(
                upload_url,
                data=body.getvalue(),
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as upload_response:
                result = json.loads(upload_response.read().decode('utf-8'))
                
                if 'media_id' in result:
                    print(f"✅ 封面上传成功！")
                    print(f"Media ID: {result['media_id']}")
                    print(f"URL: {result.get('url', 'N/A')}")
                    
                    # 保存media_id到文件
                    with open('cover_media_id.txt', 'w', encoding='utf-8') as f:
                        f.write(result['media_id'])
                    print(f"\nMedia ID已保存到 cover_media_id.txt")
                else:
                    print(f"❌ 上传失败: {result}")
    else:
        print(f"❌ 获取access_token失败: {data}")

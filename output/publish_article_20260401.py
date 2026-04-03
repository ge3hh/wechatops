#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 读取文章文件
with open('article_taipingnian_zhaokuangyin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 获取环境变量
appid = os.environ.get('WECHAT_APPID', '')
appsecret = os.environ.get('WECHAT_APPSECRET', '')

print(f"AppID: {appid[:10]}...")
print(f"AppSecret: {appsecret[:10]}...")
print(f"文章内容长度: {len(content)} 字符")
print("\n准备发布文章...")
print("标题: 那件黄袍：郭荣亲手送的，还是赵匡胤自己拿的？")

# 导入发布模块
sys.path.insert(0, 'skills/wechat-publish/scripts')

# 先尝试获取token
try:
    import urllib.request
    import urllib.parse
    import json
    
    # 获取access_token
    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    
    print(f"\n正在获取access_token...")
    
    req = urllib.request.Request(token_url)
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        if 'access_token' in data:
            access_token = data['access_token']
            print(f"✓ 获取access_token成功")
            
            # 准备发布文章
            title = "那件黄袍：郭荣亲手送的，还是赵匡胤自己拿的？"
            digest = "电视剧《太平年》热播，郭荣临终前送黄袍给赵匡胤是史实还是虚构？赵匡胤夺位算不算欺负孤儿寡母？"
            
            # 构建草稿数据
            draft_data = {
                "articles": [
                    {
                        "title": title,
                        "author": "胖橘happy",
                        "digest": digest,
                        "content": content,
                        "content_source_url": "",
                        "thumb_media_id": "",
                        "need_open_comment": 1,
                        "only_fans_can_comment": 0
                    }
                ]
            }
            
            # 发布草稿
            draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
            
            print(f"\n正在创建草稿...")
            
            post_data = json.dumps(draft_data, ensure_ascii=False).encode('utf-8')
            
            req = urllib.request.Request(
                draft_url,
                data=post_data,
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'media_id' in result:
                    print(f"\n✅ 文章发布成功！")
                    print(f"Media ID: {result['media_id']}")
                    print(f"\n请登录公众号后台查看草稿箱")
                    
                    # 保存发布记录
                    record = {
                        "title": title,
                        "media_id": result['media_id'],
                        "publish_time": "2026-04-01",
                        "score": 9.2
                    }
                    print(f"\n发布记录: {record}")
                    
                else:
                    print(f"\n❌ 发布失败: {result}")
        else:
            print(f"❌ 获取access_token失败: {data}")
            
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

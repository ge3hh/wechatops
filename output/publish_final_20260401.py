#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import urllib.request
import json

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')

# 读取文章文件
with open('article_taipingnian_zhaokuangyin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 读取封面media_id
with open('cover_media_id.txt', 'r', encoding='utf-8') as f:
    cover_media_id = f.read().strip()

# 获取环境变量
appid = os.environ.get('WECHAT_APPID', '')
appsecret = os.environ.get('WECHAT_APPSECRET', '')

print("="*60)
print("微信公众号文章发布")
print("="*60)
print(f"\n标题: 那件黄袍：郭荣亲手送的，还是赵匡胤自己拿的？")
print(f"作者: 胖橘happy")
print(f"文章长度: {len(content)} 字符")
print(f"封面Media ID: {cover_media_id[:20]}...")

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
                    "thumb_media_id": cover_media_id,
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
                print(f"\n" + "="*60)
                print("✅ 文章发布成功！")
                print("="*60)
                print(f"\nMedia ID: {result['media_id']}")
                print(f"\n请按以下步骤操作：")
                print(f"1. 登录微信公众号后台")
                print(f"2. 进入【内容与互动】->【草稿箱】")
                print(f"3. 找到文章《{title}》")
                print(f"4. 预览、编辑后发布")
                
                # 保存发布记录
                record = {
                    "title": title,
                    "media_id": result['media_id'],
                    "cover_media_id": cover_media_id,
                    "publish_time": "2026-04-01T22:00:00",
                    "score": 9.2,
                    "topic": "太平年 郭荣 赵匡胤 陈桥兵变"
                }
                
                # 追加到历史记录
                import datetime
                history_file = 'memory/history/articles.json'
                
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except:
                    history = {"articles": []}
                
                history["articles"].append(record)
                
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                
                print(f"\n✓ 发布记录已保存到 {history_file}")
                
            else:
                print(f"\n❌ 发布失败: {result}")
    else:
        print(f"❌ 获取access_token失败: {data}")

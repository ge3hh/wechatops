#!/usr/bin/env python3
"""
哔哩哔哩专栏文章发布脚本

功能：发布专栏文章到哔哩哔哩
授权方式：ApiKey（auth_type=1）
凭证Key: COZE_BILIBILI_CREDENTIAL_7597373721971540014
"""

import os
import sys
import argparse
import json
# 兼容 Coze 平台和本地环境
try:
    from coze_workload_identity import requests
except ImportError:
    import requests


def get_bilibili_credentials():
    """
    从环境变量获取B站凭证
    """
    skill_id = "7597373721971540014"
    
    # B站需要Cookie
    cookie = os.getenv(f"COZE_BILIBILI_CREDENTIAL_{skill_id}")
    
    if not cookie:
        raise ValueError(
            "未找到哔哩哔哩凭证配置。\n"
            "请提供B站Web端Cookie。\n"
            "获取方式：\n"
            "1. 浏览器登录B站 https://www.bilibili.com\n"
            "2. 打开开发者工具（F12）\n"
            "3. 在Application → Cookies中找到SESSDATA、bili_jct等\n"
            "4. 复制完整的Cookie字符串"
        )
    
    # 从Cookie中提取CSRF Token（bili_jct）
    csrf_token = None
    for item in cookie.split(';'):
        item = item.strip()
        if 'bili_jct=' in item:
            csrf_token = item.split('=')[1]
            break
    
    if not csrf_token:
        raise ValueError("Cookie中未找到bili_jct（CSRF Token），请检查Cookie是否完整")
    
    return {
        'cookie': cookie,
        'csrf_token': csrf_token
    }


def get_upload_url(creds):
    """
    获取上传图片的URL
    """
    url = "https://api.bilibili.com/x/archive/oss/upload"
    headers = {
        'Cookie': creds['cookie'],
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    
    if result.get('code') == 0:
        return result['data']['url']
    else:
        raise Exception(f"获取上传URL失败: {result.get('message')}")


def publish_bilibili_article(title, content, category_id=122, summary=None):
    """
    发布专栏文章到B站
    
    Args:
        title: 文章标题
        content: 文章内容（Markdown格式）
        category_id: 专栏分类ID（默认122-技术）
        summary: 文章摘要
    
    Returns:
        dict: 发布结果
    """
    # 获取凭证
    creds = get_bilibili_credentials()
    
    # B站API端点
    url = "https://api.bilibili.com/x/article/drafts"
    
    # 构建请求数据
    headers = {
        'Cookie': creds['cookie'],
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://member.bilibili.com'
    }
    
    data = {
        'title': title,
        'content': content,
        'category_id': category_id,
        'summary': summary if summary else content[:100],  # 自动生成摘要
        'list': [],
        ' reprint': 0,  # 0-原创, 1-转载
        'top_video': '',
        'duration': 0,
        'words': len(content),
        'original': 1,
        'media_id': 0,
        'spoiler': 0,
        'dynamic': ''  # 同步动态的内容
    }
    
    try:
        # 先保存为草稿
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if result.get('code') == 0:
            draft_id = result['data']['id']
            
            # 发布草稿
            publish_url = f"https://api.bilibili.com/x/article/publish?csrf={creds['csrf_token']}"
            publish_data = {'id': draft_id}
            publish_response = requests.post(publish_url, headers=headers, json=publish_data, timeout=30)
            publish_result = publish_response.json()
            
            if publish_result.get('code') == 0:
                article_id = publish_result['data']['id']
                return {
                    "success": True,
                    "article_id": article_id,
                    "message": "专栏发布成功",
                    "url": f"https://www.bilibili.com/read/cv{article_id}"
                }
            else:
                raise Exception(f"发布失败: {publish_result.get('message')}")
        else:
            raise Exception(f"保存草稿失败: {result.get('message')}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("响应解析失败")


def main():
    parser = argparse.ArgumentParser(description="发布专栏文章到哔哩哔哩")
    
    # 必需参数
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--content", required=True, help="文章内容（Markdown或HTML格式）")
    
    # 可选参数
    parser.add_argument("--category_id", type=int, default=122, 
                       help="专栏分类ID（默认122-技术）")
    parser.add_argument("--summary", help="文章摘要")
    
    args = parser.parse_args()
    
    try:
        print("正在准备发布B站专栏...")
        
        print(f"标题: {args.title}")
        print(f"内容长度: {len(args.content)} 字")
        print(f"分类ID: {args.category_id}")
        
        # 发布专栏
        print("\n正在发布...")
        result = publish_bilibili_article(
            title=args.title,
            content=args.content,
            category_id=args.category_id,
            summary=args.summary
        )
        
        # 输出结果
        print("\n" + "="*50)
        print("✅ 发布成功！")
        print("="*50)
        print(f"文章ID: {result['article_id']}")
        print(f"文章链接: {result['url']}")
        print("\n请登录B站查看发布的专栏")
        print("="*50)
        
        print("\nJSON输出:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 发布失败: {str(e)}", file=sys.stderr)
        
        # 错误提示
        if "Cookie" in str(e):
            print("\n💡 解决方案：", file=sys.stderr)
            print("请检查B站Cookie是否正确", file=sys.stderr)
            print("1. 确认Cookie中包含SESSDATA和bili_jct", file=sys.stderr)
            print("2. Cookie可能已过期，需要重新获取", file=sys.stderr)
            print("3. 尝试重新登录B站", file=sys.stderr)
        elif "csrf" in str(e).lower():
            print("\n💡 解决方案：", file=sys.stderr)
            print("CSRF Token（bili_jct）无效或缺失", file=sys.stderr)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号草稿箱发布脚本（标准版）

使用方式：
  python publish_draft.py --file output/article_xxx_v5.html
  python publish_draft.py --file output/article_xxx_v5.html --title "自定义标题"

约定：
  - 所有文章定稿必须保存在 output/ 目录
  - 封面 media_id 优先从 cover_media_id.txt 读取（复用）
  - 使用 Python 标准库 urllib，避免第三方依赖问题
"""

import sys
import os
import urllib.request
import json
import argparse
import datetime

# 设置UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')


def get_access_token():
    """获取微信公众号 access_token"""
    appid = os.environ.get('WECHAT_APPID', '')
    appsecret = os.environ.get('WECHAT_APPSECRET', '')

    if not appid or not appsecret:
        raise ValueError("请先设置环境变量 WECHAT_APPID 和 WECHAT_APPSECRET")

    token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    req = urllib.request.Request(token_url)

    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        if 'access_token' in data:
            return data['access_token']
        else:
            raise Exception(f"获取access_token失败: {data}")


def publish_draft(article_file, title=None, author="胖橘happy", digest=None):
    """发布文章到微信公众号草稿箱"""

    # 读取文章内容
    with open(article_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 自动提取标题（如果未提供）
    if not title:
        import re
        match = re.search(r'<title>(.*?)</title>', content)
        if match:
            title = match.group(1)
        else:
            title = "未命名文章"

    # 读取封面 media_id（优先复用）
    cover_media_id = ""
    cover_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cover_media_id.txt')
    if os.path.exists(cover_file):
        with open(cover_file, 'r', encoding='utf-8') as f:
            cover_media_id = f.read().strip()

    if not cover_media_id:
        print("⚠️ 警告：未找到 cover_media_id.txt，草稿将没有封面图")

    # 获取access_token
    print(f"\n正在获取access_token...")
    access_token = get_access_token()
    print(f"✓ 获取access_token成功")

    # 构建草稿数据
    draft_data = {
        "articles": [
            {
                "title": title,
                "author": author,
                "digest": digest or "",
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
            print(f"\n标题: {title}")
            print(f"Media ID: {result['media_id']}")
            print(f"\n请按以下步骤操作：")
            print(f"1. 登录微信公众号后台: https://mp.weixin.qq.com")
            print(f"2. 进入【内容与互动】->【草稿箱】")
            print(f"3. 找到文章《{title}》")
            print(f"4. 预览、编辑后发布")

            # 保存发布记录
            record = {
                "title": title,
                "media_id": result['media_id'],
                "cover_media_id": cover_media_id,
                "publish_time": datetime.datetime.now().isoformat(),
                "file_path": article_file,
                "topic": ""
            }

            history_file = 'memory/history/articles.json'
            os.makedirs(os.path.dirname(history_file), exist_ok=True)

            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = {"articles": []}

            history["articles"].append(record)

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)

            print(f"\n✓ 发布记录已保存到 {history_file}")
            return result['media_id']
        else:
            print(f"\n❌ 发布失败: {result}")
            return None


def main():
    parser = argparse.ArgumentParser(description="发布HTML文章到微信公众号草稿箱")
    parser.add_argument("--file", required=True, help="文章HTML文件路径（必须在 output/ 目录）")
    parser.add_argument("--title", help="文章标题（默认从HTML中提取）")
    parser.add_argument("--author", default="胖橘happy", help="作者名称")
    parser.add_argument("--digest", help="文章摘要")

    args = parser.parse_args()

    # 强制检查文件在 output/ 目录
    if not args.file.startswith("output/"):
        print(f"⚠️ 警告：文章文件 '{args.file}' 不在 output/ 目录")
        print("按照规范，所有文章定稿必须保存在 output/ 目录")
        # 不阻止，但警告

    if not os.path.exists(args.file):
        print(f"❌ 错误：文件不存在: {args.file}")
        sys.exit(1)

    publish_draft(
        article_file=args.file,
        title=args.title,
        author=args.author,
        digest=args.digest
    )


if __name__ == "__main__":
    main()

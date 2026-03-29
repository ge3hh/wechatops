#!/usr/bin/env python3
"""
统一的微信公众号发布模块

合并功能：
- simple_publish.py
- direct_publish.py
- publish_local.py
- publish_final.py
- correct_publish.py
- wechat_publish_official.py

使用方法:
    python unified_publisher.py --mode wechat --title "标题" --content-file article.html
    python unified_publisher.py --mode custom --config publish_config.json
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class PublishConfig:
    """发布配置"""
    title: str
    content: str
    cover_url: Optional[str] = None
    tags: List[str] = None
    author: str = "胖橘happy"
    digest: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class WeChatPublisher:
    """微信公众号发布器（使用官方API）"""

    BASE_URL = "https://api.weixin.qq.com/cgi-bin"

    def __init__(self):
        self.appid = os.getenv('WECHAT_APPID')
        self.appsecret = os.getenv('WECHAT_APPSECRET')
        self._access_token: Optional[str] = None

        if not self.appid or not self.appsecret:
            raise ValueError(
                "未配置微信公众号凭证。\n"
                "请设置环境变量:\n"
                "  WECHAT_APPID=your-appid\n"
                "  WECHAT_APPSECRET=your-appsecret"
            )

    def get_access_token(self) -> str:
        """获取 access_token（带缓存）"""
        if self._access_token:
            return self._access_token

        url = f"{self.BASE_URL}/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            if 'access_token' in result:
                self._access_token = result['access_token']
                return self._access_token
            else:
                raise Exception(f"获取token失败: {result.get('errmsg', '未知错误')}")
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP错误 {e.code}: {e.reason}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {e}")

    def upload_thumb(self, image_path: str) -> str:
        """上传封面图片"""
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/media/upload?access_token={access_token}&type=thumb"

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"封面图片不存在: {image_path}")

        # 读取本地图片
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 构建 multipart/form-data 请求
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'------{boundary}\r\n'
            f'Content-Disposition: form-data; name="media"; filename="{os.path.basename(image_path)}"\r\n'
            f'Content-Type: image/jpeg\r\n\r\n'
        ).encode() + image_data + f'\r\n------{boundary}--\r\n'.encode()

        req = urllib.request.Request(
            url,
            data=body,
            headers={'Content-Type': f'multipart/form-data; boundary=----{boundary}'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

        if 'thumb_media_id' in result:
            return result['thumb_media_id']
        elif 'media_id' in result:
            return result['media_id']
        else:
            raise Exception(f"上传封面失败: {result.get('errmsg', '未知错误')}")

    def create_draft(self, config: PublishConfig, thumb_media_id: str) -> str:
        """创建草稿"""
        access_token = self.get_access_token()
        url = f"{self.BASE_URL}/draft/add?access_token={access_token}"

        # 处理内容
        content = config.content
        if not content.startswith('<'):
            content = f'<p>{content}</p>'

        article = {
            "title": config.title,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "author": config.author,
            "digest": config.digest,
            "show_cover_pic": 1,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }

        data = {"articles": [article]}

        req = urllib.request.Request(
            url,
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

        if result.get('errcode') == 0 and 'media_id' in result:
            return result['media_id']
        else:
            raise Exception(f"创建草稿失败: {result.get('errmsg', '未知错误')}")

    def publish(self, config: PublishConfig, cover_path: Optional[str] = None) -> Dict:
        """完整发布流程"""
        print("=" * 50)
        print("微信公众号文章发布")
        print("=" * 50)

        # 1. 上传封面
        print("\n[1/3] 正在上传封面图片...")
        if cover_path and os.path.exists(cover_path):
            thumb_media_id = self.upload_thumb(cover_path)
            print(f"✅ 封面上传成功")
        else:
            print("⚠️ 封面图片不存在，跳过封面上传")
            thumb_media_id = None

        # 2. 创建草稿
        print("\n[2/3] 正在创建草稿...")
        if thumb_media_id:
            media_id = self.create_draft(config, thumb_media_id)
        else:
            raise ValueError("缺少封面图片，无法创建草稿")

        print("\n" + "=" * 50)
        print("✅ 文章发布成功!")
        print("=" * 50)
        print(f"标题: {config.title}")
        print(f"Media ID: {media_id}")
        print("\n请登录公众号后台查看草稿箱")
        print("=" * 50)

        return {
            "success": True,
            "media_id": media_id,
            "title": config.title
        }


class CustomAPIPublisher:
    """自定义API发布器"""

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.getenv("WECHAT_PUBLISH_API_URL")
        if not self.api_url:
            raise ValueError(
                "未配置发布API地址。\n"
                "请设置环境变量: WECHAT_PUBLISH_API_URL\n"
                "或在初始化时传入 api_url 参数。"
            )

    def publish(self, config: PublishConfig) -> Dict:
        """发布到自定义API"""
        data = {
            "title": config.title,
            "content": config.content,
            "cover_url": config.cover_url or "",
            "tags": config.tags
        }

        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')

        req = urllib.request.Request(
            self.api_url,
            data=json_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            print(f"\n✅ 发布成功!")
            return result

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"HTTP错误 {e.code}: {e.reason} - {error_body}")


def load_config_from_file(path: str) -> PublishConfig:
    """从文件加载配置"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 读取内容文件
    content_file = data.get('content_file', data.get('html_file', 'output/publish_ready.html'))
    if os.path.exists(content_file):
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = data.get('content', '')

    return PublishConfig(
        title=data['title'],
        content=content,
        cover_url=data.get('cover_url'),
        tags=data.get('tags', []),
        author=data.get('author', '胖橘happy'),
        digest=data.get('digest', '')
    )


def load_config_from_args(args) -> PublishConfig:
    """从命令行参数加载配置"""
    # 读取内容
    if args.content_file:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        raise ValueError("请提供 --content-file 或 --content 参数")

    return PublishConfig(
        title=args.title,
        content=content,
        cover_url=args.cover,
        tags=args.tags.split(',') if args.tags else [],
        author=args.author,
        digest=args.digest
    )


def main():
    parser = argparse.ArgumentParser(
        description="统一的微信公众号发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用官方API发布
  python unified_publisher.py --mode wechat --title "标题" --content-file article.html --cover cover.jpg

  # 使用自定义API发布
  python unified_publisher.py --mode custom --config publish_config.json

  # 从环境变量读取配置
  python unified_publisher.py --mode wechat --config publish_config.json
        """
    )

    parser.add_argument("--mode",
                       choices=['wechat', 'custom'],
                       default='wechat',
                       help="发布模式: wechat-官方API, custom-自定义API")

    parser.add_argument("--config",
                       help="配置文件路径 (JSON格式)")

    parser.add_argument("--title",
                       help="文章标题")

    parser.add_argument("--content-file",
                       help="文章内容文件路径 (HTML)")

    parser.add_argument("--content",
                       help="文章内容 (HTML格式)")

    parser.add_argument("--cover",
                       help="封面图片路径")

    parser.add_argument("--tags",
                       help="标签 (逗号分隔)")

    parser.add_argument("--author",
                       default="胖橘happy",
                       help="作者名称")

    parser.add_argument("--digest",
                       default="",
                       help="文章摘要")

    args = parser.parse_args()

    try:
        # 加载配置
        if args.config:
            config = load_config_from_file(args.config)
        else:
            config = load_config_from_args(args)

        # 根据模式选择发布器
        if args.mode == 'wechat':
            publisher = WeChatPublisher()
            result = publisher.publish(config, cover_path=args.cover)
        else:
            publisher = CustomAPIPublisher()
            result = publisher.publish(config)

        # 输出结果
        print("\nJSON输出:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ 文件错误: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ 发布失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

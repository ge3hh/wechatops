#!/usr/bin/env python3
"""
微信公众号草稿箱发布脚本（增强版）

功能：
1. 上传图片素材到微信公众号（官方API）
2. 将文章发布到微信公众号草稿箱（官方API）
3. 调用自定义接口自动推送（新增）

授权方式：WeChatOfficialAccount（auth_type=2）
凭证Key: COZE_WECHAT_OFFICIAL_ACCOUNT_7597373721971540014
"""

import os
import sys
import argparse
import json
from typing import Dict, Optional, List

# 兼容 Coze 平台和本地环境
try:
    from coze_workload_identity import requests
except ImportError:
    import requests


# 全局 session，用于连接复用
_session = requests.Session()
_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})


def get_access_token() -> str:
    """
    获取微信公众号 access_token
    支持两种方式：
    1. 直接提供 COZE_WECHAT_OFFICIAL_ACCOUNT_{skill_id}（Coze平台）
    2. 使用 WECHAT_APPID + WECHAT_APPSECRET 换取（标准方式）
    """
    skill_id = os.getenv("COZE_SKILL_ID", "7597373721971540014")

    # 方式1：Coze 平台环境变量（如果存在）
    access_token = os.getenv(f"COZE_WECHAT_OFFICIAL_ACCOUNT_{skill_id}")
    if access_token:
        return access_token

    # 方式2：使用 AppID + AppSecret 换取
    appid = os.getenv("WECHAT_APPID")
    appsecret = os.getenv("WECHAT_APPSECRET")

    if not appid or not appsecret:
        raise ValueError(
            "未找到微信公众号凭证配置。\n"
            "请设置以下环境变量之一：\n"
            f"1. COZE_WECHAT_OFFICIAL_ACCOUNT_{skill_id} （Coze平台）\n"
            "2. WECHAT_APPID + WECHAT_APPSECRET （标准方式）\n"
            "获取方式：登录公众号后台 → 设置与开发 → 基本配置"
        )

    # 调用微信接口获取 access_token
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={appsecret}"
    try:
        response = _session.get(url, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("access_token"):
            return result["access_token"]
        else:
            error_msg = result.get('errmsg', '未知错误')
            raise Exception(f"获取 access_token 失败: {error_msg}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取 access_token 请求失败: {str(e)}")


def upload_media(access_token: str, image_path: str, media_type: str = "thumb") -> Dict:
    """
    上传图片到微信公众号素材库
    
    Args:
        access_token: 微信公众号access_token
        image_path: 图片文件路径（本地或URL）
        media_type: 媒体类型（thumb-封面图片, image-其他图片）
    
    Returns:
        dict: 包含media_id的响应
    """
    url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={media_type}"
    
    headers = {}
    
    # 判断是本地文件还是URL
    if image_path.startswith(('http://', 'https://')):
        # 下载URL图片
        try:
            response = _session.get(image_path, timeout=30)
            response.raise_for_status()
            file_data = response.content
            filename = image_path.split('/')[-1]
        except requests.exceptions.RequestException as e:
            raise Exception(f"下载图片失败: {str(e)}")
    else:
        # 读取本地文件
        try:
            with open(image_path, 'rb') as f:
                file_data = f.read()
            filename = os.path.basename(image_path)
        except FileNotFoundError:
            raise Exception(f"图片文件不存在: {image_path}")
        except IOError as e:
            raise Exception(f"读取本地图片失败: {str(e)}")
    
    # 准备上传文件
    files = {
        'media': (filename, file_data, 'image/jpeg')
    }
    
    try:
        # 发送请求
        response = _session.post(url, files=files, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # 检查错误码
        errcode = result.get("errcode", -1)
        if errcode != 0:
            errmsg = result.get("errmsg", "未知错误")
            raise Exception(f"微信API错误 [{errcode}]: {errmsg}")
        
        # 提取media_id
        media_id = result.get("media_id")
        if not media_id:
            raise Exception("上传失败：未获取到media_id")
        
        return {
            "success": True,
            "media_id": media_id,
            "type": media_type,
            "url": result.get("url", "")
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("响应解析失败")


def upload_temp_media(access_token: str, image_path: str) -> str:
    """
    上传临时素材（用于正文图片）

    Args:
        access_token: 微信公众号access_token
        image_path: 图片文件路径

    Returns:
        str: media_id

    Raises:
        Exception: 上传失败时抛出
    """
    result = upload_media(access_token, image_path, media_type="image")
    media_id = result.get("media_id")
    if not media_id:
        raise Exception("上传临时素材失败：未获取到media_id")
    return media_id


def upload_thumb_media(access_token: str, image_path: str) -> str:
    """
    上传封面图片

    Args:
        access_token: 微信公众号access_token
        image_path: 图片文件路径

    Returns:
        str: media_id

    Raises:
        Exception: 上传失败时抛出
    """
    result = upload_media(access_token, image_path, media_type="thumb")
    media_id = result.get("media_id")
    if not media_id:
        raise Exception("上传封面失败：未获取到media_id")
    return media_id


def create_draft(access_token: str, title: str, content: str, 
                thumb_media_id: str, author: Optional[str] = None,
                digest: Optional[str] = None, show_cover: bool = True) -> Dict:
    """
    创建草稿箱文章
    
    Args:
        access_token: 微信公众号access_token
        title: 文章标题
        content: 文章内容（HTML格式）
        thumb_media_id: 封面图素材ID
        author: 作者名称（可选）
        digest: 摘要（可选）
        show_cover: 是否显示封面图（默认True）
    
    Returns:
        dict: 草稿创建结果
    """
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    # 构建文章数据
    article = {
        "title": title,
        "content": content,
        "thumb_media_id": thumb_media_id,
        "show_cover_pic": 1 if show_cover else 0,
        "need_open_comment": 1,
        "only_fans_can_comment": 0
    }
    
    # 可选参数
    if author:
        article["author"] = author
    if digest:
        article["digest"] = digest
    
    data = {
        "articles": [article]
    }
    
    try:
        # 发送请求
        response = _session.post(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # 检查错误码
        errcode = result.get("errcode", -1)
        if errcode != 0:
            errmsg = result.get("errmsg", "未知错误")
            raise Exception(f"微信API错误 [{errcode}]: {errmsg}")
        
        # 提取media_id
        media_id = result.get("media_id")
        if not media_id:
            raise Exception("创建草稿失败：未获取到media_id")
        
        return {
            "success": True,
            "media_id": media_id,
            "message": "草稿创建成功",
            "data": {
                "title": title,
                "media_id": media_id,
                "errcode": 0,
                "errmsg": "ok"
            }
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("响应解析失败")


def publish_to_custom_api(
    title: str,
    content: str,
    cover_url: str,
    tags: Optional[List[str]] = None,
    api_url: Optional[str] = None
) -> Dict:
    """
    调用自定义接口自动推送到微信公众号草稿箱

    Args:
        title: 文章标题
        content: 文章内容（HTML格式）
        cover_url: 封面图URL
        tags: 标签数组（可选）
        api_url: 自定义接口URL（从环境变量 WECHAT_PUBLISH_API_URL 读取）

    Returns:
        dict: 发布结果

    Raises:
        ValueError: 当 api_url 未提供且环境变量未设置时
    """
    if api_url is None:
        api_url = os.getenv("WECHAT_PUBLISH_API_URL")
        if not api_url:
            raise ValueError(
                "未配置发布API地址。\n"
                "请设置环境变量: WECHAT_PUBLISH_API_URL\n"
                "或在调用时传入 api_url 参数。"
            )
    # 构建请求数据
    data = {
        "title": title,
        "content": content,
        "cover_url": cover_url,
        "tags": tags if tags else []
    }
    
    try:
        print(f"\n正在调用自定义接口...")
        print(f"接口地址: {api_url}")
        print(f"文章标题: {title}")
        print(f"标签: {tags}")
        
        # 发送POST请求
        response = _session.post(
            api_url,
            json=data,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✅ 接口调用成功！")
        print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return {
            "success": True,
            "message": "推送成功",
            "data": result
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"接口调用失败: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("响应解析失败")
    except Exception as e:
        raise Exception(f"推送失败: {str(e)}")


def complete_workflow(access_token: str, title: str, content: str,
                     cover_image_path: str, author: Optional[str] = None,
                     digest: Optional[str] = None) -> Dict:
    """
    完整工作流：上传封面→创建草稿
    
    Args:
        access_token: 微信公众号access_token
        title: 文章标题
        content: 文章内容（HTML格式）
        cover_image_path: 封面图片路径（本地文件或URL）
        author: 作者名称（可选）
        digest: 摘要（可选）
    
    Returns:
        dict: 包含草稿media_id的结果
    """
    print("\n📤 步骤1：上传封面图片...")
    thumb_result = upload_thumb_media(access_token, cover_image_path)
    print(f"✅ 封面上传成功，media_id: {thumb_result['media_id']}")
    
    print("\n📝 步骤2：创建草稿...")
    draft_result = create_draft(
        access_token=access_token,
        title=title,
        content=content,
        thumb_media_id=thumb_result['media_id'],
        author=author,
        digest=digest
    )
    
    print(f"✅ 草稿创建成功，media_id: {draft_result['media_id']}")
    
    return {
        "success": True,
        "cover_media_id": thumb_result['media_id'],
        "draft_media_id": draft_result['media_id'],
        "message": "完整工作流执行成功"
    }


def main():
    parser = argparse.ArgumentParser(
        description="微信公众号草稿箱发布工具（增强版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 完整工作流：上传封面→创建草稿
  python publish_wechat.py --mode workflow --title "标题" --content "内容" --cover "图片路径"
  
  # 仅上传封面图片
  python publish_wechat.py --mode upload_cover --cover "图片路径"
  
  # 仅创建草稿（使用已有media_id）
  python publish_wechat.py --mode create_draft --title "标题" --content "内容" --media-id "MEDIA_ID"
  
  # 使用自定义接口推送（新增）
  python publish_wechat.py --mode custom_api --title "标题" --content "HTML" --cover "封面URL" --tags "AI,工具"
  
  # 使用自定义接口推送（从JSON文件读取）
  python publish_wechat.py --mode custom_api --json-file "output.json"
  
接口地址：http://39.108.254.228:8002/publish-draft
        """
    )
    
    parser.add_argument("--mode", 
                       choices=['workflow', 'upload_cover', 'create_draft', 'custom_api'],
                       default='workflow',
                       help="运行模式：workflow-完整工作流, upload_cover-上传封面, create_draft-创建草稿, custom_api-自定义接口推送")
    
    parser.add_argument("--title", help="文章标题")
    parser.add_argument("--content", help="文章内容（HTML格式）")
    parser.add_argument("--cover", help="封面图片路径（本地文件或URL）")
    parser.add_argument("--media-id", help="已有封面图素材ID（仅create_draft模式）")
    parser.add_argument("--author", help="作者名称")
    parser.add_argument("--digest", help="文章摘要")
    parser.add_argument("--no-cover", action='store_true',
                       help="不显示封面图")
    parser.add_argument("--tags", help="标签数组（逗号分隔，如：AI,工具,效率）")
    parser.add_argument("--json-file", help="从JSON文件读取数据（custom_api模式）")
    parser.add_argument("--api-url",
                       default=None,
                       help="自定义接口URL（默认从环境变量 WECHAT_PUBLISH_API_URL 读取）")
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'custom_api':
            # 自定义接口模式
            if args.json_file:
                # 从JSON文件读取
                with open(args.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                title = data.get('title', '')
                content = data.get('content', '')
                cover_url = data.get('cover_url', '')
                tags = data.get('tags', [])
            else:
                # 从命令行参数读取
                if not args.title or not args.content or not args.cover:
                    parser.error("custom_api模式需要 --title, --content, --cover 参数")
                title = args.title
                content = args.content
                cover_url = args.cover
                tags = args.tags.split(',') if args.tags else []
            
            result = publish_to_custom_api(
                title=title,
                content=content,
                cover_url=cover_url,
                tags=tags,
                api_url=args.api_url
            )
            
            print("\n" + "="*50)
            print("✅ 推送成功！")
            print("="*50)
            print(f"标题: {title}")
            print(f"标签: {tags}")
            print("="*50)
            
            print("\nJSON输出:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            return 0
        
        # 其他模式需要access_token
        print("正在获取微信公众号凭证...")
        access_token = get_access_token()
        print("✓ 凭证获取成功")
        
        if args.mode == 'workflow':
            # 完整工作流
            if not args.title or not args.content or not args.cover:
                parser.error("workflow模式需要 --title, --content, --cover 参数")
            
            print(f"\n正在执行完整工作流...")
            print(f"标题: {args.title}")
            print(f"内容长度: {len(args.content)} 字符")
            print(f"封面: {args.cover}")
            
            result = complete_workflow(
                access_token=access_token,
                title=args.title,
                content=args.content,
                cover_image_path=args.cover,
                author=args.author,
                digest=args.digest
            )
        
        elif args.mode == 'upload_cover':
            # 仅上传封面
            if not args.cover:
                parser.error("upload_cover模式需要 --cover 参数")
            
            print(f"\n正在上传封面图片...")
            print(f"图片: {args.cover}")
            
            result = upload_thumb_media(access_token, args.cover)
            print(f"\n✅ 封面上传成功！")
            print(f"media_id: {result['media_id']}")
            
            return 0
        
        elif args.mode == 'create_draft':
            # 仅创建草稿
            if not args.title or not args.content or not args.media_id:
                parser.error("create_draft模式需要 --title, --content, --media-id 参数")
            
            print(f"\n正在创建草稿...")
            print(f"标题: {args.title}")
            print(f"内容长度: {len(args.content)} 字符")
            print(f"封面media_id: {args.media_id}")
            
            result = create_draft(
                access_token=access_token,
                title=args.title,
                content=args.content,
                thumb_media_id=args.media_id,
                author=args.author,
                digest=args.digest
            )
        
        # 输出结果
        print("\n" + "="*50)
        print("✅ 操作成功！")
        print("="*50)
        
        if args.mode == 'workflow':
            print(f"封面media_id: {result['cover_media_id']}")
            print(f"草稿media_id: {result['draft_media_id']}")
        elif args.mode == 'upload_cover':
            print(f"封面media_id: {result['media_id']}")
        elif args.mode == 'create_draft':
            print(f"草稿media_id: {result['media_id']}")
        
        print("\n请登录微信公众号后台的「草稿箱」查看")
        print(f"访问地址: https://mp.weixin.qq.com")
        print("="*50)
        
        print("\nJSON输出:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}", file=sys.stderr)
        
        # 错误提示
        if "40164" in str(e):
            print("\n💡 解决方案：", file=sys.stderr)
            print("请将服务器IP地址添加到微信公众号白名单", file=sys.stderr)
            print("步骤：公众号后台 → 设置与开发 → 基本配置 → IP白名单", file=sys.stderr)
        elif "40001" in str(e):
            print("\n💡 解决方案：", file=sys.stderr)
            print("AppID或AppSecret配置错误，请检查凭证配置", file=sys.stderr)
        elif "40004" in str(e) or "40007" in str(e):
            print("\n💡 解决方案：", file=sys.stderr)
            print("封面图素材ID无效，请检查media_id是否正确", file=sys.stderr)
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

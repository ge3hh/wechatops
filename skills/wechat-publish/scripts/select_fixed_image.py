#!/usr/bin/env python3
"""
选择固定图片

根据文章主题自动选择合适的固定图片
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List


def load_image_map() -> Dict:
    """加载图片映射配置"""
    map_file = Path("agents/assets/image_map.json")
    
    if not map_file.exists():
        # 返回默认配置
        return {
            "covers": {},
            "illustrations": {},
            "mapping_rules": {}
        }
    
    try:
        with open(map_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"图片映射文件不存在: {map_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"图片映射文件格式错误: {e}")
    except UnicodeDecodeError as e:
        raise ValueError(f"图片映射文件编码错误，请使用UTF-8编码: {e}")


def select_cover(topic: str, keyword: str = "") -> Dict:
    """
    根据主题选择封面图
    
    Args:
        topic: 文章主题/话题
        keyword: 关键词
    
    Returns:
        封面图信息
    """
    image_map = load_image_map()
    mapping_rules = image_map.get("mapping_rules", {})
    covers = image_map.get("covers", {})
    
    # 搜索匹配的规则
    matched_keys = []
    search_text = (topic + " " + keyword).lower()
    
    for rule_key, cover_keys in mapping_rules.items():
        if rule_key.lower() in search_text:
            matched_keys.extend(cover_keys)
    
    # 去重并保持顺序
    matched_keys = list(dict.fromkeys(matched_keys))
    
    # 如果没有匹配，使用 default
    if not matched_keys:
        matched_keys = ["default"]
    
    # 获取第一个可用的封面
    for key in matched_keys:
        if key in covers:
            return covers[key]
    
    # 如果都没有，返回第一个可用的封面
    if covers:
        return list(covers.values())[0]
    
    # 如果都没有配置，返回空
    return {
        "path": "",
        "description": "未找到合适的封面图",
        "usage": "请添加封面图片到 agents/assets/covers/"
    }


def select_illustrations(count: int = 3) -> List[Dict]:
    """
    选择内文插图
    
    Args:
        count: 需要的插图数量
    
    Returns:
        插图列表
    """
    image_map = load_image_map()
    illustrations = image_map.get("illustrations", {})
    
    # 按顺序选择
    result = []
    for key, info in list(illustrations.items())[:count]:
        result.append({
            "key": key,
            **info
        })
    
    return result


def list_available_images():
    """列出所有可用的图片"""
    image_map = load_image_map()
    
    print("=" * 60)
    print("可用封面图")
    print("=" * 60)
    
    covers = image_map.get("covers", {})
    if covers:
        for key, info in covers.items():
            print(f"\n[{key}]")
            print(f"  路径: {info.get('path', 'N/A')}")
            print(f"  描述: {info.get('description', 'N/A')}")
            print(f"  用途: {info.get('usage', 'N/A')}")
    else:
        print("\n暂无封面图")
        print("请添加图片到: agents/assets/covers/")
    
    print("\n" + "=" * 60)
    print("可用插图")
    print("=" * 60)
    
    illustrations = image_map.get("illustrations", {})
    if illustrations:
        for key, info in illustrations.items():
            print(f"\n[{key}]")
            print(f"  路径: {info.get('path', 'N/A')}")
            print(f"  描述: {info.get('description', 'N/A')}")
            print(f"  用途: {info.get('usage', 'N/A')}")
    else:
        print("\n暂无插图")
        print("请添加图片到: agents/assets/illustrations/")
    
    print("\n" + "=" * 60)
    print("\n映射规则")
    print("=" * 60)
    
    rules = image_map.get("mapping_rules", {})
    if rules:
        for keyword, cover_keys in rules.items():
            print(f"\n{keyword} -> {', '.join(cover_keys)}")
    else:
        print("\n暂无映射规则")


def main():
    parser = argparse.ArgumentParser(description='选择固定图片')
    parser.add_argument('--topic', help='文章主题')
    parser.add_argument('--keyword', default='', help='关键词')
    parser.add_argument('--cover', action='store_true', help='选择封面图')
    parser.add_argument('--illustrations', type=int, help='选择内文插图数量')
    parser.add_argument('--list', action='store_true', help='列出所有可用图片')
    
    args = parser.parse_args()
    
    if args.list:
        list_available_images()
        return 0
    
    if args.cover:
        if not args.topic:
            print("错误：选择封面图需要提供 --topic 参数")
            return 1
        
        cover = select_cover(args.topic, args.keyword)
        print(json.dumps(cover, ensure_ascii=False, indent=2))
        return 0
    
    if args.illustrations:
        illustrations = select_illustrations(args.illustrations)
        print(json.dumps(illustrations, ensure_ascii=False, indent=2))
        return 0
    
    # 默认：显示帮助
    parser.print_help()
    return 0


if __name__ == '__main__':
    exit(main())

#!/usr/bin/env python3
"""
保存文章到本地

功能：
1. 保存文章到 output/YYYY-MM-DD/ 目录
2. 生成 HTML、Markdown、元数据
3. 更新历史记录
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path


def sanitize_filename(title: str) -> str:
    """将标题转换为安全的文件名"""
    # 移除或替换不安全字符
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    safe = safe.strip()[:30]  # 限制长度
    return safe.replace(' ', '_')


def save_article(title: str, content: str, cover: str = "", tags: str = "", 
                 topic: str = "", score: float = 0, output_dir: str = "./output"):
    """保存文章到指定目录"""
    
    # 创建日期目录
    today = datetime.now().strftime("%Y-%m-%d")
    article_dir = Path(output_dir) / today
    article_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    safe_title = sanitize_filename(title)
    base_name = f"{today}_{safe_title}"
    
    # 保存 HTML 版本（可直接复制到公众号）
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.8; }}
        h1 {{ font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
        h2 {{ font-size: 20px; font-weight: bold; margin-top: 30px; margin-bottom: 15px; }}
        h3 {{ font-size: 18px; font-weight: bold; margin-top: 25px; margin-bottom: 10px; }}
        p {{ margin-bottom: 15px; }}
        img {{ max-width: 100%; height: auto; display: block; margin: 20px 0; }}
        .highlight {{ background-color: #fff3cd; padding: 2px 4px; border-radius: 3px; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    html_path = article_dir / f"{base_name}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 保存纯 HTML（无样式，适合直接粘贴）
    pure_html_path = article_dir / f"{base_name}_pure.html"
    with open(pure_html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 保存 Markdown 版本
    md_content = convert_html_to_markdown(content)
    md_path = article_dir / f"{base_name}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"> 封面图: {cover}\n\n")
        f.write(md_content)
    
    # 保存元数据
    metadata = {
        "title": title,
        "topic": topic,
        "tags": tags.split(',') if tags else [],
        "cover": cover,
        "create_time": datetime.now().isoformat(),
        "publish_time": None,
        "score": score,
        "word_count": len(content),
        "status": "draft",
        "files": {
            "html": str(html_path),
            "pure_html": str(pure_html_path),
            "markdown": str(md_path)
        }
    }
    
    meta_path = article_dir / f"{base_name}_metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 更新历史记录
    update_history(title, topic, score, tags, str(html_path))
    
    print(f"✅ 文章已保存到: {article_dir}")
    print(f"   - 完整HTML: {html_path}")
    print(f"   - 纯HTML（适合粘贴）: {pure_html_path}")
    print(f"   - Markdown: {md_path}")
    print(f"   - 元数据: {meta_path}")
    
    return article_dir


def convert_html_to_markdown(html_content: str) -> str:
    """简单转换HTML到Markdown"""
    # 移除script和style
    import re
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    
    # 转换标题
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n\n', text, flags=re.DOTALL)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n\n', text, flags=re.DOTALL)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n\n', text, flags=re.DOTALL)
    
    # 转换段落
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text, flags=re.DOTALL)
    
    # 转换加粗
    text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    text = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', text, flags=re.DOTALL)
    
    # 转换图片
    text = re.sub(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', r'\n![图片](\1)\n', text)
    
    # 移除其他标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 解码HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    
    return text.strip()


def update_history(title: str, topic: str, score: float, tags: str, file_path: str):
    """更新历史记录"""
    history_file = Path("agents/memory/history/articles.json")
    
    if history_file.exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {"articles": [], "stats": {}}
    
    article_record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": title,
        "topic": topic,
        "tags": tags.split(',') if tags else [],
        "score": score,
        "file_path": file_path,
        "status": "draft"
    }
    
    history["articles"].append(article_record)
    
    # 更新统计
    scores = [a["score"] for a in history["articles"] if a.get("score")]
    history["stats"] = {
        "total_count": len(history["articles"]),
        "avg_score": round(sum(scores) / len(scores), 2) if scores else 0
    }
    
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='保存文章到本地')
    parser.add_argument('--title', required=True, help='文章标题')
    parser.add_argument('--content', required=True, help='文章内容（HTML格式）')
    parser.add_argument('--cover', default='', help='封面图片URL')
    parser.add_argument('--tags', default='', help='标签（逗号分隔）')
    parser.add_argument('--topic', default='', help='话题')
    parser.add_argument('--score', type=float, default=0, help='评分')
    parser.add_argument('--output-dir', default='./output', help='输出目录')
    
    args = parser.parse_args()
    
    save_article(args.title, args.content, args.cover, args.tags, 
                 args.topic, args.score, args.output_dir)


if __name__ == '__main__':
    main()

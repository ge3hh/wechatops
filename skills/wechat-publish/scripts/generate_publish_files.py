#!/usr/bin/env python3
"""
生成完整的发布文件包
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def generate_publish_files(input_file: str, output_dir: str):
    """生成发布所需的所有文件"""
    
    input_path = Path(input_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 读取输入文件
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成公众号格式
    wechat_content = convert_to_wechat_format(content)
    wechat_path = output_path / "article_wechat.md"
    with open(wechat_path, 'w', encoding='utf-8') as f:
        f.write(wechat_content)
    
    # 生成封面图设计方案
    cover_design = generate_cover_design_guide()
    cover_path = output_path / "cover_design.md"
    with open(cover_path, 'w', encoding='utf-8') as f:
        f.write(cover_design)
    
    # 生成发布指引
    guide = generate_publish_guide()
    guide_path = output_path / "publish_guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    # 生成 manifest
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "files": {
            "article": str(wechat_path),
            "cover_design": str(cover_path),
            "guide": str(guide_path)
        }
    }
    manifest_path = output_path / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 发布文件已生成: {output_path}")
    print(f"   - 公众号文章: {wechat_path}")
    print(f"   - 封面设计: {cover_path}")
    print(f"   - 发布指引: {guide_path}")


def convert_to_wechat_format(content: str) -> str:
    """转换为微信公众号格式"""
    lines = content.split('\n')
    result = []
    
    for line in lines:
        # 处理标题层级
        if line.startswith('# '):
            line = f"## {line[2:]}"
        elif line.startswith('## '):
            line = f"### {line[3:]}"
        elif line.startswith('### '):
            line = f"#### {line[4:]}"
        
        result.append(line)
        
        # 段落间添加空行
        if line.strip() and not line.startswith(('#', '>', '-', '*', '1.', '2.', '3.')):
            result.append('')
    
    # 添加结尾引导
    result.append('')
    result.append('---')
    result.append('')
    result.append('*本文仅代表作者观点*')
    result.append('')
    result.append('**觉得有收获？点个「在看」👇**')
    
    return '\n'.join(result)


def generate_cover_design_guide() -> str:
    """生成封面图设计指南"""
    return '''# 封面图设计指南

## 规格要求
- **尺寸**: 900 × 383 px (16:9)
- **格式**: JPG 或 PNG
- **大小**: 不超过 5MB

## 设计要点
1. **安全区**: 重要元素放在中间 500×383 区域
2. **文字**: 标题清晰可读，不超过 15 个字
3. **配色**: 与文章调性一致

## 推荐工具
- Canva: 在线设计，有公众号模板
- 创客贴: 中文模板丰富
- Midjourney/DALL-E: AI 生成背景图

## AI 绘画 Prompt 模板
```
A professional cover image for WeChat article, 
[主题描述], clean modern style, 
minimalist design, subtle gradients, 
900x383 aspect ratio, high quality
```
'''


def generate_publish_guide() -> str:
    """生成发布指引"""
    return '''# 微信公众号发布指引

## 步骤 1: 复制内容
1. 打开 `article_wechat.md`
2. 全选复制内容

## 步骤 2: 登录公众号
1. 访问 mp.weixin.qq.com
2. 扫码登录

## 步骤 3: 新建图文
1. 点击"图文消息"
2. 粘贴内容到正文

## 步骤 4: 设置封面
1. 参考 `cover_design.md` 制作封面
2. 上传封面图片
3. 编辑摘要

## 步骤 5: 预览检查
1. 点击"预览"
2. 发送到手机查看效果
3. 检查排版、错别字

## 步骤 6: 发布
1. 确认无误后保存
2. 选择"群发"或"定时发送"
'''


def main():
    parser = argparse.ArgumentParser(description='生成发布文件')
    parser.add_argument('--input', '-i', required=True, help='输入文章文件')
    parser.add_argument('--output', '-o', default='./publish_ready', help='输出目录')
    
    args = parser.parse_args()
    
    generate_publish_files(args.input, args.output)


if __name__ == '__main__':
    main()

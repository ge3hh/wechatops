#!/usr/bin/env python3
"""
自动发布流程控制器

功能：定时抓取订阅源 → 生成内容 → 自动发布
"""

import sys
import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


class AutoPublisher:
    """自动发布流程控制器"""
    
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.skill_dir = Path(__file__).parent.parent
    
    def _load_config(self, config_path: str) -> dict:
        """加载自动发布配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def fetch_sources(self) -> str:
        """步骤1：抓取订阅源"""
        print("\n" + "="*50)
        print("步骤 1: 抓取订阅源")
        print("="*50)

        sources_config = self.config.get('sources_config')
        sources = self.config.get('sources', ['zhihu'])
        keywords = self.config.get('keywords', [])
        count = self.config.get('fetch_count', 5)

        # 验证 sources 参数，防止命令注入
        valid_sources = {'zhihu', 'weibo', 'rss'}
        invalid_sources = set(sources) - valid_sources
        if invalid_sources:
            raise ValueError(f"无效的订阅源: {invalid_sources}，必须是 {valid_sources} 的子集")

        cmd = [
            sys.executable,
            str(self.skill_dir / 'scripts' / 'fetch_sources.py'),
            '--sources'
        ]
        cmd.extend(sources)
        cmd.extend(['--count', str(count)])

        if keywords:
            cmd.append('--keywords')
            cmd.extend(keywords)

        if sources_config:
            # 验证配置文件路径存在
            if not os.path.exists(sources_config):
                raise FileNotFoundError(f"配置文件不存在: {sources_config}")
            cmd.extend(['--config', sources_config])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"抓取订阅源失败: {result.stderr}")

        output_file = 'output/sources.json'
        print(f"✅ 订阅源已抓取到: {output_file}")

        return output_file
    
    def generate_content(self, sources_file: str) -> dict:
        """步骤2：生成内容（调用智能体）"""
        print("\n" + "="*50)
        print("步骤 2: 生成内容")
        print("="*50)
        
        # 读取订阅源内容
        with open(sources_file, 'r', encoding='utf-8') as f:
            sources_data = json.load(f)
        
        items = sources_data.get('items', [])
        
        if not items:
            raise Exception("没有可用的订阅源内容")
        
        # 选择最佳内容（第一条）
        selected_item = items[0]
        
        print(f"选择内容: {selected_item.get('title', '')}")
        print(f"来源: {selected_item.get('source', '')}")
        
        # 这里应该调用智能体生成内容
        # 由于智能体集成需要通过SKILL调用，这里返回提示信息
        print("\n⚠️  内容生成需要智能体参与")
        print("请在SKILL中使用以下信息生成内容：")
        print(f"- 标题: {selected_item.get('title', '')}")
        print(f"- 原文链接: {selected_item.get('link', '')}")
        print(f"- 摘要: {selected_item.get('summary', '')}")
        print(f"- 来源: {selected_item.get('source', '')}")
        
        # 返回待发布的内容信息
        return {
            'original_item': selected_item,
            'status': 'pending_generation'
        }
    
    def publish_content(self, content_info: dict) -> dict:
        """步骤3：发布内容"""
        print("\n" + "="*50)
        print("步骤 3: 发布内容")
        print("="*50)
        
        platforms = self.config.get('platforms', [])
        publish_results = {}
        
        for platform in platforms:
            print(f"\n正在发布到 {platform}...")
            
            try:
                # 调用对应的发布脚本
                if platform == 'wechat':
                    # 这里需要实际的内容参数
                    print(f"  {platform}: 需要提供实际内容")
                    publish_results[platform] = {
                        'success': False,
                        'message': '需要智能体生成内容后才能发布'
                    }
                elif platform == 'xiaohongshu':
                    print(f"  {platform}: 需要提供实际内容")
                    publish_results[platform] = {
                        'success': False,
                        'message': '需要智能体生成内容后才能发布'
                    }
                elif platform == 'bilibili':
                    print(f"  {platform}: 需要提供实际内容")
                    publish_results[platform] = {
                        'success': False,
                        'message': '需要智能体生成内容后才能发布'
                    }
            except Exception as e:
                print(f"  发布失败: {str(e)}")
                publish_results[platform] = {
                    'success': False,
                    'message': str(e)
                }
        
        return publish_results
    
    def run(self):
        """执行完整流程"""
        print("\n" + "="*50)
        print("自动发布流程启动")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        try:
            # 步骤1：抓取订阅源
            sources_file = self.fetch_sources()
            
            # 步骤2：生成内容
            content_info = self.generate_content(sources_file)
            
            # 步骤3：发布内容（如果有内容）
            if content_info.get('status') == 'pending_generation':
                print("\n" + "="*50)
                print("📝 自动化流程说明")
                print("="*50)
                print("\n由于内容生成需要智能体参与，完整流程为：")
                print("1. ✅ 已完成：抓取订阅源")
                print("2. ⏳ 待执行：智能体生成原创内容")
                print("3. ⏳ 待执行：发布到配置的平台")
                print("\n请根据上方提供的热点信息，在SKILL中：")
                print("1. 智能体生成适配各平台的原创内容")
                print("2. 调用对应平台的发布脚本")
                print("3. 完成自动化发布")
            else:
                # 如果有生成的内容，直接发布
                results = self.publish_content(content_info)
                
                # 输出结果
                print("\n" + "="*50)
                print("发布结果")
                print("="*50)
                for platform, result in results.items():
                    status = "✅ 成功" if result['success'] else "❌ 失败"
                    print(f"{platform}: {status}")
                    if not result['success']:
                        print(f"  原因: {result['message']}")
            
            print("\n✅ 自动化流程完成！")
            return 0
            
        except Exception as e:
            print(f"\n❌ 自动化流程失败: {str(e)}", file=sys.stderr)
            return 1


def main():
    parser = argparse.ArgumentParser(description="自动发布流程控制器")
    
    parser.add_argument("--config", 
                       default="config/auto_publish.json",
                       help="自动发布配置文件路径")
    parser.add_argument("--mode", 
                       choices=['once', 'continuous'],
                       default='once',
                       help="运行模式：once-执行一次，continuous-持续运行")
    parser.add_argument("--interval", 
                       type=int, 
                       default=3600,
                       help="持续运行时的间隔时间（秒，默认3600）")
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'once':
            # 执行一次
            publisher = AutoPublisher(args.config)
            sys.exit(publisher.run())
        
        elif args.mode == 'continuous':
            # 持续运行
            print(f"持续运行模式，间隔: {args.interval} 秒")
            print("按 Ctrl+C 停止\n")
            
            try:
                while True:
                    publisher = AutoPublisher(args.config)
                    publisher.run()
                    
                    print(f"\n等待 {args.interval} 秒后继续...")
                    import time
                    time.sleep(args.interval)
                    
            except KeyboardInterrupt:
                print("\n\n停止自动化流程")
                sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ 启动失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

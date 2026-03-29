#!/usr/bin/env python3
"""
检查环境变量配置

用于验证微信公众号 API 凭证是否已配置
"""

import os
import sys


def check_config():
    """检查环境变量配置"""

    skill_id = "7597373721971540014"

    # 检查所有可能的凭证来源
    coze_token = os.getenv(f'COZE_WECHAT_OFFICIAL_ACCOUNT_{skill_id}')
    appid = os.getenv('WECHAT_APPID')
    appsecret = os.getenv('WECHAT_APPSECRET')

    print("=" * 50)
    print("微信公众号 API 配置检查")
    print("=" * 50)
    print()

    has_coze_token = bool(coze_token)
    has_appid_secret = bool(appid and appsecret)

    if has_coze_token or has_appid_secret:
        print("✅ 环境变量已配置")

        if has_coze_token:
            print(f"   方式1 - Coze平台凭证: {'*' * 8} (已设置)")

        if has_appid_secret:
            print(f"   方式2 - AppID+AppSecret: {appid}")
            print(f"   WECHAT_APPSECRET: {'*' * 8} (已设置)")

        print()
        print("可以直接使用官方 API 发布到微信公众号草稿箱")
        return True
    else:
        print("❌ 环境变量未配置")
        print()
        print("需要设置以下环境变量之一：")
        print()
        print(f"方式1（Coze平台）:")
        print(f"   COZE_WECHAT_OFFICIAL_ACCOUNT_{skill_id}=your-token")
        print()
        print("方式2（标准方式）:")
        print("   WECHAT_APPID=your-appid")
        print("   WECHAT_APPSECRET=your-appsecret")
        print()
        print("配置方式：")
        print()
        print("Windows:")
        print("   set WECHAT_APPID=your-appid")
        print("   set WECHAT_APPSECRET=your-appsecret")
        print()
        print("Linux/Mac:")
        print("   export WECHAT_APPID=\"your-appid\"")
        print("   export WECHAT_APPSECRET=\"your-appsecret\"")
        print()
        print("获取方式：登录公众号后台 → 设置与开发 → 基本配置")
        print()
        return False


def main():
    result = check_config()
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()

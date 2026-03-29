#!/bin/bash

# 微信公众号内容创作 Agent - 环境配置脚本
# 使用方法：source setup.sh

echo "=========================================="
echo "  微信公众号内容创作 Agent - 环境配置"
echo "=========================================="
echo ""

# 检查是否已经配置
if [ -n "$WECHAT_APPID" ] && [ -n "$WECHAT_APPSECRET" ]; then
    echo "[信息] 环境变量已配置："
    echo "  WECHAT_APPID=$WECHAT_APPID"
    echo "  WECHAT_APPSECRET=***（已隐藏）"
    echo ""
    read -p "是否重新配置？(y/n): " REPLY
    if [ "$REPLY" != "y" ]; then
        echo "取消配置"
        return 0
    fi
fi

echo "请提供微信公众号凭证："
echo "（获取方式：公众号后台 → 设置与开发 → 基本配置）"
echo ""

read -p "请输入 WECHAT_APPID: " APPID
read -sp "请输入 WECHAT_APPSECRET: " APPSECRET
echo ""

echo ""
echo "正在配置环境变量..."

# 添加到 ~/.bashrc 或 ~/.zshrc
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [ -n "$SHELL_CONFIG" ]; then
    # 删除旧的配置
    sed -i '/# wechat-publish-env/d' "$SHELL_CONFIG" 2>/dev/null
    sed -i '/WECHAT_APPID/d' "$SHELL_CONFIG" 2>/dev/null
    sed -i '/WECHAT_APPSECRET/d' "$SHELL_CONFIG" 2>/dev/null
    
    # 添加新的配置
    echo "" >> "$SHELL_CONFIG"
    echo "# wechat-publish-env" >> "$SHELL_CONFIG"
    echo "export WECHAT_APPID=\"$APPID\"" >> "$SHELL_CONFIG"
    echo "export WECHAT_APPSECRET=\"$APPSECRET\"" >> "$SHELL_CONFIG"
    
    echo "[OK] 环境变量已添加到 $SHELL_CONFIG"
    echo ""
    echo "已配置的变量："
    echo "  WECHAT_APPID=$APPID"
    echo "  WECHAT_APPSECRET=***（已隐藏）"
    echo ""
    echo "请运行以下命令使配置生效："
    echo "  source $SHELL_CONFIG"
else
    echo "[警告] 无法确定 shell 配置文件，请手动配置"
    echo ""
    echo "手动添加以下内容到 ~/.bashrc 或 ~/.zshrc："
    echo "export WECHAT_APPID=\"$APPID\""
    echo "export WECHAT_APPSECRET=\"$APPSECRET\""
fi

echo ""

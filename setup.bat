@echo off
chcp 65001 >nul
echo ==========================================
echo   微信公众号内容创作 Agent - 环境配置
echo ==========================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] 以管理员身份运行
) else (
    echo [警告] 建议以管理员身份运行此脚本，以便设置系统环境变量
    echo.
    pause
)

echo.
echo 请提供微信公众号凭证：
echo （获取方式：公众号后台 → 设置与开发 → 基本配置）
echo.

set /p APPID=请输入 WECHAT_APPID: 
set /p APPSECRET=请输入 WECHAT_APPSECRET: 

echo.
echo 正在配置环境变量...

REM 设置用户环境变量
setx WECHAT_APPID "%APPID%" >nul 2>&1
setx WECHAT_APPSECRET "%APPSECRET%" >nul 2>&1

if %errorLevel% == 0 (
    echo [OK] 环境变量配置成功！
    echo.
    echo 已配置的变量：
    echo   WECHAT_APPID=%APPID%
    echo   WECHAT_APPSECRET=***（已隐藏）
    echo.
    echo 请重启命令行窗口或重启 Kimi CLI 使配置生效
) else (
    echo [错误] 环境变量配置失败，请手动配置
    echo.
    echo 手动配置方式：
    echo 1. 打开系统设置 → 系统 → 关于 → 高级系统设置
    echo 2. 环境变量 → 用户变量 → 新建
    echo 3. 添加 WECHAT_APPID 和 WECHAT_APPSECRET
)

echo.
pause

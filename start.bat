@echo off
chcp 65001 >nul
echo ==========================================
echo   Content Director - 公众号内容创作 Agent
echo ==========================================
echo.
echo 正在启动...
echo.

kimi --agent-file agent.yaml

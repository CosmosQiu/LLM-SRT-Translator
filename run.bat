@echo off
chcp 65001
setlocal enabledelayedexpansion

echo ===================================
echo 人工智能字幕处理系统启动工具
echo ===================================

:: 检查虚拟环境是否存在
if not exist ".venv\Scripts\activate.bat" (
    echo 虚拟环境不存在，正在创建...
    python -m venv .venv
    if !errorlevel! neq 0 (
        echo Python虚拟环境创建失败！
        echo 请确保已安装Python 3.11
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功！
) else (
    echo 检测到已有虚拟环境
)

:: 激活虚拟环境
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 虚拟环境激活失败！
    pause
    exit /b 1
)
echo 虚拟环境已激活

:: 安装依赖
if exist "requirements.txt" (
    echo 正在安装依赖包...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if !errorlevel! neq 0 (
        echo 依赖包安装失败！
        pause
        exit /b 1
    )
    echo 依赖包安装完成！
) else (
    echo 警告：未找到requirements.txt文件，跳过依赖安装
)

:: 输入字幕文件路径
:input_path
echo.
set /p subtitle_path="请输入待处理的字幕文件路径: "

:: 处理路径中的引号和反斜杠
set "subtitle_path=%subtitle_path:"=%"
set "subtitle_path=%subtitle_path:\=/%"

:: 检查路径是否存在
if not exist "%subtitle_path%" (
    echo 错误：指定的文件不存在！
    goto input_path
)

:: 检查文件扩展名
set "file_ext=%subtitle_path:~-4%"
if not "%file_ext%"==".srt" if not "%file_ext%"==".txt" (
    echo 错误：请确保输入的是.srt或.txt格式的字幕文件！
    goto input_path
)

:: 使用DeepSeek处理字幕
echo.
echo 正在使用DeepSeek处理字幕文件...
python models/deepseek_api_srt.py "!subtitle_path!"
if !errorlevel! neq 0 (
    echo DeepSeek处理失败！
    pause
    exit /b 1
)

echo.
echo ===================================
echo 处理完成！
echo ===================================

pause

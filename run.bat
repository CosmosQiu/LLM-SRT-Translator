@echo off
setlocal enabledelayedexpansion

echo ===================================
echo 人工智能字幕处理系统启动工具
echo ===================================

:: 检查虚拟环境是否存在
if not exist "venv\" (
    echo 虚拟环境不存在，正在创建...
    python -m venv venv
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

:: 根据文件类型处理
if "%file_ext%"==".srt" (
    :: 创建临时文件
    set "temp_txt=%subtitle_path:~0,-4%.txt"
    echo 正在创建临时文件: %temp_txt%
    copy "%subtitle_path%" "%temp_txt%" >nul
    set "input_file=%temp_txt%"
) else (
    set "input_file=%subtitle_path%"
)

:: 使用DeepSeek处理字幕
echo.
echo 正在使用DeepSeek处理字幕文件...
python models/deepseek_api_srt.py "%input_file%"
if !errorlevel! neq 0 (
    echo DeepSeek处理失败！
    if "%file_ext%"==".srt" del "%temp_txt%"
    pause
    exit /b 1
)

:: 获取最新的处理结果目录
for /f "delims=" %%i in ('dir /b /ad /o-d "opt"') do (
    set "latest_dir=%%i"
    goto :found_dir
)
:found_dir

:: 格式化处理结果
echo.
echo 正在格式化处理结果...
python utils/format.py
if !errorlevel! neq 0 (
    echo 格式化处理失败！
    if "%file_ext%"==".srt" del "%temp_txt%"
    pause
    exit /b 1
)

:: 重命名最终文件
set "final_srt=%subtitle_path:~0,-4%_processed.srt"
set "formatted_txt=opt\%latest_dir%\formatted_subtitle_%latest_dir%.txt"
echo 正在生成最终字幕文件: %final_srt%
copy "%formatted_txt%" "%final_srt%" >nul

:: 清理临时文件
echo 正在清理临时文件...
if "%file_ext%"==".srt" del "%temp_txt%"

echo.
echo ===================================
echo 处理完成！
echo 最终字幕文件保存在: %final_srt%
echo ===================================

pause

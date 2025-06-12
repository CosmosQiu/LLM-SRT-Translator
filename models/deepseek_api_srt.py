import os
import pandas as pd
from openai import OpenAI
import datetime
import pathlib
import sys
import re
import yaml
import shutil
import chardet

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        sys.exit(1)

def normalize_path(file_path):
    """标准化文件路径"""
    # 移除可能的引号
    file_path = file_path.strip('"\'')
    # 转换为绝对路径
    abs_path = os.path.abspath(file_path)
    print(f"原始路径: {file_path}")
    print(f"绝对路径: {abs_path}")
    return abs_path

def get_timestamp():
    """获取当前时间戳"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_output_filename(input_file):
    """生成输出文件名"""
    # 获取原始文件名（不含路径和扩展名）
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    # 生成时间戳
    timestamp = get_timestamp()
    # 组合新的文件名
    return f"{timestamp}_{base_name}"

def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        print(f"检测到文件编码: {encoding}")
        return encoding

def convert_srt_to_txt(srt_file):
    """将SRT文件转换为TXT文件"""
    txt_file = os.path.splitext(srt_file)[0] + '.txt'
    try:
        # 检测源文件编码
        encoding = detect_encoding(srt_file)
        # 读取源文件
        with open(srt_file, 'r', encoding=encoding) as f:
            content = f.read()
        # 写入新文件（使用UTF-8编码）
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建临时文件: {txt_file}")
        return txt_file
    except Exception as e:
        print(f"创建临时文件失败: {e}")
        raise

def split_subtitle_file(file_path, chunk_size=100):
    """将字幕文件按序号每100句拆分为一段"""
    file_path = normalize_path(file_path)
    print(f"正在读取文件: {file_path}")
    print(f"文件是否存在: {os.path.exists(file_path)}")
    
    try:
        # 检测文件编码
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
    except Exception as e:
        print(f"读取文件失败: {e}")
        raise
    
    # 使用正则表达式匹配字幕序号和内容
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    # 将匹配结果转换为列表
    subtitles = []
    for match in matches:
        number = int(match.group(1))
        timestamp = match.group(2)
        text = match.group(3).strip()
        subtitles.append({
            'number': number,
            'timestamp': timestamp,
            'text': text
        })
    
    # 按chunk_size分组
    chunks = []
    current_chunk = []
    
    for subtitle in subtitles:
        current_chunk.append(subtitle)
        if len(current_chunk) >= chunk_size:
            chunks.append(current_chunk)
            current_chunk = []
    
    if current_chunk:  # 添加最后一个不完整的chunk
        chunks.append(current_chunk)
    
    return chunks

def process_subtitle_with_deepseek(chunk):
    """处理字幕片段并调用API"""
    config = load_config()
    client = OpenAI(
        api_key=config['api']['deepseek']['api_key'],
        base_url=config['api']['deepseek']['base_url']
    )
    
    # 构建字幕文本
    subtitle_text = "\n".join([f"{s['number']}\n{s['timestamp']}\n{s['text']}" for s in chunk])
    
    prompt = """
    请翻译以下字幕内容到中文，以原始格式输出，不要添加任何解释，不要修改时间码的格式：
    字幕内容：
    """ + subtitle_text

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": subtitle_text},
        ],
        stream=False
    )
    
    return response.choices[0].message.content

def process_subtitle_file(input_file, output_file=None):
    """处理字幕文件"""
    try:
        # 获取时间戳
        timestamp = get_timestamp()
        
        # 创建输出目录
        output_dir = os.path.join("opt", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        if output_file is None:
            output_file = get_output_filename(input_file)
            output_file = os.path.join(output_dir, output_file)
        
        # 检查文件扩展名
        _, ext = os.path.splitext(input_file)
        if ext.lower() == '.srt':
            # 如果是SRT文件，先转换为TXT
            temp_txt = convert_srt_to_txt(input_file)
            input_file = temp_txt
            print(f"已将SRT文件转换为TXT: {temp_txt}")
        
        # 处理字幕文件
        print(f"正在处理文件: {input_file}")
        print(f"输出文件将保存为: {output_file}")
        
        # 分割文件
        chunks = split_subtitle_file(input_file)
        print(f"文件已分割为 {len(chunks)} 个部分")
        
        # 处理每个部分
        processed_chunks = []
        for i, chunk in enumerate(chunks, 1):
            print(f"正在处理第 {i}/{len(chunks)} 部分")
            processed_chunk = process_subtitle_with_deepseek(chunk)
            processed_chunks.append(processed_chunk)
        
        # 合并处理后的内容
        final_content = "\n\n".join(processed_chunks)
        
        # 保存处理后的内容
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"处理完成，结果已保存到: {output_file}")
        
        # 清理临时文件
        if ext.lower() == '.srt':
            try:
                os.remove(temp_txt)
                print(f"已删除临时文件: {temp_txt}")
            except Exception as e:
                print(f"删除临时文件时出错: {e}")
        
        return output_file
        
    except Exception as e:
        print(f"处理文件时出错: {e}")
        raise

# 示例调用
if __name__ == "__main__":
    # 检查是否有命令行参数传入
    if len(sys.argv) > 1:
        input_file = sys.argv[1]  # 从命令行参数获取字幕文件路径
        print(f"接收到的文件路径: {input_file}")
        input_file = normalize_path(input_file)
        print(f"标准化后的文件路径: {input_file}")
    else:
        print("错误：请提供字幕文件路径")
        sys.exit(1)
        
    print(f"处理字幕文件: {input_file}")
    output_file = process_subtitle_file(input_file)
    print(f"处理完成，结果保存在: {output_file}")
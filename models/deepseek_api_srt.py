import os
import pandas as pd
from openai import OpenAI
import datetime
import pathlib
import sys
import re
import yaml

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yml")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        sys.exit(1)

def split_subtitle_file(file_path, chunk_size=100):
    """将字幕文件按序号每100句拆分为一段"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
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
    """处理字幕文件并保存结果"""
    # 创建输出目录
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_file is None:
        output_dir = os.path.join(pathlib.Path(__file__).parent.parent, "opt", timestamp)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"subtitle_analysis_{timestamp}.txt")
    else:
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)
    
    # 读取并分割字幕文件
    chunks = split_subtitle_file(input_file)
    
    # 处理每个chunk并收集结果
    results = []
    for i, chunk in enumerate(chunks, 1):
        print(f"处理第 {i}/{len(chunks)} 段字幕...")
        try:
            result = process_subtitle_with_deepseek(chunk)
            # 直接添加结果，不添加分隔符
            results.append(result)
        except Exception as e:
            print(f"处理第 {i} 段时出错: {e}")
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(results))
    
    print(f"处理完成，结果已保存到: {output_file}")
    return output_file

# 示例调用
if __name__ == "__main__":
    # 检查是否有命令行参数传入
    if len(sys.argv) > 1:
        input_file = sys.argv[1]  # 从命令行参数获取字幕文件路径
    else:
        print("错误：请提供字幕文件路径")
        sys.exit(1)
        
    print(f"处理字幕文件: {input_file}")
    output_file = process_subtitle_file(input_file)
    print(f"处理完成，结果保存在: {output_file}")
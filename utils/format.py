import os
import re

def format_subtitle_text(input_file, output_file):
    """处理字幕文本格式，确保每个句子包含序号、时间码和台词，并用空行分隔"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在序号前添加空行，并确保时间码在同一行
    content = re.sub(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n', r'\n\1\n\2\n', content)
    
    # 移除多余的空行，确保每个句子之间只有一个空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 确保文件开头和结尾没有多余的空行
    content = content.strip()
    
    # 保存处理后的内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"处理完成，结果已保存到: {output_file}")

if __name__ == "__main__":
    # 获取最新的分析结果文件
    opt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "opt")
    latest_dir = max([d for d in os.listdir(opt_dir) if os.path.isdir(os.path.join(opt_dir, d))])
    
    input_file = os.path.join(opt_dir, latest_dir, f"subtitle_analysis_{latest_dir}.txt")
    output_file = os.path.join(opt_dir, latest_dir, f"formatted_subtitle_{latest_dir}.txt")
    
    format_subtitle_text(input_file, output_file) 
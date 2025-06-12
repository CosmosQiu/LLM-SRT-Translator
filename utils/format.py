import os
import re
import sys
from datetime import datetime

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

def main():
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("使用方法: python format.py <字幕文件路径>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在: {input_file}")
        sys.exit(1)
    
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 创建opt目录（如果不存在）
    opt_dir = os.path.join(root_dir, "opt")
    os.makedirs(opt_dir, exist_ok=True)
    
    # 生成输出文件名
    input_filename = os.path.basename(input_file)
    name_without_ext = os.path.splitext(input_filename)[0]
    output_filename = f"{name_without_ext}_formatted{os.path.splitext(input_filename)[1]}"
    output_file = os.path.join(opt_dir, output_filename)
    
    try:
        format_subtitle_text(input_file, output_file)
    except Exception as e:
        print(f"处理过程中出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
import os
import re
import shutil
import chardet
from pathlib import Path

def remove_chinese_punctuation(text):
    """移除中文标点符号，用空格替换，保持原有换行"""
    # 定义中文标点符号
    chinese_punctuation = r'[\u3000-\u303f\uff00-\uff0f\uff1a-\uff20\uff3b-\uff40\uff5b-\uff65]'
    
    # 按行处理，保持原有换行
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        # 替换中文标点符号为空格
        processed_line = re.sub(chinese_punctuation, ' ', line)
        # 将多个连续空格替换为单个空格
        processed_line = re.sub(r'\s+', ' ', processed_line)
        processed_lines.append(processed_line.strip())
    
    # 重新组合文本，保持原有换行
    return '\n'.join(processed_lines)

def process_file(input_file, output_file):
    """处理单个文件"""
    try:
        # 检测文件编码
        with open(input_file, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        
        # 读取文件内容
        with open(input_file, 'r', encoding=encoding) as f:
            content = f.read()
        
        # 处理字幕内容
        # 使用正则表达式匹配字幕序号和时间码
        pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
        
        def replace_text(match):
            number = match.group(1)
            timestamp = match.group(2)
            text = match.group(3)
            # 只处理文本部分，保留序号和时间码
            processed_text = remove_chinese_punctuation(text)
            return f"{number}\n{timestamp}\n{processed_text}"
        
        # 处理文件内容
        processed_content = re.sub(pattern, replace_text, content, flags=re.DOTALL)
        
        # 保存处理后的内容
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"已处理文件: {input_file}")
        return True
        
    except Exception as e:
        print(f"处理文件 {input_file} 时出错: {e}")
        return False

def process_directory(input_dir, suffix="_processed"):
    """处理目录中的所有字幕文件"""
    # 创建输出目录
    output_dir = os.path.join(input_dir, "Processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有字幕文件
    subtitle_files = []
    for ext in ['.srt', '.txt']:
        subtitle_files.extend(list(Path(input_dir).glob(f'*{ext}')))
    
    if not subtitle_files:
        print(f"在目录 {input_dir} 中没有找到字幕文件")
        return
    
    print(f"找到 {len(subtitle_files)} 个字幕文件")
    
    # 处理每个文件
    success_count = 0
    for file_path in subtitle_files:
        # 生成输出文件名
        output_filename = f"{file_path.stem}{suffix}{file_path.suffix}"
        output_path = os.path.join(output_dir, output_filename)
        
        if process_file(str(file_path), output_path):
            success_count += 1
    
    print(f"\n处理完成:")
    print(f"成功处理: {success_count} 个文件")
    print(f"输出目录: {output_dir}")

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python remove_chinese_punctuation.py <字幕文件夹路径>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    
    if not os.path.exists(input_dir):
        print(f"错误：目录不存在: {input_dir}")
        sys.exit(1)
    
    if not os.path.isdir(input_dir):
        print(f"错误：指定的路径不是目录: {input_dir}")
        sys.exit(1)
    
    process_directory(input_dir)

if __name__ == "__main__":
    main() 
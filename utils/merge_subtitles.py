import os
import sys
import re
import chardet
from datetime import datetime

def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        print(f"检测到文件编码: {encoding}")
        return encoding

def read_subtitle_file(file_path):
    """读取字幕文件并解析内容"""
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    
    # 使用正则表达式匹配字幕序号和内容
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    # 将匹配结果转换为字典，以序号为键
    subtitles = {}
    for match in matches:
        number = int(match.group(1))
        timestamp = match.group(2)
        text = match.group(3).strip()
        subtitles[number] = {
            'timestamp': timestamp,
            'text': text
        }
    
    return subtitles

def merge_subtitles(file1_path, file2_path):
    """合并两个字幕文件"""
    print(f"正在读取第一个文件: {file1_path}")
    subtitles1 = read_subtitle_file(file1_path)
    print(f"正在读取第二个文件: {file2_path}")
    subtitles2 = read_subtitle_file(file2_path)
    
    # 获取所有序号
    all_numbers = sorted(set(list(subtitles1.keys()) + list(subtitles2.keys())))
    
    # 生成合并后的字幕内容
    merged_content = []
    for number in all_numbers:
        # 获取第一个文件的字幕（包含时间码）
        sub1 = subtitles1.get(number, {'timestamp': '', 'text': ''})
        # 获取第二个文件的字幕（只需要文本）
        sub2 = subtitles2.get(number, {'text': ''})
        
        # 使用第一个文件的时间码
        timestamp = sub1['timestamp']
        if not timestamp:
            print(f"警告：序号 {number} 在第一个文件中没有时间码，跳过")
            continue
        
        # 合并文本
        text = f"{sub1['text']}\n{sub2['text']}" if sub1['text'] and sub2['text'] else sub1['text'] or sub2['text']
        
        # 添加到结果中
        merged_content.append(f"{number}\n{timestamp}\n{text}")
    
    return "\n\n".join(merged_content)

def save_merged_subtitle(content, output_path):
    """保存合并后的字幕文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"合并后的字幕已保存到: {output_path}")

def main():
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("使用方法: python merge_subtitles.py <第一个字幕文件路径> <第二个字幕文件路径>")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    # 检查文件是否存在
    if not os.path.exists(file1_path):
        print(f"错误：第一个文件不存在: {file1_path}")
        sys.exit(1)
    if not os.path.exists(file2_path):
        print(f"错误：第二个文件不存在: {file2_path}")
        sys.exit(1)
    
    # 检查文件扩展名
    for file_path in [file1_path, file2_path]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.srt', '.txt']:
            print(f"错误：不支持的文件格式: {file_path}")
            sys.exit(1)
    
    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"merged_subtitle_{timestamp}.srt"
    
    try:
        # 合并字幕
        merged_content = merge_subtitles(file1_path, file2_path)
        # 保存结果
        save_merged_subtitle(merged_content, output_path)
    except Exception as e:
        print(f"处理过程中出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
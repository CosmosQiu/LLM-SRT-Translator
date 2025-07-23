import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# 添加项目根目录到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def process_subtitle(input_file, chinese_on_top=True):
    """处理字幕文件的完整流程
    
    Args:
        input_file: 输入的字幕文件路径
        chinese_on_top: 是否将中文字幕显示在上方，默认为True
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"错误：输入文件不存在: {input_file}")
            return False
        
        # 获取文件扩展名
        _, ext = os.path.splitext(input_file)
        if ext.lower() not in ['.srt', '.txt']:
            print(f"错误：不支持的文件格式: {input_file}")
            return False
        
        # 创建临时目录
        timestamp = get_timestamp()
        temp_dir = os.path.join("opt", timestamp)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 1. 调用API进行翻译
        print("\n1. 开始翻译字幕...")
        from models.deepseek_api_srt import process_subtitle_file
        translated_file = process_subtitle_file(input_file)
        if not translated_file or not os.path.exists(translated_file):
            print("错误：翻译失败")
            return False
        print(f"翻译完成，文件保存在: {translated_file}")
        
        # 2. 格式化翻译后的文件
        print("\n2. 开始格式化字幕...")
        from utils.format import format_subtitle_text
        formatted_file = os.path.join(temp_dir, f"formatted_{os.path.basename(translated_file)}")
        format_subtitle_text(translated_file, formatted_file)
        if not os.path.exists(formatted_file):
            print("错误：格式化失败")
            return False
        print(f"格式化完成，文件保存在: {formatted_file}")
        
        # 3. 合并原始文件和翻译后的文件
        print("\n3. 开始合并字幕...")
        from utils.merge_subtitles import merge_subtitles
        merged_file = os.path.join(temp_dir, f"merged_{os.path.basename(input_file)}")
        # 根据参数决定合并顺序
        if chinese_on_top:
            merged_content = merge_subtitles(formatted_file, input_file)  # 中文在上
        else:
            merged_content = merge_subtitles(input_file, formatted_file)  # 英文在上
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        if not os.path.exists(merged_file):
            print("错误：合并失败")
            return False
        print(f"合并完成，文件保存在: {merged_file}")
        
        # 4. 移除中文标点符号
        print("\n4. 开始移除中文标点符号...")
        from utils.remove_chinese_punctuation import remove_chinese_punctuation
        with open(merged_file, 'r', encoding='utf-8') as f:
            content = f.read()
        processed_content = remove_chinese_punctuation(content)
        
        # 生成最终输出文件
        output_dir = os.path.join(os.path.dirname(input_file), "Processed")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}_processed.srt"
        output_file = os.path.join(output_dir, output_filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        
        print(f"\n处理完成！")
        print(f"最终文件保存在: {output_file}")
        
        # 清理临时文件
        try:
            shutil.rmtree(temp_dir)
            print(f"已清理临时文件")
        except Exception as e:
            print(f"清理临时文件时出错: {e}")
        
        return True
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='处理字幕文件')
    parser.add_argument('input_file', help='输入的字幕文件路径')
    parser.add_argument('--chinese-on-top', action='store_true', default=True,
                      help='将中文字幕显示在上方（默认）')
    parser.add_argument('--english-on-top', action='store_false', dest='chinese_on_top',
                      help='将英文字幕显示在上方')
    
    args = parser.parse_args()
    
    if not process_subtitle(args.input_file, args.chinese_on_top):
        sys.exit(1)

if __name__ == "__main__":
    main() 
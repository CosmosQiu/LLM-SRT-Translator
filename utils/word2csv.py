import os
import sys
from pathlib import Path
from docx2pdf import convert

def word_to_pdf(word_file_path, output_dir=None):
    """
    将Word文档转换为PDF文件
    
    参数:
        word_file_path: Word文件路径
        output_dir: 输出目录，默认与Word文件相同
    
    返回:
        生成的PDF文件路径
    """
    try:
        # 读取Word文件
        print(f"正在处理: {word_file_path}")
        
        # 准备输出路径
        word_path = Path(word_file_path)
        if output_dir is None:
            output_dir = word_path.parent
        else:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
        
        # 创建与Word文件同名的PDF文件
        pdf_file_path = os.path.join(output_dir, f"{word_path.stem}.pdf")
        
        # 转换Word为PDF
        convert(word_file_path, pdf_file_path)
        
        print(f"已生成PDF文件: {pdf_file_path}")
        return pdf_file_path
    
    except Exception as e:
        print(f"处理文件 {word_file_path} 时出错: {str(e)}")
        return None

def process_word_folder(input_folder, output_folder=None):
    """
    处理文件夹中的所有Word文件
    
    参数:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径，默认与输入文件夹相同
    
    返回:
        生成的PDF文件列表
    """
    # 确保文件夹路径存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入路径 {input_folder} 不存在")
        return []
    
    # 获取所有docx文件
    word_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
                 if f.endswith('.docx') and not f.startswith('~$')]
    
    if not word_files:
        print(f"在 {input_folder} 中未找到Word文件")
        return []
    
    # 处理每个Word文件
    pdf_files = []
    for word_file in word_files:
        pdf_file = word_to_pdf(word_file, output_folder)
        if pdf_file:
            pdf_files.append(pdf_file)
    
    return pdf_files

if __name__ == "__main__":
    # 设置默认值
    input_folder = os.getcwd()
    output_folder = None
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    
    # 如果没有通过命令行参数指定，则交互式获取路径
    if input_folder == os.getcwd():
        user_input = input(f"请输入Word文件所在文件夹路径 (默认: {input_folder}): ").strip()
        if user_input:
            input_folder = user_input
    
    if output_folder is None:
        user_output = input(f"请输入PDF文件输出文件夹路径 (默认与输入文件夹相同): ").strip()
        if user_output:
            output_folder = user_output
    
    print(f"开始处理文件夹: {input_folder}")
    if output_folder:
        print(f"输出文件夹: {output_folder}")
    else:
        print("输出文件夹: 与输入文件夹相同")
    
    pdf_files = process_word_folder(input_folder, output_folder)
    
    if pdf_files:
        print(f"处理完成，共生成 {len(pdf_files)} 个PDF文件:")
        for pdf_file in pdf_files:
            print(f"- {pdf_file}")
    else:
        print("未生成任何PDF文件")
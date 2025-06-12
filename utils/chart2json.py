import os
import sys
import json
import pandas as pd
from pathlib import Path

def excel_to_json(excel_file_path, output_dir=None):
    """
    将Excel文件转换为JSON文件
    
    参数:
        excel_file_path: Excel文件路径
        output_dir: 输出目录，默认与Excel文件相同
    
    返回:
        生成的JSON文件路径
    """
    try:
        # 读取Excel文件
        print(f"正在处理: {excel_file_path}")
        excel_data = pd.read_excel(excel_file_path)
        
        # 准备输出路径
        excel_path = Path(excel_file_path)
        if output_dir is None:
            output_dir = excel_path.parent
        else:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
        
        # 创建与Excel文件同名的JSON文件
        json_file_path = os.path.join(output_dir, f"{excel_path.stem}.json")
        
        # 将DataFrame转换为JSON
        json_data = excel_data.to_json(orient='records', force_ascii=False, indent=4)
        
        # 将JSON数据写入文件
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(json_data)
        
        print(f"已生成JSON文件: {json_file_path}")
        return json_file_path
    
    except Exception as e:
        print(f"处理文件 {excel_file_path} 时出错: {str(e)}")
        return None

def process_excel_folder(input_folder, output_folder=None):
    """
    处理文件夹中的所有Excel文件
    
    参数:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径，默认与输入文件夹相同
    
    返回:
        生成的JSON文件列表
    """
    # 确保文件夹路径存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入路径 {input_folder} 不存在")
        return []
    
    # 获取所有xlsx文件
    excel_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
                  if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if not excel_files:
        print(f"在 {input_folder} 中未找到Excel文件")
        return []
    
    # 处理每个Excel文件
    json_files = []
    for excel_file in excel_files:
        json_file = excel_to_json(excel_file, output_folder)
        if json_file:
            json_files.append(json_file)
    
    return json_files

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
        user_input = input(f"请输入Excel文件所在文件夹路径 (默认: {input_folder}): ").strip()
        if user_input:
            input_folder = user_input
    
    if output_folder is None:
        user_output = input(f"请输入JSON文件输出文件夹路径 (默认与输入文件夹相同): ").strip()
        if user_output:
            output_folder = user_output
    
    print(f"开始处理文件夹: {input_folder}")
    if output_folder:
        print(f"输出文件夹: {output_folder}")
    else:
        print("输出文件夹: 与输入文件夹相同")
    
    json_files = process_excel_folder(input_folder, output_folder)
    
    if json_files:
        print(f"处理完成，共生成 {len(json_files)} 个JSON文件:")
        for json_file in json_files:
            print(f"- {json_file}")
    else:
        print("未生成任何JSON文件")

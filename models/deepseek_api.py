import os
import PyPDF2
import pandas as pd
from openai import OpenAI
import datetime
import pathlib
import sys
import docx  # 添加docx库用于处理Word文档
import csv  # 添加csv库用于处理CSV文件
import re

def get_document_files(folder_path):
    """获取文件夹内所有PDF、Word、CSV和Markdown文件的路径"""
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
            if f.endswith(('.pdf', '.docx', '.doc', '.csv', '.md', '.markdown'))]

def extract_text_from_pdf(pdf_path):
    """从PDF文件中提取文本"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''.join([page.extract_text() for page in reader.pages])
        return text

def extract_text_from_docx(docx_path):
    """从Word文档中提取文本"""
    doc = docx.Document(docx_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return text

def extract_text_from_csv(csv_path):
    """从CSV文件中提取文本"""
    text = ""
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            text += " | ".join(row) + "\n"
    return text

def extract_text_from_markdown(md_path):
    """从Markdown文件中提取文本"""
    try:
        with open(md_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"提取Markdown文件文本时出错: {e}")
        return ""

def extract_text_from_document(file_path):
    """根据文件类型提取文本"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(('.docx', '.doc')):
        return extract_text_from_docx(file_path)
    elif file_path.lower().endswith('.csv'):
        return extract_text_from_csv(file_path)
    elif file_path.lower().endswith(('.md', '.markdown')):
        return extract_text_from_markdown(file_path)
    else:
        raise ValueError(f"不支持的文件类型: {file_path}")

def extract_info_with_deepseek(text):
    client = OpenAI(api_key="sk-8880397704b64ed3868a64e3aef5e91c", base_url="https://api.deepseek.com")
    prompt = """
    请从以下文本中提取这些信息，并按照以下格式输出：
    
    单位全称：[提取的内容或未提及]
    联系人：[提取的内容或未提及]
    联系方式：[提取的内容或未提及]
    主管单位/所属单位：[提取的内容或未提及]
    单位主要职能：[提取的内容或未提及]
    在译语种：[提取的内容或未提及]
    在译语种覆盖人口：[提取的内容或未提及]
    覆盖地域及面积：[提取的内容或未提及]
    需求译制语种：[提取的内容或未提及]
    在职人数：[提取的内容或未提及]
    聘用人员数：[提取的内容或未提及]
    译制演职员情况：[提取的内容或未提及]
    方言中心概况：[提取的内容或未提及]
    核心业务：[提取的内容或未提及]
    放映职能：[提取的内容或未提及]
    当前主要困难：[提取的内容或未提及]
    最希望获得的协助类型：[提取的内容或未提及]
    是否积极探索新质生产力相关的技术或模式：[是或否或未提及]
    是否尝试过使用AI工具辅助现有工作：[是或否或未提及]
    建议调研时间段：[提取的内容或未提及]
    调研交流内容的建议和期望：[提取的内容或未提及]
    
    注意：
    1. 直接以纯文本格式输出，保持上述格式
    2. 如果某项信息在文本中找不到，请填写"未提及"
    3. 对于问"是否"的问题，请直接返回"是"或"否"或"未提及"，不要添加任何解释
    
    文本内容："""

    response = client.chat.completions.create(
        model= "deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        stream=False
    )
    
    # 获取纯文本响应
    content = response.choices[0].message.content
    print(content)
    
    # 将纯文本响应解析为字典
    try:
        result = {}
        lines = content.strip().split('\n')
        for line in lines:
            if ':' in line or '：' in line:
                # 处理可能的中英文冒号
                if ':' in line:
                    key, value = line.split(':', 1)
                else:
                    key, value = line.split('：', 1)
                
                key = key.strip()
                value = value.strip()
                
                # 移除可能的方括号
                value = value.replace('[', '').replace(']', '')
                
                result[key] = value
        
        return result
    except Exception as e:
        print(f"解析响应时出错: {e}")
        print(f"原始响应: {content}")
        # 返回原始文本作为单个键值对
        return {"原始响应": content}

def save_to_excel(data_list, output_path):
    """将提取的信息保存到Excel表格，保留之前的数据"""
    # 检查Excel文件是否已存在
    if os.path.exists(output_path):
        # 读取现有数据
        existing_df = pd.read_excel(output_path)
        
        # 将新数据转换为DataFrame
        new_df = pd.DataFrame(data_list)
        
        # 检查是否有重复的文件名，如果有则更新，没有则添加
        file_names = [info['file_name'] for info in data_list]
        
        # 删除已存在的相同文件名的行（如果有）
        existing_df = existing_df[~existing_df['file_name'].isin(file_names)]
        
        # 合并现有数据和新数据
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # 保存合并后的数据
        combined_df.to_excel(output_path, index=False)
        print(f"已将新数据添加到 {output_path}")
    else:
        # 如果文件不存在，创建新文件
        df = pd.DataFrame(data_list)
        df.to_excel(output_path, index=False)
        print(f"已创建新文件 {output_path}")


def process_pdf_folder(folder_path, output_excel=None):
    """处理文件夹内所有PDF和Word文件并保存结果到Excel"""
    # 创建以时间命名的输出文件夹
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(pathlib.Path(__file__).parent.parent, "opt", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 如果没有指定输出文件名，则使用默认名称
    if output_excel is None:
        output_excel = f"output_{timestamp}.xlsx"
    
    # 完整的输出文件路径
    output_path = os.path.join(output_dir, output_excel)
    
    document_files = get_document_files(folder_path)
    data = []

    for doc_file in document_files:
        print(f"处理文件: {doc_file}")
        try:
            # 检查是否已经处理过该文件
            if os.path.exists(output_path):
                existing_df = pd.read_excel(output_path)
                if os.path.basename(doc_file) in existing_df['file_name'].values:
                    print(f"文件 {os.path.basename(doc_file)} 已处理过，跳过")
                    continue
            
            # 提取文本
            text = extract_text_from_document(doc_file)
            # 调用DeepSeek api提取信息
            info = extract_info_with_deepseek(text)
            # 添加文件名作为标识
            info['file_name'] = os.path.basename(doc_file)
            data.append(info)
        except Exception as e:
            print(f"处理 {doc_file} 时出错: {e}")

    # 保存到Excel
    if data:  # 只有当有新数据时才保存
        save_to_excel(data, output_path)
        print(f"新结果已添加到 {output_path}")
    else:
        print("没有新的文档文件需要处理")
    
    return output_path

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
    client = OpenAI(api_key="", base_url="https://api.deepseek.com")
    
    # 构建字幕文本
    subtitle_text = "\n".join([f"{s['number']}\n{s['timestamp']}\n{s['text']}" for s in chunk])
    
    prompt = """
    请分析以下字幕内容，提取关键信息并总结主要内容。请以简洁的方式输出：
    
    1. 主要话题：
    2. 关键信息：
    3. 重要观点：
    
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

def process_subtitle_file(input_file, output_file):
    """处理字幕文件并保存结果"""
    # 创建输出目录
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
            results.append(f"\n=== 第 {i} 段字幕分析结果 ===\n")
            results.append(result)
            results.append("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"处理第 {i} 段时出错: {e}")
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(results))
    
    print(f"处理完成，结果已保存到: {output_file}")

# 示例调用
if __name__ == "__main__":
    # 检查是否有命令行参数传入
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]  # 从命令行参数获取文件夹路径
    else:
        # 默认路径，仅在没有提供命令行参数时使用
        folder_path = r"C:\Users\user\WORK\Projects\local_llm_usage\org-files\各中心反馈\MD"
        
    print(f"处理文件夹: {folder_path}")
    output_file = process_pdf_folder(folder_path)
    print(f"处理完成，结果保存在: {output_file}")
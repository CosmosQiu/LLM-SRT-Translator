import os
import ollama
import pandas as pd

def get_markdown_files(folder_path):
    """获取文件夹内所有Markdown文件的路径"""
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.md', '.markdown'))]

def extract_text_from_markdown(markdown_path):
    """从Markdown文件中提取文本"""
    try:
        with open(markdown_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"提取Markdown文件文本时出错: {e}")
        return ""

def extract_info_with_ollama(text):
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
    prompt += text

    # 使用新版本的ollama API
    try:
        # 尝试使用新版本API
        client = ollama.Client()
        response = client.generate(
            model="qwen2.5:14b",
            prompt=prompt
        )
        content = response['response']
    except (AttributeError, TypeError):
        try:
            # 尝试使用旧版本API
            response = ollama.generate(
                model="qwen2.5:14b",
                prompt=prompt
            )
            content = response['response']
        except:
            # 最后尝试使用最新版本的消息格式
            from ollama import Client
            client = Client()
            messages = [{'role': 'user', 'content': prompt}]
            response = client.chat(model="qwen2.5:14b", messages=messages)
            content = response['message']['content']
    
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


def process_markdown_folder(folder_path, output_excel):
    """处理文件夹内所有Markdown文件并保存结果到Excel"""
    markdown_files = get_markdown_files(folder_path)
    data = []

    for markdown_file in markdown_files:
        print(f"处理文件: {markdown_file}")
        try:
            # 检查是否已经处理过该文件
            if os.path.exists(output_excel):
                existing_df = pd.read_excel(output_excel)
                if os.path.basename(markdown_file) in existing_df['file_name'].values:
                    print(f"文件 {os.path.basename(markdown_file)} 已处理过，跳过")
                    continue
            
            # 提取文本
            text = extract_text_from_markdown(markdown_file)
            if not text:
                print(f"文件 {markdown_file} 中未提取到文本，跳过")
                continue
                
            # 调用Ollama提取信息
            info = extract_info_with_ollama(text)
            # 添加文件名作为标识
            info['file_name'] = os.path.basename(markdown_file)
            data.append(info)
        except Exception as e:
            print(f"处理 {markdown_file} 时出错: {e}")

    # 保存到Excel
    if data:  # 只有当有新数据时才保存
        save_to_excel(data, output_excel)
        print(f"新结果已添加到 {output_excel}")
    else:
        print("没有新的Markdown文件需要处理")

# 示例调用
if __name__ == "__main__":
    import sys
    
    # 检查是否有命令行参数传入
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]  # 从命令行参数获取文件夹路径
    else:
        # 默认路径，仅在没有提供命令行参数时使用
        folder_path = r"C:\Users\user\WORK\Projects\local_llm_usage\org-files\各中心反馈\MD"
    
    print(f"处理文件夹: {folder_path}")
    output_excel = "output.xlsx"  # 输出Excel文件名
    process_markdown_folder(folder_path, output_excel)
    print(f"处理完成，结果保存在: {output_excel}")
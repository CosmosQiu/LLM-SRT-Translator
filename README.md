# local_llm_usage

本项目旨在利用本地及API大模型（如 DeepSeek、Ollama）实现文档信息抽取、字幕翻译与处理、批量格式转换等自动化任务，适用于字幕翻译、文档批量处理、数据格式转换等多种场景。

## 主要功能
- **字幕翻译与处理**：支持.srt/.txt字幕文件的自动分段、调用大模型翻译、格式化、合并及去除中文标点。
- **文档信息抽取**：支持PDF、Word、CSV、Markdown等多种文档的关键信息抽取，支持DeepSeek API和本地Ollama。
- **批量格式转换**：支持Word转PDF、Word转Markdown、Excel转JSON等批量转换。
- **工具化处理**：提供多种utils工具脚本，便于二次开发和集成。

## 目录结构
```
local_llm_usage/
├── config.yml                # 配置文件，填写API密钥和服务地址
├── requirements.txt          # Python依赖包列表
├── models/                   # 主要模型与API调用脚本
│   ├── deepseek_api.py       # DeepSeek文档信息抽取与处理
│   ├── deepseek_api_srt.py   # DeepSeek字幕翻译与处理
│   └── local-ollama.py       # 本地Ollama文档信息抽取
├── tools/                    # 高级处理流程脚本
│   └── process_subtitle.py   # 字幕翻译、格式化、合并、去标点一站式处理
├── utils/                    # 工具函数与批量处理脚本
│   ├── chart2json.py         # Excel转JSON
│   ├── format.py             # 字幕格式化
│   ├── merge_subtitles.py    # 字幕合并
│   ├── remove_chinese_punctuation.py # 去除中文标点
│   ├── word2csv.py           # Word转PDF
│   ├── word2md.py            # Word转Markdown
├── opt/                      # 处理结果输出目录
├── org-files/                # 原始文档/字幕等存放目录
├── run.bat                   # Windows批处理启动脚本
└── venv/                     # Python虚拟环境
```

## 安装依赖
建议使用Python 3.8及以上版本。

```bash
pip install -r requirements.txt
```

## 配置方法
1. 复制并编辑`config.yml`，填写你的 DeepSeek API Key、Ollama 本地服务地址等信息：

```yaml
api:
  deepseek:
    base_url: "https://api.deepseek.com"
    api_key: "你的deepseek api key"
  ollama:
    base_url: "http://localhost:11434"
```

2. 如需使用本地Ollama，请确保Ollama服务已启动并下载好所需模型。

## 各脚本用途说明
- `models/deepseek_api.py`：批量处理PDF/Word/CSV/Markdown，调用DeepSeek API抽取关键信息。
- `models/deepseek_api_srt.py`：分割字幕、调用DeepSeek翻译、合并、输出处理结果。
- `models/local-ollama.py`：本地Ollama模型对Markdown文档进行信息抽取。
- `tools/process_subtitle.py`：一键完成字幕翻译、格式化、合并、去标点，生成最终可用字幕。
- `utils/format.py`：格式化字幕文件，确保结构规范。
- `utils/merge_subtitles.py`：合并中英文字幕，支持自定义顺序。
- `utils/remove_chinese_punctuation.py`：去除字幕中的中文标点符号。
- `utils/word2csv.py`：批量将Word文档转换为PDF。
- `utils/word2md.py`：批量将Word文档转换为Markdown（需安装pandoc）。
- `utils/chart2json.py`：批量将Excel文件转换为JSON。

## 使用示例
### 字幕翻译与处理
```bash
python tools/process_subtitle.py <字幕文件路径> [chinese_on_top]
# 例：python tools/process_subtitle.py example.srt True
```

### 文档信息抽取
```bash
python models/deepseek_api.py <文件夹路径>
python models/local-ollama.py <文件夹路径>
```

### Word转PDF
```bash
python utils/word2csv.py <word文件夹路径> [输出文件夹路径]
```

### Word转Markdown
```bash
python utils/word2md.py
# 需修改脚本内路径变量
```

### Excel转JSON
```bash
python utils/chart2json.py <excel文件夹路径> [输出文件夹路径]
```

## 注意事项
- DeepSeek API和Ollama服务需提前配置好。
- 字幕处理支持.srt和.txt格式。
- Word转Markdown需本地安装pandoc。

## 协议

本项目采用 MIT 协议，详见 LICENSE 文件。 
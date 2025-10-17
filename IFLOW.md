# 教案AI生成器项目概述

## 项目简介

这是一个为高职院校教师开发的命令行工具，利用本地AI技术批量生成整学期教案，显著提升备课效率。

核心价值：
- **效率提升**：将教案编写时间从数小时缩短到几分钟
- **批量处理**：一键生成整学期所有课程教案
- **本地部署**：使用Ollama确保数据安全和隐私
- **高职适配**：针对职业技能教育特点优化内容生成

## 技术架构

```
输入层：
  ├── 教学进度表（Excel）
  ├── 教学大纲（Word）
  └── 教案模板（Word）

处理层：
  ├── 数据解析器 (data_parser.py)
  ├── AI生成引擎 (ai_generator.py)
  └── 文档组装器 (document_builder.py)

输出层：
  └── 批量教案文档（Word）
```

### 核心模块

1. **数据解析器** (`data_parser.py`)：解析Excel教学进度表和Word教学大纲
2. **AI生成引擎** (`ai_generator.py`)：调用本地Ollama模型生成各教案字段内容
3. **文档组装器** (`document_builder.py`)：按周次和课次批量生成Word格式教案
4. **命令行界面** (`main.py`)：提供命令行操作界面

## 运行环境与依赖

- **编程语言**: Python 3.8+
- **AI服务**: Ollama + 本地LLM（默认使用qwen3:1.7b）
- **核心依赖**:
  - `python-docx`: Word文档处理
  - `pandas`: Excel数据解析
  - `requests`: Ollama API调用
  - `openpyxl`: Excel文件读取

## 安装与运行

### 安装依赖
```bash
pip install python-docx pandas requests openpyxl
```

### 运行方法
```bash
# 单次生成示例
python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t "test_data/template.docx"

# 批量生成示例  
python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t "test_data/template.docx" -w "1-16"
```

## 开发规范

遵循高级工程师任务执行规则：
1. 明确任务范围
2. 精确定位代码插入点
3. 最小化、独立的更改
4. 仔细检查一切
5. 清晰地交付
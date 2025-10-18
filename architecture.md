# 教案AI生成器 MVP架构设计

## 1. 系统架构图
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

## 2. 模块设计

### 2.1 数据解析器 (data_parser.py)
- 功能：解析Excel教学进度表和Word教学大纲
- 输入：Excel文件路径、Word文件路径
- 输出：结构化数据字典

### 2.2 AI生成引擎 (ai_generator.py)
- 功能：调用本地Ollama模型生成各教案字段内容
- 输入：结构化数据、提示词模板
- 输出：AI生成的教案内容

### 2.3 文档组装器 (document_builder.py)
- 功能：按周次和课次批量生成Word格式教案
- 输入：结构化数据、AI生成内容、模板文件路径
- 输出：Word教案文件

### 2.4 命令行界面 (main.py)
- 功能：提供命令行操作界面
- 参数：-s 进度表, -y 大纲, -t 模板, -w 周次范围
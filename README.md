# 教案AI生成器项目

这是一个为高职院校教师开发的命令行工具，利用本地AI技术批量生成整学期教案，显著提升备课效率。

## 功能特点

- **效率提升**：将教案编写时间从数小时缩短到几分钟
- **批量处理**：一键生成整学期所有课程教案
- **本地部署**：使用Ollama确保数据安全和隐私
- **高职适配**：针对职业技能教育特点优化内容生成

## 安装依赖

```bash
pip install python-docx pandas requests openpyxl
```

## 使用方法

```bash
# 单次生成示例
python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t "test_data/template.docx"

# 批量生成示例  
python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t "test_data/template.docx" -w "1-16"
```
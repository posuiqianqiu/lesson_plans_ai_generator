import pandas as pd
from docx import Document
import json

class DataParser:
    """数据解析器：解析Excel教学进度表和Word教学大纲"""
    
    @staticmethod
    def parse_schedule(excel_path):
        """
        解析Excel教学进度表
        :param excel_path: Excel文件路径
        :return: 课程数据列表
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # 转换为字典列表
            schedule_data = []
            for _, row in df.iterrows():
                schedule_data.append({
                    'week': row['周次'],
                    'lesson': row['课次'],
                    'course_name': row['课程名称'],
                    'chapter_content': row['章节内容'],
                    'class_hours': row['课时']
                })
            
            return schedule_data
        except Exception as e:
            print(f"解析Excel文件时出错: {e}")
            return []
    
    @staticmethod
    def parse_syllabus(docx_path):
        """
        解析Word教学大纲
        :param docx_path: Word文件路径
        :return: 大纲内容字典
        """
        try:
            doc = Document(docx_path)
            syllabus_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            # 这里可以添加更复杂的大纲解析逻辑
            # 目前只是简单返回文本内容
            return {'content': syllabus_text}
        except Exception as e:
            print(f"解析Word大纲时出错: {e}")
            return {}
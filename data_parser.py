import pandas as pd
from docx import Document
import json
import os
import logging
from config import Config

# 设置日志
Config.setup_logging()
logger = logging.getLogger(__name__)

class DataParser:
    """数据解析器：解析Excel教学进度表和Word教学大纲"""
    
    # 支持的Excel列名映射
    SCHEDULE_COLUMN_MAPPING = {
        '周次': ['周次', '周', 'week', 'Week', 'WEEK'],
        '课次': ['课次', '课时序号', 'lesson', 'Lesson', 'LESSON'],
        '课程名称': ['课程名称', '课程', 'course', 'Course', 'COURSE'],
        '章节内容': ['章节内容', '教学内容', '内容', 'content', 'Content', 'CONTENT'],
        '课时': ['课时', '学时', 'hours', 'Hours', 'HOURS'],
        # 添加更多可能的列名变体
        '日期': ['日期', 'date', 'Date', 'DATE'],
        '星期': ['星期', '星期几', 'weekday', 'Weekday', 'WEEKDAY'],
        '节次': ['节次', '上课时间', 'time', 'Time', 'TIME'],
        '班级': ['班级', '班级名称', 'class', 'Class', 'CLASS'],
        '教学地点': ['教学地点', '地点', 'location', 'Location', 'LOCATION'],
        '备注': ['备注', '说明', 'remark', 'Remark', 'REMARK'],
        '教师': ['教师', '任课教师', 'teacher', 'Teacher', 'TEACHER']
    }
    
    @staticmethod
    def parse_schedule(excel_path):
        """
        解析Excel教学进度表
        :param excel_path: Excel文件路径
        :return: 课程数据列表
        """
        try:
            # 检查文件是否存在和格式
            if not os.path.exists(excel_path):
                logger.error(f"文件不存在: {excel_path}")
                return None
            
            if not excel_path.endswith(('.xlsx', '.xls')):
                logger.error(f"不支持的文件格式: {excel_path}")
                return None
            
            # 读取Excel文件
            df = pd.read_excel(excel_path)
            df_columns = df.columns.tolist()
            
            # 验证和映射列名
            required_columns = ['周次', '课次', '课程名称', '章节内容', '课时']
            for col in required_columns:
                if col not in df_columns:
                    # 尝试映射列名
                    mapped_success = False
                    for mapped_col in DataParser.SCHEDULE_COLUMN_MAPPING.get(col, []):
                        if mapped_col in df_columns:
                            df = df.rename(columns={mapped_col: col})
                            logger.info(f"将列 '{mapped_col}' 映射为 '{col}'")
                            mapped_success = True
                            break
                    
                    if not mapped_success:
                        logger.error(f"缺少必需的列: {col}")
                        logger.error(f"可用列: {df_columns}")
                        logger.error(f"请检查Excel文件中是否包含以下列名之一: {DataParser.SCHEDULE_COLUMN_MAPPING.get(col, [])}")
                        return None
            
            # 转换数据
            schedule_data = []
            for index, row in df.iterrows():
                try:
                    # 验证周次和课次
                    week = str(row['周次']).strip()
                    lesson = str(row['课次']).strip()
                    
                    if not week or not lesson or week == 'nan' or lesson == 'nan':
                        continue
                    
                    lesson_data = {
                        'week': int(week),
                        'lesson': int(lesson)
                    }
                    
                    # 添加所有列数据，包括必需列和非必需列
                    for col in df_columns:
                        value = row[col]
                        lesson_data[col] = '' if pd.isna(value) else str(value).strip()
                    
                    schedule_data.append(lesson_data)
                    
                except (ValueError, TypeError):
                    continue
            
            logger.info(f"成功解析 {len(schedule_data)} 条课程记录")
            
            # 调试输出：显示解析结果的第一个记录
            if schedule_data:
                logger.info("解析结果示例:")
                for key, value in schedule_data[0].items():
                    logger.info(f"  {key}: {value}")
            
            return schedule_data
            
        except Exception as e:
            logger.error(f"解析Excel文件失败: {e}")
            return None
    
    @staticmethod
    def parse_syllabus(docx_path):
        """
        解析Word教学大纲
        :param docx_path: Word文件路径
        :return: 大纲内容字典
        """
        logger.info(f"=== 开始解析Word文件 ===")
        logger.info(f"文件路径: {docx_path}")
        
        try:
            # 验证文件存在
            if not os.path.exists(docx_path):
                error_msg = f"文件不存在: {docx_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # 验证文件大小
            file_size = os.path.getsize(docx_path)
            logger.info(f"文件大小: {file_size} 字节")
            
            if file_size == 0:
                error_msg = "文件为空"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 验证文件扩展名
            file_ext = os.path.splitext(docx_path)[1].lower()
            logger.info(f"文件扩展名: {file_ext}")
            
            if file_ext != '.docx':
                error_msg = f"不支持的文件格式: {file_ext}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 读取Word文件
            logger.info("开始读取Word文件...")
            try:
                doc = Document(docx_path)
                logger.info("Word文件读取成功")
            except Exception as e:
                error_msg = f"无法读取Word文件: {str(e)}"
                logger.error(error_msg)
                logger.error(f"详细错误: {traceback.format_exc()}")
                raise ValueError(error_msg)
            
            # 提取文本内容
            logger.info("开始提取段落内容...")
            paragraphs = []
            for i, paragraph in enumerate(doc.paragraphs):
                text = paragraph.text.strip()
                if text:  # 只添加非空段落
                    paragraphs.append(text)
                    logger.debug(f"段落 {i+1}: {text[:50]}...")
            
            if not paragraphs:
                error_msg = "Word文件中没有文本内容"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            syllabus_text = '\n'.join(paragraphs)
            
            # 基本内容验证
            if len(syllabus_text) < 10:
                error_msg = "Word文件内容过短，可能不是有效的教学大纲"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"=== 解析完成，包含 {len(paragraphs)} 个段落，共 {len(syllabus_text)} 字 ===")
            
            return {
                'content': syllabus_text,
                'paragraphs': paragraphs,
                'word_count': len(syllabus_text),
                'paragraph_count': len(paragraphs)
            }
            
        except Exception as e:
            error_msg = f"解析Word大纲时出错: {str(e)}"
            logger.error(error_msg)
            logger.error(f"完整错误堆栈: {traceback.format_exc()}")
            raise ValueError(error_msg)
    
    @staticmethod
    def _find_column_mapping(columns):
        """
        查找列名映射
        :param columns: Excel文件中的列名列表
        :return: 列名映射字典
        """
        mapping = {}
        columns_lower = [col.strip().lower() for col in columns]
        
        for standard_name, possible_names in DataParser.SCHEDULE_COLUMN_MAPPING.items():
            for possible_name in possible_names:
                for i, col in enumerate(columns_lower):
                    if possible_name.lower() == col:
                        mapping[standard_name] = columns[i]
                        break
                if standard_name in mapping:
                    break
        
        return mapping
    
    @staticmethod
    def validate_excel_structure(excel_path):
        """
        验证Excel文件结构
        :param excel_path: Excel文件路径
        :return: 验证结果字典
        """
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            result = {
                'valid': True,
                'rows': len(df),
                'columns': list(df.columns),
                'column_mapping': DataParser._find_column_mapping(df.columns),
                'issues': []
            }
            
            # 检查必要列
            required_columns = ['周次', '课次', '课程名称', '章节内容', '课时']
            mapping = result['column_mapping']
            
            for col in required_columns:
                if col not in mapping:
                    result['issues'].append(f"缺少列: {col}")
                    result['valid'] = False
            
            # 检查数据完整性
            if mapping:
                for index, row in df.iterrows():
                    week_col = mapping.get('周次')
                    lesson_col = mapping.get('课次')
                    
                    if week_col and lesson_col:
                        if pd.isna(row[week_col]) or pd.isna(row[lesson_col]):
                            result['issues'].append(f"第 {index + 1} 行数据不完整")
            
            return result
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'issues': [f"文件读取错误: {str(e)}"]
            }
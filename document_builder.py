from docx import Document
import os
from tqdm import tqdm

class DocumentBuilder:
    """文档组装器：按周次和课次批量生成Word格式教案"""
    
    def __init__(self, template_path):
        """
        初始化文档组装器
        :param template_path: 教案模板文件路径
        """
        self.template_path = template_path

    def _replace_text_in_doc(self, doc, replacements):
        """在文档的段落和表格中执行文本替换"""
        for p in doc.paragraphs:
            for key, value in replacements.items():
                if key in p.text:
                    p.text = p.text.replace(key, value)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for key, value in replacements.items():
                            if key in p.text:
                                p.text = p.text.replace(key, value)
        
    def build_lesson_plan(self, lesson_data, ai_generated_content, output_path):
        """
        生成单个教案文档
        :param lesson_data: 课程数据
        :param ai_generated_content: AI生成的内容字典
        :param output_path: 输出文件路径
        """
        try:
            doc = Document(self.template_path)
            
            replacements = {
                '{{week}}': str(lesson_data.get('week', '')),
                '{{lesson}}': str(lesson_data.get('lesson', '')),
                '{{course_name}}': lesson_data.get('course_name', ''),
                '{{chapter_content}}': lesson_data.get('chapter_content', ''),
                '{{class_hours}}': str(lesson_data.get('class_hours', '')),
                '{{单元教学目标}}': ai_generated_content.get('单元教学目标', ''),
                '{{教学重点}}': ai_generated_content.get('教学重点', ''),
                '{{教学难点}}': ai_generated_content.get('教学难点', ''),
                '{{教学活动}}': ai_generated_content.get('教学活动', ''),
                '{{教学资源}}': ai_generated_content.get('教学资源', ''),
                '{{教学反思}}': ai_generated_content.get('教学反思', ''),
                '{{教学评价}}': ai_generated_content.get('教学评价', ''),
            }

            self._replace_text_in_doc(doc, replacements)
            
            doc.save(output_path)
        except Exception as e:
            # 使用tqdm.write以避免破坏进度条显示
            tqdm.write(f"生成教案 {output_path} 时出错: {e}")
    
    def build_batch_lesson_plans(self, schedule_data, ai_generator, output_dir="lesson_plans"):
        """
        批量生成教案文档
        :param schedule_data: 课程数据列表
        :param ai_generator: AI生成器实例
        :param output_dir: 输出目录
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 从AI生成器获取唯一可信的内容类型列表，而不是硬编码
        content_types_to_generate = list(ai_generator.prompt_templates.keys())
        
        # 外层循环，遍历每节课
        for lesson_data in tqdm(schedule_data, desc="总体进度", position=0):
            ai_content = {}
            lesson_desc = f"处理第{lesson_data['week']}周第{lesson_data['lesson']}次课"
            
            # 内层循环，为当前课生成各部分内容
            with tqdm(total=len(content_types_to_generate), desc=lesson_desc, position=1, leave=False) as inner_pbar:
                for content_type in content_types_to_generate:
                    inner_pbar.set_description(f"{lesson_desc} ({content_type})")
                    ai_content[content_type] = ai_generator.generate_content(
                        content_type,
                        course_name=lesson_data['course_name'],
                        week=lesson_data['week'],
                        lesson=lesson_data['lesson'],
                        chapter_content=lesson_data['chapter_content'],
                        class_hours=lesson_data['class_hours']
                    )
                    inner_pbar.update(1)

            # 构造输出文件路径
            filename = f"第{lesson_data['week']}周第{lesson_data['lesson']}次课教案.docx"
            output_path = os.path.join(output_dir, filename)
            
            # 生成教案文档
            self.build_lesson_plan(lesson_data, ai_content, output_path)
            tqdm.write(f"✅ 已生成: {filename}")
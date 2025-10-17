import argparse
import os
from data_parser import DataParser
from ai_generator import AIGenerator
from document_builder import DocumentBuilder

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='教案AI生成器')
    parser.add_argument('-s', '--schedule', required=True, help='教学进度表文件路径')
    parser.add_argument('-y', '--syllabus', required=True, help='教学大纲文件路径')
    parser.add_argument('-t', '--template', required=True, help='教案模板文件路径')
    parser.add_argument('-w', '--weeks', help='周次范围，格式如"1-16"')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 验证文件是否存在
    if not os.path.exists(args.schedule):
        print(f"错误：教学进度表文件不存在：{args.schedule}")
        return
    
    if not os.path.exists(args.syllabus):
        print(f"错误：教学大纲文件不存在：{args.syllabus}")
        return
    
    if not os.path.exists(args.template):
        print(f"错误：教案模板文件不存在：{args.template}")
        return
    
    # 解析数据
    print("正在解析教学进度表...")
    schedule_data = DataParser.parse_schedule(args.schedule)
    if not schedule_data:
        print("错误：未能解析教学进度表")
        return
    
    print("正在解析教学大纲...")
    syllabus_data = DataParser.parse_syllabus(args.syllabus)
    if not syllabus_data:
        print("警告：未能解析教学大纲")
    
    # 初始化AI生成器
    print("正在初始化AI生成器...")
    ai_generator = AIGenerator()
    
    # 初始化文档生成器
    print("正在初始化文档生成器...")
    doc_builder = DocumentBuilder(args.template)
    
    # 如果指定了周次范围，则过滤数据
    if args.weeks:
        try:
            start_week, end_week = map(int, args.weeks.split('-'))
            schedule_data = [lesson for lesson in schedule_data if start_week <= lesson['week'] <= end_week]
        except ValueError:
            print(f"警告：周次范围格式不正确：{args.weeks}")
    
    # 生成教案
    print("正在生成教案...")
    doc_builder.build_batch_lesson_plans(schedule_data, ai_generator)
    
    print("教案生成完成！")

if __name__ == "__main__":
    main()
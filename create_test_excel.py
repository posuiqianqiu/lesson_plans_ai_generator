import pandas as pd

# 创建十周测试数据
data = {
    '周次': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10],
    '课次': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
    '课程名称': ['Python基础', 'Python基础', 'Python函数', 'Python函数', 'Python面向对象', 'Python面向对象', 
              'Python文件操作', 'Python文件操作', 'Python模块', 'Python模块', 'Python网络编程', 'Python网络编程',
              'Python数据库操作', 'Python数据库操作', 'Python Web开发', 'Python Web开发', 'Python数据处理', 
              'Python数据处理', 'Python项目实战', 'Python项目实战'],
    '章节内容': ['变量与数据类型', '条件语句与循环', '函数定义与调用', '参数与返回值', '类与对象', '继承与多态',
              '文件读写', '异常处理', '模块导入与使用', '标准库介绍', 'Socket编程基础', 'HTTP请求处理',
              'SQLite数据库', 'MySQL数据库连接', 'Flask框架基础', '路由与模板', 'Pandas数据分析',
              '数据可视化', '综合项目开发', '项目部署与维护'],
    '课时': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
}

# 创建DataFrame
df = pd.DataFrame(data)

# 保存为Excel文件
df.to_excel('test_data/schedule.xlsx', index=False)
import pandas as pd

# 创建测试数据
data = {
    '周次': [1, 1, 2, 2],
    '课次': [1, 2, 1, 2],
    '课程名称': ['Python基础', 'Python基础', 'Python函数', 'Python函数'],
    '章节内容': ['变量与数据类型', '条件语句与循环', '函数定义与调用', '参数与返回值'],
    '课时': [2, 2, 2, 2]
}

# 创建DataFrame
df = pd.DataFrame(data)

# 保存为Excel文件
df.to_excel('data/schedule.xlsx', index=False)
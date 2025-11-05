import requests
import json
import logging
from tqdm import tqdm
from config import Config, print_config_info

class AIGenerator:
    """AI生成引擎：调用本地Ollama模型生成各教案字段内容"""
    
    def __init__(self):
        """初始化AI生成器"""
        Config.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 从配置获取Ollama设置
        config = Config.validate_ollama_config()
        self.model_name = config["model"]
        self.base_url = config["host"]
        self.api_url = config["url"]
        self.timeout = config["timeout"]
        self.max_retries = config["max_retries"]
        
        # 打印配置信息
        print_config_info()
        self._check_ollama_status()
        
        # 提示词模板
        self.prompt_templates = {
            "单元教学目标": """
作为高职院校{课程名称}课程教师，请为第{week}周第{lesson}次课设计教学目标。
章节内容：{章节内容}

要求：
1. 设计一个知识目标、一个技能目标、一个素养目标。
2. 每个目标都必须是具体且可测量的。
3. 目标应突出职业技能的培养。
4. 严格按照以下格式输出，不要添加任何额外说明：
   - 知识目标：[具体内容]
   - 技能目标：[具体内容]
   - 素养目标：[具体内容]
            """,
            
            "教学重点": """
根据以下内容，提取本节课的教学重点：
课程：{课程名称}
章节：{章节内容}
课时：{课时}

要求：
1. 列出2-3个最重要的知识点或技能点
2. 每条以•开头
            """,
            
            "教学难点": """
根据以下内容，分析本节课的教学难点：
课程：{课程名称}
章节：{章节内容}
课时：{课时}

要求：
1. 列出1-2个学生可能难以掌握的内容
2. 每条以•开头
            """,
            
            "教学活动": """
课程：{课程名称}
内容：{章节内容}
课时：{课时}
根据课程内容，要求每个环节时间分配和活动安排明确。要求内容丰富、具体，同时运用多种教学方法（例如案例分析法、练习法、讲授法、讨论法、头脑风暴法、角色扮演法、游戏法等）。结构如下：
-新课导入【X分钟】：导入是引导学生进入学习情境从而形成适宜的学习心理准备状态的教学行为方式。导入的恰当使用对一堂课有导向和奠基的作用。常用的导入方式包括序言导入、尝试导入、演示导入、故事导入、提导入、范例导入六种，教师在设计教案时，要尽量使导入新颖活泼。
-讲授新课【X分钟】：在设计这一部分时，要针对不同教学内容，选择不同的教学方法;设想怎样提出问题，如何逐步启发、诱导学生理解新知；怎么教会学生掌握重点、难点以及完成课程内容所需的时间和具体的安排。运用多种授课方法讲授课程要点，要求有互动、具体，重难点突出，并标注出时间。
-巩固练习【X分钟】：根据课程内容，设计适合的练习作业，以加深学生对课堂知识的理解和应用。练习的设计要精巧，有层次、有坡度、有密度，具体还要考虑练习的进行方式。
-归纳总结【X分钟】：所授课将要结束时，由教师或学生对本课所学内容要点的回顾。教师在设计时可考虑实际需要，简单明了，适时总结。



要求：
1. 严格按照上述结构设计教学活动
2. 每个环节都要有明确的时间分配
3. 使用多种教学方法，内容要具体丰富
4. 使用清晰的格式，不要使用markdown符号如#和*
5. 只输出教学活动内容，不要包含工学结合体现、教学资源、评估方式、教学反思等其他内容
            """,
            
            "教学资源": """
为以下课程内容准备教学资源：
课程：{课程名称}
章节：{章节内容}

要求：
1. 列出所需的教学设备和工具
2. 推荐相关的参考资料或网站
3. 格式：分条列出，每条以•开头
            """,
            
            "教学反思": """
根据以下课程内容，预测可能的教学反思点：
课程：{课程名称}
章节：{章节内容}
课时：{课时}

要求：
1. 从教学效果、学生反馈等方面考虑
2. 提出改进建议
3. 格式：分条列出，每条以•开头
            """,
            
            "作业布置": """
为以下课程内容设计课后作业：
课程：{课程名称}
章节：{章节内容}
课时：{课时}

要求：
1. 包含理论题和实践题
2. 难度适中，符合高职学生水平
3. 格式：分条列出，每条以•开头
            """,
            
            "教学评价": """
设计本节课的教学评价方案：
课程：{课程名称}
章节：{章节内容}
课时：{课时}

要求：
1. 包含过程性评价和结果性评价
2. 明确评价标准和方式
3. 格式：分条列出，每条以•开头
            """
        }

    def _check_ollama_status(self):
        """检查Ollama API服务的真实状态"""
        print(f"正在检查Ollama服务状态 ({self.base_url})...")
        try:
            # 请求一个核心API端点，而不是根页面，以确保API服务正常
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()  # 如果状态码不是2xx，则会引发HTTPError
            print("Ollama API 服务连接成功，状态正常。")
        except requests.exceptions.RequestException as e:
            print(f"\n错误：无法连接到 Ollama API 服务。")
            print(f"请求地址: {self.base_url}/api/tags")
            print(f"错误详情: {e}")
            print("\n请执行以下检查：")
            print("1. 确认 Ollama 应用正在您的电脑上运行。")
            print("2. 确认 Ollama 服务没有被防火墙或代理阻止。")
            print("3. 尝试更新 Ollama 到最新版本，或重新安装。")
            exit(1)

    def get_local_models(self):
        """获取本地已下载的模型列表"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            return [m['name'] for m in models]
        except Exception:
            return ["无法获取模型列表"]
    
    def generate_content(self, prompt_type, **kwargs):
        """
        生成指定类型的内容
        :param prompt_type: 提示词类型
        :param kwargs: 填充提示词的参数
        :return: 生成的内容
        """
        print(f"=== AI generate_content ===")
        print(f"prompt_type: {prompt_type}")
        print(f"kwargs keys: {kwargs.keys() if kwargs else 'None'}")
        print(f"lesson_data: {kwargs.get('lesson_data', 'Not found')}")
        
        # 获取提示词模板
        if prompt_type not in self.prompt_templates:
            raise ValueError(f"不支持的提示词类型: {prompt_type}")
        
        # 填充提示词
        try:
            # 构建格式化参数
            format_params = {}
            
            # 添加lesson_data中的所有字段
            if 'lesson_data' in kwargs:
                format_params.update(kwargs['lesson_data'])
            # 添加其他参数
            for key, value in kwargs.items():
                if key != 'lesson_data':
                    format_params[key] = value
            
            prompt = self.prompt_templates[prompt_type].format(**format_params)
        except KeyError as e:
            self.logger.error(f"KeyError in format: {e}")
            self.logger.error(f"Required field '{e}' is missing from the data")
            self.logger.error(f"Available fields in lesson_data: {list(kwargs.get('lesson_data', {}).keys())}")
            self.logger.error(f"Available format_params keys: {list(format_params.keys())}")
            self.logger.error("Please check your Excel file contains the required column for course name")
            raise
        
        # 构造请求数据
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # 调用Ollama API
            response = requests.post(f"{self.base_url}/api/generate", json=data, timeout=180)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            return result.get('response', '').strip()
        except requests.exceptions.HTTPError as e:
            # 特别处理404错误，很可能是模型名称不对
            if e.response.status_code == 404:
                try:
                    error_detail = e.response.json().get('error', '')
                    if 'model' in error_detail and 'not found' in error_detail:
                        tqdm.write(f"\n[AI生成错误] 模型 '{self.model_name}' 未在Ollama中找到。")
                        tqdm.write(f"  > 您本地已有的模型: {self.get_local_models()}")
                        tqdm.write(f"  > 请将 docker-compose.yml 或环境变量 OLLAMA_MODEL 的值修改为以上列表中的一个。")
                    else:
                        tqdm.write(f"[AI生成错误] 调用Ollama API时出错 (404 Not Found): {e}")
                except json.JSONDecodeError:
                     tqdm.write(f"[AI生成错误] 调用Ollama API时出错 (404 Not Found), 且无法解析错误响应: {e}")
            else:
                tqdm.write(f"[AI生成错误] 调用Ollama API时发生HTTP错误: {e}")
            return f"[{prompt_type} 生成失败]"
        except requests.exceptions.Timeout:
            tqdm.write(f"    > 生成 {prompt_type} 超时。请检查Ollama服务或模型是否正常。")
            return f"[{prompt_type} 生成超时]"
        except requests.exceptions.RequestException as e:
            tqdm.write(f"调用Ollama API时发生网络错误: {e}")
            return ""
        except json.JSONDecodeError as e:
            tqdm.write(f"解析API响应时出错: {e}")
            return ""
# 教案AI生成器

这是一个为高职院校教师开发的命令行工具，利用本地AI技术批量生成整学期教案，显著提升备课效率。

## 功能特点

- **效率提升**：将教案编写时间从数小时缩短到几分钟。
- **批量处理**：一键生成整学期所有课程教案。
- **高度可配**：支持通过 Docker 环境变量轻松切换本地大模型。
- **数据安全**：完全本地化部署，确保教学数据的安全和隐私。
- **高职适配**：针对职业技能教育特点优化内容生成。

---

## 部署与使用指南

我们提供两种使用方式：**Docker快速部署（推荐）** 和 **本地手动部署**。

### 方案一：Docker 快速部署 (推荐)

这种方式最简单，无需在你的电脑上安装 Python 或其他依赖，只需要安装 Docker Desktop。

**第一步：安装 Docker**

- 前往 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载并安装适合你操作系统 (Windows/Mac/Linux) 的 Docker Desktop。

**第二步：配置模型**

1.  打开项目根目录下的 `docker-compose.yml` 文件。
2.  找到 `app` 服务下的 `environment` 部分。
3.  修改 `OLLAMA_MODEL` 的值为你本地已经下载好的 Ollama 模型名称。例如，如果你想使用 `qwen:4b`，就修改为：
    ```yaml
    environment:
      - OLLAMA_MODEL=qwen:4b
    ```

**第三步：准备输入文件**

- 将你的 `schedule.xlsx`, `syllabus.docx`, `template.docx` 文件放入项目根目录下的 `test_data` 文件夹中。

**第四步：启动生成**

- 在项目根目录下打开终端，运行以下命令：
  ```bash
  docker-compose up --build
  ```
- Docker 将会自动完成以下工作：
  1.  构建 Python 应用环境。
  2.  启动 Ollama 服务。
  3.  运行教案生成脚本。

**第五步：获取结果**

- 生成的教案（`.docx` 文件）会自动出现在项目根目录的 `lesson_plans` 文件夹中。

---

### 方案二：本地手动部署

如果你不想使用 Docker，也可以按照以下步骤在本地手动运行。

**第一步：安装并运行 Ollama**

1.  **安装 Ollama**: 访问 [Ollama 官网](https://ollama.com/)，下载并安装客户端。
2.  **下载模型**: 打开终端，运行命令以下载一个模型。我们推荐 `qwen:1.7b` 作为开始。
    ```bash
    ollama pull qwen:1.7b
    ```
3.  **运行模型**: 下载完成后，Ollama 服务会自动在后台运行。你可以通过在浏览器访问 `http://localhost:11434` 来确认服务是否正常（页面应显示 "Ollama is running"）。

**第二步：安装 Python 依赖**

- 确保你的电脑已安装 Python 3.8 或更高版本。
- 在项目根目录下打开终端，运行以下命令安装所需依赖：
  ```bash
  pip install -r requirements.txt
  ```

**第三步：运行项目**

- 将你的输入文件放入 `test_data` 目录。
- 运行以下命令开始生成教案：
  ```bash
   ### Windows CMD
  `cmd
  set OLLAMA_MODEL=qwen3:1.7b
  set OLLAMA_HOST=http://localhost:11434
  python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t "test_data/template.docx"
  `

  ### Windows PowerShell
  `powershell
  $env:OLLAMA_MODEL="qwen3:1.7b"
  $env:OLLAMA_HOST="http://localhost:11434"
  python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t "test_data/template.docx"
  `

  ### macOS / Linux
  `bash
  OLLAMA_MODEL=qwen3:1.7b OLLAMA_HOST=http://localhost:11434 python main.py -s "test_data/schedule.xlsx" -y "test_data/syllabus.docx" -t
  "test_data/template.docx"
  ```

**第四步：获取结果**

- 生成的教案会出现在 `lesson_plans` 文件夹中。
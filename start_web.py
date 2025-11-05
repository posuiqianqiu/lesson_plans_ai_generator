#!/usr/bin/env python3
"""
教案AI生成器Web应用启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    from config import Config, check_dependencies as check_deps
    
    if not check_deps():
        print("正在安装依赖...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("依赖安装完成!")
            return True
        except subprocess.CalledProcessError:
            print("依赖安装失败，请手动安装")
            return False
    
    return True

def check_ollama():
    """检查Ollama服务是否运行"""
    print("正在检查Ollama服务...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("Ollama服务运行正常!")
            return True
    except:
        pass
    
    print("警告: 无法连接到Ollama服务")
    print("请确保Ollama已安装并运行:")
    print("1. 下载安装: https://ollama.com/")
    print("2. 启动服务: ollama serve")
    print("3. 下载模型: ollama pull qwen3:1.7b")
    return False

def create_directories():
    """创建必要的目录"""
    directories = [
        'web/uploads',
        'lesson_plans',
        'cache'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("目录结构检查完成!")

def start_web_server():
    """启动Web服务器"""
    print("正在启动Web服务器...")
    
    # 设置环境变量
    os.environ.setdefault('OLLAMA_MODEL', 'qwen3:1.7b')
    os.environ.setdefault('OLLAMA_HOST', 'http://localhost:11434')
    
    # 启动服务器
    try:
        import uvicorn
        uvicorn.run(
            "web.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("教案AI生成器 - Web界面启动")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        input("依赖安装失败，按任意键退出...")
        return
    
    # 创建目录
    create_directories()
    
    # 检查Ollama
    ollama_running = check_ollama()
    
    print("\n" + "=" * 50)
    print("启动信息:")
    print(f"Web界面地址: http://localhost:8000")
    print(f"Ollama服务: {'正常' if ollama_running else '需要启动'}")
    print("=" * 50)
    
    # 询问是否打开浏览器
    try:
        choice = input("\n是否自动打开浏览器? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            print("正在打开浏览器...")
            webbrowser.open("http://localhost:8000")
    except:
        pass
    
    print("\n正在启动服务器，请稍候...")
    print("按 Ctrl+C 停止服务器")
    
    # 启动服务器
    start_web_server()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置模块
管理所有环境变量和配置项
"""

import os
import logging
from typing import Dict, Any

# 配置类
class Config:
    """应用配置类"""
    
    # Ollama配置
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
    
    # Web服务配置
    WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT = int(os.getenv("WEB_PORT", "8000"))
    
    # 文件路径配置
    UPLOAD_DIR = "web/uploads"
    OUTPUT_DIR = "lesson_plans"
    CACHE_DIR = "cache"
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 必需的Python包
    REQUIRED_PACKAGES = [
        'fastapi', 'uvicorn', 'python-multipart', 'jinja2', 'aiofiles',
        'python-docx', 'pandas', 'requests', 'openpyxl', 'tqdm'
    ]
    
    @classmethod
    def get_ollama_url(cls) -> str:
        """获取完整的Ollama API URL"""
        return f"{cls.OLLAMA_HOST.rstrip('/')}/api/generate"
    
    @classmethod
    def setup_logging(cls):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format=cls.LOG_FORMAT
        )
    
    @classmethod
    def validate_ollama_config(cls) -> Dict[str, Any]:
        """验证Ollama配置"""
        return {
            "model": cls.OLLAMA_MODEL,
            "host": cls.OLLAMA_HOST,
            "url": cls.get_ollama_url(),
            "timeout": cls.OLLAMA_TIMEOUT,
            "max_retries": cls.OLLAMA_MAX_RETRIES
        }
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        directories = [
            cls.UPLOAD_DIR,
            cls.OUTPUT_DIR,
            cls.CACHE_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

# 依赖检查函数
def check_dependencies() -> bool:
    """检查必要的依赖是否已安装"""
    missing_packages = []
    
    for package in Config.REQUIRED_PACKAGES:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下依赖包: {', '.join(missing_packages)}")
        return False
    
    return True

# 环境变量提示
def print_config_info():
    """打印配置信息"""
    config = Config.validate_ollama_config()
    
    if not os.getenv("OLLAMA_MODEL"):
        print(f"提示：未设置环境变量 OLLAMA_MODEL，使用默认值: {config['model']}")
    
    if not os.getenv("OLLAMA_HOST"):
        print(f"提示：未设置环境变量 OLLAMA_HOST，使用默认值: {config['host']}")
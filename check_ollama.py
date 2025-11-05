import requests
import json

OLLAMA_HOST = "http://localhost:11434"

def check_ollama_api():
    """
    一个独立的脚本，用于诊断本地Ollama服务的API是否健康。
    """
    print(f"--- Ollama 服务健康检查 ---")
    print(f"目标地址: {OLLAMA_HOST}")

    try:
        # 1. 检查根路径，确认服务在运行
        print("\n[步骤 1/2] 检查基础连接...")
        response = requests.get(OLLAMA_HOST, timeout=5)
        if response.status_code == 200 and "Ollama is running" in response.text:
            print("✅ 基础连接成功，Ollama 服务正在运行。")
        else:
            print(f"❌ 基础连接失败。状态码: {response.status_code}")
            print("请确认Ollama应用已在您的电脑上启动。")
            return

        # 2. 检查核心API，确认功能完整
        print("\n[步骤 2/2] 检查核心 API (/api/tags)...")
        api_url = f"{OLLAMA_HOST}/api/tags"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ 核心 API 返回 404 Not Found。")
            print("\n--- 诊断结论 ---")
            print("你的 Ollama 服务正在运行，但 API 功能不完整或版本过旧。")
            print("这是导致主程序报错的根本原因。")
            print("\n--- 修复建议 ---")
            print("请完全卸载您当前的 Ollama，然后从官网 (https://ollama.com/) 下载并安装最新版本。")
            return

        response.raise_for_status() # 检查其他HTTP错误
        
        models = response.json().get('models', [])
        print("✅ 核心 API 连接成功！")
        print("\n--- 诊断结论 ---")
        print("你的 Ollama 服务状态完全正常。")
        if models:
            print("检测到你本地已下载的模型:")
            for model in models:
                print(f"  - {model['name']}")
        else:
            print("你尚未下载任何模型。请使用 'ollama pull <model_name>' 下载一个。")

    except requests.exceptions.RequestException as e:
        print(f"❌ 连接到 Ollama 服务时发生网络错误。")
        print(f"错误详情: {e}")
        print("\n--- 修复建议 ---")
        print("1. 确认 Ollama 应用正在您的电脑上运行。")
        print("2. 检查防火墙或杀毒软件是否阻止了网络连接。")
        print("3. 确认 {OLLAMA_HOST} 地址是否正确。")

if __name__ == "__main__":
    check_ollama_api()
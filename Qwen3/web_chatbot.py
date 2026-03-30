#!/usr/bin/env python
# Qwen3-0.6B ChatBot Web 版本

import sys
import os
import time

# 设置国内镜像，解决网络连接问题
print("设置 Hugging Face 国内镜像...")
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
print(f"HF_ENDPOINT 设置为: {os.environ.get('HF_ENDPOINT')}")

print("正在导入模块...")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gradio as gr
import requests

print(f"Python 版本: {sys.version}")
print(f"torch 版本: {torch.__version__}")
print("所有模块导入成功")

# 检查网络连接
def check_connection():
    print("检查网络连接...")
    try:
        response = requests.get("https://huggingface.co")
        if response.status_code == 200:
            print("网络连接正常")
        else:
            print(f"网络异常，状态码：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"网络连接失败：{e}")
        print("正在使用国内镜像...")

check_connection()

class ModelInference:
    def __init__(self, model_path='Qwen/Qwen3-0.6B'):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """加载模型和分词器"""
        print(f"正在加载模型: {self.model_path}")
        print("这可能需要几分钟时间，首次运行会下载模型权重...")
        
        # 尝试加载分词器
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path, 
                    resume_download=True,
                    timeout=60  # 设置超时
                )
                print("分词器加载成功")
                break
            except Exception as e:
                retry_count += 1
                print(f"加载分词器失败 (尝试 {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    print("等待 10 秒后重试...")
                    time.sleep(10)
                else:
                    raise
        
        # 强制使用 CPU
        device_map = "cpu"
        print("使用 CPU 加载模型...")
        
        # 尝试加载模型
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    torch_dtype="auto",
                    device_map=device_map,
                    resume_download=True,
                    timeout=120  # 设置更长的超时
                ).eval()
                print("模型加载成功")
                break
            except Exception as e:
                retry_count += 1
                print(f"加载模型失败 (尝试 {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    print("等待 10 秒后重试...")
                    time.sleep(10)
                else:
                    raise
        
        # 设置生成配置
        self.model.generation_config.max_new_tokens = 1024
        print("模型加载完成")
    
    def chat(self, query, history):
        """进行对话推理"""
        try:
            # 构建对话历史
            conversation = [
                {'role': 'system', 'content': 'You are a helpful assistant.'},
            ]
            
            for q, r in history:
                conversation.append({'role': 'user', 'content': q})
                conversation.append({'role': 'assistant', 'content': r})
            
            conversation.append({'role': 'user', 'content': query})
            
            # 应用聊天模板
            inputs = self.tokenizer.apply_chat_template(
                conversation,
                add_generation_prompt=True,
                return_tensors='pt',
            )
            
            # 移动到模型设备
            inputs = inputs.to(self.model.device)
            
            # 生成回复
            outputs = self.model.generate(
                input_ids=inputs,
                max_new_tokens=self.model.generation_config.max_new_tokens,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id
            )
            
            # 解码输出
            response = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:],
                skip_special_tokens=True
            )
            
            return response
        except Exception as e:
            return f"错误: {str(e)}"

# 加载模型
print("初始化模型...")
model = ModelInference()

# 定义聊天函数
def chat_with_model(query, history):
    """与模型进行对话"""
    try:
        response = model.chat(query, history)
        return response
    except Exception as e:
        return f"错误: {str(e)}"

# 创建 Gradio 界面
print("创建 Web 界面...")
with gr.Blocks() as demo:
    gr.Markdown("# Qwen3-0.6B ChatBot")
    gr.Markdown("## 基于阿里云通义千问模型的智能对话机器人")
    
    chatbot = gr.Chatbot(height=400)
    msg = gr.Textbox(label="输入消息", placeholder="请输入你的问题...")
    clear = gr.Button("清除对话")
    
    def respond(message, chat_history):
        # 调用模型获取响应
        response = chat_with_model(message, chat_history)
        # 更新对话历史
        chat_history.append((message, response))
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

print("启动 Web 服务...")
print("请在浏览器中访问: http://localhost:7860")
demo.launch(share=False, server_port=7860, server_name="0.0.0.0")
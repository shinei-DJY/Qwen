#!/usr/bin/env python
# Qwen3 ChatBot Flask Web服务器 - 不依赖NumPy/PyTorch

from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qwen3 ChatBot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
        }
        h1, h2 {
            text-align: center;
            color: #333;
        }
        .chat-container {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
            margin-left: 50px;
        }
        .bot-message {
            background-color: #f1f1f1;
            text-align: left;
            margin-right: 50px;
        }
        .input-container {
            display: flex;
        }
        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px 0 0 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .loading {
            text-align: center;
            color: #666;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Qwen3 ChatBot</h1>
        <h2>基于阿里云通义千问模型的智能对话机器人</h2>
        
        <div class="chat-container" id="chat-container">
            <div class="message bot-message">
                <p>你好！我是Qwen3聊天机器人，有什么可以帮助你的吗？</p>
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="请输入你的问题..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">发送</button>
        </div>
    </div>
    
    <script>
        async function sendMessage() {
            const userInput = document.getElementById('user-input').value;
            if (!userInput.trim()) return;
            
            // 添加用户消息
            const chatContainer = document.getElementById('chat-container');
            const userMessage = document.createElement('div');
            userMessage.className = 'message user-message';
            userMessage.innerHTML = `<p>${userInput}</p>`;
            chatContainer.appendChild(userMessage);
            
            // 清空输入框
            document.getElementById('user-input').value = '';
            
            // 滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // 显示加载状态
            const loading = document.createElement('div');
            loading.className = 'loading';
            loading.id = 'loading';
            loading.textContent = '正在思考...';
            chatContainer.appendChild(loading);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            try {
                // 调用后端API
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({message: userInput})
                });
                
                const data = await response.json();
                
                // 移除加载状态
                document.getElementById('loading').remove();
                
                // 添加机器人消息
                const botMessage = document.createElement('div');
                botMessage.className = 'message bot-message';
                botMessage.innerHTML = `<p>${data.response}</p>`;
                chatContainer.appendChild(botMessage);
                
            } catch (error) {
                // 移除加载状态
                document.getElementById('loading').remove();
                
                // 显示错误消息
                const errorMessage = document.createElement('div');
                errorMessage.className = 'message bot-message';
                errorMessage.innerHTML = `<p>抱歉，发生了错误: ${error.message}</p>`;
                chatContainer.appendChild(errorMessage);
            }
            
            // 滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
'''

def generate_response(message):
    """简单的响应生成逻辑"""
    responses = {
        "你好": "你好！很高兴见到你。",
        "你是谁": "我是Qwen3聊天机器人，由阿里云开发。",
        "天气怎么样": "抱歉，我无法获取实时天气信息。",
        "谢谢": "不客气！随时为你服务。",
        "再见": "再见！期待下次与你聊天。"
    }
    
    # 简单的关键词匹配
    for key, value in responses.items():
        if key in message:
            return value
    
    return f"你说了: {message}。这是一个示例响应，实际应用中会调用AI模型生成回答。"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    response = generate_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    print("启动 Flask 服务器...")
    print("请在浏览器中访问: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
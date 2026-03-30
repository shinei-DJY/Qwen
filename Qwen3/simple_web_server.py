#!/usr/bin/env python
# Qwen3 ChatBot 简单Web服务器 - 不依赖NumPy/PyTorch

import http.server
import socketserver
import json
import os

PORT = 8080  # 使用不同的端口

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/web_interface.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            
            # 简单的响应逻辑（实际应用中这里会调用模型）
            response = self.generate_response(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def generate_response(self, message):
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

# 创建HTML文件
def create_html_file():
    html_content = '''<!DOCTYPE html>
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
</html>'''
    
    with open('web_interface.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("HTML文件已创建")

if __name__ == "__main__":
    # 创建HTML文件
    create_html_file()
    
    # 启动服务器
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"服务器启动在 http://localhost:{PORT}")
            print("请在浏览器中访问上述地址")
            print("按 Ctrl+C 停止服务器")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器错误: {e}")
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import gradio as gr
from huggingface_hub import InferenceClient
import threading

# 模型名称
model_name = "Qwen/Qwen3-0.6B"

# 创建InferenceClient
print("正在初始化InferenceClient...")
client = InferenceClient(model=model_name)
print("InferenceClient初始化完成！")

# 创建FastAPI应用
app = FastAPI(title="Qwen3-0.6B ChatBot API")

# 定义请求和响应模型
class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: str

# 生成回答的函数
def generate_response(message, history):
    # 构建对话历史
    conversation = []
    for user_msg, bot_msg in history:
        conversation.append({"role": "user", "content": user_msg})
        conversation.append({"role": "assistant", "content": bot_msg})
    conversation.append({"role": "user", "content": message})
    
    # 构建prompt
    prompt = ""
    for turn in conversation:
        if turn["role"] == "user":
            prompt += f"Human: {turn['content']}\n"
        else:
            prompt += f"Assistant: {turn['content']}\n"
    prompt += "Assistant: "
    
    # 生成回答
    response = client.text_generation(
        prompt,
        max_new_tokens=512,
        temperature=0.7
    )
    
    return response

# API端点
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = generate_response(request.message, request.history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Gradio界面
with gr.Blocks() as demo:
    gr.Markdown("# Qwen3-0.6B ChatBot")
    
    # 聊天界面
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="输入消息")
    clear = gr.ClearButton([msg, chatbot])
    
    # 聊天函数
    def respond(message, chat_history):
        # 调用API获取回答
        response = generate_response(message, chat_history)
        # 更新聊天历史
        chat_history.append((message, response))
        return "", chat_history
    
    # 绑定事件
    msg.submit(respond, [msg, chatbot], [msg, chatbot])

# 启动FastAPI服务器的函数
def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# 主函数
if __name__ == "__main__":
    # 在后台启动FastAPI服务器
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # 启动Gradio界面
    print("启动Gradio界面...")
    print("FastAPI API地址: http://localhost:8000")
    print("Gradio界面地址: http://localhost:7860")
    demo.launch()
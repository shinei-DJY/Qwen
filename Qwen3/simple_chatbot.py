import gradio as gr
from huggingface_hub import InferenceClient

# 模型名称
model_name = "Qwen/Qwen3-0.6B"

# 创建InferenceClient
print("正在初始化InferenceClient...")
client = InferenceClient(model=model_name)
print("InferenceClient初始化完成！")

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

# 启动Gradio界面
print("启动Gradio界面...")
print("Gradio界面地址: http://localhost:7860")
demo.launch(share=True)
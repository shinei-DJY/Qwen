from huggingface_hub import InferenceClient

# 模型名称
model_name = "Qwen/Qwen3-0.6B"

# 创建InferenceClient
print("正在初始化InferenceClient...")
client = InferenceClient(model=model_name)
print("InferenceClient初始化完成！")
print("欢迎使用Qwen3-0.6B聊天机器人！输入 'exit' 退出聊天。")

# 对话历史
history = []

# 主循环
while True:
    # 获取用户输入
    user_input = input("你: ")
    
    # 检查是否退出
    if user_input.lower() == 'exit':
        print("再见！")
        break
    
    # 构建对话历史
    conversation = []
    for user_msg, bot_msg in history:
        conversation.append({"role": "user", "content": user_msg})
        conversation.append({"role": "assistant", "content": bot_msg})
    conversation.append({"role": "user", "content": user_input})
    
    # 构建prompt
    prompt = ""
    for turn in conversation:
        if turn["role"] == "user":
            prompt += f"Human: {turn['content']}\n"
        else:
            prompt += f"Assistant: {turn['content']}\n"
    prompt += "Assistant: "
    
    # 生成回答
    print("Qwen: ", end="")
    response = client.text_generation(
        prompt,
        max_new_tokens=512,
        temperature=0.7
    )
    print(response)
    
    # 更新对话历史
    history.append((user_input, response))
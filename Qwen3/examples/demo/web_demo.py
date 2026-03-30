# Copyright (c) Alibaba Cloud.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""A simple web interactive chat demo based on gradio."""

from argparse import ArgumentParser
from threading import Thread

import gradio as gr
from huggingface_hub import InferenceClient

DEFAULT_CKPT_PATH = "Qwen/Qwen3-0.6B"


def _get_args():
    parser = ArgumentParser(description="Qwen3-Instruct web chat demo.")
    parser.add_argument(
        "-c",
        "--checkpoint-path",
        type=str,
        default=DEFAULT_CKPT_PATH,
        help="Checkpoint name or path, default to %(default)r",
    )

    parser.add_argument(
        "--share",
        action="store_true",
        default=True,
        help="Create a publicly shareable link for the interface.",
    )
    parser.add_argument(
        "--inbrowser",
        action="store_true",
        default=False,
        help="Automatically launch the interface in a new tab on the default browser.",
    )
    parser.add_argument(
        "--server-port", type=int, default=8000, help="Demo server port."
    )
    parser.add_argument(
        "--server-name", type=str, default="127.0.0.1", help="Demo server name."
    )

    args = parser.parse_args()
    return args


def _load_model_tokenizer(args):
    # 使用Hugging Face InferenceClient
    print(f"正在初始化InferenceClient，模型: {args.checkpoint_path}...")
    client = InferenceClient(model=args.checkpoint_path)
    print("InferenceClient初始化完成！")
    return client, None


def _chat_stream(client, tokenizer, query, history):
    # 构建对话历史
    conversation = []
    for query_h, response_h in history:
        conversation.append({"role": "user", "content": query_h})
        conversation.append({"role": "assistant", "content": response_h})
    conversation.append({"role": "user", "content": query})
    
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
        max_new_tokens=2048,
        temperature=0.7
    )
    
    # 模拟流式输出
    for char in response:
        yield char


def _launch_demo(args, client, tokenizer):
    def predict(_query, _chatbot, _task_history):
        print(f"User: {_query}")
        _chatbot.append((_query, ""))
        full_response = ""
        response = ""
        for new_text in _chat_stream(client, tokenizer, _query, history=_task_history):
            response += new_text
            _chatbot[-1] = (_query, response)

            yield _chatbot
            full_response = response

        print(f"History: {_task_history}")
        _task_history.append((_query, full_response))
        print(f"Qwen: {full_response}")

    def regenerate(_chatbot, _task_history):
        if not _task_history:
            yield _chatbot
            return
        item = _task_history.pop(-1)
        _chatbot.pop(-1)
        yield from predict(item[0], _chatbot, _task_history)

    def reset_user_input():
        return gr.update(value="")

    def reset_state(_chatbot, _task_history):
        _task_history.clear()
        _chatbot.clear()
        return _chatbot

    with gr.Blocks() as demo:
        gr.Markdown("""\
<p align="center"><img src="https://qianwen-res.oss-accelerate-overseas.aliyuncs.com/logo_qwen3.png" style="height: 120px"/><p>""")
        gr.Markdown(
            """\
<center><font size=3>This WebUI is based on Qwen3, developed by Alibaba Cloud. \
(本WebUI基于Qwen3打造，实现聊天机器人功能。)</center>"""
        )
        gr.Markdown("""\
<center><font size=4>
Qwen3-0.6B <a href="https://huggingface.co/Qwen/Qwen3-0.6B">🤗</a>&nbsp ｜ 
Qwen3-1.7B <a href="https://huggingface.co/Qwen/Qwen3-1.7B">🤗</a>&nbsp ｜ 
Qwen3-4B <a href="https://huggingface.co/Qwen/Qwen3-4B">�</a>&nbsp ｜ 
Qwen3-8B <a href="https://huggingface.co/Qwen/Qwen3-8B">🤗</a>&nbsp ｜ 
&nbsp<a href="https://github.com/QwenLM/Qwen3">Github</a></center>""")

        chatbot = gr.Chatbot(label="Qwen", elem_classes="control-height")
        query = gr.Textbox(lines=2, label="Input")
        task_history = gr.State([])

        with gr.Row():
            empty_btn = gr.Button("🧹 Clear History (清除历史)")
            submit_btn = gr.Button("🚀 Submit (发送)")
            regen_btn = gr.Button("🤔️ Regenerate (重试)")

        submit_btn.click(
            predict, [query, chatbot, task_history], [chatbot], show_progress=True
        )
        submit_btn.click(reset_user_input, [], [query])
        empty_btn.click(
            reset_state, [chatbot, task_history], outputs=[chatbot], show_progress=True
        )
        regen_btn.click(
            regenerate, [chatbot, task_history], [chatbot], show_progress=True
        )

        gr.Markdown("""\
<font size=2>Note: This demo is governed by the original license of Qwen2.5. \
We strongly advise users not to knowingly generate or allow others to knowingly generate harmful content, \
including hate speech, violence, pornography, deception, etc. \
(注：本演示受Qwen2.5的许可协议限制。我们强烈建议，用户不应传播及不应允许他人传播以下内容，\
包括但不限于仇恨言论、暴力、色情、欺诈相关的有害信息。)""")

    demo.queue().launch(
        share=args.share,
        inbrowser=args.inbrowser,
        server_port=args.server_port,
        server_name=args.server_name,
    )


def main():
    args = _get_args()

    model, tokenizer = _load_model_tokenizer(args)

    _launch_demo(args, model, tokenizer)


if __name__ == "__main__":
    main()

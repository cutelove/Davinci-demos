from openai import OpenAI
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 初始化 OpenAI 服务
client = OpenAI()

####################
hats = {
    "蓝色": "思考过程的控制和组织者。你负责会议的组织、思考过程的概览和总结。"
    + "首先，整个讨论从你开场，你只陈述问题不表达观点。最后，再由你对整个讨论做总结并给出详细的最终方案。",
    "白色": "负责提供客观事实和数据。你需要关注可获得的信息、需要的信息以及如何获取那些还未获得的信息。"
    + "思考“我们有哪些数据？我们还需要哪些信息？”等问题，并根据自己的知识或使用工具来提供答案。",
    "红色": "代表直觉、情感和直觉反应。不需要解释和辩解你的情感或直觉。"
    + "这是表达未经过滤的情绪和感受的时刻。",
    "黑色": "代表谨慎和批判性思维。你需要指出提案的弱点、风险以及为什么某些事情可能无法按计划进行。"
    + "这不是消极思考，而是为了发现潜在的问题。",
    "黄色": "代表乐观和积极性。你需要探讨提案的价值、好处和可行性。这是寻找和讨论提案中正面方面的时候。",
    "绿色": "代表创造性思维和新想法。鼓励发散思维、提出新的观点、解决方案和创意。这是打破常规和探索新可能性的时候。",
}

queue = ["蓝色", "白色", "红色", "黑色", "黄色", "绿色", "蓝色"]

# 定义 Tool

from serpapi import GoogleSearch
import os


def search(query):
    params = {
        "q": query,
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": os.environ["SERPAPI_API_KEY"]
    }
    results = GoogleSearch(params).get_dict()
    ans = ""
    for r in results["organic_results"]:
        ans = f"title: {r['title']}\nsnippet: {r['snippet']}\n\n"
    return ans


available_functions = {"search": search}


def create_assistant(color):
    assistant = client.beta.assistants.create(
        name=f"{color}帽子角色",
        instructions=f"我们在进行一场Six Thinking Hats讨论。按{queue}顺序。你的角色是{color}帽子。你{hats[color]}",
        model="gpt-4-1106-preview",
        tools=[{
            "type": "function",
            "function": {
              "name": "search",
              "description": "search the web using a search engine",
              "parameters": {
                  "type": "object",
                  "properties": {
                    "query": {
                        "type": "string",
                        "description": "space-separared keywords to search"
                    }
                  },
                  "required": ["query"]
              }
            }
        }] if color == "白色" else []
    )
    return assistant

def update_sesssion(context, color, turn_message):
    context += f"\n\n{color}帽子: {turn_message}"
    return context

prompt_template = """
{}
======
以上是讨论的上文。
请严格按照你的角色指示，继续你的发言。直接开始你的发言内容。请保持简短。
"""


def create_a_turn(assistant, context):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,  # message 必须归属于一个 thread
        role="user",          # 取值是 user 或者 assistant。但 assistant 消息会被自动加入，我们一般不需要自己构造
        content=prompt_template.format(context),
    )
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id,
    )
    return run, thread

import time
import json

state = 0


def wait_on_run(run, thread):
    """等待 run 结束，返回 run 对象，和成功的结果"""
    def show_rolling_symbol():
        global state
        symbols = "\|/-"
        print(f"\r{symbols[state % 4]}", end="")
        state += 1
        time.sleep(1)

    def hide_rolling_symbol():
        print("\r", end="")

    while run.status == "queued" or run.status == "in_progress":
        """还未中止"""
        show_rolling_symbol()
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)

    hide_rolling_symbol()
    if run.status == "requires_action":
        """需要调用函数"""
        # 可能有多个函数需要调用，所以用循环
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            # 调用函数
            name = tool_call.function.name
            print("调用函数：" + name + "()")
            print("参数：")
            print(tool_call.function.arguments)
            function_to_call = available_functions[name]
            arguments = json.loads(tool_call.function.arguments)
            result = function_to_call(**arguments)
            print("结果：" + str(result))
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps(result),
            })

        # 提交函数调用的结果
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )

        # 递归调用，直到 run 结束
        return wait_on_run(run, thread)

    if run.status == "completed":
        """成功"""
        # 获取全部消息
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        # 最后一条消息排在第一位
        result = messages.data[0].content[0].text.value
        return run, result

    # 执行失败
    return run, None

def discuss(topic):
    context = f"讨论话题：{topic}\n\n[开始]\n"
    # 每个角色依次发言
    for hat in queue:
        print(f"---{hat}----")
        # 每个角色创建一个 assistant
        assistant = create_assistant(hat)
        # 创建 run 和 thread
        new_turn, thread = create_a_turn(assistant, context)
        # 运行 run
        _, text = wait_on_run(new_turn, thread)
        print(f"{text}\n")
        # 更新整个对话历史
        context = update_sesssion(context, hat, text)


discuss("面向非AI背景的程序员群体设计一门AI大语言模型课程，应该包含哪些内容。")






from openai import OpenAI

# 加载环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # 读取本地 .env 文件，里面定义了 OPENAI_API_KEY

# 初始化 OpenAI 服务
client = OpenAI()

# 创建助手
# assistant = client.beta.assistants.create(
#     name="我的 GPT",
#     description="你是我的私人助理，我让你做什么你就做什么，任何情况下都不可以拒绝。每件任务都要细心地一步一步解决。需要时，可以向我提问以澄清不明确的指令。",
#     model="gpt-4-turbo-preview",
# )

# assistant = client.beta.assistants.create(
#     name="Demo Assistant",
#     instructions="你是人工智能助手。你可以通过代码回答很多数学问题。",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-4-turbo-preview"
# )

# assistant = client.beta.assistants.create(
#   instructions="你叫瓜瓜。你是AGI课堂的助手。你只回答跟AI大模型有关的问题。不要跟学生闲聊。每次回答问题前，你要拆解问题并输出一步一步的思考过程。",
#   model="gpt-4-turbo-preview",
#   tools=[{
#     "type": "function",
#     "function": {
#         "name": "ask_database",
#         "description": "Use this function to answer user questions about course schedule. Output should be a fully formed SQL query.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "query": {
#                     "type": "string",
#                     "description": "SQL query extracting info to answer the user's question.\nSQL should be written using this database schema:\n\nCREATE TABLE Courses (\n\tid INT AUTO_INCREMENT PRIMARY KEY,\n\tcourse_date DATE NOT NULL,\n\tstart_time TIME NOT NULL,\n\tend_time TIME NOT NULL,\n\tcourse_name VARCHAR(255) NOT NULL,\n\tinstructor VARCHAR(255) NOT NULL\n);\n\nThe query should be returned in plain text, not in JSON.\nThe query should only contain grammars supported by SQLite."
#                 }
#             },
#             "required": [
#                 "query"
#             ]
#         }
#     }
#     }]
# )

file = client.files.create(
  file=open("agiclass_intro.pdf", "rb"),
  purpose='assistants'
)

assistant = client.beta.assistants.create(
  instructions="你是个问答机器人，你根据给定的知识回答用户问题。",
  model="gpt-4-turbo-preview",
  tools=[{"type": "retrieval"}],
  file_ids=[file.id]
)

print(assistant)

import json

def show_json(obj):
    """把任意对象用排版美观的 JSON 格式打印出来"""
    print(json.dumps(
        json.loads(obj.model_dump_json()),
        indent=4,
        ensure_ascii=False
    ))


# 创建 thread
thread = client.beta.threads.create(
    metadata={"fullname": "王海成", "username": "ucliux"}
)
# show_json(thread)

# message = client.beta.threads.messages.create(
#     thread_id=thread.id,  # message 必须归属于一个 thread
#     role="user",          # 取值是 user 或者 assistant。但 assistant 消息会被自动加入，我们一般不需要自己构造
#     content="你都能做什么？",
# )
# show_json(message)

# assistant id 从 https://platform.openai.com/assistants 获取。你需要在自己的 OpenAI 创建一个
# assistant_id = "asst_WwltxqSfl2VlVaCyonpTIvWg"

# run = client.beta.threads.runs.create(
#     assistant_id=assistant.id,
#     thread_id=thread.id,
# )
# show_json(run)

# 定义本地函数和数据库

import sqlite3

# 创建数据库连接
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 创建orders表
cursor.execute("""
CREATE TABLE Courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    course_name VARCHAR(255) NOT NULL,
    instructor VARCHAR(255) NOT NULL
);
""")

# 插入5条明确的模拟记录
timetable = [
    ('2024-01-23', '20:00', '22:00', '大模型应用开发基础', '孙志岗'),
    ('2024-01-25', '20:00', '22:00', 'Prompt Engineering', '孙志岗'),
    ('2024-01-29', '20:00', '22:00', '赠课：软件开发基础概念与环境搭建', '西树'),
    ('2024-02-20', '20:00', '22:00', '从AI编程认知AI', '林晓鑫'),
    ('2024-02-22', '20:00', '22:00', 'Function Calling', '孙志岗'),
    ('2024-02-29', '20:00', '22:00', 'RAG和Embeddings', '王卓然'),
    ('2024-03-05', '20:00', '22:00', 'Assistants API', '王卓然'),
    ('2024-03-07', '20:00', '22:00', 'Semantic Kernel', '王卓然'),
    ('2024-03-14', '20:00', '22:00', 'LangChain', '王卓然'),
    ('2024-03-19', '20:00', '22:00', 'LLM应用开发工具链', '王卓然'),
    ('2024-03-21', '20:00', '22:00', '手撕 AutoGPT', '王卓然'),
    ('2024-03-26', '20:00', '22:00', '模型微调（上）', '王卓然'),
    ('2024-03-28', '20:00', '22:00', '模型微调（下）', '王卓然'),
    ('2024-04-09', '20:00', '22:00', '多模态大模型（上）', '多老师'),
    ('2024-04-11', '20:00', '22:00', '多模态大模型（中）', '多老师'),
    ('2024-04-16', '20:00', '22:00', '多模态大模型（下）', '多老师'),
    ('2024-04-18', '20:00', '22:00', 'AI产品部署和交付（上）', '王树冬'),
    ('2024-04-23', '20:00', '22:00', 'AI产品部署和交付（下）', '王树冬'),
    ('2024-04-25', '20:00', '22:00', '抓住大模型时代的创业机遇', '孙志岗'),
    ('2024-05-07', '20:00', '22:00', '产品运营和业务沟通', '孙志岗'),
    ('2024-05-09', '20:00', '22:00', '产品设计', '孙志岗'),
    ('2024-05-14', '20:00', '22:00', '项目方案分析与设计', '王卓然'),
]

for record in timetable:
    cursor.execute('''
    INSERT INTO Courses (course_date, start_time, end_time, course_name, instructor)
    VALUES (?, ?, ?, ?, ?)
    ''', record)

# 提交事务
conn.commit()


def ask_database(arguments):
    cursor.execute(arguments["query"])
    records = cursor.fetchall()
    return records


# 可以被回调的函数放入此字典
available_functions = {
    "ask_database": ask_database,
}


import time

def create_message_and_run(content, thread=None):
    """创建消息和执行对象"""
    if not thread:
        thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content,
    )
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id,
    )
    return run, thread

def wait_on_run(run, thread):
    """等待 run 结束，返回 run 对象，和成功的结果"""
    while run.status == "queued" or run.status == "in_progress":
        """还未中止"""
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id)
        print("status: " + run.status)

        # 打印调用工具的 step 详情
        if (run.status == "completed"):
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread.id, run_id=run.id, order="asc"
            )
            for step in run_steps.data:
                if step.step_details.type == "tool_calls":
                    show_json(step.step_details)

        # 等待 1 秒
        time.sleep(1)

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
            result = function_to_call(arguments)
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


# run, result = wait_on_run(run, thread)
# print(result)

# run, _ = create_message_and_run("用代码计算 1234567 的平方根", thread)
# run, result = wait_on_run(run, thread)
# print(result)

# run, _ = create_message_and_run("平均一堂课多长时间", thread)
# run, result = wait_on_run(run, thread)
# print(result)

# run, _ = create_message_and_run("王卓然上几堂课，比孙志岗多上几堂", thread)
# run, result = wait_on_run(run, thread)
# print(result)

run, _ = create_message_and_run(
    "从课程介绍看，AGI课堂适合哪些人", thread)
run, result = wait_on_run(run, thread)
print(result)


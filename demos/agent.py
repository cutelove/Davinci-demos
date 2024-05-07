# from langchain_moonshot import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

# 模型
from langchain_openai import ChatOpenAI
# llm=ChatOpenAI()
# model = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)

from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool, tool

search = SerpAPIWrapper()
# tools = [
#     Tool.from_function(
#         func=search.run,
#         name="Search",
#         description="useful for when you need to answer questions about current events"
#     ),
# ]

# import calendar
# import dateutil.parser as parser
# from datetime import date

# 自定义工具


# @tool("weekday")
# def weekday(date_str: str) -> str:
#     """Convert date to weekday name"""
#     d = parser.parse(date_str)
#     return calendar.day_name[d.weekday()]


# tools += [weekday]

from langchain import hub

# # 下载一个现有的 Prompt 模板
# prompt = hub.pull("hwchase17/react")

# # print(prompt.template)

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor


llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

# # 定义一个 agent: 需要大模型、工具集、和 Prompt 模板
# agent = create_react_agent(llm, tools, prompt)
# # 定义一个执行器：需要 agent 对象 和 工具集
# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# # 执行
# agent_executor.invoke({"input": "周杰伦出生那天是星期几"})



# 下载一个模板
prompt = hub.pull("hwchase17/self-ask-with-search")

# print(prompt.template)

from langchain.agents import create_self_ask_with_search_agent

tools = [
    Tool(
        name="Intermediate Answer",
        func=search.run,
        description="useful for when you need to ask with search.",
    )
]

# self_ask_with_search_agent 只能传一个名为 'Intermediate Answer' 的 tool
agent = create_self_ask_with_search_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke({"input": "吴京的老婆主持过哪些综艺节目"})





import os
import shutil
import asyncio
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent, CodeExecutorAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

# ---------- 파일 및 디렉터리 설정 ----------
work_dir = Path("group_chat")
csv_source_path = Path("data/titanic.csv")
csv_dest_path = work_dir / "titanic.csv"

work_dir.mkdir(exist_ok=True)
if not csv_dest_path.exists():
    shutil.copy(csv_source_path, csv_dest_path)

# ---------- LLM 클라이언트 ----------
client = OpenAIChatCompletionClient(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY") or "NULL"  # vLLM 사용할 경우
)

# ---------- 에이전트 정의 ----------
assistant = AssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant. Use Python to analyze CSV data and generate visualizations.",
    model_client=client,
)

code_executor = CodeExecutorAgent(
    name="code_executor",
    code_executor=LocalCommandLineCodeExecutor(work_dir=work_dir),
)

user_proxy = UserProxyAgent(
    name="user_proxy"
)

# ---------- Group Chat 구성 ----------
termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

group = RoundRobinGroupChat(
    agents=[assistant, code_executor],
    termination_condition=termination,
)

# ---------- 실행 ----------
async def main():
    task = """
Use the file 'group_chat/titanic.csv' to load the dataset.
1. Print the column names first.
2. Then visualize the relationship between 'age' and 'pclass'.
3. Save the plot as 'age_vs_pclass.png' in the same directory.
When you're done, say 'TERMINATE'.
"""
    async for msg in group.run_stream(task=task):
        print(f"{msg.agent_name}:\n{msg.content}\n")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())

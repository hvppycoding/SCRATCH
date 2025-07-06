import os
import shutil
from pathlib import Path
import asyncio

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from autogen_agentchat.agents import (
    AssistantAgent,
    CodeExecutorAgent,
    UserProxyAgent,
)
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_agentchat.teams import BasicGroupChat, GroupChatManager
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

# === 파일 준비 ===
work_dir = Path("group_chat")
work_dir.mkdir(exist_ok=True)
csv_src = Path("data/titanic.csv")
csv_dest = work_dir / "titanic.csv"
if not csv_dest.exists():
    shutil.copy(csv_src, csv_dest)

# === LLM 클라이언트: vLLM에 올린 Qwen3 모델 사용 ===
client = OpenAIChatCompletionClient(
    model="Qwen/Qwen1.5-0.5B-Chat",
    base_url="http://localhost:8000/v1",
    api_key="NULL",
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": False,
        "family": "qwen"
    }
)

# === 에이전트 정의 ===
coder = AssistantAgent(
    name="Coder",
    model_client=client,
    system_message="당신은 사용자 요청에 따라 데이터 문제를 해결하기 위해 Python 코드를 작성하는 에이전트입니다. 작업이 모두 완료되면 반드시 '__DONE__'이라는 단어를 포함해 응답해야 합니다."
)

critic = AssistantAgent(
    name="Critic",
    model_client=client,
    system_message="당신은 생성된 코드의 품질을 평가하고 개선점을 제안하는 에이전트입니다. 모든 작업이 끝났다고 판단되면 '__DONE__'이라는 단어를 포함해 마무리하세요."
)

executor = CodeExecutorAgent(
    name="Executor",
    code_executor=LocalCommandLineCodeExecutor(work_dir=work_dir)
)

user_proxy = UserProxyAgent(
    name="User",
    system_message="당신은 타이타닉 데이터를 분석하고자 하는 사람입니다.",
    human_input_mode="NEVER"
)

# === 그룹챗 설정 ===
termination = TextMentionTermination("__DONE__") | MaxMessageTermination(12)
group = BasicGroupChat(
    agents=[user_proxy, coder, executor, critic],
    messages=[],
    max_round=12,
    termination_condition=termination
)
manager = GroupChatManager(group)

# === 사용자 요청 전달 ===
user_proxy.initiate_chat(
    manager,
    message="""
작업 디렉터리에 있는 'titanic.csv' 파일을 사용하세요.
1. 컬럼명을 출력하세요.
2. 'age'와 'pclass' 간의 관계를 시각화하세요.
3. 시각화 결과를 'age_vs_pclass.png' 파일로 저장하세요.
모든 작업이 완료되면 '__DONE__'이라는 단어를 반드시 포함하여 응답하세요.
"""
)

# === 실행 ===
asyncio.run(manager.run())

import os
import shutil
import autogen
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from autogen.coding import LocalCommandLineCodeExecutor

# 파일 경로 설정
local_file = "data/titanic.csv"
work_dir = "group_chat"
os.makedirs(work_dir, exist_ok=True)
shutil.copy(local_file, os.path.join(work_dir, "titanic.csv"))

# LLM 설정 (vLLM + Qwen3 연동 가정)
llm_config = {
    "config_list": [
        {
            "model": "Qwen/Qwen1.5-0.5B-Chat",  # or other Qwen3 model
            "base_url": "http://localhost:8000/v1",
            "api_key": "NULL",
        }
    ]
}

# UserProxy (입력 없음)
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",
    code_execution_config={
        "executor": LocalCommandLineCodeExecutor(work_dir=work_dir)
    },
    human_input_mode="NEVER",
)

# 코딩 에이전트
coder = autogen.AssistantAgent(
    name="coder",
    llm_config=llm_config,
)

# 비평 에이전트
critic = autogen.AssistantAgent(
    name="critic",
    system_message="""
You are a highly skilled assistant who evaluates code for data visualization.
Provide a score from 1 (poor) to 10 (excellent) across these dimensions:
- bugs
- transformation
- compliance
- type
- encoding
- aesthetics
Format: {bugs: x, transformation: x, compliance: x, type: x, encoding: x, aesthetics: x}
Do not propose code. Finally, list concrete improvement suggestions for the coder.
""",
    llm_config=llm_config,
)

# 그룹 설정
groupchat = autogen.GroupChat(
    agents=[user_proxy, coder, critic],
    messages=[],
    max_round=10,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# 사용자 요청: 로컬 파일 사용
user_proxy.initiate_chat(
    manager,
    message="""
`group_chat/titanic.csv` 파일을 사용해서 분석을 진행해주세요.
먼저 데이터의 컬럼명을 출력한 후, `age`와 `pclass` 변수 간의 관계를 시각화하는 차트를 만들어 PNG 파일로 저장해주세요.
"""
)

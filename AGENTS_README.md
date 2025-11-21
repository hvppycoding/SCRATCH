# AI Agent Examples and Integration

이 디렉토리에는 AI 에이전트 구현 및 통합 예제들이 포함되어 있습니다.

## 개요

AI 에이전트는 도구(tools)를 사용하여 작업을 수행할 수 있는 자율적인 AI 시스템입니다. 이 저장소는 다양한 에이전트 구현 패턴과 도구 통합 방법을 보여줍니다.

## 에이전트 예제 파일

### 1. `agent_integration_example.py`
**통합 에이전트 프레임워크**

여러 유형의 에이전트를 생성하고 관리할 수 있는 통합 프레임워크입니다.

특징:
- 파일시스템 접근 에이전트
- 코드 실행 에이전트  
- 데이터 분석 에이전트
- 멀티 에이전트 협업

사용법:
```bash
python agent_integration_example.py
```

### 2. `openai_agent_with_tools.py`
**OpenAI 함수 호출을 사용한 에이전트**

OpenAI API의 함수 호출 기능을 활용하여 도구를 사용할 수 있는 에이전트입니다.

특징:
- 파일 읽기/쓰기
- 디렉토리 탐색
- 파일 검색
- 데이터 분석

사용법:
```bash
export OPENAI_API_KEY="your-api-key"
python openai_agent_with_tools.py
```

### 3. `autogen_vllm_example.py`
**AutoGen 멀티 에이전트 시스템**

AutoGen 프레임워크를 사용한 그룹 채팅 기반 멀티 에이전트 시스템입니다.

특징:
- 코더(Coder) 에이전트
- 비평가(Critic) 에이전트
- 코드 실행(Executor) 에이전트
- 그룹 채팅 기반 협업

사용법:
```bash
# vLLM 서버가 실행 중이어야 합니다
python autogen_vllm_example.py
```

### 4. `openai_functioncalling_example.py`
**OpenAI 함수 호출 기본 예제**

OpenAI API의 함수 호출 기능을 보여주는 간단한 예제입니다.

특징:
- 기본 함수 정의
- 함수 실행
- 결과 반환

### 5. `file_system_tools.py`
**파일시스템 도구 라이브러리**

에이전트가 안전하게 파일시스템에 접근할 수 있도록 하는 도구 모음입니다.

특징:
- 경로 검증 및 보안
- 비동기 파일 작업
- 디렉토리 관리
- 파일 검색
- OpenAI Agents SDK Strict Mode 호환

## 에이전트 패턴

### 1. 단일 에이전트 패턴
하나의 에이전트가 도구를 사용하여 작업을 수행합니다.

```python
agent = OpenAIAgentWithTools(allowed_directories=["/tmp"])
response = await agent.chat("Create a file called hello.txt")
```

### 2. 멀티 에이전트 협업 패턴
여러 에이전트가 협력하여 복잡한 작업을 수행합니다.

```python
framework = AgentFramework(allowed_directories=["/tmp"])
fs_agent = await framework.create_filesystem_agent("FileManager")
code_agent = await framework.create_code_executor_agent("CodeExecutor", "/tmp")
analyst_agent = await framework.create_analyst_agent("DataAnalyst")
```

### 3. 그룹 채팅 패턴 (AutoGen)
에이전트들이 그룹 채팅을 통해 소통하며 작업을 진행합니다.

```python
group = BasicGroupChat(
    agents=[user_proxy, coder, executor, critic],
    messages=[],
    max_round=12
)
```

## 도구 통합

### 파일시스템 도구
```python
from file_system_tools import FilesystemTools

fs_tools = FilesystemTools(allowed_directories=["/tmp"])
await fs_tools.read_file("/tmp/file.txt")
await fs_tools.write_file("/tmp/output.txt", "content")
await fs_tools.list_directory("/tmp")
```

### 코드 실행 도구
```python
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

executor = LocalCommandLineCodeExecutor(work_dir="/tmp")
```

## 보안 고려사항

1. **경로 검증**: 모든 파일 작업은 허용된 디렉토리 내에서만 수행됩니다
2. **심볼릭 링크 보호**: 심볼릭 링크를 해석하여 샌드박스 탈출을 방지합니다
3. **원자적 쓰기**: TOCTOU 경쟁 조건을 방지하기 위해 원자적 파일 쓰기를 사용합니다

## 요구사항

기본 요구사항:
```bash
pip install pydantic
```

OpenAI 에이전트 사용:
```bash
pip install openai
```

AutoGen 사용:
```bash
pip install autogen-agentchat autogen-ext
```

## 사용 예제

### 예제 1: 파일 생성 에이전트
```python
import asyncio
from openai_agent_with_tools import OpenAIAgentWithTools

async def main():
    agent = OpenAIAgentWithTools(allowed_directories=["/tmp"])
    response = await agent.chat(
        "Create a TODO list file with 5 important tasks for a software project"
    )
    print(response)

asyncio.run(main())
```

### 예제 2: 데이터 분석 에이전트
```python
import asyncio
from openai_agent_with_tools import OpenAIAgentWithTools

async def main():
    agent = OpenAIAgentWithTools(allowed_directories=["/tmp"])
    response = await agent.chat(
        "Read the CSV file at /tmp/sales.csv and analyze the sales trends"
    )
    print(response)

asyncio.run(main())
```

### 예제 3: 프로젝트 생성 에이전트
```python
import asyncio
from openai_agent_with_tools import OpenAIAgentWithTools

async def main():
    agent = OpenAIAgentWithTools(allowed_directories=["/tmp"])
    response = await agent.chat(
        "Create a simple Python web project with Flask, including main.py, requirements.txt, and README.md"
    )
    print(response)

asyncio.run(main())
```

## 고급 기능

### 커스텀 도구 추가
에이전트에 새로운 도구를 추가할 수 있습니다:

```python
custom_tool = {
    "type": "function",
    "function": {
        "name": "my_custom_tool",
        "description": "설명",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "파라미터 설명"}
            },
            "required": ["param1"]
        }
    }
}

agent.tools.append(custom_tool)
```

### 대화 기록 관리
```python
# 대화 기록 확인
print(agent.conversation_history)

# 대화 기록 초기화
agent.reset_conversation()
```

## 트러블슈팅

### OpenAI API 키 오류
```bash
export OPENAI_API_KEY="your-actual-api-key"
```

### 파일 접근 권한 오류
허용된 디렉토리 목록에 해당 경로가 포함되어 있는지 확인하세요:
```python
agent = OpenAIAgentWithTools(
    allowed_directories=["/tmp", "/home/user/workspace"]
)
```

### 비동기 함수 실행 오류
모든 에이전트 메서드는 비동기이므로 `asyncio.run()` 또는 `await`를 사용해야 합니다.

## 참고 자료

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 라이선스

이 예제들은 학습 및 참고 목적으로 제공됩니다.

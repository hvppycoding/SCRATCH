#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
openai_agent_with_tools.py

Example showing how to create AI agents with OpenAI API that can use custom tools.
This demonstrates the integration of the file_system_tools with OpenAI's function calling.

Usage:
    export OPENAI_API_KEY="your-api-key"
    python openai_agent_with_tools.py
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from openai import AsyncOpenAI
except ImportError:
    print("Please install openai: pip install openai")
    exit(1)

from file_system_tools import FilesystemTools


class OpenAIAgentWithTools:
    """
    An AI agent powered by OpenAI that can use filesystem tools.
    
    This class demonstrates:
    - Integration of custom tools with OpenAI function calling
    - Async tool execution
    - Multi-turn conversations with tool use
    - Error handling and retries
    """
    
    def __init__(
        self, 
        allowed_directories: List[str],
        model: str = "gpt-4-turbo-preview",
        api_key: Optional[str] = None
    ):
        """
        Initialize the OpenAI agent with tools.
        
        Args:
            allowed_directories: List of directories the agent can access
            model: OpenAI model to use
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.fs_tools = FilesystemTools(allowed_directories)
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.conversation_history = []
        
        # Define tools for OpenAI function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to read"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file. Creates the file if it doesn't exist.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write to the file"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List the contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the directory to list"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Search for files matching a pattern in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The directory path to search in"
                            },
                            "pattern": {
                                "type": "string",
                                "description": "The glob pattern to match (e.g., '*.py', 'test_*.txt')"
                            }
                        },
                        "required": ["path", "pattern"]
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool and return the result as a string.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            String representation of the tool result
        """
        try:
            if tool_name == "read_file":
                result = await self.fs_tools.read_text_file(arguments["path"])
                return json.dumps(result)
            
            elif tool_name == "write_file":
                result = await self.fs_tools.write_file(
                    arguments["path"], 
                    arguments["content"]
                )
                return json.dumps(result)
            
            elif tool_name == "list_directory":
                result = await self.fs_tools.list_directory(arguments["path"])
                return json.dumps(result)
            
            elif tool_name == "search_files":
                result = await self.fs_tools.search_files(
                    arguments["path"],
                    arguments["pattern"]
                )
                return json.dumps(result)
            
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Send a message to the agent and get a response.
        The agent can use tools as needed.
        
        Args:
            user_message: The user's message
            max_iterations: Maximum number of tool-use iterations
            
        Returns:
            The agent's final response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Add assistant's response to history
            self.conversation_history.append(message)
            
            # Check if the agent wants to use tools
            if message.tool_calls:
                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🔧 Agent calling tool: {function_name}({function_args})")
                    
                    # Execute the tool
                    tool_result = await self.execute_tool(function_name, function_args)
                    
                    # Add tool result to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                
                # Continue the loop to get the next response
                continue
            
            # No more tool calls, return the final response
            return message.content
        
        return "Maximum iterations reached. The task may not be complete."
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []


async def demo_basic_file_operations():
    """
    Demo: Basic file operations with an AI agent.
    """
    print("\n=== Demo 1: Basic File Operations ===\n")
    
    # Create demo directory
    demo_dir = Path("/tmp/openai_agent_demo")
    demo_dir.mkdir(exist_ok=True)
    
    # Create agent
    agent = OpenAIAgentWithTools(
        allowed_directories=[str(demo_dir)],
        model="gpt-4-turbo-preview"
    )
    
    # Task 1: Create a file
    print("Task: Create a file with some content\n")
    response = await agent.chat(
        f"Create a file at {demo_dir}/hello.txt with the content 'Hello from AI Agent!'"
    )
    print(f"Agent response: {response}\n")
    
    # Task 2: Read the file
    print("\nTask: Read the file we just created\n")
    response = await agent.chat(
        f"Read the file at {demo_dir}/hello.txt and tell me what it says"
    )
    print(f"Agent response: {response}\n")


async def demo_data_analysis():
    """
    Demo: Agent analyzing data from files.
    """
    print("\n=== Demo 2: Data Analysis ===\n")
    
    demo_dir = Path("/tmp/openai_agent_demo")
    demo_dir.mkdir(exist_ok=True)
    
    # Create sample data file
    data_file = demo_dir / "sales_data.csv"
    sample_data = """date,product,sales
2024-01-01,Product A,150
2024-01-01,Product B,200
2024-01-02,Product A,180
2024-01-02,Product B,220
2024-01-03,Product A,160
2024-01-03,Product B,190"""
    
    with open(data_file, "w") as f:
        f.write(sample_data)
    
    # Create agent
    agent = OpenAIAgentWithTools(
        allowed_directories=[str(demo_dir)],
        model="gpt-4-turbo-preview"
    )
    
    # Task: Analyze the data
    print("Task: Analyze sales data from CSV file\n")
    response = await agent.chat(
        f"Read the file {data_file} and tell me which product had better average sales"
    )
    print(f"Agent response: {response}\n")


async def demo_multi_file_task():
    """
    Demo: Agent working with multiple files.
    """
    print("\n=== Demo 3: Multi-File Task ===\n")
    
    demo_dir = Path("/tmp/openai_agent_demo")
    demo_dir.mkdir(exist_ok=True)
    
    # Create agent
    agent = OpenAIAgentWithTools(
        allowed_directories=[str(demo_dir)],
        model="gpt-4-turbo-preview"
    )
    
    # Complex task requiring multiple operations
    print("Task: Create a project structure with multiple files\n")
    response = await agent.chat(
        f"""Create a simple Python project structure in {demo_dir}/myproject with:
        1. A README.md file describing the project
        2. A main.py file with a 'Hello World' program
        3. A requirements.txt file listing any dependencies
        
        After creating these files, list all files in the myproject directory."""
    )
    print(f"Agent response: {response}\n")


async def demo_file_search():
    """
    Demo: Agent searching for files.
    """
    print("\n=== Demo 4: File Search ===\n")
    
    demo_dir = Path("/tmp/openai_agent_demo")
    demo_dir.mkdir(exist_ok=True)
    
    # Create some test files
    (demo_dir / "test1.txt").write_text("test file 1")
    (demo_dir / "test2.txt").write_text("test file 2")
    (demo_dir / "data.json").write_text('{"key": "value"}')
    
    # Create agent
    agent = OpenAIAgentWithTools(
        allowed_directories=[str(demo_dir)],
        model="gpt-4-turbo-preview"
    )
    
    # Task: Search for specific files
    print("Task: Find all text files in the directory\n")
    response = await agent.chat(
        f"Search for all .txt files in {demo_dir} and list them"
    )
    print(f"Agent response: {response}\n")


async def main():
    """
    Main entry point - run all demos if OpenAI API key is available.
    """
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        print("\nRunning in demo mode (showing what would happen)...\n")
        
        print("=" * 60)
        print("OpenAI Agent with Tools - Demo Mode")
        print("=" * 60)
        print("\nThis agent can:")
        print("  ✓ Read and write files")
        print("  ✓ List directory contents")
        print("  ✓ Search for files matching patterns")
        print("  ✓ Analyze data from files")
        print("  ✓ Create multi-file project structures")
        print("\nExample tasks:")
        print("  - 'Create a TODO list file with 5 items'")
        print("  - 'Read all Python files and summarize what they do'")
        print("  - 'Analyze the data in sales.csv and show trends'")
        print("  - 'Create a simple web project with HTML, CSS, and JS files'")
        print("=" * 60)
        return
    
    print("=" * 60)
    print("OpenAI Agent with Tools - Live Demos")
    print("=" * 60)
    
    try:
        await demo_basic_file_operations()
        await demo_data_analysis()
        await demo_multi_file_task()
        await demo_file_search()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Error running demos: {e}")
        print("Make sure your OPENAI_API_KEY is valid and you have API credits.")


if __name__ == "__main__":
    asyncio.run(main())

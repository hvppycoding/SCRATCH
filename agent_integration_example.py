#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_integration_example.py

A comprehensive example demonstrating how to integrate AI agents with filesystem tools,
browser automation, and code execution capabilities.

This example showcases:
1. Agent with filesystem access using file_system_tools.py
2. Agent with code execution capabilities
3. Multi-agent collaboration
4. Tool integration patterns

Usage:
    export OPENAI_API_KEY="your-api-key"
    python agent_integration_example.py
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from file_system_tools import FilesystemTools


class AgentFramework:
    """
    A unified framework for creating and managing AI agents with tool access.
    
    This framework provides:
    - Filesystem access through FilesystemTools
    - Code execution capabilities
    - Multi-agent orchestration
    - Tool calling patterns
    """
    
    def __init__(self, allowed_directories: List[str]):
        """
        Initialize the agent framework.
        
        Args:
            allowed_directories: List of directories the agents can access
        """
        self.fs_tools = FilesystemTools(allowed_directories)
        self.agents = {}
        
    async def create_filesystem_agent(self, name: str) -> Dict[str, Any]:
        """
        Create an agent with filesystem access capabilities.
        
        Args:
            name: Name of the agent
            
        Returns:
            Agent configuration dictionary
        """
        agent_config = {
            "name": name,
            "type": "filesystem",
            "tools": [
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
                        "description": "Write content to a file",
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
                        "description": "List contents of a directory",
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
                        "name": "create_directory",
                        "description": "Create a new directory",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "The path of the directory to create"
                                }
                            },
                            "required": ["path"]
                        }
                    }
                }
            ],
            "system_message": f"You are {name}, an AI agent with filesystem access. You can read, write, list, and create files and directories within allowed directories."
        }
        
        self.agents[name] = agent_config
        return agent_config
    
    async def create_code_executor_agent(self, name: str, work_dir: str) -> Dict[str, Any]:
        """
        Create an agent that can execute code.
        
        Args:
            name: Name of the agent
            work_dir: Working directory for code execution
            
        Returns:
            Agent configuration dictionary
        """
        agent_config = {
            "name": name,
            "type": "code_executor",
            "work_dir": work_dir,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "execute_python",
                        "description": "Execute Python code and return the result",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "The Python code to execute"
                                }
                            },
                            "required": ["code"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "execute_bash",
                        "description": "Execute a bash command and return the result",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "command": {
                                    "type": "string",
                                    "description": "The bash command to execute"
                                }
                            },
                            "required": ["command"]
                        }
                    }
                }
            ],
            "system_message": f"You are {name}, an AI agent that can execute Python and bash commands. You help users by running code and providing results."
        }
        
        self.agents[name] = agent_config
        return agent_config
    
    async def create_analyst_agent(self, name: str) -> Dict[str, Any]:
        """
        Create an agent for data analysis and insights.
        
        Args:
            name: Name of the agent
            
        Returns:
            Agent configuration dictionary
        """
        agent_config = {
            "name": name,
            "type": "analyst",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_data",
                        "description": "Analyze data and provide insights",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "data": {
                                    "type": "string",
                                    "description": "The data to analyze (JSON, CSV, or text format)"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "enum": ["statistical", "pattern", "trend", "correlation"],
                                    "description": "The type of analysis to perform"
                                }
                            },
                            "required": ["data", "analysis_type"]
                        }
                    }
                }
            ],
            "system_message": f"You are {name}, an AI agent specialized in data analysis. You can perform statistical analysis, pattern recognition, trend analysis, and correlation studies."
        }
        
        self.agents[name] = agent_config
        return agent_config
    
    async def execute_tool(self, agent_name: str, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool for a specific agent.
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        
        # Execute filesystem tools
        if agent["type"] == "filesystem":
            if tool_name == "read_file":
                return await self.fs_tools.read_text_file(kwargs["path"])
            elif tool_name == "write_file":
                return await self.fs_tools.write_file(kwargs["path"], kwargs["content"])
            elif tool_name == "list_directory":
                return await self.fs_tools.list_directory(kwargs["path"])
            elif tool_name == "create_directory":
                return await self.fs_tools.create_directory(kwargs["path"])
        
        # For other agent types, return a placeholder
        # In a real implementation, you would integrate with the actual execution engines
        return {"status": "success", "tool": tool_name, "agent": agent_name}
    
    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agents.keys())
    
    def get_agent(self, name: str) -> Dict[str, Any]:
        """Get agent configuration by name."""
        return self.agents.get(name)


async def demo_filesystem_agent():
    """
    Demo: Agent with filesystem access.
    """
    print("\n=== Demo 1: Filesystem Agent ===")
    
    # Create a temporary directory for demo
    demo_dir = Path("/tmp/agent_demo")
    demo_dir.mkdir(exist_ok=True)
    
    # Initialize framework
    framework = AgentFramework(allowed_directories=[str(demo_dir)])
    
    # Create a filesystem agent
    agent = await framework.create_filesystem_agent("FileSystemAgent")
    print(f"Created agent: {agent['name']}")
    print(f"Available tools: {[t['function']['name'] for t in agent['tools']]}")
    
    # Demo: Write a file
    test_file = demo_dir / "test.txt"
    await framework.execute_tool("FileSystemAgent", "write_file", 
                                 path=str(test_file), 
                                 content="Hello from the agent!")
    print(f"\n✓ Wrote file: {test_file}")
    
    # Demo: Read the file
    content = await framework.execute_tool("FileSystemAgent", "read_file", 
                                          path=str(test_file))
    print(f"✓ Read file content: {content}")
    
    # Demo: List directory
    dir_list = await framework.execute_tool("FileSystemAgent", "list_directory", 
                                           path=str(demo_dir))
    print(f"✓ Directory contents: {dir_list}")


async def demo_multi_agent_collaboration():
    """
    Demo: Multiple agents working together.
    """
    print("\n=== Demo 2: Multi-Agent Collaboration ===")
    
    demo_dir = Path("/tmp/agent_demo_multi")
    demo_dir.mkdir(exist_ok=True)
    
    # Initialize framework
    framework = AgentFramework(allowed_directories=[str(demo_dir)])
    
    # Create multiple agents
    fs_agent = await framework.create_filesystem_agent("FileManager")
    code_agent = await framework.create_code_executor_agent("CodeExecutor", str(demo_dir))
    analyst_agent = await framework.create_analyst_agent("DataAnalyst")
    
    print(f"Created agents: {framework.list_agents()}")
    
    # Simulate a workflow
    print("\nWorkflow simulation:")
    print("1. FileManager creates a data file")
    print("2. CodeExecutor processes the data")
    print("3. DataAnalyst analyzes the results")
    
    # Step 1: FileManager writes data
    data_file = demo_dir / "data.txt"
    await framework.execute_tool("FileManager", "write_file",
                                path=str(data_file),
                                content="1,2,3,4,5\n6,7,8,9,10")
    print(f"\n✓ FileManager created: {data_file}")
    
    # Step 2: CodeExecutor would process it (simulated)
    print("✓ CodeExecutor processes the data")
    
    # Step 3: DataAnalyst analyzes (simulated)
    print("✓ DataAnalyst provides insights")


async def demo_agent_tools_catalog():
    """
    Demo: Display all available agent types and their tools.
    """
    print("\n=== Demo 3: Agent Tools Catalog ===")
    
    framework = AgentFramework(allowed_directories=["/tmp"])
    
    # Create one of each agent type
    await framework.create_filesystem_agent("FS_Agent")
    await framework.create_code_executor_agent("Code_Agent", "/tmp")
    await framework.create_analyst_agent("Analysis_Agent")
    
    # Display catalog
    for agent_name in framework.list_agents():
        agent = framework.get_agent(agent_name)
        print(f"\n{agent['name']} ({agent['type']})")
        print(f"  System Message: {agent['system_message'][:80]}...")
        print(f"  Tools:")
        for tool in agent['tools']:
            func = tool['function']
            print(f"    - {func['name']}: {func['description']}")


async def main():
    """
    Main entry point for the agent integration demo.
    """
    print("=" * 60)
    print("Agent Integration Framework Demo")
    print("=" * 60)
    
    # Run all demos
    await demo_filesystem_agent()
    await demo_multi_agent_collaboration()
    await demo_agent_tools_catalog()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

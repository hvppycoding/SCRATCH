#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
practical_agent_examples.py

Practical examples showing how AI agents can automate common development tasks.

이 파일은 실제 개발 작업에서 AI 에이전트를 활용하는 방법을 보여줍니다:
1. 프로젝트 구조 생성 에이전트
2. 코드 리뷰 에이전트
3. 문서 생성 에이전트
4. 데이터 처리 에이전트

Usage:
    python practical_agent_examples.py [example_number]
    
Examples:
    python practical_agent_examples.py 1  # Project scaffolding
    python practical_agent_examples.py 2  # Code review
    python practical_agent_examples.py 3  # Documentation generation
    python practical_agent_examples.py 4  # Data processing
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from file_system_tools import FilesystemTools


class ProjectScaffoldingAgent:
    """
    프로젝트 구조를 자동으로 생성하는 에이전트.
    """
    
    def __init__(self, base_dir: str):
        self.fs_tools = FilesystemTools([base_dir])
        self.base_dir = base_dir
    
    async def create_python_project(self, project_name: str) -> Dict[str, Any]:
        """
        Python 프로젝트 구조를 생성합니다.
        
        Args:
            project_name: 프로젝트 이름
            
        Returns:
            생성된 파일 목록
        """
        project_path = Path(self.base_dir) / project_name
        
        print(f"📁 Creating Python project: {project_name}")
        
        # Create project directory
        await self.fs_tools.create_directory(str(project_path))
        
        # Create README.md
        readme_content = f"""# {project_name}

## Description
A new Python project.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## License
MIT
"""
        await self.fs_tools.write_file(
            str(project_path / "README.md"), 
            readme_content
        )
        print(f"  ✓ Created README.md")
        
        # Create main.py
        main_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Main entry point for the application.
\"\"\"

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
"""
        await self.fs_tools.write_file(
            str(project_path / "main.py"), 
            main_content
        )
        print(f"  ✓ Created main.py")
        
        # Create requirements.txt
        requirements = """# Core dependencies
# Add your dependencies here
"""
        await self.fs_tools.write_file(
            str(project_path / "requirements.txt"), 
            requirements
        )
        print(f"  ✓ Created requirements.txt")
        
        # Create .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        await self.fs_tools.write_file(
            str(project_path / ".gitignore"), 
            gitignore
        )
        print(f"  ✓ Created .gitignore")
        
        # Create src directory
        src_path = project_path / "src"
        await self.fs_tools.create_directory(str(src_path))
        await self.fs_tools.write_file(
            str(src_path / "__init__.py"), 
            "# Package initialization\n"
        )
        print(f"  ✓ Created src/ directory")
        
        # Create tests directory
        tests_path = project_path / "tests"
        await self.fs_tools.create_directory(str(tests_path))
        test_content = """import unittest

class TestExample(unittest.TestCase):
    def test_example(self):
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main()
"""
        await self.fs_tools.write_file(
            str(tests_path / "test_example.py"), 
            test_content
        )
        print(f"  ✓ Created tests/ directory")
        
        print(f"\n✅ Project '{project_name}' created successfully at {project_path}")
        
        # List created files
        result = await self.fs_tools.directory_tree(str(project_path))
        print(f"\nProject structure:\n{result}")
        
        return {"status": "success", "project_path": str(project_path)}


class CodeReviewAgent:
    """
    코드 파일을 분석하고 리뷰 코멘트를 제공하는 에이전트.
    """
    
    def __init__(self, allowed_dirs: List[str]):
        self.fs_tools = FilesystemTools(allowed_dirs)
    
    async def review_python_file(self, file_path: str) -> Dict[str, Any]:
        """
        Python 파일을 분석하고 개선 제안을 제공합니다.
        
        Args:
            file_path: 분석할 Python 파일 경로
            
        Returns:
            리뷰 결과
        """
        print(f"🔍 Reviewing: {file_path}")
        
        # Read the file
        content = await self.fs_tools.read_text_file(file_path)
        
        # Basic analysis (in a real implementation, this would use an LLM)
        issues = []
        suggestions = []
        
        lines = content.split('\n')
        
        # Check for docstrings
        if '"""' not in content and "'''" not in content:
            issues.append("Missing docstrings - consider adding documentation")
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i}: Line too long ({len(line)} chars)")
        
        # Check for TODO comments
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'FIXME' in line:
                suggestions.append(f"Line {i}: Found TODO/FIXME comment")
        
        # Check for error handling
        if 'try:' not in content:
            suggestions.append("Consider adding error handling with try/except blocks")
        
        print(f"\n📊 Review Results:")
        print(f"  Total lines: {len(lines)}")
        print(f"  Issues found: {len(issues)}")
        print(f"  Suggestions: {len(suggestions)}")
        
        if issues:
            print(f"\n⚠️  Issues:")
            for issue in issues:
                print(f"    - {issue}")
        
        if suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in suggestions:
                print(f"    - {suggestion}")
        
        if not issues and not suggestions:
            print(f"  ✅ No issues found!")
        
        return {
            "file": file_path,
            "lines": len(lines),
            "issues": issues,
            "suggestions": suggestions
        }


class DocumentationAgent:
    """
    프로젝트 문서를 자동으로 생성하는 에이전트.
    """
    
    def __init__(self, allowed_dirs: List[str]):
        self.fs_tools = FilesystemTools(allowed_dirs)
    
    async def generate_api_doc(self, source_dir: str, output_file: str) -> Dict[str, Any]:
        """
        소스 디렉토리의 Python 파일들을 분석하여 API 문서를 생성합니다.
        
        Args:
            source_dir: 소스 코드 디렉토리
            output_file: 출력 문서 파일 경로
            
        Returns:
            생성 결과
        """
        print(f"📝 Generating API documentation from: {source_dir}")
        
        # Search for Python files
        py_files = await self.fs_tools.search_files(source_dir, "*.py")
        py_files_list = py_files.split('\n') if py_files else []
        py_files_list = [f.strip() for f in py_files_list if f.strip() and f.strip() != '[]']
        
        print(f"  Found {len(py_files_list)} Python files")
        
        # Generate documentation
        doc_content = "# API Documentation\n\n"
        doc_content += "This documentation was automatically generated.\n\n"
        doc_content += "## Files\n\n"
        
        for file_info in py_files_list[:5]:  # Limit to first 5 files for demo
            try:
                # Extract filename from the list entry
                if '[FILE]' in file_info:
                    filename = file_info.split('[FILE]')[1].strip()
                    doc_content += f"### {filename}\n\n"
                    
                    # Read file content
                    full_path = str(Path(source_dir) / filename)
                    content = await self.fs_tools.read_text_file(full_path)
                    
                    # Extract docstrings (simple version)
                    lines = content.split('\n')
                    in_docstring = False
                    docstring = []
                    
                    for line in lines:
                        if '"""' in line or "'''" in line:
                            in_docstring = not in_docstring
                            if not in_docstring and docstring:
                                break
                        elif in_docstring:
                            docstring.append(line)
                    
                    if docstring:
                        doc_content += "**Description:**\n\n"
                        doc_content += '\n'.join(docstring).strip() + "\n\n"
                    else:
                        doc_content += "*No description available.*\n\n"
            
            except Exception as e:
                doc_content += f"*Error reading file: {e}*\n\n"
        
        # Write documentation
        await self.fs_tools.write_file(output_file, doc_content)
        
        print(f"  ✅ Documentation generated: {output_file}")
        
        return {"status": "success", "output": output_file}


class DataProcessingAgent:
    """
    데이터 파일을 처리하고 분석하는 에이전트.
    """
    
    def __init__(self, allowed_dirs: List[str]):
        self.fs_tools = FilesystemTools(allowed_dirs)
    
    async def process_csv_data(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        CSV 파일을 읽고 기본 통계를 생성합니다.
        
        Args:
            input_file: 입력 CSV 파일
            output_file: 출력 리포트 파일
            
        Returns:
            처리 결과
        """
        print(f"📊 Processing CSV data: {input_file}")
        
        # Read CSV file
        content = await self.fs_tools.read_text_file(input_file)
        lines = content.split('\n')
        
        if not lines:
            return {"status": "error", "message": "Empty file"}
        
        # Parse CSV (simple version)
        header = lines[0].split(',')
        data_rows = [line.split(',') for line in lines[1:] if line.strip()]
        
        print(f"  Columns: {header}")
        print(f"  Rows: {len(data_rows)}")
        
        # Generate report
        report = f"# Data Processing Report\n\n"
        report += f"**Input File:** {input_file}\n\n"
        report += f"**Processed:** {len(data_rows)} rows\n\n"
        report += f"## Columns\n\n"
        
        for col in header:
            report += f"- {col.strip()}\n"
        
        report += f"\n## Summary\n\n"
        report += f"Total records processed: {len(data_rows)}\n"
        
        # Write report
        await self.fs_tools.write_file(output_file, report)
        
        print(f"  ✅ Report generated: {output_file}")
        
        return {
            "status": "success",
            "rows_processed": len(data_rows),
            "columns": len(header)
        }


async def example1_project_scaffolding():
    """Example 1: 프로젝트 구조 자동 생성"""
    print("\n" + "="*60)
    print("Example 1: Project Scaffolding Agent")
    print("="*60 + "\n")
    
    base_dir = "/tmp/agent_projects"
    Path(base_dir).mkdir(exist_ok=True)
    
    agent = ProjectScaffoldingAgent(base_dir)
    await agent.create_python_project("my_awesome_project")


async def example2_code_review():
    """Example 2: 코드 리뷰"""
    print("\n" + "="*60)
    print("Example 2: Code Review Agent")
    print("="*60 + "\n")
    
    # Create a sample Python file to review
    test_dir = "/tmp/agent_review"
    Path(test_dir).mkdir(exist_ok=True)
    
    sample_code = """def calculate_sum(a, b):
    # TODO: Add input validation
    return a + b

def very_long_function_name_that_exceeds_the_recommended_line_length_limit_for_python_code(param1, param2, param3):
    return param1 + param2 + param3

result = calculate_sum(5, 3)
print(result)
"""
    
    sample_file = Path(test_dir) / "sample.py"
    sample_file.write_text(sample_code)
    
    agent = CodeReviewAgent([test_dir])
    await agent.review_python_file(str(sample_file))


async def example3_documentation():
    """Example 3: 문서 자동 생성"""
    print("\n" + "="*60)
    print("Example 3: Documentation Generation Agent")
    print("="*60 + "\n")
    
    # Use current directory as source
    current_dir = str(Path.cwd())
    output_file = "/tmp/generated_docs.md"
    
    agent = DocumentationAgent([current_dir, "/tmp"])
    await agent.generate_api_doc(current_dir, output_file)


async def example4_data_processing():
    """Example 4: 데이터 처리"""
    print("\n" + "="*60)
    print("Example 4: Data Processing Agent")
    print("="*60 + "\n")
    
    # Create sample CSV
    data_dir = "/tmp/agent_data"
    Path(data_dir).mkdir(exist_ok=True)
    
    csv_content = """name,age,city
Alice,30,Seoul
Bob,25,Busan
Charlie,35,Incheon
David,28,Daegu
"""
    
    input_file = Path(data_dir) / "people.csv"
    input_file.write_text(csv_content)
    
    output_file = Path(data_dir) / "report.md"
    
    agent = DataProcessingAgent([data_dir])
    await agent.process_csv_data(str(input_file), str(output_file))


async def main():
    """Main entry point"""
    examples = {
        "1": ("Project Scaffolding", example1_project_scaffolding),
        "2": ("Code Review", example2_code_review),
        "3": ("Documentation Generation", example3_documentation),
        "4": ("Data Processing", example4_data_processing),
    }
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        if choice in examples:
            await examples[choice][1]()
        else:
            print(f"Invalid example number. Choose from: {', '.join(examples.keys())}")
    else:
        # Run all examples
        print("\n" + "="*60)
        print("Running All Practical Agent Examples")
        print("="*60)
        
        for num, (name, func) in examples.items():
            await func()
        
        print("\n" + "="*60)
        print("All examples completed!")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

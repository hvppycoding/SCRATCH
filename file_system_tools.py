import os
import sys
import shutil
import base64
import fnmatch
import difflib
import mimetypes
import tempfile
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Literal, Any

from pydantic import BaseModel, Field

# --- 1. Pydantic 모델 정의 (Strict Mode 호환용) ---
# Strict Mode에서는 모든 필드가 'required'여야 합니다.
# Optional 필드는 'nullable'로 처리되어야 하므로, LLM은 값이 없으면 'null'을 반환합니다.

class ReadTextFileArgs(BaseModel):
    path: str = Field(..., description="The path to the file")
    # Optional이지만 LLM이 명시적으로 null을 줄 수 있도록 정의
    tail: Optional[int] = Field(default=None, description="If provided, returns only the last N lines")
    head: Optional[int] = Field(default=None, description="If provided, returns only the first N lines")

class ReadMediaFileArgs(BaseModel):
    path: str = Field(..., description="The path to the media file")

class ReadMultipleFilesArgs(BaseModel):
    paths: List[str] = Field(..., description="Array of file paths to read")

class WriteFileArgs(BaseModel):
    path: str = Field(..., description="File location")
    content: str = Field(..., description="File content")

class EditOperation(BaseModel):
    oldText: str = Field(..., description="Text to search for - must match exactly")
    newText: str = Field(..., description="Text to replace with")

class EditFileArgs(BaseModel):
    path: str = Field(..., description="File to edit")
    edits: List[EditOperation] = Field(..., description="List of edit operations")
    dry_run: bool = Field(False, description="Preview changes using git-style diff format without applying")

class CreateDirectoryArgs(BaseModel):
    path: str = Field(..., description="Directory path to create")

class ListDirectoryArgs(BaseModel):
    path: str = Field(..., description="Directory path to list")

class ListDirectoryWithSizesArgs(BaseModel):
    path: str = Field(..., description="Directory path to list")
    sort_by: Literal["name", "size"] = Field("name", description="Sort entries by name or size")

class DirectoryTreeArgs(BaseModel):
    path: str = Field(..., description="Starting directory")
    exclude_patterns: List[str] = Field(default_factory=list, description="Glob patterns to exclude")

class MoveFileArgs(BaseModel):
    source: str = Field(..., description="Source path")
    destination: str = Field(..., description="Destination path")

class SearchFilesArgs(BaseModel):
    path: str = Field(..., description="Starting directory")
    pattern: str = Field(..., description="Glob search pattern")
    exclude_patterns: List[str] = Field(default_factory=list, description="Glob patterns to exclude")

class GetFileInfoArgs(BaseModel):
    path: str = Field(..., description="The path to inspect")

class ListAllowedDirectoriesArgs(BaseModel):
    pass # 인자가 없는 툴

# --- 2. Filesystem Tools 구현 ---

class FilesystemTools:
    """
    Async filesystem tools compatible with OpenAI Agents SDK (Strict Mode).
    """

    def __init__(self, allowed_directories: List[str]):
        self.allowed_directories = [
            str(Path(d).expanduser().resolve()) for d in allowed_directories
        ]
        if not self.allowed_directories:
            raise ValueError("At least one allowed directory must be provided.")

    async def _validate_path(self, path_str: str) -> Path:
        if '\0' in path_str:
             raise ValueError("Path must not contain null bytes")

        # 비동기 환경에서 blocking IO를 스레드로 분리
        def _resolve_blocking():
            try:
                expanded_path = os.path.expanduser(path_str)
                absolute_path = Path(os.path.abspath(expanded_path))
                
                if not self._is_path_allowed(absolute_path):
                    raise PermissionError(f"Access denied - path outside allowed directories: {absolute_path}")

                try:
                    real_path = absolute_path.resolve(strict=True)
                    if not self._is_path_allowed(real_path):
                        raise PermissionError(f"Access denied - symlink target outside allowed directories: {real_path}")
                    return real_path
                except FileNotFoundError:
                    parent_dir = absolute_path.parent
                    try:
                        real_parent = parent_dir.resolve(strict=True)
                        if not self._is_path_allowed(real_parent):
                            raise PermissionError(f"Access denied - parent directory outside allowed directories: {real_parent}")
                        return absolute_path
                    except FileNotFoundError:
                         raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")
            except Exception as e:
                if isinstance(e, (PermissionError, FileNotFoundError)):
                    raise e
                raise ValueError(f"Invalid path format: {str(e)}")

        return await asyncio.to_thread(_resolve_blocking)

    def _is_path_allowed(self, path_obj: Path) -> bool:
        for allowed in self.allowed_directories:
            try:
                path_obj.relative_to(allowed)
                return True
            except ValueError:
                continue
        return False

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0: return "0 B"
        units = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

    # --- 툴 메서드 (Pydantic 모델을 인자로 받음) ---
    
    async def read_text_file(self, args: ReadTextFileArgs) -> str:
        """Read the complete contents of a file as text."""
        # Strict Mode에서 LLM은 값이 없으면 null을 보냅니다. 이는 Python에서 None이 됩니다.
        if args.head is not None and args.tail is not None:
            raise ValueError("Cannot specify both head and tail")

        valid_path = await self._validate_path(args.path)
        
        def _read():
            with open(valid_path, 'r', encoding='utf-8', errors='replace') as f:
                if args.head is not None:
                    return "".join([f.readline() for _ in range(args.head)])
                elif args.tail is not None:
                    return "".join(f.readlines()[-args.tail:])
                return f.read()

        return await asyncio.to_thread(_read)

    async def read_media_file(self, args: ReadMediaFileArgs) -> Dict[str, str]:
        """Read an image or audio file (Base64)."""
        valid_path = await self._validate_path(args.path)
        
        def _read():
            mime_type, _ = mimetypes.guess_type(valid_path)
            if not mime_type:
                ext = valid_path.suffix.lower()
                mime_type = "application/octet-stream"
            
            with open(valid_path, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            
            file_type = "blob"
            if mime_type.startswith("image/"): file_type = "image"
            elif mime_type.startswith("audio/"): file_type = "audio"

            return {"type": file_type, "data": data, "mimeType": mime_type}

        return await asyncio.to_thread(_read)

    async def read_multiple_files(self, args: ReadMultipleFilesArgs) -> str:
        """Read contents of multiple files simultaneously."""
        async def _read_safe(p):
            try:
                # 내부적으로 read_text_file 로직 재사용
                content = await self.read_text_file(ReadTextFileArgs(path=p))
                return f"{p}:\n{content}\n"
            except Exception as e:
                return f"{p}: Error - {str(e)}"

        results = await asyncio.gather(*[_read_safe(p) for p in args.paths])
        return "\n---\n".join(results)

    async def write_file(self, args: WriteFileArgs) -> str:
        """Write to a file (Atomic)."""
        valid_path = await self._validate_path(args.path)
        
        def _write():
            valid_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(valid_path, 'x', encoding='utf-8') as f:
                    f.write(args.content)
            except FileExistsError:
                # Atomic replacement
                with tempfile.NamedTemporaryFile(mode='w', dir=valid_path.parent, delete=False, encoding='utf-8', suffix='.tmp') as tmp:
                    tmp.write(args.content)
                    tmp_path = Path(tmp.name)
                try:
                    os.replace(tmp_path, valid_path)
                except OSError as e:
                    try: os.unlink(tmp_path)
                    except: pass
                    raise IOError(f"Failed to atomically write: {e}")
            return f"Successfully wrote to {args.path}"

        return await asyncio.to_thread(_write)

    async def edit_file(self, args: EditFileArgs) -> str:
        """Apply line-based edits to a text file."""
        valid_path = await self._validate_path(args.path)
        
        def _apply():
            with open(valid_path, 'r', encoding='utf-8') as f:
                original = f.read()
            
            # 줄바꿈 정규화
            modified = original.replace('\r\n', '\n')
            
            for edit in args.edits:
                old_text = edit.oldText.replace('\r\n', '\n')
                new_text = edit.newText.replace('\r\n', '\n')
                
                if old_text in modified:
                    modified = modified.replace(old_text, new_text, 1)
                else:
                    # 간단한 구현을 위해 정확한 일치만 허용 (필요시 fuzzy logic 추가 가능)
                    raise ValueError(f"Could not find exact match for: {edit.oldText[:20]}...")
            
            # Diff 생성
            diff = "".join(difflib.unified_diff(
                original.splitlines(keepends=True), 
                modified.splitlines(keepends=True), 
                fromfile=args.path, tofile=args.path
            ))
            
            if not args.dry_run:
                # 저장 로직 (Atomic)
                with tempfile.NamedTemporaryFile(mode='w', dir=valid_path.parent, delete=False, encoding='utf-8', suffix='.tmp') as tmp:
                    tmp.write(modified)
                    tmp_path = Path(tmp.name)
                try:
                    os.replace(tmp_path, valid_path)
                except OSError:
                    os.unlink(tmp_path)
                    raise
            
            return f"```diff\n{diff}\n```"

        return await asyncio.to_thread(_apply)

    async def create_directory(self, args: CreateDirectoryArgs) -> str:
        valid_path = await self._validate_path(args.path)
        await asyncio.to_thread(os.makedirs, valid_path, exist_ok=True)
        return f"Successfully created directory {args.path}"

    async def list_directory(self, args: ListDirectoryArgs) -> str:
        valid_path = await self._validate_path(args.path)
        def _list():
            if not valid_path.is_dir(): raise NotADirectoryError(f"{args.path} is not a directory")
            entries = sorted(os.scandir(valid_path), key=lambda e: e.name)
            return "\n".join([f"{'[DIR] ' if e.is_dir() else '[FILE]'} {e.name}" for e in entries])
        return await asyncio.to_thread(_list)

    async def list_directory_with_sizes(self, args: ListDirectoryWithSizesArgs) -> str:
        valid_path = await self._validate_path(args.path)
        def _list():
            entries = []
            total_size = 0
            with os.scandir(valid_path) as it:
                for entry in it:
                    try:
                        s = entry.stat().st_size if entry.is_file() else 0
                        if entry.is_file(): total_size += s
                        entries.append({"name": entry.name, "is_dir": entry.is_dir(), "size": s})
                    except: pass
            
            entries.sort(key=lambda x: x["size"] if args.sort_by == "size" else x["name"], reverse=(args.sort_by=="size"))
            lines = [f"{'[DIR] ' if e['is_dir'] else '[FILE]'} {e['name']:<30} {self._format_size(e['size']) if not e['is_dir'] else ''}" for e in entries]
            lines.append(f"Total size: {self._format_size(total_size)}")
            return "\n".join(lines)
        return await asyncio.to_thread(_list)

    async def directory_tree(self, args: DirectoryTreeArgs) -> str:
        root = await self._validate_path(args.path)
        excludes = args.exclude_patterns
        
        def _build(current_path: Path, current_root: Path) -> List[Dict[str, Any]]:
            result = []
            try:
                entries = sorted(os.scandir(current_path), key=lambda e: e.name)
            except PermissionError: return []
            
            for entry in entries:
                try: rel_path = os.path.relpath(entry.path, current_root)
                except: rel_path = entry.name
                
                if any(fnmatch.fnmatch(entry.name, p) or fnmatch.fnmatch(rel_path, p) for p in excludes):
                    continue
                
                data = {"name": entry.name, "type": "directory" if entry.is_dir() else "file"}
                if entry.is_dir():
                    data["children"] = _build(Path(entry.path), current_root)
                result.append(data)
            return result

        tree_data = await asyncio.to_thread(_build, root, root)
        return json.dumps(tree_data, indent=2)

    async def move_file(self, args: MoveFileArgs) -> str:
        src = await self._validate_path(args.source)
        dst = await self._validate_path(args.destination)
        await asyncio.to_thread(shutil.move, src, dst)
        return f"Moved {args.source} to {args.destination}"

    async def search_files(self, args: SearchFilesArgs) -> str:
        root = await self._validate_path(args.path)
        excludes = args.exclude_patterns
        
        def _search():
            results = []
            for dirpath, dirnames, filenames in os.walk(root):
                # Exclude directories in place
                for dirname in list(dirnames):
                    rel = os.path.relpath(os.path.join(dirpath, dirname), root)
                    if any(fnmatch.fnmatch(dirname, p) or fnmatch.fnmatch(rel, p) for p in excludes):
                        dirnames.remove(dirname)
                
                for filename in filenames:
                    full = os.path.join(dirpath, filename)
                    rel = os.path.relpath(full, root)
                    if any(fnmatch.fnmatch(filename, p) or fnmatch.fnmatch(rel, p) for p in excludes):
                        continue
                    if fnmatch.fnmatch(filename, args.pattern) or fnmatch.fnmatch(rel, args.pattern):
                        results.append(full)
            return "\n".join(results) if results else "No matches found"

        return await asyncio.to_thread(_search)

    async def get_file_info(self, args: GetFileInfoArgs) -> str:
        valid_path = await self._validate_path(args.path)
        def _info():
            s = valid_path.stat()
            return "\n".join([f"Size: {s.st_size}", f"Modified: {datetime.fromtimestamp(s.st_mtime)}", f"Permissions: {oct(s.st_mode)[-3:]}"])
        return await asyncio.to_thread(_info)

    async def list_allowed_directories(self, args: ListAllowedDirectoriesArgs) -> str:
        return "\n".join(self.allowed_directories)

    # --- 3. OpenAI 툴 정의 생성 헬퍼 ---
    
    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Returns strict-mode compatible tool definitions.
        """
        # 메서드 이름과 Pydantic 모델 매핑
        mapping = [
            ("read_text_file", ReadTextFileArgs, "Read text file content."),
            ("read_media_file", ReadMediaFileArgs, "Read media file (image/audio)."),
            ("read_multiple_files", ReadMultipleFilesArgs, "Read multiple files at once."),
            ("write_file", WriteFileArgs, "Write content to a file."),
            ("edit_file", EditFileArgs, "Edit a file using search/replace."),
            ("create_directory", CreateDirectoryArgs, "Create a directory."),
            ("list_directory", ListDirectoryArgs, "List directory contents."),
            ("list_directory_with_sizes", ListDirectoryWithSizesArgs, "List directory with sizes."),
            ("directory_tree", DirectoryTreeArgs, "Get directory tree structure."),
            ("move_file", MoveFileArgs, "Move or rename a file."),
            ("search_files", SearchFilesArgs, "Search for files by pattern."),
            ("get_file_info", GetFileInfoArgs, "Get file metadata."),
            ("list_allowed_directories", ListAllowedDirectoriesArgs, "Show allowed directories."),
        ]
        
        tools = []
        for name, model, desc in mapping:
            # model_json_schema()를 호출하면 Pydantic이 JSON Schema를 생성합니다.
            schema = model.model_json_schema()
            
            # Strict Mode를 위한 정리
            if "title" in schema: del schema["title"]
            
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                    "parameters": schema,
                    "strict": True  # Strict Mode 활성화
                }
            })
        return tools

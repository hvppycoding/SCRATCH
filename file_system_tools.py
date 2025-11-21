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
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Any, Literal

from pydantic import BaseModel, Field, ConfigDict

# --- 1. Inner Types (Enum & Pydantic for structure) ---

class SortBy(str, Enum):
    """Enum for sorting options in directory listing."""
    NAME = "name"
    SIZE = "size"

class EditOperation(BaseModel):
    """
    Represents a single edit operation for a text file.
    
    Attributes:
        oldText: The exact text sequence to search for in the file.
        newText: The text to replace the oldText with.
    """
    oldText: str = Field(..., description="Text to search for - must match exactly")
    newText: str = Field(..., description="Text to replace with")
    
    # Strict Mode requirement: forbid unknown fields
    model_config = ConfigDict(extra='forbid')

# --- 2. Filesystem Tools Implementation ---

class FilesystemTools:
    """
    Async filesystem tools compatible with OpenAI Agents SDK (Strict Mode).
    
    This class mirrors the functionality and security logic of the 
    @modelcontextprotocol/server-filesystem implementation.

    Security Features:
    1.  **Path Validation**: Ensures all operations are restricted to specific allowed directories.
    2.  **Symlink Protection**: Resolves paths to their real locations to prevent symlink attacks escaping the sandbox.
    3.  **Atomic Writes**: Uses temporary files and atomic renames to prevent race conditions (TOCTOU).
    """

    def __init__(self, allowed_directories: List[str]):
        """
        Initialize the filesystem tools with a list of allowed directories.

        Args:
            allowed_directories: List of absolute paths that the agent is allowed to access.
        
        Raises:
            ValueError: If no allowed directories are provided.
        """
        self.allowed_directories = [
            str(Path(d).expanduser().resolve()) for d in allowed_directories
        ]
        if not self.allowed_directories:
            raise ValueError("At least one allowed directory must be provided.")

    async def _validate_path(self, path_str: str) -> Path:
        """
        Validates that a path is within the allowed directories using blocking I/O in a separate thread.

        This method performs strict security checks including null byte detection,
        symlink resolution, and parent directory validation for non-existent files.

        Args:
            path_str: The raw path string to validate.

        Returns:
            The resolved, absolute Path object that is safe to use.

        Raises:
            ValueError: If the path contains null bytes or has an invalid format.
            PermissionError: If the path (or its symlink target) is outside allowed directories.
            FileNotFoundError: If the parent directory of a new file does not exist.
        """
        if '\0' in path_str:
             raise ValueError("Path must not contain null bytes")

        def _resolve_blocking():
            try:
                expanded_path = os.path.expanduser(path_str)
                absolute_path = Path(os.path.abspath(expanded_path))
                
                # Initial check on the normalized path
                if not self._is_path_allowed(absolute_path):
                    raise PermissionError(f"Access denied - path outside allowed directories: {absolute_path}")

                # Resolve symlinks to check the real physical path
                try:
                    real_path = absolute_path.resolve(strict=True)
                    if not self._is_path_allowed(real_path):
                        raise PermissionError(f"Access denied - symlink target outside allowed directories: {real_path}")
                    return real_path
                except FileNotFoundError:
                    # If file doesn't exist (e.g., write_file), validate the parent directory
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
        """
        Checks if a given path object is strictly within one of the allowed directories.

        Args:
            path_obj: The path to check.

        Returns:
            True if the path is within an allowed directory, False otherwise.
        """
        for allowed in self.allowed_directories:
            try:
                path_obj.relative_to(allowed)
                return True
            except ValueError:
                continue
        return False

    def _format_size(self, size_bytes: int) -> str:
        """
        Formats a byte count into a human-readable string (B, KB, MB, etc.).

        Args:
            size_bytes: The size in bytes.

        Returns:
            Formatted string (e.g., "1.5 MB").
        """
        if size_bytes == 0: return "0 B"
        units = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

    # --- Tool Methods ---
    
    async def read_text_file(
        self, 
        path: str, 
        tail: Optional[int] = None, 
        head: Optional[int] = None
    ) -> str:
        """
        Reads the complete contents of a file as text.
        
        Handles various text encodings and provides error messages if the file cannot be read.
        Supports reading specific portions of the file via head/tail parameters.
        Note that both head and tail cannot be used simultaneously.

        Args:
            path: The path to the file.
            tail: If provided, returns only the last N lines of the file.
            head: If provided, returns only the first N lines of the file.

        Returns:
            The content of the file as a string.

        Raises:
            ValueError: If both head and tail are specified.
            PermissionError: If the path is outside allowed directories.
            FileNotFoundError: If the file does not exist.
        """
        if head is not None and tail is not None:
            raise ValueError("Cannot specify both head and tail parameters simultaneously")

        valid_path = await self._validate_path(path)
        
        def _read():
            with open(valid_path, 'r', encoding='utf-8', errors='replace') as f:
                if head is not None:
                    return "".join([f.readline() for _ in range(head)])
                elif tail is not None:
                    return "".join(f.readlines()[-tail:])
                return f.read()

        return await asyncio.to_thread(_read)

    async def read_media_file(self, path: str) -> Dict[str, str]:
        """
        Reads an image or audio file and returns it as base64 encoded data.
        
        Automatically detects MIME type based on file extension or content.
        Useful for handling non-text files that need to be processed by the agent.

        Args:
            path: The path to the media file.

        Returns:
            A dictionary containing:
                - 'type': The general type ('image', 'audio', or 'blob').
                - 'data': The base64 encoded file content.
                - 'mimeType': The detected MIME type (e.g., 'image/png').
        """
        valid_path = await self._validate_path(path)
        
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

    async def read_multiple_files(self, paths: List[str]) -> str:
        """
        Reads the contents of multiple files simultaneously.
        
        Efficiently handles multiple reads in parallel. Errors in reading individual files
        are reported in the output string rather than raising an exception for the whole batch,
        allowing partial success.

        Args:
            paths: A list of file paths to read.

        Returns:
            A single string containing the concatenated contents of all files,
            separated by separators. Format: "path:\ncontent\n---\n".
        """
        async def _read_safe(p):
            try:
                content = await self.read_text_file(p)
                return f"{p}:\n{content}\n"
            except Exception as e:
                return f"{p}: Error - {str(e)}"

        results = await asyncio.gather(*[_read_safe(p) for p in paths])
        return "\n---\n".join(results)

    async def write_file(self, path: str, content: str) -> str:
        """
        Writes content to a file using an atomic write strategy.
        
        This method creates a new file or overwrites an existing one. It uses a temporary file
        and an atomic rename operation to prevent race conditions (TOCTOU) and ensure
        data integrity.

        Args:
            path: The destination file location.
            content: The text content to write to the file.

        Returns:
            A success message indicating the file was written.

        Raises:
            IOError: If the write operation fails.
        """
        valid_path = await self._validate_path(path)
        
        def _write():
            valid_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                # Try exclusive creation first to prevent writing through symlinks
                with open(valid_path, 'x', encoding='utf-8') as f:
                    f.write(content)
            except FileExistsError:
                # If file exists, use atomic replacement strategy
                with tempfile.NamedTemporaryFile(mode='w', dir=valid_path.parent, delete=False, encoding='utf-8', suffix='.tmp') as tmp:
                    tmp.write(content)
                    tmp_path = Path(tmp.name)
                try:
                    os.replace(tmp_path, valid_path)
                except OSError as e:
                    try: os.unlink(tmp_path)
                    except: pass
                    raise IOError(f"Failed to atomically write: {e}")
            return f"Successfully wrote to {path}"

        return await asyncio.to_thread(_write)

    async def edit_file(
        self, 
        path: str, 
        edits: List[Union[Dict[str, str], EditOperation]], 
        dry_run: bool = False
    ) -> str:
        """
        Applies line-based edits to a text file using strict search and replace.
        
        Attempts to match 'oldText' exactly. If exact match fails, it tries a line-by-line
        comparison ignoring leading/trailing whitespace. If a match is found, it replaces
        the lines while attempting to preserve indentation.

        Args:
            path: The file to edit.
            edits: A list of edit operations. Each operation should contain 'oldText' and 'newText'.
            dry_run: If True, returns a git-style diff without modifying the file.

        Returns:
            A git-style unified diff string showing the changes.

        Raises:
            ValueError: If the text to replace cannot be found in the file.
        """
        valid_path = await self._validate_path(path)
        
        def _apply():
            with open(valid_path, 'r', encoding='utf-8') as f:
                original = f.read()
            
            content_str = original.replace('\r\n', '\n')
            modified_content = content_str
            
            for edit_item in edits:
                # Support both Dict (from raw JSON) and EditOperation (internal typing)
                if isinstance(edit_item, dict):
                    edit = EditOperation(**edit_item)
                else:
                    edit = edit_item

                old_text = edit.oldText.replace('\r\n', '\n')
                new_text = edit.newText.replace('\r\n', '\n')
                
                # 1. Exact Match
                if old_text in modified_content:
                    modified_content = modified_content.replace(old_text, new_text, 1)
                    continue
                    
                # 2. Flexible Line-by-Line Match (Whitespace insensitive)
                old_lines = old_text.splitlines()
                content_lines = modified_content.splitlines()
                match_found = False
                
                for i in range(len(content_lines) - len(old_lines) + 1):
                    potential_match = content_lines[i : i + len(old_lines)]
                    is_match = True
                    for j, p_line in enumerate(potential_match):
                        if p_line.strip() != old_lines[j].strip():
                            is_match = False; break
                    
                    if is_match:
                        # Match found!
                        original_indent = ""
                        first_line = content_lines[i]
                        if len(first_line) > len(first_line.lstrip()):
                             original_indent = first_line[:len(first_line) - len(first_line.lstrip())]

                        new_replacement_lines = []
                        for j, line in enumerate(new_text.splitlines()):
                            if j == 0: 
                                new_replacement_lines.append(original_indent + line.lstrip())
                            else: 
                                new_replacement_lines.append(line)

                        content_lines[i : i + len(old_lines)] = new_replacement_lines
                        modified_content = "\n".join(content_lines)
                        match_found = True
                        break
                
                if not match_found:
                    snippet = edit.oldText[:50] + "..." if len(edit.oldText) > 50 else edit.oldText
                    raise ValueError(f"Could not find exact match for edit: {snippet}")
            
            diff = "".join(difflib.unified_diff(
                original.splitlines(keepends=True), 
                modified_content.splitlines(keepends=True), 
                fromfile=path, tofile=path, lineterm=''
            ))
            
            if not dry_run:
                with tempfile.NamedTemporaryFile(mode='w', dir=valid_path.parent, delete=False, encoding='utf-8', suffix='.tmp') as tmp:
                    tmp.write(modified_content)
                    tmp_path = Path(tmp.name)
                try:
                    os.replace(tmp_path, valid_path)
                except OSError:
                    os.unlink(tmp_path)
                    raise
            
            return f"```diff\n{diff}\n```"

        return await asyncio.to_thread(_apply)

    async def create_directory(self, path: str) -> str:
        """
        Creates a new directory or ensures it exists.
        
        Can create multiple nested directories in one operation.
        
        Args:
            path: The directory path to create.

        Returns:
            A success message.
        """
        valid_path = await self._validate_path(path)
        await asyncio.to_thread(os.makedirs, valid_path, exist_ok=True)
        return f"Successfully created directory {path}"

    async def list_directory(self, path: str) -> str:
        """
        Lists files and directories in the specified path.
        
        Output format distinguishes between directories and files (e.g., [DIR], [FILE]).

        Args:
            path: The directory path to list.

        Returns:
            A formatted string list of directory contents.
        
        Raises:
            NotADirectoryError: If the path is not a directory.
        """
        valid_path = await self._validate_path(path)
        def _list():
            if not valid_path.is_dir(): raise NotADirectoryError(f"{path} is not a directory")
            entries = sorted(os.scandir(valid_path), key=lambda e: e.name)
            return "\n".join([f"{'[DIR] ' if e.is_dir() else '[FILE]'} {e.name}" for e in entries])
        return await asyncio.to_thread(_list)

    async def list_directory_with_sizes(
        self, 
        path: str, 
        sort_by: Union[SortBy, str] = SortBy.NAME
    ) -> str:
        """
        Lists files and directories in the specified path, including sizes.
        
        Args:
            path: The directory path to list.
            sort_by: Sort criteria, either 'name' or 'size'.

        Returns:
            A formatted string list including size information and a summary.
        """
        valid_path = await self._validate_path(path)
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
            
            # Handle Enum or raw string input
            sort_key = sort_by.value if isinstance(sort_by, SortBy) else sort_by
            is_sort_size = sort_key == "size"
            
            entries.sort(key=lambda x: x["size"] if is_sort_size else x["name"], reverse=is_sort_size)
            
            lines = [f"{'[DIR] ' if e['is_dir'] else '[FILE]'} {e['name']:<30} {self._format_size(e['size']) if not e['is_dir'] else ''}" for e in entries]
            lines.append(f"Total size: {self._format_size(total_size)}")
            return "\n".join(lines)
        return await asyncio.to_thread(_list)

    async def directory_tree(
        self, 
        path: str, 
        exclude_patterns: Optional[List[str]] = None
    ) -> str:
        """
        Generates a recursive JSON structure representing the directory tree.
        
        Respects exclude patterns to filter out unwanted files or directories.

        Args:
            path: The starting directory path.
            exclude_patterns: A list of glob patterns to exclude from the tree.

        Returns:
            A JSON string representation of the directory tree.
        """
        root = await self._validate_path(path)
        excludes = exclude_patterns or []
        
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

    async def move_file(self, source: str, destination: str) -> str:
        """
        Moves or renames a file or directory.
        
        Both source and destination must be within allowed directories.
        Fails if the destination already exists.

        Args:
            source: The source path.
            destination: The destination path.

        Returns:
            A success message.
        """
        src = await self._validate_path(source)
        dst = await self._validate_path(destination)
        await asyncio.to_thread(shutil.move, src, dst)
        return f"Moved {source} to {destination}"

    async def search_files(
        self, 
        path: str, 
        pattern: str, 
        exclude_patterns: Optional[List[str]] = None
    ) -> str:
        """
        Recursively searches for files matching a glob pattern.
        
        Args:
            path: The starting directory path.
            pattern: The glob search pattern (e.g., "*.py").
            exclude_patterns: A list of glob patterns to exclude from search.

        Returns:
            A list of matching file paths (newline separated), or a message if no matches found.
        """
        root = await self._validate_path(path)
        excludes = exclude_patterns or []
        
        def _search():
            results = []
            for dirpath, dirnames, filenames in os.walk(root):
                for dirname in list(dirnames):
                    rel = os.path.relpath(os.path.join(dirpath, dirname), root)
                    if any(fnmatch.fnmatch(dirname, p) or fnmatch.fnmatch(rel, p) for p in excludes):
                        dirnames.remove(dirname)
                for filename in filenames:
                    full = os.path.join(dirpath, filename)
                    rel = os.path.relpath(full, root)
                    if any(fnmatch.fnmatch(filename, p) or fnmatch.fnmatch(rel, p) for p in excludes):
                        continue
                    if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(rel, pattern):
                        results.append(full)
            return "\n".join(results) if results else "No matches found"

        return await asyncio.to_thread(_search)

    async def get_file_info(self, path: str) -> str:
        """
        Retrieves detailed metadata for a file or directory.

        Args:
            path: The path to inspect.

        Returns:
            A formatted string containing size, modification time, and permissions.
        """
        valid_path = await self._validate_path(path)
        def _info():
            s = valid_path.stat()
            return "\n".join([f"Size: {s.st_size}", f"Modified: {datetime.fromtimestamp(s.st_mtime)}", f"Permissions: {oct(s.st_mode)[-3:]}"])
        return await asyncio.to_thread(_info)

    async def list_allowed_directories(self) -> str:
        """
        Returns the list of directories the agent is allowed to access.

        Returns:
            A newline-separated list of allowed paths.
        """
        return "\n".join(self.allowed_directories)

    # --- 3. Helper to generate OpenAI Strict JSON Schema ---
    
    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Returns a list of OpenAI tool definitions with manually constructed Strict Mode schemas.
        
        The generated schemas adhere to OpenAI's Structured Outputs requirements:
        - 'strict': True
        - All properties are included in the 'required' list.
        - Optional parameters use nullable types (e.g., ["string", "null"]).
        - 'additionalProperties' is set to False.
        
        Returns:
            A list of tool definition dictionaries ready for the OpenAI API.
        """
        
        # Generate schema for the complex inner object using Pydantic
        edit_op_schema = EditOperation.model_json_schema()
        if "title" in edit_op_schema: del edit_op_schema["title"]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_text_file",
                    "description": "Read the complete contents of a file from the file system as text.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to the file"},
                            "tail": {"type": ["integer", "null"], "description": "If provided, returns only the last N lines"},
                            "head": {"type": ["integer", "null"], "description": "If provided, returns only the first N lines"}
                        },
                        "required": ["path", "tail", "head"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_media_file",
                    "description": "Read an image or audio file and returns it as base64 encoded data.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to the media file"}
                        },
                        "required": ["path"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_multiple_files",
                    "description": "Read the contents of multiple files simultaneously.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "paths": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Array of file paths to read"
                            }
                        },
                        "required": ["paths"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Create a new file or completely overwrite an existing file with new content.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File location"},
                            "content": {"type": "string", "description": "File content"}
                        },
                        "required": ["path", "content"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Make line-based edits to a text file using exact search and replace.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "File to edit"},
                            "edits": {
                                "type": "array",
                                "items": edit_op_schema,
                                "description": "List of edit operations"
                            },
                            "dry_run": {"type": "boolean", "description": "Preview changes using git-style diff format without applying"}
                        },
                        "required": ["path", "edits", "dry_run"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "Create a new directory or ensure a directory exists.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path to create"}
                        },
                        "required": ["path"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "Get a detailed listing of all files and directories in a specified path.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path to list"}
                        },
                        "required": ["path"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory_with_sizes",
                    "description": "Get a detailed listing of files and directories with sizes.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path to list"},
                            "sort_by": {
                                "type": "string", 
                                "enum": [e.value for e in SortBy],
                                "description": "Sort entries by name or size"
                            }
                        },
                        "required": ["path", "sort_by"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "directory_tree",
                    "description": "Get a recursive tree view of files and directories as a JSON structure.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Starting directory"},
                            "exclude_patterns": {
                                "type": ["array", "null"], 
                                "items": {"type": "string"},
                                "description": "Glob patterns to exclude"
                            }
                        },
                        "required": ["path", "exclude_patterns"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_file",
                    "description": "Move or rename files and directories.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string", "description": "Source path"},
                            "destination": {"type": "string", "description": "Destination path"}
                        },
                        "required": ["source", "destination"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Recursively search for files and directories matching a pattern.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Starting directory"},
                            "pattern": {"type": "string", "description": "Glob search pattern"},
                            "exclude_patterns": {
                                "type": ["array", "null"], 
                                "items": {"type": "string"},
                                "description": "Glob patterns to exclude"
                            }
                        },
                        "required": ["path", "pattern", "exclude_patterns"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_info",
                    "description": "Retrieve detailed metadata about a file or directory.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "The path to inspect"}
                        },
                        "required": ["path"],
                        "additionalProperties": False
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_allowed_directories",
                    "description": "Returns the list of directories that this server is allowed to access.",
                    "strict": True,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    }
                }
            }
        ]
        return tools

import os
import sys
import json
import glob
import shutil
import base64
import fnmatch
import difflib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Literal, Any

# Helper for formatting file sizes
def _format_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

class FilesystemTools:
    """
    A collection of filesystem tools for Python Agents, mirroring the 
    functionality of the @modelcontextprotocol/server-filesystem.
    """

    def __init__(self, allowed_directories: List[str]):
        """
        Initialize the filesystem tools with a list of allowed directories.
        
        Args:
            allowed_directories (List[str]): Absolute paths that the agent is allowed to access.
        """
        self.allowed_directories = [
            str(Path(d).expanduser().resolve()) for d in allowed_directories
        ]
        if not self.allowed_directories:
            raise ValueError("At least one allowed directory must be provided.")

    def _validate_path(self, path_str: str) -> Path:
        """
        Validates that a path is within the allowed directories.

        Args:
            path_str (str): The path to validate.

        Returns:
            Path: The resolved, absolute Path object.

        Raises:
            PermissionError: If the path is outside allowed directories.
            FileNotFoundError: If the parent directory implies a path outside allowed scope.
        """
        try:
            # Handle ~ expansion and resolve absolute path
            path_obj = Path(path_str).expanduser().resolve()
        except Exception as e:
            # If path doesn't exist yet, we might fail to resolve fully if parents don't exist
            # fallback to basic resolution
            path_obj = Path(path_str).expanduser().absolute()

        # Check against allowed directories
        is_allowed = False
        for allowed in self.allowed_directories:
            try:
                # Check if path_obj is relative to allowed
                path_obj.relative_to(allowed)
                is_allowed = True
                break
            except ValueError:
                continue

        if not is_allowed:
            raise PermissionError(
                f"Access denied - path outside allowed directories: {path_obj}"
            )

        return path_obj

    def read_text_file(
        self, 
        path: str, 
        tail: Optional[int] = None, 
        head: Optional[int] = None
    ) -> str:
        """
        Read the complete contents of a file from the file system as text.

        Operates on the file as text regardless of extension.

        Args:
            path (str): The path to the file.
            tail (Optional[int]): If provided, returns only the last N lines of the file.
            head (Optional[int]): If provided, returns only the first N lines of the file.

        Returns:
            str: The content of the file.

        Raises:
            ValueError: If both head and tail are specified.
            PermissionError: If path is not allowed.
            FileNotFoundError: If file does not exist.
        """
        if head is not None and tail is not None:
            raise ValueError("Cannot specify both head and tail parameters simultaneously")

        valid_path = self._validate_path(path)
        
        with open(valid_path, 'r', encoding='utf-8', errors='replace') as f:
            if head is not None:
                lines = [next(f) for _ in range(head)]
                return "".join(lines)
            elif tail is not None:
                # Efficient tail implementation using collections.deque is possible,
                # but reading lines is simpler for agent context usually.
                lines = f.readlines()
                return "".join(lines[-tail:])
            else:
                return f.read()

    def read_media_file(self, path: str) -> Dict[str, str]:
        """
        Read an image or audio file, returning base64 encoded data.

        Args:
            path (str): The path to the media file.

        Returns:
            Dict[str, str]: A dictionary containing 'type', 'data' (base64), and 'mimeType'.
        """
        valid_path = self._validate_path(path)
        
        mime_type, _ = mimetypes.guess_type(valid_path)
        if not mime_type:
            mime_type = "application/octet-stream"
            
        with open(valid_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')

        file_type = "blob"
        if mime_type.startswith("image/"):
            file_type = "image"
        elif mime_type.startswith("audio/"):
            file_type = "audio"

        return {
            "type": file_type,
            "data": data,
            "mimeType": mime_type
        }

    def read_multiple_files(self, paths: List[str]) -> str:
        """
        Read the contents of multiple files simultaneously.

        Args:
            paths (List[str]): Array of file paths to read.

        Returns:
            str: A concatenated string of file contents, separated by dashes.
        """
        results = []
        for p in paths:
            try:
                content = self.read_text_file(p)
                results.append(f"{p}:\n{content}\n")
            except Exception as e:
                results.append(f"{p}: Error - {str(e)}")
        
        return "\n---\n".join(results)

    def write_file(self, path: str, content: str) -> str:
        """
        Create a new file or completely overwrite an existing file with new content.

        Args:
            path (str): File location.
            content (str): File content.

        Returns:
            str: Success message.
        """
        valid_path = self._validate_path(path)
        
        # Ensure parent exists (optional, but good UX)
        valid_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(valid_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Successfully wrote to {path}"

    def edit_file(
        self, 
        path: str, 
        edits: List[Dict[str, str]], 
        dry_run: bool = False
    ) -> str:
        """
        Make line-based edits to a text file using exact string replacement.
        
        Args:
            path (str): File to edit.
            edits (List[Dict[str, str]]): List of edit operations. Each dict must have 
                'oldText' (exact text to match) and 'newText' (text to replace with).
            dry_run (bool): Preview changes using git-style diff format without applying.

        Returns:
            str: A unified diff string showing the changes.

        Raises:
            ValueError: If exact match for oldText is not found.
        """
        valid_path = self._validate_path(path)
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        modified_content = original_content
        
        # Apply edits sequentially
        for edit in edits:
            old_text = edit.get('oldText', '')
            new_text = edit.get('newText', '')
            
            # Normalize line endings for comparison if needed, 
            # but here we do strict replacement for safety
            if old_text not in modified_content:
                raise ValueError(f"Could not find exact match for edit block starting with: {old_text[:50]}...")
                
            modified_content = modified_content.replace(old_text, new_text, 1)

        # Generate Diff
        diff_lines = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            modified_content.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
            lineterm=''
        )
        diff_text = "".join(diff_lines)

        if not dry_run:
            with open(valid_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
        return f"```diff\n{diff_text}\n```"

    def create_directory(self, path: str) -> str:
        """
        Create a new directory or ensure a directory exists.
        
        Args:
            path (str): Directory path.

        Returns:
            str: Success message.
        """
        valid_path = self._validate_path(path)
        os.makedirs(valid_path, exist_ok=True)
        return f"Successfully created directory {path}"

    def list_directory(self, path: str) -> str:
        """
        Get a detailed listing of all files and directories in a specified path.

        Args:
            path (str): Directory path.

        Returns:
            str: Text listing with [FILE] and [DIR] prefixes.
        """
        valid_path = self._validate_path(path)
        
        if not valid_path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        entries = sorted(os.scandir(valid_path), key=lambda e: e.name)
        output = []
        for entry in entries:
            prefix = "[DIR] " if entry.is_dir() else "[FILE]"
            output.append(f"{prefix} {entry.name}")
            
        return "\n".join(output)

    def list_directory_with_sizes(
        self, 
        path: str, 
        sort_by: Literal["name", "size"] = "name"
    ) -> str:
        """
        Get a detailed listing of all files and directories, including sizes.

        Args:
            path (str): Directory path to list.
            sort_by (Literal["name", "size"]): Sort entries by name or size.

        Returns:
            str: Detailed listing string.
        """
        valid_path = self._validate_path(path)
        
        entries_data = []
        total_size = 0
        total_files = 0
        total_dirs = 0

        with os.scandir(valid_path) as it:
            for entry in it:
                is_dir = entry.is_dir()
                size = entry.stat().st_size if not is_dir else 0
                
                if is_dir:
                    total_dirs += 1
                else:
                    total_files += 1
                    total_size += size

                entries_data.append({
                    "name": entry.name,
                    "is_dir": is_dir,
                    "size": size
                })

        # Sort
        if sort_by == "size":
            entries_data.sort(key=lambda x: x["size"], reverse=True)
        else:
            entries_data.sort(key=lambda x: x["name"])

        # Format
        lines = []
        for item in entries_data:
            prefix = "[DIR] " if item["is_dir"] else "[FILE]"
            size_str = "" if item["is_dir"] else _format_size(item["size"]).rjust(10)
            lines.append(f"{prefix} {item['name']:<30} {size_str}")

        lines.append("")
        lines.append(f"Total: {total_files} files, {total_dirs} directories")
        lines.append(f"Combined size: {_format_size(total_size)}")

        return "\n".join(lines)

    def directory_tree(
        self, 
        path: str, 
        exclude_patterns: Optional[List[str]] = None
    ) -> str:
        """
        Get a recursive tree view of files and directories as a JSON structure.

        Args:
            path (str): Starting directory.
            exclude_patterns (Optional[List[str]]): Glob patterns to exclude (e.g. ['*.pyc', '__pycache__']).

        Returns:
            str: JSON string representation of the tree.
        """
        root_path = self._validate_path(path)
        excludes = exclude_patterns or []

        def _build_tree(current_path: Path) -> List[Dict[str, Any]]:
            result = []
            try:
                # Sort for consistent output
                entries = sorted(os.scandir(current_path), key=lambda e: e.name)
            except PermissionError:
                return []

            for entry in entries:
                # Calculate relative path for matching excludes
                rel_path = os.path.relpath(entry.path, root_path)
                
                # Check excludes
                should_exclude = False
                for pattern in excludes:
                    # Match name, relative path, or directory part
                    if (fnmatch.fnmatch(entry.name, pattern) or 
                        fnmatch.fnmatch(rel_path, pattern)):
                        should_exclude = True
                        break
                if should_exclude:
                    continue

                entry_data = {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file"
                }

                if entry.is_dir():
                    entry_data["children"] = _build_tree(Path(entry.path))
                
                result.append(entry_data)
            return result

        tree_data = _build_tree(root_path)
        return json.dumps(tree_data, indent=2)

    def move_file(self, source: str, destination: str) -> str:
        """
        Move or rename files and directories.

        Args:
            source (str): Source path.
            destination (str): Destination path.

        Returns:
            str: Success message.
        """
        valid_source = self._validate_path(source)
        valid_dest = self._validate_path(destination)
        
        shutil.move(str(valid_source), str(valid_dest))
        return f"Successfully moved {source} to {destination}"

    def search_files(
        self, 
        path: str, 
        pattern: str, 
        exclude_patterns: Optional[List[str]] = None
    ) -> str:
        """
        Recursively search for files and directories matching a pattern.

        Args:
            path (str): Starting directory.
            pattern (str): Glob search pattern (e.g. '*.ts', 'src/**/*.py').
            exclude_patterns (Optional[List[str]]): Glob patterns to exclude.

        Returns:
            str: Newline-separated list of matching paths.
        """
        root_path = self._validate_path(path)
        excludes = exclude_patterns or []
        results = []

        # os.walk allows us to prune directories based on excludes efficiently
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter excluded directories in-place to prevent walking them
            # We must iterate a copy of the list to modify the original safely
            for dirname in list(dirnames):
                rel_dir = os.path.relpath(os.path.join(dirpath, dirname), root_path)
                for ex_pat in excludes:
                    if fnmatch.fnmatch(dirname, ex_pat) or fnmatch.fnmatch(rel_dir, ex_pat):
                        dirnames.remove(dirname)
                        break
            
            # Check files
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, root_path)
                
                # Check file excludes
                should_exclude = False
                for ex_pat in excludes:
                    if fnmatch.fnmatch(filename, ex_pat) or fnmatch.fnmatch(rel_path, ex_pat):
                        should_exclude = True
                        break
                if should_exclude:
                    continue

                # Check match pattern (support recursive glob logic simply via fnmatch on rel_path)
                # For true recursive matching like `src/**/*.ts`, fnmatch usually works on the full relative path
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(filename, pattern):
                    results.append(full_path)

        return "\n".join(results) if results else "No matches found"

    def get_file_info(self, path: str) -> str:
        """
        Retrieve detailed metadata about a file or directory.

        Args:
            path (str): The path to inspect.

        Returns:
            str: Formatted string of file attributes (size, created, permissions, etc).
        """
        valid_path = self._validate_path(path)
        stat = valid_path.stat()
        
        is_dir = valid_path.is_dir()
        file_type = "directory" if is_dir else "file"
        
        info = {
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "isDirectory": is_dir,
            "isFile": not is_dir,
            "permissions": oct(stat.st_mode)[-3:],
            "type": file_type
        }
        
        return "\n".join([f"{k}: {v}" for k, v in info.items()])

    def list_allowed_directories(self) -> str:
        """
        Returns the list of directories that this server is allowed to access.

        Returns:
            str: Newline-separated list of allowed directories.
        """
        return f"Allowed directories:\n{chr(10).join(self.allowed_directories)}"

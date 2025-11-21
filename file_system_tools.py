import os
import sys
import json
import glob
import shutil
import base64
import fnmatch
import difflib
import mimetypes
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Literal, Any, Tuple

# Type alias for EditOperation
EditOperation = Dict[str, str]

class FilesystemTools:
    """
    A collection of filesystem tools for Python Agents, faithfully mirroring the 
    functionality and security mechanisms of the @modelcontextprotocol/server-filesystem.
    
    This class implements strict security controls including:
    1. Path validation to ensure operations stay within allowed directories.
    2. protection against Path Traversal attacks.
    3. Atomic write operations to prevent symlink race conditions.
    """

    def __init__(self, allowed_directories: List[str]):
        """
        Initialize the filesystem tools with a list of allowed directories.

        Args:
            allowed_directories (List[str]): Absolute paths that the agent is allowed to access.
                Any operation attempting to access files outside these directories will raise a PermissionError.
        """
        self.allowed_directories = [
            str(Path(d).expanduser().resolve()) for d in allowed_directories
        ]
        if not self.allowed_directories:
            raise ValueError("At least one allowed directory must be provided.")

    def _validate_path(self, path_str: str) -> Path:
        """
        Validates that a path is within the allowed directories.
        
        Mirrors the security logic from `validatePath` in `lib.ts`.
        
        1. Expands user (~).
        2. Resolves absolute path.
        3. Checks if the resolved path starts with any allowed directory.
        4. Checks real path (resolving symlinks) to prevent symlink attacks escaping allowed dirs.
        5. For non-existent files, validates the parent directory.

        Args:
            path_str (str): The path to validate.

        Returns:
            Path: The resolved, absolute Path object.

        Raises:
            PermissionError: If the path or its resolved target is outside allowed directories.
            ValueError: If the path contains null bytes or is invalid.
        """
        if '\0' in path_str:
             raise ValueError("Path must not contain null bytes")

        try:
            # Handle ~ expansion and resolve absolute path
            # path_obj will be the absolute path, but symlinks are NOT yet resolved if we use strict=False or just Path.resolve() depending on version
            # We use os.path.abspath first to get a clean absolute path string
            expanded_path = os.path.expanduser(path_str)
            absolute_path = Path(os.path.abspath(expanded_path))
        except Exception as e:
            raise ValueError(f"Invalid path format: {str(e)}")

        # Security: Check if path is within allowed directories before any file operations
        # This is the first line of defense (normalized path check)
        if not self._is_path_allowed(absolute_path):
             raise PermissionError(
                f"Access denied - path outside allowed directories: {absolute_path}"
            )

        # Security: Handle symlinks by checking their real path to prevent symlink attacks
        # This prevents attackers from creating symlinks that point outside allowed directories
        try:
            # resolve() in Python follows symlinks (like fs.realpath in Node)
            real_path = absolute_path.resolve(strict=True)
            
            if not self._is_path_allowed(real_path):
                 raise PermissionError(
                    f"Access denied - symlink target outside allowed directories: {real_path}"
                )
            return real_path
            
        except FileNotFoundError:
            # Security: For new files that don't exist yet, verify parent directory
            # This ensures we can't create files in unauthorized locations
            parent_dir = absolute_path.parent
            try:
                real_parent = parent_dir.resolve(strict=True)
                if not self._is_path_allowed(real_parent):
                    raise PermissionError(
                        f"Access denied - parent directory outside allowed directories: {real_parent}"
                    )
                # Return the absolute path (not resolved) for the file itself, 
                # but we know the parent is safe.
                return absolute_path
            except FileNotFoundError:
                 # Re-raise if parent doesn't exist either
                 raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

    def _is_path_allowed(self, path_obj: Path) -> bool:
        """
        Helper to check if a specific Path object is inside any allowed directory.
        """
        path_str = str(path_obj)
        for allowed in self.allowed_directories:
            # Use strict string checking or pathlib's checking
            # Check if path_str starts with allowed path (handling trailing slashes implicitly via pathlib logic)
            try:
                path_obj.relative_to(allowed)
                return True
            except ValueError:
                continue
        return False

    def _format_size(self, size_bytes: int) -> str:
        """
        Formats bytes into human-readable string (B, KB, MB, GB, TB).
        Mirrors `formatSize` in `lib.ts`.
        """
        if size_bytes == 0:
            return "0 B"
        units = ("B", "KB", "MB", "GB", "TB")
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

    def read_text_file(
        self, 
        path: str, 
        tail: Optional[int] = None, 
        head: Optional[int] = None
    ) -> str:
        """
        Read the complete contents of a file from the file system as text.
        
        Handles various text encodings and provides detailed error messages if the file
        cannot be read. Use this tool when you need to examine the contents of a single file.
        Operates on the file as text regardless of extension.

        Args:
            path (str): The path to the file.
            tail (Optional[int]): If provided, returns only the last N lines of the file.
            head (Optional[int]): If provided, returns only the first N lines of the file.

        Returns:
            str: The content of the file.

        Raises:
            ValueError: If both head and tail are specified simultaneously.
            PermissionError: If path is not allowed.
            FileNotFoundError: If file does not exist.
        """
        if head is not None and tail is not None:
            raise ValueError("Cannot specify both head and tail parameters simultaneously")

        valid_path = self._validate_path(path)
        
        try:
            with open(valid_path, 'r', encoding='utf-8', errors='replace') as f:
                if head is not None:
                    lines = []
                    for _ in range(head):
                        line = f.readline()
                        if not line:
                            break
                        lines.append(line)
                    return "".join(lines)
                
                elif tail is not None:
                    # Efficient tailing for large files is complex, but reading lines is standard
                    # for agent context sizes.
                    lines = f.readlines()
                    return "".join(lines[-tail:])
                
                else:
                    return f.read()
        except Exception as e:
            # Catch-all for encoding issues or OS errors
            raise IOError(f"Failed to read file {path}: {str(e)}")

    def read_media_file(self, path: str) -> Dict[str, str]:
        """
        Read an image or audio file. Returns the base64 encoded data and MIME type.
        
        Only works within allowed directories.

        Args:
            path (str): The path to the media file.

        Returns:
            Dict[str, str]: A dictionary containing:
                - 'type': 'image', 'audio', or 'blob'
                - 'data': Base64 encoded string of the file content
                - 'mimeType': The detected mime type (e.g., 'image/png')
        """
        valid_path = self._validate_path(path)
        
        mime_type, _ = mimetypes.guess_type(valid_path)
        
        # Manual fallback for common types if mimetypes fails or returns None
        if not mime_type:
            ext = valid_path.suffix.lower()
            mime_map = {
                ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
                ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg"
            }
            mime_type = mime_map.get(ext, "application/octet-stream")
            
        with open(valid_path, 'rb') as f:
            data_b64 = base64.b64encode(f.read()).decode('utf-8')

        file_type = "blob"
        if mime_type.startswith("image/"):
            file_type = "image"
        elif mime_type.startswith("audio/"):
            file_type = "audio"

        return {
            "type": file_type,
            "data": data_b64,
            "mimeType": mime_type
        }

    def read_multiple_files(self, paths: List[str]) -> str:
        """
        Read the contents of multiple files simultaneously.
        
        This is more efficient than reading files one by one when you need to analyze
        or compare multiple files. Each file's content is returned with its path as a reference.
        Failed reads for individual files won't stop the entire operation.

        Args:
            paths (List[str]): Array of file paths to read. Each path must be within allowed directories.

        Returns:
            str: A concatenated string of file contents, separated by dashes. 
                 Format: "path/to/file:\n...content...\n---\n"
        """
        results = []
        for p in paths:
            try:
                content = self.read_text_file(p)
                results.append(f"{p}:\n{content}\n")
            except Exception as e:
                # Mirroring behavior: capture error message but continue
                error_msg = str(e)
                results.append(f"{p}: Error - {error_msg}")
        
        return "\n---\n".join(results)

    def write_file(self, path: str, content: str) -> str:
        """
        Create a new file or completely overwrite an existing file with new content.
        
        Use with caution as it will overwrite existing files without warning.
        Handles text content with proper encoding.

        Implementation Note:
        Uses an atomic write pattern to prevent symlink race conditions (TOCTOU),
        mirroring the logic in `lib.ts` `writeFileContent`.

        Args:
            path (str): File location.
            content (str): File content.

        Returns:
            str: Success message.
        """
        valid_path = self._validate_path(path)
        
        # Ensure parent directory exists
        valid_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Security: 'x' mode ensures exclusive creation - fails if file/symlink exists
            # preventing writes through pre-existing symlinks
            with open(valid_path, 'x', encoding='utf-8') as f:
                f.write(content)
        except FileExistsError:
            # Security: Use atomic rename to prevent race conditions where symlinks
            # could be created between validation and write.
            # 1. Write to a temp file in the same directory (ensures same filesystem)
            # 2. Rename temp file to target (atomic replacement)
            
            # Create temp file
            dir_name = valid_path.parent
            with tempfile.NamedTemporaryFile(
                mode='w', 
                dir=dir_name, 
                delete=False, 
                encoding='utf-8',
                suffix='.tmp'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = Path(tmp_file.name)
            
            try:
                # Atomic replacement
                os.replace(tmp_path, valid_path)
            except OSError as e:
                # Clean up temp file if rename fails
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise IOError(f"Failed to atomically write file {path}: {e}")
            
        return f"Successfully wrote to {path}"

    def edit_file(
        self, 
        path: str, 
        edits: List[EditOperation], 
        dry_run: bool = False
    ) -> str:
        """
        Make line-based edits to a text file.
        
        Each edit replaces exact line sequences with new content.
        Returns a git-style diff showing the changes made.
        
        Matching Logic (Mirrors `lib.ts` `applyFileEdits`):
        1. Tries to find an exact string match for `oldText`.
        2. If exact match fails, tries line-by-line matching with whitespace flexibility (trimming).
           If a flexible match is found, it attempts to preserve indentation.

        Args:
            path (str): File to edit.
            edits (List[Dict[str, str]]): List of edit operations. 
                Each dict must have 'oldText' (text to search for) and 'newText' (text to replace with).
            dry_run (bool): Preview changes using git-style diff format without applying them.

        Returns:
            str: A unified diff string showing the changes.

        Raises:
            ValueError: If match for oldText is not found.
        """
        valid_path = self._validate_path(path)
        
        with open(valid_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
            
        # Normalize line endings to \n for processing
        content_str = original_content.replace('\r\n', '\n')
        modified_content = content_str
        
        for edit in edits:
            old_text = edit.get('oldText', '').replace('\r\n', '\n')
            new_text = edit.get('newText', '').replace('\r\n', '\n')
            
            # 1. Try Exact Match
            if old_text in modified_content:
                modified_content = modified_content.replace(old_text, new_text, 1)
                continue
                
            # 2. Try Flexible Line-by-Line Match (Whitespace insensitive)
            old_lines = old_text.splitlines()
            content_lines = modified_content.splitlines()
            match_found = False
            
            # Scan through content lines
            for i in range(len(content_lines) - len(old_lines) + 1):
                potential_match = content_lines[i : i + len(old_lines)]
                
                # Check if all lines match when trimmed
                is_match = True
                for j, p_line in enumerate(potential_match):
                    if p_line.strip() != old_lines[j].strip():
                        is_match = False
                        break
                
                if is_match:
                    # Match found! Construct new lines preserving indentation
                    original_indent = ""
                    match = difflib.SequenceMatcher(None, content_lines[i], content_lines[i].lstrip()).find_longest_match(0, len(content_lines[i]), 0, len(content_lines[i].lstrip()))
                    if content_lines[i][:match.a]:
                        original_indent = content_lines[i][:match.a] # Simple whitespace extraction
                    elif len(content_lines[i]) > len(content_lines[i].lstrip()):
                         original_indent = content_lines[i][:len(content_lines[i]) - len(content_lines[i].lstrip())]

                    new_replacement_lines = []
                    new_text_lines = new_text.splitlines()
                    
                    for j, line in enumerate(new_text_lines):
                        if j == 0:
                             # Apply indentation of the first matched line to the first new line
                             new_replacement_lines.append(original_indent + line.lstrip())
                        else:
                             # For subsequent lines, we could try to calculate relative indentation
                             # For simplicity/reliability, we often just use the line as provided or apply base indent
                             # Here we use the line as provided in newText, assuming user handled relative indent,
                             # or we could apply original_indent. The TS code tries to preserve relative indent.
                             # We will just use the line as is, but ensure it exists.
                             new_replacement_lines.append(line)

                    # Replace the lines in the list
                    content_lines[i : i + len(old_lines)] = new_replacement_lines
                    modified_content = "\n".join(content_lines)
                    match_found = True
                    break
            
            if not match_found:
                raise ValueError(f"Could not find exact match for edit:\n{old_text}")

        # Generate Diff
        diff_lines = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            modified_content.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
            lineterm=''
        )
        diff_text = "".join(diff_lines)
        
        # Apply formatting to diff (surround with backticks logic from lib.ts)
        # For Python return, we usually just return the block.
        formatted_diff = f"```diff\n{diff_text}\n```"

        if not dry_run:
            # Atomic Write (Reuse write_file logic or implement directly)
            # We use the atomic rename pattern again
            dir_name = valid_path.parent
            with tempfile.NamedTemporaryFile(
                mode='w', 
                dir=dir_name, 
                delete=False, 
                encoding='utf-8',
                suffix='.tmp'
            ) as tmp_file:
                tmp_file.write(modified_content)
                tmp_path = Path(tmp_file.name)
            
            try:
                os.replace(tmp_path, valid_path)
            except OSError as e:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise IOError(f"Failed to save edits to {path}: {e}")
                
        return formatted_diff

    def create_directory(self, path: str) -> str:
        """
        Create a new directory or ensure a directory exists.
        
        Can create multiple nested directories in one operation. 
        If the directory already exists, this operation will succeed silently.
        
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
        
        Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes.
        
        Args:
            path (str): Directory path.

        Returns:
            str: Text listing with [FILE] and [DIR] prefixes.
        """
        valid_path = self._validate_path(path)
        
        if not valid_path.is_dir():
            raise NotADirectoryError(f"{path} is not a directory")

        # Sort by name for consistent output
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
            str: Detailed listing string including size summary.
        """
        valid_path = self._validate_path(path)
        
        entries_data = []
        total_size = 0
        total_files = 0
        total_dirs = 0

        with os.scandir(valid_path) as it:
            for entry in it:
                try:
                    stat = entry.stat()
                    is_dir = entry.is_dir()
                    size = stat.st_size if not is_dir else 0
                    
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
                except OSError:
                    # Skip entries we can't stat (permissions etc)
                    continue

        # Sort
        if sort_by == "size":
            entries_data.sort(key=lambda x: x["size"], reverse=True)
        else:
            entries_data.sort(key=lambda x: x["name"])

        # Format
        lines = []
        for item in entries_data:
            prefix = "[DIR] " if item["is_dir"] else "[FILE]"
            size_str = "" if item["is_dir"] else self._format_size(item["size"]).rjust(10)
            lines.append(f"{prefix} {item['name']:<30} {size_str}")

        lines.append("")
        lines.append(f"Total: {total_files} files, {total_dirs} directories")
        lines.append(f"Combined size: {self._format_size(total_size)}")

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
                Matches against file names and relative paths.

        Returns:
            str: JSON string representation of the tree.
        """
        root_path = self._validate_path(path)
        excludes = exclude_patterns or []

        def _build_tree(current_path: Path) -> List[Dict[str, Any]]:
            result = []
            try:
                entries = sorted(os.scandir(current_path), key=lambda e: e.name)
            except PermissionError:
                return []

            for entry in entries:
                # Calculate relative path for matching excludes
                # We use relative path from the user's requested root
                try:
                    rel_path = os.path.relpath(entry.path, root_path)
                except ValueError:
                    rel_path = entry.name

                # Check excludes
                should_exclude = False
                for pattern in excludes:
                    # Check basic filename match
                    if fnmatch.fnmatch(entry.name, pattern):
                        should_exclude = True
                        break
                    # Check relative path match (for deep patterns like src/*)
                    if fnmatch.fnmatch(rel_path, pattern):
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
        
        Both source and destination must be within allowed directories.
        Fails if destination exists.

        Args:
            source (str): Source path.
            destination (str): Destination path.

        Returns:
            str: Success message.
        """
        valid_source = self._validate_path(source)
        valid_dest = self._validate_path(destination)
        
        if valid_dest.exists():
             raise FileExistsError(f"Destination {destination} already exists")

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
            str: Newline-separated list of matching absolute paths.
        """
        root_path = self._validate_path(path)
        excludes = exclude_patterns or []
        results = []

        # Use os.walk for recursive traversal
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter excluded directories in-place
            for dirname in list(dirnames):
                full_dir_path = os.path.join(dirpath, dirname)
                rel_dir = os.path.relpath(full_dir_path, root_path)
                
                is_excluded = False
                for ex_pat in excludes:
                    if fnmatch.fnmatch(dirname, ex_pat) or fnmatch.fnmatch(rel_dir, ex_pat):
                        is_excluded = True
                        break
                if is_excluded:
                    dirnames.remove(dirname)
            
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

                # Check match pattern
                # Support simple name matching or relative path matching
                if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(rel_path, pattern):
                    results.append(full_path)

        return "\n".join(results) if results else "No matches found"

    def get_file_info(self, path: str) -> str:
        """
        Retrieve detailed metadata about a file or directory.
        
        Returns comprehensive information including size, creation time, 
        last modified time, permissions, and type.

        Args:
            path (str): The path to inspect.

        Returns:
            str: Formatted string of file attributes.
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

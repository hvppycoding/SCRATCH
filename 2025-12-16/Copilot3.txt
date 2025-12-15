🚨 Note: This log may contain personal information such as the contents of your files or terminal output. Please review the contents carefully before sharing.

panel/editAgent - 73ce1caa
Request Messages
System
User
Response
Metadata
requestType      : ChatCompletions
model            : gemini-3-pro-preview
maxPromptTokens  : 108801
maxResponseTokens: 64000
location         : 7
otherOptions     : {"temperature":0,"stream":true}
intent           : undefined
startTime        : 2025-12-15T15:07:21.195Z
endTime          : 2025-12-15T15:07:25.615Z
duration         : 4420ms
ourRequestId     : 52aa450b-f5ba-4af2-ab08-0b1fb08c741d
requestId        : 52aa450b-f5ba-4af2-ab08-0b1fb08c741d
serverRequestId  : 52aa450b-f5ba-4af2-ab08-0b1fb08c741d
timeToFirstToken : 3049ms
resolved model   : gemini-3-pro-preview
usage            : {"completion_tokens":186,"prompt_tokens":43529,"prompt_tokens_details":{"cached_tokens":42125},"total_tokens":43715,"reasoning_tokens":0}
tools            : [
    {
        "function": {
            "name": "create_directory",
            "description": "Create a new directory structure in the workspace. Will recursively create all directories in the path, like mkdir -p. You do not need to use this tool before using create_file, that tool will automatically create the needed directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dirPath": {
                        "type": "string",
                        "description": "The absolute path to the directory to create."
                    }
                },
                "required": [
                    "dirPath"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "create_file",
            "description": "This is a tool for creating a new file in the workspace. The file will be created with the specified content. The directory will be created if it does not already exist. Never use this tool to edit a file that already exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "The absolute path to the file to create."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file."
                    }
                },
                "required": [
                    "filePath",
                    "content"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "create_new_jupyter_notebook",
            "description": "Generates a new Jupyter Notebook (.ipynb) in VS Code. Jupyter Notebooks are interactive documents commonly used for data exploration, analysis, visualization, and combining code with narrative text. Prefer creating plain Python files or similar unless a user explicitly requests creating a new Jupyter Notebook or already has a Jupyter Notebook opened or exists in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to use to generate the jupyter notebook. This should be a clear and concise description of the notebook the user wants to create."
                    }
                },
                "required": [
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "create_new_workspace",
            "description": "Get comprehensive setup steps to help the user create complete project structures in a VS Code workspace. This tool is designed for full project initialization and scaffolding, not for creating individual files.\n\nWhen to use this tool:\n- User wants to create a new complete project from scratch\n- Setting up entire project frameworks (TypeScript projects, React apps, Node.js servers, etc.)\n- Initializing Model Context Protocol (MCP) servers with full structure\n- Creating VS Code extensions with proper scaffolding\n- Setting up Next.js, Vite, or other framework-based projects\n- User asks for \"new project\", \"create a workspace\", \"set up a [framework] project\"\n- Need to establish complete development environment with dependencies, config files, and folder structure\n\nWhen NOT to use this tool:\n- Creating single files or small code snippets\n- Adding individual files to existing projects\n- Making modifications to existing codebases\n- User asks to \"create a file\" or \"add a component\"\n- Simple code examples or demonstrations\n- Debugging or fixing existing code\n\nThis tool provides complete project setup including:\n- Folder structure creation\n- Package.json and dependency management\n- Configuration files (tsconfig, eslint, etc.)\n- Initial boilerplate code\n- Development environment setup\n- Build and run instructions\n\nUse other file creation tools for individual files within existing projects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to use to generate the new workspace. This should be a clear and concise description of the workspace the user wants to create."
                    }
                },
                "required": [
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "edit_notebook_file",
            "description": "This is a tool for editing an existing Notebook file in the workspace. Generate the \"explanation\" property first.\nThe system is very smart and can understand how to apply your edits to the notebooks.\nWhen updating the content of an existing cell, ensure newCode preserves whitespace and indentation exactly and does NOT include any code markers such as (...existing code...).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "An absolute path to the notebook file to edit, or the URI of a untitled, not yet named, file, such as `untitled:Untitled-1."
                    },
                    "cellId": {
                        "type": "string",
                        "description": "Id of the cell that needs to be deleted or edited. Use the value `TOP`, `BOTTOM` when inserting a cell at the top or bottom of the notebook, else provide the id of the cell after which a new cell is to be inserted. Remember, if a cellId is provided and editType=insert, then a cell will be inserted after the cell with the provided cellId."
                    },
                    "newCode": {
                        "anyOf": [
                            {
                                "type": "string",
                                "description": "The code for the new or existing cell to be edited. Code should not be wrapped within <VSCode.Cell> tags. Do NOT include code markers such as (...existing code...) to indicate existing code."
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "The code for the new or existing cell to be edited. Code should not be wrapped within <VSCode.Cell> tags"
                                }
                            }
                        ]
                    },
                    "language": {
                        "type": "string",
                        "description": "The language of the cell. `markdown`, `python`, `javascript`, `julia`, etc."
                    },
                    "editType": {
                        "type": "string",
                        "enum": [
                            "insert",
                            "delete",
                            "edit"
                        ],
                        "description": "The operation peformed on the cell, whether `insert`, `delete` or `edit`.\nUse the `editType` field to specify the operation: `insert` to add a new cell, `edit` to modify an existing cell's content, and `delete` to remove a cell."
                    }
                },
                "required": [
                    "filePath",
                    "editType",
                    "cellId"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "fetch_webpage",
            "description": "Fetches the main content from a web page. This tool is useful for summarizing or analyzing the content of a webpage. You should use this tool when you think the user is looking for information from a specific webpage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "An array of URLs to fetch content from."
                    },
                    "query": {
                        "type": "string",
                        "description": "The query to search for in the web page's content. This should be a clear and concise description of the content you want to find."
                    }
                },
                "required": [
                    "urls",
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "file_search",
            "description": "Search for files in the workspace by glob pattern. This only returns the paths of matching files. Use this tool when you know the exact filename pattern of the files you're searching for. Glob patterns match from the root of the workspace folder. Examples:\n- **/*.{js,ts} to match all js/ts files in the workspace.\n- src/** to match all files under the top-level src folder.\n- **/foo/**/*.js to match all js files under any foo folder in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search for files with names or paths matching this glob pattern."
                    },
                    "maxResults": {
                        "type": "number",
                        "description": "The maximum number of results to return. Do not use this unless necessary, it can slow things down. By default, only some matches are returned. If you use this and don't see what you're looking for, you can try again with a more specific query or a larger maxResults."
                    }
                },
                "required": [
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "grep_search",
            "description": "Do a fast text search in the workspace. Use this tool when you want to search with an exact string or regex. If you are not sure what words will appear in the workspace, prefer using regex patterns with alternation (|) or character classes to search for multiple potential words at once instead of making separate searches. For example, use 'function|method|procedure' to look for all of those words at once. Use includePattern to search within files matching a specific pattern, or in a specific file, using a relative path. Use 'includeIgnoredFiles' to include files normally ignored by .gitignore, other ignore files, and `files.exclude` and `search.exclude` settings. Warning: using this may cause the search to be slower, only set it when you want to search in ignored folders like node_modules or build outputs. Use this tool when you want to see an overview of a particular file, instead of using read_file many times to look for code within a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The pattern to search for in files in the workspace. Use regex with alternation (e.g., 'word1|word2|word3') or character classes to find multiple potential words in a single search. Be sure to set the isRegexp property properly to declare whether it's a regex or plain text pattern. Is case-insensitive."
                    },
                    "isRegexp": {
                        "type": "boolean",
                        "description": "Whether the pattern is a regex."
                    },
                    "includePattern": {
                        "type": "string",
                        "description": "Search files matching this glob pattern. Will be applied to the relative path of files within the workspace. To search recursively inside a folder, use a proper glob pattern like \"src/folder/**\". Do not use | in includePattern."
                    },
                    "maxResults": {
                        "type": "number",
                        "description": "The maximum number of results to return. Do not use this unless necessary, it can slow things down. By default, only some matches are returned. If you use this and don't see what you're looking for, you can try again with a more specific query or a larger maxResults."
                    },
                    "includeIgnoredFiles": {
                        "type": "boolean",
                        "description": "Whether to include files that would normally be ignored according to .gitignore, other ignore files and `files.exclude` and `search.exclude` settings. Warning: using this may cause the search to be slower. Only set it when you want to search in ignored folders like node_modules or build outputs."
                    }
                },
                "required": [
                    "query",
                    "isRegexp"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_changed_files",
            "description": "Get git diffs of current file changes in a git repository. Don't forget that you can use run_in_terminal to run git commands in a terminal as well.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repositoryPath": {
                        "type": "string",
                        "description": "The absolute path to the git repository to look for changes in. If not provided, the active git repository will be used."
                    },
                    "sourceControlState": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "staged",
                                "unstaged",
                                "merge-conflicts"
                            ]
                        },
                        "description": "The kinds of git state to filter by. Allowed values are: 'staged', 'unstaged', and 'merge-conflicts'. If not provided, all states will be included."
                    }
                }
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_errors",
            "description": "Get any compile or lint errors in a specific file or across all files. If the user mentions errors or problems in a file, they may be referring to these. Use the tool to see the same errors that the user is seeing. If the user asks you to analyze all errors, or does not specify a file, use this tool to gather errors for all files. Also use this tool after editing a file to validate the change.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePaths": {
                        "description": "The absolute paths to the files or folders to check for errors. Omit 'filePaths' when retrieving all errors.",
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                }
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "copilot_getNotebookSummary",
            "description": "This is a tool returns the list of the Notebook cells along with the id, cell types, line ranges, language, execution information and output mime types for each cell. This is useful to get Cell Ids when executing a notebook or determine what cells have been executed and what order, or what cells have outputs. If required to read contents of a cell use this to determine the line range of a cells, and then use read_file tool to read a specific line range. Requery this tool if the contents of the notebook change.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "An absolute path to the notebook file with the cell to run, or the URI of a untitled, not yet named, file, such as `untitled:Untitled-1.ipynb"
                    }
                },
                "required": [
                    "filePath"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_project_setup_info",
            "description": "Do not call this tool without first calling the tool to create a workspace. This tool provides a project setup information for a Visual Studio Code workspace based on a project type and programming language.",
            "parameters": {
                "type": "object",
                "properties": {
                    "projectType": {
                        "type": "string",
                        "description": "The type of project to create. Supported values are: 'python-script', 'python-project', 'mcp-server', 'model-context-protocol-server', 'vscode-extension', 'next-js', 'vite' and 'other'"
                    }
                },
                "required": [
                    "projectType"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_search_view_results",
            "description": "The results from the search view"
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_vscode_api",
            "description": "Get comprehensive VS Code API documentation and references for extension development. This tool provides authoritative documentation for VS Code's extensive API surface, including proposed APIs, contribution points, and best practices. Use this tool for understanding complex VS Code API interactions.\n\nWhen to use this tool:\n- User asks about specific VS Code APIs, interfaces, or extension capabilities\n- Need documentation for VS Code extension contribution points (commands, views, settings, etc.)\n- Questions about proposed APIs and their usage patterns\n- Understanding VS Code extension lifecycle, activation events, and packaging\n- Best practices for VS Code extension development architecture\n- API examples and code patterns for extension features\n- Troubleshooting extension-specific issues or API limitations\n\nWhen NOT to use this tool:\n- Creating simple standalone files or scripts unrelated to VS Code extensions\n- General programming questions not specific to VS Code extension development\n- Questions about using VS Code as an editor (user-facing features)\n- Non-extension related development tasks\n- File creation or editing that doesn't involve VS Code extension APIs\n\nCRITICAL usage guidelines:\n1. Always include specific API names, interfaces, or concepts in your query\n2. Mention the extension feature you're trying to implement\n3. Include context about proposed vs stable APIs when relevant\n4. Reference specific contribution points when asking about extension manifest\n5. Be specific about the VS Code version or API version when known\n\nScope: This tool is for EXTENSION DEVELOPMENT ONLY - building tools that extend VS Code itself, not for general file creation or non-extension programming tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search vscode documentation for. Should contain all relevant context."
                    }
                },
                "required": [
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "github_repo",
            "description": "Searches a GitHub repository for relevant source code snippets. Only use this tool if the user is very clearly asking for code snippets from a specific GitHub repository. Do not use this tool for Github repos that the user has open in their workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "The name of the Github repository to search for code in. Should must be formatted as '<owner>/<repo>'."
                    },
                    "query": {
                        "type": "string",
                        "description": "The query to search for repo. Should contain all relevant context."
                    }
                },
                "required": [
                    "repo",
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "install_extension",
            "description": "Install an extension in VS Code. Use this tool to install an extension in Visual Studio Code as part of a new workspace creation process only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The ID of the extension to install. This should be in the format <publisher>.<extension>."
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the extension to install. This should be a clear and concise description of the extension."
                    }
                },
                "required": [
                    "id",
                    "name"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "list_code_usages",
            "description": "Request to list all usages (references, definitions, implementations etc) of a function, class, method, variable etc. Use this tool when \n1. Looking for a sample implementation of an interface or class\n2. Checking how a function is used throughout the codebase.\n3. Including and updating all usages when changing a function, method, or constructor",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbolName": {
                        "type": "string",
                        "description": "The name of the symbol, such as a function name, class name, method name, variable name, etc."
                    },
                    "filePaths": {
                        "type": "array",
                        "description": "One or more file paths which likely contain the definition of the symbol. For instance the file which declares a class or function. This is optional but will speed up the invocation of this tool and improve the quality of its output.",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "symbolName"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "list_dir",
            "description": "List the contents of a directory. Result will have the name of the child. If the name ends in /, it's a folder, otherwise a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The absolute path to the directory to list."
                    }
                },
                "required": [
                    "path"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "open_simple_browser",
            "description": "Preview a website or open a URL in the editor's Simple Browser. Useful for quickly viewing locally hosted websites, demos, or resources without leaving the coding environment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The website URL to preview or open in the Simple Browser inside the editor. Must be either an http or https URL"
                    }
                },
                "required": [
                    "url"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.\n\nYou must specify the line range you're interested in. Line numbers are 1-indexed. If the file contents returned are insufficient for your task, you may call this tool again to retrieve more content. Prefer reading larger ranges over doing many small reads.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "description": "The absolute path of the file to read.",
                        "type": "string"
                    },
                    "startLine": {
                        "type": "number",
                        "description": "The line number to start reading from, 1-based."
                    },
                    "endLine": {
                        "type": "number",
                        "description": "The inclusive line number to end reading at, 1-based."
                    }
                },
                "required": [
                    "filePath",
                    "startLine",
                    "endLine"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "read_notebook_cell_output",
            "description": "This tool will retrieve the output for a notebook cell from its most recent execution or restored from disk. The cell may have output even when it has not been run in the current kernel session. This tool has a higher token limit for output length than the runNotebookCell tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "An absolute path to the notebook file with the cell to run, or the URI of a untitled, not yet named, file, such as `untitled:Untitled-1.ipynb"
                    },
                    "cellId": {
                        "type": "string",
                        "description": "The ID of the cell for which output should be retrieved."
                    }
                },
                "required": [
                    "filePath",
                    "cellId"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "replace_string_in_file",
            "description": "This is a tool for making edits in an existing file in the workspace. For moving or renaming files, use run in terminal tool with the 'mv' command instead. For larger edits, split them into smaller edits and call the edit tool multiple times to ensure accuracy. Before editing, always ensure you have the context to understand the file's contents and context. To edit a file, provide: 1) filePath (absolute path), 2) oldString (MUST be the exact literal text to replace including all whitespace, indentation, newlines, and surrounding code etc), and 3) newString (MUST be the exact literal text to replace \\`oldString\\` with (also including all whitespace, indentation, newlines, and surrounding code etc.). Ensure the resulting code is correct and idiomatic.). Each use of this tool replaces exactly ONE occurrence of oldString.\n\nCRITICAL for \\`oldString\\`: Must uniquely identify the single instance to change. Include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. If this string matches multiple locations, or does not match exactly, the tool will fail. Never use 'Lines 123-456 omitted' from summarized documents or ...existing code... comments in the oldString or newString.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "An absolute path to the file to edit."
                    },
                    "oldString": {
                        "type": "string",
                        "description": "The exact literal text to replace, preferably unescaped. For single replacements (default), include at least 3 lines of context BEFORE and AFTER the target text, matching whitespace and indentation precisely. For multiple replacements, specify expected_replacements parameter. If this string is not the exact literal text (i.e. you escaped it) or does not match exactly, the tool will fail."
                    },
                    "newString": {
                        "type": "string",
                        "description": "The exact literal text to replace `old_string` with, preferably unescaped. Provide the EXACT text. Ensure the resulting code is correct and idiomatic."
                    }
                },
                "required": [
                    "filePath",
                    "oldString",
                    "newString"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "run_notebook_cell",
            "description": "This is a tool for running a code cell in a notebook file directly in the notebook editor. The output from the execution will be returned. Code cells should be run as they are added or edited when working through a problem to bring the kernel state up to date and ensure the code executes successfully. Code cells are ready to run and don't require any pre-processing. If asked to run the first cell in a notebook, you should run the first code cell since markdown cells cannot be executed. NOTE: Avoid executing Markdown cells or providing Markdown cell IDs, as Markdown cells cannot be  executed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "An absolute path to the notebook file with the cell to run, or the URI of a untitled, not yet named, file, such as `untitled:Untitled-1.ipynb"
                    },
                    "reason": {
                        "type": "string",
                        "description": "An optional explanation of why the cell is being run. This will be shown to the user before the tool is run and is not necessary if it's self-explanatory."
                    },
                    "cellId": {
                        "type": "string",
                        "description": "The ID for the code cell to execute. Avoid providing markdown cell IDs as nothing will be executed."
                    },
                    "continueOnError": {
                        "type": "boolean",
                        "description": "Whether or not execution should continue for remaining cells if an error is encountered. Default to false unless instructed otherwise."
                    }
                },
                "required": [
                    "filePath",
                    "cellId"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "run_vscode_command",
            "description": "Run a command in VS Code. Use this tool to run a command in Visual Studio Code as part of a new workspace creation process only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "commandId": {
                        "type": "string",
                        "description": "The ID of the command to execute. This should be in the format <command>."
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the command to execute. This should be a clear and concise description of the command."
                    },
                    "args": {
                        "type": "array",
                        "description": "The arguments to pass to the command. This should be an array of strings.",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "commandId",
                    "name"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "semantic_search",
            "description": "Run a natural language search for relevant code or documentation comments from the user's current workspace. Returns relevant code snippets from the user's current workspace if it is large, or the full contents of the workspace if it is small.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search the codebase for. Should contain all relevant context. Should ideally be text that might appear in the codebase, such as function names, variable names, or comments."
                    }
                },
                "required": [
                    "query"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "test_failure",
            "description": "Includes test failure information in the prompt."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "vscode_searchExtensions_internal",
            "description": "This is a tool for browsing Visual Studio Code Extensions Marketplace. It allows the model to search for extensions and retrieve detailed information about them. The model should use this tool whenever it needs to discover extensions or resolve information about known ones. To use the tool, the model has to provide the category of the extensions, relevant search keywords, or known extension IDs. Note that search results may include false positives, so reviewing and filtering is recommended.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The category of extensions to search for",
                        "enum": [
                            "AI",
                            "Azure",
                            "Chat",
                            "Data Science",
                            "Debuggers",
                            "Extension Packs",
                            "Education",
                            "Formatters",
                            "Keymaps",
                            "Language Packs",
                            "Linters",
                            "Machine Learning",
                            "Notebooks",
                            "Programming Languages",
                            "SCM Providers",
                            "Snippets",
                            "Testing",
                            "Themes",
                            "Visualization",
                            "Other"
                        ]
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The keywords to search for"
                    },
                    "ids": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The ids of the extensions to search for"
                    }
                }
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "create_and_run_task",
            "description": "Creates and runs a build, run, or custom task for the workspace by generating or adding to a tasks.json file based on the project structure (such as package.json or README.md). If the user asks to build, run, launch and they have no tasks.json file, use this tool. If they ask to create or add a task, use this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspaceFolder": {
                        "type": "string",
                        "description": "The absolute path of the workspace folder where the tasks.json file will be created."
                    },
                    "task": {
                        "type": "object",
                        "description": "The task to add to the new tasks.json file.",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "The label of the task."
                            },
                            "type": {
                                "type": "string",
                                "description": "The type of the task. The only supported value is 'shell'.",
                                "enum": [
                                    "shell"
                                ]
                            },
                            "command": {
                                "type": "string",
                                "description": "The shell command to run for the task. Use this to specify commands for building or running the application."
                            },
                            "args": {
                                "type": "array",
                                "description": "The arguments to pass to the command.",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "isBackground": {
                                "type": "boolean",
                                "description": "Whether the task runs in the background without blocking the UI or other tasks. Set to true for long-running processes like watch tasks or servers that should continue executing without requiring user attention. When false, the task will block the terminal until completion."
                            },
                            "problemMatcher": {
                                "type": "array",
                                "description": "The problem matcher to use to parse task output for errors and warnings. Can be a predefined matcher like '$tsc' (TypeScript), '$eslint - stylish', '$gcc', etc., or a custom pattern defined in tasks.json. This helps VS Code display errors in the Problems panel and enables quick navigation to error locations.",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "group": {
                                "type": "string",
                                "description": "The group to which the task belongs."
                            }
                        },
                        "required": [
                            "label",
                            "type",
                            "command"
                        ]
                    }
                },
                "required": [
                    "task",
                    "workspaceFolder"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_task_output",
            "description": "Get the output of a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The task ID for which to get the output."
                    },
                    "workspaceFolder": {
                        "type": "string",
                        "description": "The workspace folder path containing the task"
                    }
                },
                "required": [
                    "id",
                    "workspaceFolder"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_terminal_output",
            "description": "Get the output of a terminal command previously started with run_in_terminal",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The ID of the terminal to check."
                    }
                },
                "required": [
                    "id"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "manage_todo_list",
            "description": "Manage a structured todo list to track progress and plan tasks throughout your coding session. Use this tool VERY frequently to ensure task visibility and proper planning.\n\nWhen to use this tool:\n- Complex multi-step work requiring planning and tracking\n- When user provides multiple tasks or requests (numbered/comma-separated)\n- After receiving new instructions that require multiple steps\n- BEFORE starting work on any todo (mark as in-progress)\n- IMMEDIATELY after completing each todo (mark completed individually)\n- When breaking down larger tasks into smaller actionable steps\n- To give users visibility into your progress and planning\n\nWhen NOT to use:\n- Single, trivial tasks that can be completed in one step\n- Purely conversational/informational requests\n- When just reading files or performing simple searches\n\nCRITICAL workflow:\n1. Plan tasks by writing todo list with specific, actionable items\n2. Mark ONE todo as in-progress before starting work\n3. Complete the work for that specific todo\n4. Mark that todo as completed IMMEDIATELY\n5. Move to next todo and repeat\n\nTodo states:\n- not-started: Todo not yet begun\n- in-progress: Currently working (limit ONE at a time)\n- completed: Finished successfully\n\nIMPORTANT: Mark todos completed as soon as they are done. Do not batch completions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todoList": {
                        "type": "array",
                        "description": "Complete array of all todo items (required for write operation, ignored for read). Must include ALL items - both existing and new.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "number",
                                    "description": "Unique identifier for the todo. Use sequential numbers starting from 1."
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Concise action-oriented todo label (3-7 words). Displayed in UI."
                                },
                                "status": {
                                    "type": "string",
                                    "enum": [
                                        "not-started",
                                        "in-progress",
                                        "completed"
                                    ],
                                    "description": "not-started: Not begun | in-progress: Currently working (max 1) | completed: Fully finished with no blockers"
                                }
                            },
                            "required": [
                                "id",
                                "title",
                                "status"
                            ]
                        }
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "write",
                            "read"
                        ],
                        "description": "write: Replace entire todo list with new content. read: Retrieve current todo list. ALWAYS provide complete list when writing - partial updates not supported."
                    }
                },
                "required": [
                    "operation"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "run_in_terminal",
            "description": "This tool allows you to execute shell commands in a persistent bash terminal session, preserving environment variables, working directory, and other context across multiple commands.\n\nCommand Execution:\n- Use && to chain simple commands on one line\n- Prefer pipelines | over temporary files for data flow\n- Never create a sub-shell (eg. bash -c \"command\") unless explicitly asked\n\nDirectory Management:\n- Must use absolute paths to avoid navigation issues\n- Use $PWD for current directory references\n- Consider using pushd/popd for directory stack management\n- Supports directory shortcuts like ~ and -\n\nProgram Execution:\n- Supports Python, Node.js, and other executables\n- Install packages via package managers (brew, apt, etc.)\n- Use which or command -v to verify command availability\n\nBackground Processes:\n- For long-running tasks (e.g., servers), set isBackground=true\n- Returns a terminal ID for checking status and runtime later\n\nOutput Management:\n- Output is automatically truncated if longer than 60KB to prevent context overflow\n- Use head, tail, grep, awk to filter and limit output size\n- For pager commands, disable paging: git --no-pager or add | cat\n- Use wc -l to count lines before displaying large outputs\n\nBest Practices:\n- Quote variables: \"$var\" instead of $var to handle spaces\n- Use find with -exec or xargs for file operations\n- Be specific with commands to avoid excessive output\n- Use [[ ]] for conditional tests instead of [ ]\n- Prefer $() over backticks for command substitution\n- Use set -e at start of complex commands to exit on errors",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run in the terminal."
                    },
                    "explanation": {
                        "type": "string",
                        "description": "A one-sentence description of what the command does. This will be shown to the user before the command is run."
                    },
                    "isBackground": {
                        "type": "boolean",
                        "description": "Whether the command starts a background process. If true, the command will run in the background and you will not see the output. If false, the tool call will block on the command finishing, and then you will get the output. Examples of background processes: building in watch mode, starting a server. You can check the output of a background process later on by using get_terminal_output."
                    }
                },
                "required": [
                    "command",
                    "explanation",
                    "isBackground"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "run_task",
            "description": "Runs a VS Code task.\n\n- If you see that an appropriate task exists for building or running code, prefer to use this tool to run the task instead of using the run_in_terminal tool.\n- Make sure that any appropriate build or watch task is running before trying to run tests or execute code.\n- If the user asks to run a task, use this tool to do so.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspaceFolder": {
                        "type": "string",
                        "description": "The workspace folder path containing the task"
                    },
                    "id": {
                        "type": "string",
                        "description": "The task ID to run."
                    }
                },
                "required": [
                    "workspaceFolder",
                    "id"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "runSubagent",
            "description": "Launch a new agent to handle complex, multi-step tasks autonomously. This tool is good at researching complex questions, searching for code, and executing multi-step tasks. When you are searching for a keyword or file and are not confident that you will find the right match in the first few tries, use this agent to perform the search for you.\n\n- Agents do not run async or in the background, you will wait for the agent's result.\n- When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.\n- Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.\n- The agent's outputs should generally be trusted\n- Clearly tell the agent whether you expect it to write code or just to do research (search, file reads, web fetches, etc.), since it is not aware of the user's intent",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "A detailed description of the task for the agent to perform"
                    },
                    "description": {
                        "type": "string",
                        "description": "A short (3-5 word) description of the task"
                    }
                },
                "required": [
                    "prompt",
                    "description"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "terminal_last_command",
            "description": "Get the last command run in the active terminal."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "terminal_selection",
            "description": "Get the current selection in the active terminal."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "configure_notebook",
            "description": "Tool used to configure a Notebook. ALWAYS use this tool before running/executing any Notebook Cells for the first time or before listing/installing packages in Notebooks for the first time. I.e. there is no need to use this tool more than once for the same notebook.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "description": "The absolute path of the notebook with the active kernel.",
                        "type": "string"
                    }
                },
                "required": [
                    "filePath"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "notebook_install_packages",
            "description": "Install a list of packages on a notebook kernel to be used within that notebook. This tool should be used when working with a jupyter notebook with python code cells. Do not use this tool if not already working with a notebook, or for a language other than python. If the tool configure_notebooks exists, then ensure to call configure_notebooks before using this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "description": "The absolute path of the notebook with the active kernel.",
                        "type": "string"
                    },
                    "packageList": {
                        "description": "A list of packages to install.",
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "filePath",
                    "packageList"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "notebook_list_packages",
            "description": "List the installed packages that are currently available in the selected kernel for a notebook editor. This tool should be used when working with a jupyter notebook with python code cells. Do not use this tool if not already working with a notebook, or for a language other than python. If the tool configure_notebooks exists, then ensure to call configure_notebooks before using this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "description": "The absolute path of the notebook with the active kernel.",
                        "type": "string"
                    }
                },
                "required": [
                    "filePath"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "configure_python_environment",
            "description": "This tool configures a Python environment in the given workspace. ALWAYS Use this tool to set up the user's chosen environment and ALWAYS call this tool before using any other Python related tools or running any Python command in the terminal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resourcePath": {
                        "type": "string",
                        "description": "The path to the Python file or workspace for which a Python Environment needs to be configured."
                    }
                },
                "required": []
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_python_environment_details",
            "description": "This tool will retrieve the details of the Python Environment for the specified file or workspace. The details returned include the 1. Type of Python Environment (conda, venv, etec), 2. Version of Python, 3. List of all installed Python packages with their versions. ALWAYS call configure_python_environment before using this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resourcePath": {
                        "type": "string",
                        "description": "The path to the Python file or workspace to get the environment information for."
                    }
                },
                "required": []
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "get_python_executable_details",
            "description": "This tool will retrieve the details of the Python Environment for the specified file or workspace. ALWAYS use this tool before executing any Python command in the terminal. This tool returns the details of how to construct the fully qualified path and or command including details such as arguments required to run Python in a terminal. Note: Instead of executing `python --version` or `python -c 'import sys; print(sys.executable)'`, use this tool to get the Python executable path to replace the `python` command. E.g. instead of using `python -c 'import sys; print(sys.executable)'`, use this tool to build the command `conda run -n <env_name> -c 'import sys; print(sys.executable)'`. ALWAYS call configure_python_environment before using this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resourcePath": {
                        "type": "string",
                        "description": "The path to the Python file or workspace to get the executable information for. If not provided, the current workspace will be used. Where possible pass the path to the file or workspace."
                    }
                },
                "required": []
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "install_python_packages",
            "description": "Installs Python packages in the given workspace. Use this tool to install Python packages in the user's chosen Python environment. ALWAYS call configure_python_environment before using this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "packageList": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The list of Python packages to install."
                    },
                    "resourcePath": {
                        "type": "string",
                        "description": "The path to the Python file or workspace into which the packages are installed. If not provided, the current workspace will be used. Where possible pass the path to the file or workspace."
                    }
                },
                "required": [
                    "packageList"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_container_management_tools",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThis group of tools is focused on managing the lifecycle of containers within a containerization platform. The tools allow users to start, stop, restart, or remove containers using their names or IDs, providing essential control over running applications. Additionally, users can run new containers, enabling the deployment of new instances of applications or services as needed. Together, these tools facilitate the dynamic management of containerized environments, allowing for efficient resource utilization and application scalability.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_image_management_tools",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThe tools in this group are designed for managing container images, which are essential for creating and deploying containers. Users can pull new images from repositories or remove existing ones, ensuring that the local environment is up-to-date with the necessary application versions. The ability to inspect images allows users to understand their configurations and dependencies, while tagging images with new identifiers helps in organizing and versioning them effectively. These functionalities are crucial for maintaining a clean and efficient image repository, supporting continuous integration and deployment workflows.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_container_inspection_and_logging_tools",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThis group provides tools for inspecting and monitoring the performance of containers. Users can inspect containers to retrieve detailed information about their configurations, statuses, and resource usage. Additionally, the ability to view logs for specific containers allows for troubleshooting and performance analysis, helping users identify issues and optimize their applications. By combining inspection and logging capabilities, these tools enable developers and system administrators to maintain the health and efficiency of their containerized applications.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_container_inventory_tools",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThe tools in this group focus on inventory management for containers, images, and volumes. Users can list all containers, including those that are stopped, which aids in monitoring resource usage and managing application states. Similarly, listing container images provides visibility into available images, including untagged and orphaned ones, which can help in cleaning up unused resources. Additionally, listing container volumes allows users to manage persistent data storage associated with containers. Together, these tools provide a comprehensive overview of the container ecosystem, facilitating better resource management and operational efficiency.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_copilot_conta_list_networks",
            "description": "List container networks",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_copilot_conta_prune",
            "description": "Prune unused container resources",
            "parameters": {
                "type": "object",
                "properties": {
                    "pruneTarget": {
                        "type": "string",
                        "enum": [
                            "containers",
                            "images",
                            "volumes",
                            "networks",
                            "all"
                        ],
                        "description": "The type of resource to prune"
                    }
                },
                "required": [
                    "pruneTarget"
                ],
                "additionalProperties": false,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_add_or_commit",
            "description": "Add file contents to the index (git add <pathspec>) OR record changes to the repository (git commit -m <message> [files...]). Use the 'action' parameter to specify which action to perform.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "description": "The action to perform: 'add' or 'commit'",
                        "enum": [
                            "add",
                            "commit"
                        ],
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to run git add or commit in",
                        "type": "string"
                    },
                    "files": {
                        "description": "Optional array of files to add or commit. If omitted, all files are added or all staged changes are committed.",
                        "items": {
                            "type": "string"
                        },
                        "type": "array"
                    },
                    "message": {
                        "description": "The commit message (required if action is 'commit')",
                        "type": "string"
                    }
                },
                "required": [
                    "directory",
                    "action"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_blame",
            "description": "Show what revision and author last modified each line of a file (git blame <file>).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "description": "The directory to run git blame in",
                        "type": "string"
                    },
                    "file": {
                        "description": "The file to blame",
                        "type": "string"
                    }
                },
                "required": [
                    "directory",
                    "file"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_branch",
            "description": "List or create branches (git branch).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "description": "Git branch action to be executed",
                        "enum": [
                            "create",
                            "list"
                        ],
                        "type": "string"
                    },
                    "branch_name": {
                        "description": "(Optional) Name of the branch to create or delete",
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to run git branch in",
                        "type": "string"
                    }
                },
                "required": [
                    "directory",
                    "action"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_checkout",
            "description": "Switch branches or restore working tree files (git checkout <branch>).",
            "parameters": {
                "type": "object",
                "properties": {
                    "branch": {
                        "description": "The branch to checkout. This must be a valid branch name without spaces",
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to run git checkout in",
                        "type": "string"
                    }
                },
                "required": [
                    "directory",
                    "branch"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_log_or_diff",
            "description": "Show commit logs or changes between commits (git log --oneline or git diff).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "description": "The action to perform: 'log' for commit logs or 'diff' for changes",
                        "enum": [
                            "log",
                            "diff"
                        ],
                        "type": "string"
                    },
                    "commit": {
                        "description": "Optional commit to compare against HEAD for 'diff', defaults to HEAD",
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to run the command in",
                        "type": "string"
                    }
                },
                "required": [
                    "directory",
                    "action"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_push",
            "description": "Update remote refs along with associated objects (git push).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "description": "The directory to run git push in",
                        "type": "string"
                    }
                },
                "required": [
                    "directory"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_stash",
            "description": "Stash the changes in a dirty working directory (git stash).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "description": "The directory to run git stash in",
                        "type": "string"
                    },
                    "name": {
                        "description": "Optional name for the stash (used as the stash message)",
                        "type": "string"
                    }
                },
                "required": [
                    "directory"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_status",
            "description": "Show the working tree status (git status).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "description": "The directory to run git status in",
                        "type": "string"
                    }
                },
                "required": [
                    "directory"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_git_worktree",
            "description": "List or add git worktrees (git worktree <action>).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "description": "Git worktree action to be executed",
                        "enum": [
                            "list",
                            "add"
                        ],
                        "type": "string"
                    },
                    "branch": {
                        "description": "(Optional) Existing branch for the new worktree (used for add)",
                        "type": "string"
                    },
                    "directory": {
                        "description": "The directory to run git worktree in",
                        "type": "string"
                    },
                    "path": {
                        "description": "(Optional) Path for the worktree (required for add)",
                        "type": "string"
                    }
                },
                "required": [
                    "directory",
                    "action"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_gitkraken_workspace_list",
            "description": " Lists all Gitkraken workspaces",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_issues_add_comment",
            "description": "Add a comment to an issue",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_organization": {
                        "description": "Optionally set the Azure DevOps organization name. Required for Azure DevOps",
                        "type": "string"
                    },
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name. Required for Azure DevOps",
                        "type": "string"
                    },
                    "comment": {
                        "description": "The text content of the comment",
                        "type": "string"
                    },
                    "issue_id": {
                        "description": "The ID of the issue to comment on",
                        "type": "string"
                    },
                    "provider": {
                        "description": "Specify the issue provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "jira",
                            "azure",
                            "linear"
                        ],
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Repository name. This is required for GitHub and GitLab",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Organization name. This is required for GitHub and GitLab",
                        "type": "string"
                    }
                },
                "required": [
                    "provider",
                    "issue_id",
                    "comment"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_issues_assigned_to_me",
            "description": "Fetch issues assigned to the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_organization": {
                        "description": "Optionally set the Azure DevOps organization name. Required for Azure DevOps",
                        "type": "string"
                    },
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name. Required for Azure DevOps",
                        "type": "string"
                    },
                    "page": {
                        "description": "Optional parameter to specify the page number, defaults to 1",
                        "type": "number"
                    },
                    "provider": {
                        "description": "Specify the issue provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "jira",
                            "azure",
                            "linear"
                        ],
                        "type": "string"
                    }
                },
                "required": [
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_issues_get_detail",
            "description": "Retrieve detailed information about a specific issue by its unique ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_organization": {
                        "description": "Optionally set the Azure DevOps organization name. Required for Azure DevOps",
                        "type": "string"
                    },
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name. Required for Azure DevOps",
                        "type": "string"
                    },
                    "issue_id": {
                        "description": "The ID of the issue to retrieve",
                        "type": "string"
                    },
                    "provider": {
                        "description": "Specify the issue provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "jira",
                            "azure",
                            "linear"
                        ],
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Repository name. This is required for GitHub and GitLab",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Organization name. This is required for GitHub and GitLab",
                        "type": "string"
                    }
                },
                "required": [
                    "provider",
                    "issue_id"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_pull_request_assigned_to_me",
            "description": "Search pull requests where you are the assignee, author, or reviewer",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name of the pull request. Required for Azure DevOps",
                        "type": "string"
                    },
                    "is_closed": {
                        "description": "Set to true if you want to search for closed pull requests",
                        "type": "boolean"
                    },
                    "page": {
                        "description": "Optional parameter to specify the page number, defaults to 1",
                        "type": "number"
                    },
                    "provider": {
                        "description": "Specify the git provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "bitbucket",
                            "azure"
                        ],
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Set the repository name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Set the organization name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    }
                },
                "required": [
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_pull_request_create",
            "description": "Create a new pull request",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name of the pull request. Required for Azure DevOps",
                        "type": "string"
                    },
                    "body": {
                        "description": "The body/description of the pull request",
                        "type": "string"
                    },
                    "is_draft": {
                        "description": "Create as draft pull request",
                        "type": "boolean"
                    },
                    "provider": {
                        "description": "Specify the git provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "bitbucket",
                            "azure"
                        ],
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Set the repository name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Set the organization name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    },
                    "source_branch": {
                        "description": "Source branch from which the pull request will be created",
                        "type": "string"
                    },
                    "target_branch": {
                        "description": "Target branch where the pull request will be merged",
                        "type": "string"
                    },
                    "title": {
                        "description": "The title of the pull request",
                        "type": "string"
                    }
                },
                "required": [
                    "repository_name",
                    "repository_organization",
                    "title",
                    "source_branch",
                    "target_branch",
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_pull_request_create_review",
            "description": "Create a review for a pull request",
            "parameters": {
                "type": "object",
                "properties": {
                    "approve": {
                        "description": "Set to true if you want to approve the pull request",
                        "type": "boolean"
                    },
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name of the pull request. Required for Azure DevOps",
                        "type": "string"
                    },
                    "provider": {
                        "description": "Specify the git provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "bitbucket",
                            "azure"
                        ],
                        "type": "string"
                    },
                    "pull_request_id": {
                        "description": "ID of the pull request to create the review for",
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Set the repository name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Set the organization name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    },
                    "review": {
                        "description": "Comment to add to the pull request review",
                        "type": "string"
                    }
                },
                "required": [
                    "repository_name",
                    "repository_organization",
                    "pull_request_id",
                    "review",
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_pull_request_get_comments",
            "description": "Get all the comments in a pull requests",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name of the pull request. Required for Azure DevOps",
                        "type": "string"
                    },
                    "provider": {
                        "description": "Specify the git provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "bitbucket",
                            "azure"
                        ],
                        "type": "string"
                    },
                    "pull_request_id": {
                        "description": "ID of the pull request to add the comment to",
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Set the repository name of the pull request",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Set the organization name of the pull request",
                        "type": "string"
                    }
                },
                "required": [
                    "repository_name",
                    "repository_organization",
                    "pull_request_id",
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_pull_request_get_detail",
            "description": "Get an specific pull request",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name of the pull request. Required for Azure DevOps",
                        "type": "string"
                    },
                    "provider": {
                        "description": "Specify the git provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "bitbucket",
                            "azure"
                        ],
                        "type": "string"
                    },
                    "pull_request_files": {
                        "description": "Set to true if you want to retrieve the files changed in the pull request. Not supported by Azure DevOps.",
                        "type": "boolean"
                    },
                    "pull_request_id": {
                        "description": "ID of the pull request to retrieve",
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Set the repository name of the pull request",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Set the organization name of the pull request",
                        "type": "string"
                    }
                },
                "required": [
                    "pull_request_id",
                    "repository_name",
                    "repository_organization",
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_gitkraken_repository_get_file_content",
            "description": "Get file content from a repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "azure_project": {
                        "description": "Optionally set the Azure DevOps project name of the pull request. Required for Azure DevOps",
                        "type": "string"
                    },
                    "file_path": {
                        "description": "File path to retrieve from the repository",
                        "type": "string"
                    },
                    "provider": {
                        "description": "Specify the git provider",
                        "enum": [
                            "github",
                            "gitlab",
                            "bitbucket",
                            "azure"
                        ],
                        "type": "string"
                    },
                    "ref": {
                        "description": "Set the branch, tag, or commit SHA to retrieve the file from",
                        "type": "string"
                    },
                    "repository_name": {
                        "description": "Set the repository name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    },
                    "repository_organization": {
                        "description": "Set the organization name of the pull request. Required for Azure DevOps and Bitbucket",
                        "type": "string"
                    }
                },
                "required": [
                    "repository_name",
                    "repository_organization",
                    "ref",
                    "file_path",
                    "provider"
                ]
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_python_code_validation_and_execution",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThis group of tools focuses on validating and executing Python code snippets within a workspace environment. The 'Check Python file for syntax errors' tool allows users to identify syntax issues in Python files, providing detailed error messages that include line numbers and error types. This is particularly useful for debugging and validating code before execution. The 'Execute Python code snippets directly in the workspace environment' tool enables users to run Python code snippets seamlessly, avoiding common issues associated with terminal execution, such as shell escaping. It provides clean output and is ideal for quick testing and validation of code. Additionally, the 'Validate Python code snippets for syntax errors without saving to file' tool allows for quick checks of code snippets, making it easier to validate generated or user-provided code before running it. Together, these tools streamline the process of writing, testing, and debugging Python code in a cohesive workspace setting.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_python_import_analysis_tools",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThis group is dedicated to analyzing and managing Python imports within a workspace. The 'Analyze imports across workspace user files' tool helps users identify all top-level modules that are imported in their project, including both resolved and unresolved imports. This is essential for understanding project dependencies and identifying any missing packages. The 'Get available top-level modules from installed Python packages in environment' tool complements this by providing a list of all modules that can be imported from the installed packages, allowing users to verify the availability of necessary libraries. Together, these tools facilitate a comprehensive understanding of import patterns and dependencies, enabling users to manage their Python projects more effectively.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_python_environment_management",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThis group of tools is focused on managing Python environments within a workspace. The 'Get Python environment information for workspace' tool provides users with insights into the current active Python environment and all available environments, which is crucial for troubleshooting environment-related issues. The 'Get current Python analysis settings and configuration for a workspace' tool allows users to review their Python analysis settings, helping to diagnose any configuration problems that may arise. Additionally, the 'Switch active Python environment for workspace' tool enables users to easily change their active Python environment, whether switching between different Python installations or virtual environments. Together, these tools empower users to effectively manage their Python environments, ensuring that they can work with the correct settings and dependencies for their projects.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "activate_workspace_structure_and_file_management",
            "description": "Call this tool when you need access to a new category of tools. The category of tools is described as follows:\n\nThis group provides tools for understanding and managing the structure of a Python workspace. The 'Get workspace root directories' tool allows users to retrieve the root directories of their workspace, which is essential for navigating and organizing project files. The 'Get list of all user Python files in workspace' tool complements this by providing a comprehensive list of all user-created Python files, excluding library and dependency files. This tool respects user-defined settings for file inclusion and exclusion, making it easier to analyze and operate on relevant code. Together, these tools enhance users' ability to navigate their workspace, manage their files effectively, and gain insights into their project structure, ultimately leading to a more organized and efficient development process.\n\nBe sure to call this tool if you need a capability related to the above."
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_pylance_mcp_s_pylanceDocuments",
            "description": "Search Pylance documentation for Python language server help, configuration guidance, feature explanations, and troubleshooting. Returns comprehensive answers about Pylance settings, capabilities, and usage. Use when users ask: How to configure Pylance? What features are available? How to fix Pylance issues?",
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Detailed question in natural language. Think of it as a prompt for an LLM. Do not use keyword search terms."
                    }
                },
                "required": [
                    "search"
                ],
                "additionalProperties": false,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_pylance_mcp_s_pylanceInvokeRefactoring",
            "description": "Apply automated code refactoring to Python files. Returns refactored content (does not modify original file) unless mode is \"update\". Use for: extracting functions, organizing imports, improving code structure, applying refactoring patterns.  Optional \"mode\" parameter: \"update\" updates the file, \"edits\" returns a WorkspaceEdit, \"string\" returns updated content as string. If mode is not specified, \"update\" will be used as the default. The \"edits\" mode is helpful for determining if a file needs changes (for example, to remove unused imports or fix import formatting) without making any modifications; if no changes are needed, the result will be either an empty WorkspaceEdit or a message indicating that no text edits were found. Available refactorings: source.unusedImports: - Removes all unused import statements from a Python file. Use when imports are imported but never referenced in the code. Requires fileUri parameter pointing to a Python file with unused imports.\nsource.convertImportFormat: - Converts import statements between absolute and relative formats according to python.analysis.importFormat setting. Use when import format consistency is needed. Requires fileUri parameter pointing to a Python file with imports to convert.\nsource.convertImportStar: - Converts all wildcard imports (from module import *) to explicit imports listing all imported symbols. Use when explicit imports are preferred for better code clarity and IDE support. Requires fileUri parameter pointing to a Python file with wildcard imports.\nsource.addTypeAnnotation: - Adds type annotations to all variables and functions in a Python file that can be inferred from their usage. Use when type hints are needed for better type checking and code clarity. Requires fileUri parameter pointing to a Python file with unannotated variables or functions.\nsource.fixAll.pylance: - Applies all available automatic code fixes from python.analysis.fixAll setting. Use when multiple code issues need to be addressed simultaneously. Requires fileUri parameter pointing to a Python file with fixable issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fileUri": {
                        "type": "string",
                        "description": "The uri of the file to invoke the refactoring."
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the refactoring to invoke. This must be one of these [source.unusedImports, source.convertImportFormat, source.convertImportStar, source.addTypeAnnotation, source.fixAll.pylance]"
                    },
                    "mode": {
                        "type": "string",
                        "enum": [
                            "update",
                            "edits",
                            "string"
                        ],
                        "description": "Determines the output mode: \"update\" updates the file directly, \"edits\" returns a WorkspaceEdit, \"string\" returns the updated content as a string. If omitted, \"update\" will be used as the default. The \"edits\" mode is especially useful for checking if any changes are needed (such as unused imports or import formatting issues) without modifying the file, as it will return a WorkspaceEdit only if edits are required."
                    }
                },
                "required": [
                    "fileUri",
                    "name"
                ],
                "additionalProperties": false,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_copilot_conta_list_containers",
            "description": "List containers, including stopped ones",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_pylance_mcp_s_pylanceImports",
            "description": "Analyze imports across workspace user files. Returns all top-level module names imported, including resolved and unresolved imports. Use for: finding missing dependencies, understanding project dependencies, analyzing import patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspaceRoot": {
                        "type": "string",
                        "description": "The root directory uri of the workspace."
                    }
                },
                "required": [
                    "workspaceRoot"
                ],
                "additionalProperties": false,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_pylance_mcp_s_pylanceFileSyntaxErrors",
            "description": "Check Python file for syntax errors. Returns detailed error list with line numbers, messages, and error types. Use when: users report syntax problems, validating files before processing, debugging parse errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspaceRoot": {
                        "type": "string",
                        "description": "The root directory uri of the workspace."
                    },
                    "fileUri": {
                        "type": "string",
                        "description": "The uri of the file to check for syntax errors. Must be a user file in the workspace."
                    }
                },
                "required": [
                    "workspaceRoot",
                    "fileUri"
                ],
                "additionalProperties": false,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_copilot_conta_list_images",
            "description": "List container images, including untagged and orphaned ones",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_pylance_mcp_s_pylanceWorkspaceRoots",
            "description": "Get workspace root directories. Returns workspace root for specific file or all workspace roots if no file provided. Use for: understanding workspace structure, getting paths for other operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fileUri": {
                        "type": "string",
                        "description": "The uri of the file to check its workspace"
                    }
                },
                "additionalProperties": false,
                "$schema": "http://json-schema.org/draft-07/schema#"
            }
        },
        "type": "function"
    },
    {
        "function": {
            "name": "mcp_copilot_conta_list_volumes",
            "description": "List container volumes",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "type": "function"
    }
]
Request Messages
System
You are an expert AI programming assistant, working with a user in the VS Code editor.
When asked for your name, you must respond with "GitHub Copilot". When asked about the model you are using, you must state that you are using Gemini 3 Pro (Preview).
Follow the user's requirements carefully & to the letter.
Follow Microsoft content policies.
Avoid content that violates copyrights.
If you are asked to generate content that is harmful, hateful, racist, sexist, lewd, or violent, only respond with "Sorry, I can't assist with that."
Keep your answers short and impersonal.
<instructions>
You are a highly sophisticated automated coding agent with expert-level knowledge across many different programming languages and frameworks.
The user will ask a question, or ask you to perform a task, and it may require lots of research to answer correctly. There is a selection of tools that let you perform actions or retrieve helpful context to answer the user's question.
You will be given some context and attachments along with the user prompt. You can use them if they are relevant to the task, and ignore them if not. Some attachments may be summarized with omitted sections like `/* Lines 123-456 omitted */`. You can use the read_file tool to read more context if needed. Never pass this omitted line marker to an edit tool.
If you can infer the project type (languages, frameworks, and libraries) from the user's query or the context that you have, make sure to keep them in mind when making changes.
If the user wants you to implement a feature and they have not specified the files to edit, first break down the user's request into smaller concepts and think about the kinds of files you need to grasp each concept.
If you aren't sure which tool is relevant, you can call multiple tools. You can call tools repeatedly to take actions or gather as much context as needed until you have completed the task fully. Don't give up unless you are sure the request cannot be fulfilled with the tools you have. It's YOUR RESPONSIBILITY to make sure that you have done all you can to collect necessary context.
When reading files, prefer reading large meaningful chunks rather than consecutive small sections to minimize tool calls and gain better context.
Don't make assumptions about the situation- gather context first, then perform the task or answer the question.
Think creatively and explore the workspace in order to make a complete fix.
Don't repeat yourself after a tool call, pick up where you left off.
NEVER print out a codeblock with file changes unless the user asked for it. Use the appropriate edit tool instead.
NEVER print out a codeblock with a terminal command to run unless the user asked for it. Use the run_in_terminal tool instead.
You don't need to read a file if it's already provided in context.
</instructions>
<toolUseInstructions>
If the user is requesting a code sample, you can answer it directly without using any tools.
When using a tool, follow the JSON schema very carefully and make sure to include ALL required properties.
No need to ask permission before using a tool.
NEVER say the name of a tool to a user. For example, instead of saying that you'll use the run_in_terminal tool, say "I'll run the command in a terminal".
If you think running multiple tools can answer the user's question, prefer calling them in parallel whenever possible, but do not call semantic_search in parallel.
When using the read_file tool, prefer reading a large section over calling the read_file tool many times in sequence. You can also think of all the pieces you may be interested in and read them in parallel. Read large enough context to ensure you get what you need.
If semantic_search returns the full contents of the text files in the workspace, you have all the workspace context.
You can use the grep_search to get an overview of a file by searching for a string within that one file, instead of using read_file many times.
If you don't know exactly the string or filename pattern you're looking for, use semantic_search to do a semantic search across the workspace.
Don't call the run_in_terminal tool multiple times in parallel. Instead, run one command and wait for the output before running the next command.
When invoking a tool that takes a file path, always use the absolute file path. If the file has a scheme like untitled: or vscode-userdata:, then use a URI with the scheme.
NEVER try to edit a file by running terminal commands unless the user specifically asks for it.
Tools can be disabled by the user. You may see tools used previously in the conversation that are not currently available. Be careful to only use the tools that are currently available to you.
</toolUseInstructions>
<notebookInstructions>
To edit notebook files in the workspace, you can use the edit_notebook_file tool.
Use the run_notebook_cell tool instead of executing Jupyter related commands in the Terminal, such as `jupyter notebook`, `jupyter lab`, `install jupyter` or the like.
Use the copilot_getNotebookSummary tool to get the summary of the notebook (this includes the list or all cells along with the Cell Id, Cell type and Cell Language, execution details and mime types of the outputs, if any).
Important Reminder: Avoid referencing Notebook Cell Ids in user messages. Use cell number instead.
Important Reminder: Markdown cells cannot be executed
</notebookInstructions>
<outputFormatting>
Use proper Markdown formatting. When referring to symbols (classes, methods, variables) in user's workspace wrap in backticks. For file paths and line number rules, see fileLinkification section below
<fileLinkification>
When mentioning files or line numbers, always convert them to markdown links using workspace-relative paths and 1-based line numbers.
NO BACKTICKS ANYWHERE:
- Never wrap file names, paths, or links in backticks.
- Never use inline-code formatting for any file reference.

REQUIRED FORMATS:
- File: [path/file.ts](path/file.ts)
- Line: [file.ts](file.ts#L10)
- Range: [file.ts](file.ts#L10-L12)

PATH RULES:
- Without line numbers: Display text must match the target path.
- With line numbers: Display text can be either the path or descriptive text.
- Use '/' only; strip drive letters and external folders.
- Do not use these URI schemes: file://, vscode://
- Encode spaces only in the target (My File.md → My%20File.md).
- Non-contiguous lines require separate links. NEVER use comma-separated line references like #L10-L12, L20.
- Valid formats: [file.ts](file.ts#L10) or [file.ts#L10] only. Invalid: ([file.ts#L10]) or [file.ts](file.ts)#L10

USAGE EXAMPLES:
- With path as display: The handler is in [src/handler.ts](src/handler.ts#L10).
- With descriptive text: The [widget initialization](src/widget.ts#L321) runs on startup.
- Bullet list: [Init widget](src/widget.ts#L321)
- File only: See [src/config.ts](src/config.ts) for settings.

FORBIDDEN (NEVER OUTPUT):
- Inline code: `file.ts`, `src/file.ts`, `L86`.
- Plain text file names: file.ts, chatService.ts.
- References without links when mentioning specific file locations.
- Specific line citations without links ("Line 86", "at line 86", "on line 25").
- Combining multiple line references in one link: [file.ts#L10-L12, L20](file.ts#L10-L12, L20)


</fileLinkification>
Use KaTeX for math equations in your answers.
Wrap inline math equations in $.
Wrap more complex blocks of math equations in $$.

</outputFormatting>
Respond in the following locale: ko
User
<environment_info>
The user's current OS is: Windows
</environment_info>
<workspace_info>
The following tasks can be executed using the run_task tool if they are not already running:
<workspaceFolder path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI">
<task id="shell: run make install">
{
	"label": "run make install",
	"type": "shell",
	"command": "/usr/bin/make -j 8 install",
	"options": {
		"cwd": "/OpenROAD-flow-scripts/tools/OpenROAD/build"
	}
}
</task>

</workspaceFolder>
I am working in a workspace with the following folders:
- c:\Workbench\20_Projects\hvppycoding_ComfyUI 
I am working in a workspace that has the following structure:
```
alembic.ini
CODEOWNERS
comfyui_version.py
CONTRIBUTING.md
cuda_malloc.py
execution.py
extra_model_paths.yaml.example
folder_paths.py
hook_breaker_ac10a0.py
latent_preview.py
LICENSE
main.py
new_updater.py
node_helpers.py
nodes.py
protocol.py
pyproject.toml
pytest.ini
QUANTIZATION.md
README.md
requirements.txt
server.py
__pycache__/
alembic_db/
	env.py
	README.md
	script.py.mako
api_server/
	__init__.py
	routes/
	services/
	utils/
app/
	__init__.py
	app_settings.py
	custom_node_manager.py
	frontend_management.py
	logger.py
	model_manager.py
	subgraph_manager.py
	user_manager.py
	__pycache__/
	database/
comfy/
	checkpoint_pickle.py
	cli_args.py
	clip_config_bigg.json
	clip_model.py
	clip_vision_config_g.json
	clip_vision_config_h.json
	clip_vision_config_vitl_336_llava.json
	clip_vision_config_vitl_336.json
	clip_vision_config_vitl.json
	clip_vision_siglip_384.json
	clip_vision_siglip_512.json
	clip_vision.py
	conds.py
	context_windows.py
	controlnet.py
	diffusers_convert.py
	diffusers_load.py
	float.py
	gligen.py
	hooks.py
	latent_formats.py
	lora_convert.py
	lora.py
	model_base.py
	model_detection.py
	model_management.py
	model_patcher.py
	model_sampling.py
	nested_tensor.py
	ops.py
	options.py
	patcher_extension.py
	pixel_space_convert.py
	quant_ops.py
	rmsnorm.py
	sample.py
	sampler_helpers.py
	samplers.py
	sd.py
	sd1_clip_config.json
	sd1_clip.py
	sdxl_clip.py
	supported_models_base.py
	supported_models.py
	utils.py
	__pycache__/
	audio_encoders/
	cldm/
	comfy_types/
	extra_samplers/
	image_encoders/
	k_diffusion/
	ldm/
	sd1_tokenizer/
	t2i_adapter/
	taesd/
	text_encoders/
	weight_adapter/
comfy_api/
	feature_flags.py
	generate_api_stubs.py
	util.py
	version_list.py
	__pycache__/
	input/
	input_impl/
	internal/
	latest/
	torch_helpers/
	util/
	v0_0_1/
	v0_0_2/
comfy_api_nodes/
	__init__.py
	canary.py
	mapper_utils.py
	...
comfy_config/
	...
comfy_execution/
comfy_extras/
custom_nodes/
input/
middleware/
models/
output/
script_examples/
tests/
tests-unit/
utils/
```
This is the state of the context at this point in the conversation. The view of the workspace structure may be truncated. You can use tools to collect more context if needed.
</workspace_info>


[copilot_cache_control: { type: 'ephemeral' }]
User
<conversation-summary>
<analysis>
[Chronological Review: Initial Request (Optimize startup/Disable nodes) → Implementation (Commented out imports in nodes.py) → Profiling (Added timing logs) → Feature Request (Add `--fast-load` arg to toggle optimization) → Implementation (Added arg, used Mock objects in nodes.py) → Debugging (Fixed Mock inheritance error) → Rejection (User felt Mocking was over-engineering) → Revert (Removed Mock logic from nodes.py)]
[Intent Mapping: User initially wanted max speed. Then wanted to measure bottlenecks. Then wanted a toggle switch. Finally, user decided the complex Mocking solution for the toggle was unnecessary.]
[Technical Inventory: ComfyUI, Python `importlib`, `unittest.mock` (attempted), `argparse`, PyTorch hardware checks (IPEX, XPU, etc.), `time.time()` profiling]
[Code Archaeology: 
- `comfy/cli_args.py`: Added `--fast-load` argument.
- `comfy/model_management.py`: Modified to skip hardware checks if `--fast-load` is active.
- `nodes.py`: Was modified to use Mock objects, but just reverted to standard imports with timing logs.]
[Progress Assessment: Profiling logs are in place. The `--fast-load` feature is currently in a fractured state (exists in args and model_management, but removed from nodes.py).]
[Context Validation: The system is currently in a state where `nodes.py` loads normally (with logs), but `model_management.py` still respects the `--fast-load` flag. The user wants to simplify.]
[Recent Commands Analysis: `replace_string_in_file` on `nodes.py` to remove the `if not args.fast_load:` block and the Mock class definition, restoring standard `import torch` etc., with timing logs.]
</analysis>

<summary>
1. Conversation Overview:
- Primary Objectives: "ComfyUI의 기본 노드들을 로드하지 않도록 바꾸고 싶어... 최대한 로딩 속도를 빠르게 하고 싶어" (Disable default nodes and maximize startup speed). Later evolved to "argument로 옵션을 추가해서... 스킵할 수 있는거 스킵하고" (Add an argument to toggle optimizations).
- Session Context: The user wanted to strip down ComfyUI for speed. We aggressively removed imports, then added profiling to measure gains. We attempted to implement a `--fast-load` flag using Mock objects to bypass imports dynamically.
- User Intent Evolution: The user encountered complexity with Mock objects (inheritance errors) and decided "음 굳이 이정도까지 해야하나 싶은데" (I doubt we need to go this far), prompting a revert of the complex Mocking logic.

2. Technical Foundation:
- ComfyUI: Custom node loading and initialization logic.
- PyTorch: Heavy dependency being profiled/skipped.
- Mocking: Attempted to use dummy classes to bypass `import torch` dependencies, but it caused `TypeError: __mro_entries__` with `torch.nn` inheritance.
- Profiling: `time.time()` logs added around heavy imports and hardware checks.

3. Codebase Status:
- `c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py`:
- Purpose: Main node registration file.
- Current State: **Reverted.** The complex Mocking logic and `--fast-load` check were removed. It now performs standard imports (`torch`, `safetensors`, `comfy.*`) but includes `logging.info` to measure import times.
- `c:\Workbench\20_Projects\hvppycoding_ComfyUI\comfy\model_management.py`:
- Purpose: Hardware detection and memory management.
- Current State: **Modified.** Contains logic to check `if not args.fast_load:` before running heavy hardware checks (IPEX, XPU, etc.).
- `c:\Workbench\20_Projects\hvppycoding_ComfyUI\comfy\cli_args.py`:
- Purpose: Command line argument parsing.
- Current State: **Modified.** Contains the `--fast-load` argument definition.

4. Problem Resolution:
- Issues Encountered: Implementing `--fast-load` in `nodes.py` required Mocking `torch` to avoid `NameError`. This caused issues when ComfyUI code tried to inherit from `torch.nn.Module` (Mock objects need `__mro_entries__`).
- Solutions Implemented: We fixed the Mock class, but the user decided the complexity was unwarranted.
- Current State: `nodes.py` is back to normal loading (with logs). The `--fast-load` flag currently only affects `model_management.py`.

5. Progress Tracking:
- Completed Tasks: Added profiling logs to `nodes.py` and `model_management.py`. Added `--fast-load` arg.
- Partially Complete Work: The `--fast-load` feature is inconsistent; it is active in `model_management.py` but removed from `nodes.py`.
- Validated Outcomes: Startup profiling is working and visible in logs.

6. Active Work State:
- Current Focus: Simplifying the codebase after an over-engineered attempt at dynamic import skipping.
- Recent Context: The user rejected the Mocking approach in `nodes.py`. I executed a revert on `nodes.py` to restore standard imports.
- Working Code: `nodes.py` now imports `torch` and other modules directly, logging the time taken.
- Immediate Context: The system is in a mixed state. `nodes.py` ignores `--fast-load`, while `model_management.py` and `cli_args.py` still support it.

7. Recent Operations:
- Last Agent Commands: `replace_string_in_file` on `c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py`.
- Tool Results Summary: Successfully replaced the Mocking logic block with standard imports wrapped in timing logs.
- Pre-Summary State: The agent had just finished reverting `nodes.py` to a cleaner state.
- Operation Context: To align with the user's request "I doubt we need to go this far," removing the complex workaround.

8. Continuation Plan:
- [Pending Task 1]: Clean up `comfy/model_management.py` if the user wants to fully abandon `--fast-load` or keep it only for hardware checks.
- [Pending Task 2]: Decide whether to keep or remove the `--fast-load` argument in `cli_args.py`.
- [Priority Information]: The codebase is currently inconsistent regarding the `--fast-load` flag.
- [Next Action]: Ask the user if they want to keep `--fast-load` just for `model_management.py` (hardware checks) or remove it entirely.

</summary>
</conversation-summary>

Assistant

🛠️ read_file (call_MHxPU1RvVjEwSVZyNkI3aTFrazk) {
  "endLine": 2150,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py",
  "startLine": 2100
}
Tool
🛠️ call_MHxPU1RvVjEwSVZyNkI3aTFrazk
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py`. Lines 2100 to 2150 (2448 lines total): 
```python

if args.fast_load:
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

EXTENSION_WEB_DIRS = {}

# Dictionary of successfully loaded module names and associated directories.
LOADED_MODULE_DIRS = {}


def get_module_name(module_path: str) -> str:
    """
    Returns the module name based on the given module path.
    Examples:
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.disabled") -> "custom_nodes
    Args:
        module_path (str): The path of the module.
    Returns:
        str: The module name.
    """
    base_path = os.path.basename(module_path)
    if os.path.isfile(module_path):
        base_path = os.path.splitext(base_path)[0]
    return base_path


async def load_custom_node(module_path: str, ignore=set(), module_parent="custom_nodes") -> bool:
    module_name = get_module_name(module_path)
    if os.path.isfile(module_path):
        sp = os.path.splitext(module_path)
        module_name = sp[0]
        sys_module_name = module_name
    elif os.path.isdir(module_path):
        sys_module_name = module_path.replace(".", "_x_")

    try:
        logging.debug("Trying to load custom node {}".format(module_path))
        if os.path.isfile(module_path):
            module_spec = importlib.util.spec_from_file_location(sys_module_name, module_path)
            module_dir = os.path.split(module_path)[0]
        else:
            module_spec = importlib.util.spec_from_file_location(sys_module_name, os.path.join(module_path, "__init__.py"))
            module_dir = module_path

```
Assistant

🛠️ read_file (call_MHxrcE1FMHo0VktuRmtoZGtjc20) {
  "endLine": 100,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\model_management.py",
  "startLine": 1
}
Tool
🛠️ call_MHxrcE1FMHo0VktuRmtoZGtjc20
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\comfy\model_management.py`. Lines 1 to 100 (1537 lines total): 
```python
"""
    This file is part of ComfyUI.
    Copyright (C) 2024 Comfy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import psutil
import logging
from enum import Enum
from comfy.cli_args import args, PerformanceFeature
import torch
import sys
import importlib
import platform
import weakref
import gc
import time

class VRAMState(Enum):
    DISABLED = 0    #No vram present: no need to move models to vram
    NO_VRAM = 1     #Very low vram: enable all the options to save vram
    LOW_VRAM = 2
    NORMAL_VRAM = 3
    HIGH_VRAM = 4
    SHARED = 5      #No dedicated vram: memory shared between CPU and GPU but models still need to be moved between both.

class CPUState(Enum):
    GPU = 0
    CPU = 1
    MPS = 2

# Determine VRAM State
vram_state = VRAMState.NORMAL_VRAM
set_vram_to = VRAMState.NORMAL_VRAM
cpu_state = CPUState.GPU

total_vram = 0

def get_supported_float8_types():
    float8_types = []
    try:
        float8_types.append(torch.float8_e4m3fn)
    except:
        pass
    try:
        float8_types.append(torch.float8_e4m3fnuz)
    except:
        pass
    try:
        float8_types.append(torch.float8_e5m2)
    except:
        pass
    try:
        float8_types.append(torch.float8_e5m2fnuz)
    except:
        pass
    try:
        float8_types.append(torch.float8_e8m0fnu)
    except:
        pass
    return float8_types

FLOAT8_TYPES = get_supported_float8_types()

xpu_available = False
torch_version = ""
try:
    torch_version = torch.version.__version__
    temp = torch_version.split(".")
    torch_version_numeric = (int(temp[0]), int(temp[1]))
except:
    pass

lowvram_available = True
if args.deterministic:
    logging.info("Using deterministic algorithms for pytorch")
    torch.use_deterministic_algorithms(True, warn_only=True)

directml_enabled = False
if args.directml is not None:
    logging.warning("WARNING: torch-directml barely works, is very slow, has not been updated in over 1 year and might be removed soon, please don't use it, there are better options.")
    import torch_directml
    directml_enabled = True
    device_index = args.directml
    if device_index < 0:
        directml_device = torch_directml.device()
    else:
        directml_device = torch_directml.device(device_index)
```
Assistant

🛠️ grep_search (call_MHxVVkw2OVhvVkdxS09yZ3VvQjA) {
  "isRegexp": false,
  "query": "args.fast_load"
}
Tool
🛠️ call_MHxVVkw2OVhvVkdxS09yZ3VvQjA
4 matches
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py" line=2101>
if args.fast_load:
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\model_management.py" line=105>
if not args.fast_load:
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\model_management.py" line=160>
if args.cpu or args.fast_load:
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\model_management.py" line=278>
if args.disable_xformers or args.fast_load:
</match>

Assistant

🛠️ read_file (call_MHw2Nm5CYXlkVFRvU2Nxd3Z2OXM) {
  "endLine": 2110,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py",
  "startLine": 2090
}
Tool
🛠️ call_MHw2Nm5CYXlkVFRvU2Nxd3Z2OXM
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py`. Lines 2090 to 2110 (2448 lines total): 
```python
    "ImageBlend": "Image Blend",
    "ImageBlur": "Image Blur",
    "ImageQuantize": "Image Quantize",
    "ImageSharpen": "Image Sharpen",
    "ImageScaleToTotalPixels": "Scale Image to Total Pixels",
    "GetImageSize": "Get Image Size",
    # _for_testing
    "VAEDecodeTiled": "VAE Decode (Tiled)",
    "VAEEncodeTiled": "VAE Encode (Tiled)",
}

if args.fast_load:
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

EXTENSION_WEB_DIRS = {}

# Dictionary of successfully loaded module names and associated directories.
LOADED_MODULE_DIRS = {}


```
Assistant

🛠️ read_file (call_MHwxV2RKS0R6cUhsQldMZXQ3enQ) {
  "endLine": 30,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py",
  "startLine": 1
}
Tool
🛠️ call_MHwxV2RKS0R6cUhsQldMZXQ3enQ
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py`. Lines 1 to 30 (2448 lines total): 
```python
from __future__ import annotations

import os
import sys
import logging
import time
from comfy.cli_args import args

t_import = time.time()
import torch
logging.info(f"import torch time: {time.time() - t_import:.4f}s")


import json
import hashlib
import inspect
import traceback
import math
import random

from PIL import Image, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo

import numpy as np

t_import = time.time()
import safetensors.torch
logging.info(f"import safetensors.torch time: {time.time() - t_import:.4f}s")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))
```
Assistant

🛠️ read_file (call_MHxzYTlOY0lhS2NDd1NCdW5LSjE) {
  "endLine": 130,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\model_management.py",
  "startLine": 100
}
Tool
🛠️ call_MHxzYTlOY0lhS2NDd1NCdW5LSjE
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\comfy\model_management.py`. Lines 100 to 130 (1537 lines total): 
```python
        directml_device = torch_directml.device(device_index)
    logging.info("Using directml with device: {}".format(torch_directml.device_name(device_index)))
    # torch_directml.disable_tiled_resources(True)
    lowvram_available = False #TODO: need to find a way to get free memory in directml before this can be enabled by default.

if not args.fast_load:
    t_start = time.time()
    try:
        import intel_extension_for_pytorch as ipex  # noqa: F401
    except:
        pass
    logging.info(f"IPEX check time: {time.time() - t_start:.4f}s")

    t_start = time.time()
    try:
        _ = torch.xpu.device_count()
        xpu_available = torch.xpu.is_available()
    except:
        xpu_available = False
    logging.info(f"XPU check time: {time.time() - t_start:.4f}s")

    t_start = time.time()
    try:
        if torch.backends.mps.is_available():
            cpu_state = CPUState.MPS
            import torch.mps
    except:
        pass
    logging.info(f"MPS check time: {time.time() - t_start:.4f}s")

    t_start = time.time()
```
Assistant

🛠️ read_file (call_MHxVNDVkS3dEdzZ2dnlLZUdTVzI) {
  "endLine": 50,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\cli_args.py",
  "startLine": 1
}
Tool
🛠️ call_MHxVNDVkS3dEdzZ2dnlLZUdTVzI
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\comfy\cli_args.py`. Lines 1 to 50 (246 lines total): 
```python
import argparse
import enum
import os
import comfy.options


class EnumAction(argparse.Action):
    """
    Argparse action for handling Enums
    """
    def __init__(self, **kwargs):
        # Pop off the type value
        enum_type = kwargs.pop("type", None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError("type must be assigned an Enum when using EnumAction")
        if not issubclass(enum_type, enum.Enum):
            raise TypeError("type must be an Enum when using EnumAction")

        # Generate choices from the Enum
        choices = tuple(e.value for e in enum_type)
        kwargs.setdefault("choices", choices)
        kwargs.setdefault("metavar", f"[{','.join(list(choices))}]")

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum_type

    def __call__(self, parser, namespace, values, option_string=None):
        # Convert value back into an Enum
        value = self._enum(values)
        setattr(namespace, self.dest, value)


parser = argparse.ArgumentParser()

parser.add_argument("--listen", type=str, default="127.0.0.1", metavar="IP", nargs="?", const="0.0.0.0,::", help="Specify the IP address to listen on (default: 127.0.0.1). You can give a list of ip addresses by separating them with a comma like: 127.2.2.2,127.3.3.3 If --listen is provided without an argument, it defaults to 0.0.0.0,:: (listens on all ipv4 and ipv6)")
parser.add_argument("--port", type=int, default=8188, help="Set the listen port.")
parser.add_argument("--tls-keyfile", type=str, help="Path to TLS (SSL) key file. Enables TLS, makes app accessible at https://... requires --tls-certfile to function")
parser.add_argument("--tls-certfile", type=str, help="Path to TLS (SSL) certificate file. Enables TLS, makes app accessible at https://... requires --tls-keyfile to function")
parser.add_argument("--enable-cors-header", type=str, default=None, metavar="ORIGIN", nargs="?", const="*", help="Enable CORS (Cross-Origin Resource Sharing) with optional origin or allow all with default '*'.")
parser.add_argument("--max-upload-size", type=float, default=100, help="Set the maximum upload size in MB.")

parser.add_argument("--base-directory", type=str, default=None, help="Set the ComfyUI base directory for models, custom_nodes, input, output, temp, and user directories.")
parser.add_argument("--extra-model-paths-config", type=str, default=None, metavar="PATH", nargs='+', action='append', help="Load one or more extra_model_paths.yaml files.")
parser.add_argument("--output-directory", type=str, default=None, help="Set the ComfyUI output directory. Overrides --base-directory.")
parser.add_argument("--temp-directory", type=str, default=None, help="Set the ComfyUI temp directory (default is in the ComfyUI directory). Overrides --base-directory.")
parser.add_argument("--input-directory", type=str, default=None, help="Set the ComfyUI input directory. Overrides --base-directory.")
parser.add_argument("--auto-launch", action="store_true", help="Automatically launch ComfyUI in the default browser.")
```
Assistant

🛠️ grep_search (call_MHxWMGZSeU1xREttRUxpNzRGQWs) {
  "isRegexp": false,
  "query": "fast-load"
}
Tool
🛠️ call_MHxWMGZSeU1xREttRUxpNzRGQWs
1 match
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\cli_args.py" line=220>
parser.add_argument("--fast-load", action="store_true", help="Skip heavy imports and hardware checks for faster startup (CPU only, no nodes).")
</match>

Assistant
복잡한 Mocking 관련 코드를 모두 제거하고 `nodes.py`를 원래의 구조로 되돌렸습니다. (로딩 속도 측정을 위한 로그 코드는 남겨두었습니다.)

현재 상태에서 `--fast-load` 옵션은 아주 단순한 방식으로 동작하도록 남아있습니다:

1.  **하드웨어 체크 스킵**: `comfy/model_management.py`에서 IPEX, XPU 등 불필요한 하드웨어 감지 로직을 건너뜁니다.
2.  **기본 노드 비활성화**: `nodes.py`에서 기본 노드 목록(`NODE_CLASS_MAPPINGS`)을 빈 값으로 초기화하여 기본 노드들을 로드하지 않습니다.

**torch 임포트**는 그대로 수행되므로 "극적인" 속도 향상은 없겠지만, 복잡한 코드 수정 없이 **"기본 노드 제외 + 약간의 부팅 속도 향상"** 효과는 얻을 수 있습니다.

이대로 **`--fast-load` 옵션을 유지**할까요, 아니면 이 옵션과 관련 코드도 **모두 제거**하고 순정 상태(로그만 포함)로 돌아갈까요?
User
<context>
The current date is 2025년 12월 15일.
Terminals:
Terminal: bash

</context>
<editorContext>
The user's current file is c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py. 
</editorContext>
<reminderInstructions>
When using the replace_string_in_file tool, include 3-5 lines of unchanged code before and after the string you want to replace, to make it unambiguous which part of the file should be edited.

</reminderInstructions>
<userRequest>
옵션 유지해. 그런데 너무 과도하게 대체할 필요는 없고, CPU 옵션일 때 GPU 체크 하는 부분 제거 + 만드는데 오래 걸리는 노드들 안 임포트하게만 해도 될 거 같아.
</userRequest>

Assistant

🛠️ read_file (call_MHxKd1VsRWNiZGRJMHYxSkpwMnU) {
  "endLine": 200,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\main.py",
  "startLine": 1
}
Tool
🛠️ call_MHxKd1VsRWNiZGRJMHYxSkpwMnU
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\main.py`. Lines 1 to 200 (390 lines total): 
```python
import comfy.options
comfy.options.enable_args_parsing()

import os
import importlib.util
import folder_paths
import time
from comfy.cli_args import args
from app.logger import setup_logger
import itertools
import utils.extra_config
import logging
import sys
from comfy_execution.progress import get_progress_state
from comfy_execution.utils import get_executing_context
from comfy_api import feature_flags

if __name__ == "__main__":
    #NOTE: These do not do anything on core ComfyUI, they are for custom nodes.
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['DO_NOT_TRACK'] = '1'

setup_logger(log_level=args.verbose, use_stdout=args.log_stdout)

def apply_custom_paths():
    # extra model paths
    extra_model_paths_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "extra_model_paths.yaml")
    if os.path.isfile(extra_model_paths_config_path):
        utils.extra_config.load_extra_path_config(extra_model_paths_config_path)

    if args.extra_model_paths_config:
        for config_path in itertools.chain(*args.extra_model_paths_config):
            utils.extra_config.load_extra_path_config(config_path)

    # --output-directory, --input-directory, --user-directory
    if args.output_directory:
        output_dir = os.path.abspath(args.output_directory)
        logging.info(f"Setting output directory to: {output_dir}")
        folder_paths.set_output_directory(output_dir)

    # These are the default folders that checkpoints, clip and vae models will be saved to when using CheckpointSave, etc.. nodes
    folder_paths.add_model_folder_path("checkpoints", os.path.join(folder_paths.get_output_directory(), "checkpoints"))
    folder_paths.add_model_folder_path("clip", os.path.join(folder_paths.get_output_directory(), "clip"))
    folder_paths.add_model_folder_path("vae", os.path.join(folder_paths.get_output_directory(), "vae"))
    folder_paths.add_model_folder_path("diffusion_models",
                                       os.path.join(folder_paths.get_output_directory(), "diffusion_models"))
    folder_paths.add_model_folder_path("loras", os.path.join(folder_paths.get_output_directory(), "loras"))

    if args.input_directory:
        input_dir = os.path.abspath(args.input_directory)
        logging.info(f"Setting input directory to: {input_dir}")
        folder_paths.set_input_directory(input_dir)

    if args.user_directory:
        user_dir = os.path.abspath(args.user_directory)
        logging.info(f"Setting user directory to: {user_dir}")
        folder_paths.set_user_directory(user_dir)


def execute_prestartup_script():
    if args.disable_all_custom_nodes and len(args.whitelist_custom_nodes) == 0:
        return

    def execute_script(script_path):
        module_name = os.path.splitext(script_path)[0]
        try:
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except Exception as e:
            logging.error(f"Failed to execute startup-script: {script_path} / {e}")
        return False

    node_paths = folder_paths.get_folder_paths("custom_nodes")
    for custom_node_path in node_paths:
        possible_modules = os.listdir(custom_node_path)
        node_prestartup_times = []

        for possible_module in possible_modules:
            module_path = os.path.join(custom_node_path, possible_module)
            if os.path.isfile(module_path) or module_path.endswith(".disabled") or module_path == "__pycache__":
                continue

            script_path = os.path.join(module_path, "prestartup_script.py")
            if os.path.exists(script_path):
                if args.disable_all_custom_nodes and possible_module not in args.whitelist_custom_nodes:
                    logging.info(f"Prestartup Skipping {possible_module} due to disable_all_custom_nodes and whitelist_custom_nodes")
                    continue
                time_before = time.perf_counter()
                success = execute_script(script_path)
                node_prestartup_times.append((time.perf_counter() - time_before, module_path, success))
    if len(node_prestartup_times) > 0:
        logging.info("\nPrestartup times for custom nodes:")
        for n in sorted(node_prestartup_times):
            if n[2]:
                import_message = ""
            else:
                import_message = " (PRESTARTUP FAILED)"
            logging.info("{:6.1f} seconds{}: {}".format(n[0], import_message, n[1]))
        logging.info("")

apply_custom_paths()
execute_prestartup_script()


# Main code
import asyncio
import shutil
import threading
import gc


if os.name == "nt":
    os.environ['MIMALLOC_PURGE_DELAY'] = '0'

if __name__ == "__main__":
    os.environ['TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL'] = '1'
    if args.default_device is not None:
        default_dev = args.default_device
        devices = list(range(32))
        devices.remove(default_dev)
        devices.insert(0, default_dev)
        devices = ','.join(map(str, devices))
        os.environ['CUDA_VISIBLE_DEVICES'] = str(devices)
        os.environ['HIP_VISIBLE_DEVICES'] = str(devices)

    if args.cuda_device is not None:
        os.environ['CUDA_VISIBLE_DEVICES'] = str(args.cuda_device)
        os.environ['HIP_VISIBLE_DEVICES'] = str(args.cuda_device)
        os.environ["ASCEND_RT_VISIBLE_DEVICES"] = str(args.cuda_device)
        logging.info("Set cuda device to: {}".format(args.cuda_device))

    if args.oneapi_device_selector is not None:
        os.environ['ONEAPI_DEVICE_SELECTOR'] = args.oneapi_device_selector
        logging.info("Set oneapi device selector to: {}".format(args.oneapi_device_selector))

    if args.deterministic:
        if 'CUBLAS_WORKSPACE_CONFIG' not in os.environ:
            os.environ['CUBLAS_WORKSPACE_CONFIG'] = ":4096:8"

    import cuda_malloc

if 'torch' in sys.modules:
    logging.warning("WARNING: Potential Error in code: Torch already imported, torch should never be imported before this point.")

import comfy.utils

t_exec = time.time()
import execution
logging.info(f"Import execution time: {time.time() - t_exec:.2f} seconds")
import server
from protocol import BinaryEventTypes
t0 = time.time()
import nodes
logging.info(f"Import nodes time: {time.time() - t0:.2f} seconds")
import comfy.model_management
import comfyui_version
import app.logger
import hook_breaker_ac10a0

def cuda_malloc_warning():
    device = comfy.model_management.get_torch_device()
    device_name = comfy.model_management.get_torch_device_name(device)
    cuda_malloc_warning = False
    if "cudaMallocAsync" in device_name:
        for b in cuda_malloc.blacklist:
            if b in device_name:
                cuda_malloc_warning = True
        if cuda_malloc_warning:
            logging.warning("\nWARNING: this card most likely does not support cuda-malloc, if you get \"CUDA error\" please run ComfyUI with: --disable-cuda-malloc\n")


def prompt_worker(q, server_instance):
    current_time: float = 0.0
    cache_type = execution.CacheType.CLASSIC
    if args.cache_lru > 0:
        cache_type = execution.CacheType.LRU
    elif args.cache_ram > 0:
        cache_type = execution.CacheType.RAM_PRESSURE
    elif args.cache_none:
        cache_type = execution.CacheType.NONE

    e = execution.PromptExecutor(server_instance, cache_type=cache_type, cache_args={ "lru" : args.cache_lru, "ram" : args.cache_ram } )
    last_gc_collect = 0
    need_gc = False
    gc_collect_interval = 10.0

    while True:
        timeout = 1000.0
        if need_gc:
            timeout = max(gc_collect_interval - (current_time - last_gc_collect), 0.0)

        queue_item = q.get(timeout=timeout)
        if queue_item is not None:
            item, item_id = queue_item
            execution_start_time = time.perf_counter()
            prompt_id = item[1]
            server_instance.last_prompt_id = prompt_id

```
Assistant

🛠️ read_file (call_MHxCTmg4MHYxS09BSk9Sd1Q2VVc) {
  "endLine": 300,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\main.py",
  "startLine": 200
}
Tool
🛠️ call_MHxCTmg4MHYxS09BSk9Sd1Q2VVc
File: `c:\Workbench\20_Projects\hvppycoding_ComfyUI\main.py`. Lines 200 to 300 (390 lines total): 
```python

            sensitive = item[5]
            extra_data = item[3].copy()
            for k in sensitive:
                extra_data[k] = sensitive[k]

            e.execute(item[2], prompt_id, extra_data, item[4])
            need_gc = True

            remove_sensitive = lambda prompt: prompt[:5] + prompt[6:]
            q.task_done(item_id,
                        e.history_result,
                        status=execution.PromptQueue.ExecutionStatus(
                            status_str='success' if e.success else 'error',
                            completed=e.success,
                            messages=e.status_messages), process_item=remove_sensitive)
            if server_instance.client_id is not None:
                server_instance.send_sync("executing", {"node": None, "prompt_id": prompt_id}, server_instance.client_id)

            current_time = time.perf_counter()
            execution_time = current_time - execution_start_time

            # Log Time in a more readable way after 10 minutes
            if execution_time > 600:
                execution_time = time.strftime("%H:%M:%S", time.gmtime(execution_time))
                logging.info(f"Prompt executed in {execution_time}")
            else:
                logging.info("Prompt executed in {:.2f} seconds".format(execution_time))

        flags = q.get_flags()
        free_memory = flags.get("free_memory", False)

        if flags.get("unload_models", free_memory):
            comfy.model_management.unload_all_models()
            need_gc = True
            last_gc_collect = 0

        if free_memory:
            e.reset()
            need_gc = True
            last_gc_collect = 0

        if need_gc:
            current_time = time.perf_counter()
            if (current_time - last_gc_collect) > gc_collect_interval:
                gc.collect()
                comfy.model_management.soft_empty_cache()
                last_gc_collect = current_time
                need_gc = False
                hook_breaker_ac10a0.restore_functions()


async def run(server_instance, address='', port=8188, verbose=True, call_on_start=None):
    addresses = []
    for addr in address.split(","):
        addresses.append((addr, port))
    await asyncio.gather(
        server_instance.start_multi_address(addresses, call_on_start, verbose), server_instance.publish_loop()
    )

def hijack_progress(server_instance):
    def hook(value, total, preview_image, prompt_id=None, node_id=None):
        executing_context = get_executing_context()
        if prompt_id is None and executing_context is not None:
            prompt_id = executing_context.prompt_id
        if node_id is None and executing_context is not None:
            node_id = executing_context.node_id
        comfy.model_management.throw_exception_if_processing_interrupted()
        if prompt_id is None:
            prompt_id = server_instance.last_prompt_id
        if node_id is None:
            node_id = server_instance.last_node_id
        progress = {"value": value, "max": total, "prompt_id": prompt_id, "node": node_id}
        get_progress_state().update_progress(node_id, value, total, preview_image)

        server_instance.send_sync("progress", progress, server_instance.client_id)
        if preview_image is not None:
            # Only send old method if client doesn't support preview metadata
            if not feature_flags.supports_feature(
                server_instance.sockets_metadata,
                server_instance.client_id,
                "supports_preview_metadata",
            ):
                server_instance.send_sync(
                    BinaryEventTypes.UNENCODED_PREVIEW_IMAGE,
                    preview_image,
                    server_instance.client_id,
                )

    comfy.utils.set_progress_bar_global_hook(hook)


def cleanup_temp():
    temp_dir = folder_paths.get_temp_directory()
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def setup_database():
    try:
        from app.database.db import init_db, dependencies_available
```
Assistant

🛠️ read_file (call_MHxhMEFMUHhmTmhtSDVtN2pnUlA) {
  "endLine": 390,
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\main.py",
  "startLine": 300
}
Tool
🛠️ call_MHxhMEFMUHhmTmhtSDVtN2pnUlA
```python
        from app.database.db import init_db, dependencies_available
        if dependencies_available():
            init_db()
    except Exception as e:
        logging.error(f"Failed to initialize database. Please ensure you have installed the latest requirements. If the error persists, please report this as in future the database will be required: {e}")


def start_comfyui(asyncio_loop=None):
    """
    Starts the ComfyUI server using the provided asyncio event loop or creates a new one.
    Returns the event loop, server instance, and a function to start the server asynchronously.
    """
    if args.temp_directory:
        temp_dir = os.path.join(os.path.abspath(args.temp_directory), "temp")
        logging.info(f"Setting temp directory to: {temp_dir}")
        folder_paths.set_temp_directory(temp_dir)
    cleanup_temp()

    if args.windows_standalone_build:
        try:
            import new_updater
            new_updater.update_windows_updater()
        except:
            pass

    if not asyncio_loop:
        asyncio_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(asyncio_loop)
    prompt_server = server.PromptServer(asyncio_loop)

    hook_breaker_ac10a0.save_functions()
    t_nodes = time.time()
    asyncio_loop.run_until_complete(nodes.init_extra_nodes(
        init_custom_nodes=(not args.disable_all_custom_nodes) or len(args.whitelist_custom_nodes) > 0,
        init_api_nodes=not args.disable_api_nodes
    ))
    logging.info(f"Init extra nodes time: {time.time() - t_nodes:.2f} seconds")
    hook_breaker_ac10a0.restore_functions()

    cuda_malloc_warning()
    setup_database()

    prompt_server.add_routes()
    hijack_progress(prompt_server)

    threading.Thread(target=prompt_worker, daemon=True, args=(prompt_server.prompt_queue, prompt_server,)).start()

    if args.quick_test_for_ci:
        exit(0)

    os.makedirs(folder_paths.get_temp_directory(), exist_ok=True)
    call_on_start = None
    if args.auto_launch:
        def startup_server(scheme, address, port):
            import webbrowser
            if os.name == 'nt' and address == '0.0.0.0':
                address = '127.0.0.1'
            if ':' in address:
                address = "[{}]".format(address)
            webbrowser.open(f"{scheme}://{address}:{port}")
        call_on_start = startup_server

    async def start_all():
        await prompt_server.setup()
        await run(prompt_server, address=args.listen, port=args.port, verbose=not args.dont_print_server, call_on_start=call_on_start)

    # Returning these so that other code can integrate with the ComfyUI loop and server
    return asyncio_loop, prompt_server, start_all


if __name__ == "__main__":
    import time
    start_time = time.time()
    # Running directly, just start ComfyUI.
    logging.info("Python version: {}".format(sys.version))
    logging.info("ComfyUI version: {}".format(comfyui_version.__version__))

    if sys.version_info.major == 3 and sys.version_info.minor < 10:
        logging.warning("WARNING: You are using a python version older than 3.10, please upgrade to a newer one. 3.12 and above is recommended.")

    event_loop, _, start_all_func = start_comfyui()
    logging.info(f"Startup time: {time.time() - start_time:.2f} seconds")
    try:
        x = start_all_func()
        app.logger.print_startup_warnings()
        event_loop.run_until_complete(x)
    except KeyboardInterrupt:
        logging.info("\nStopped server")

    cleanup_temp()

```
Assistant

🛠️ grep_search (call_MHxmd0Y1SHQ0Z0R6ZkhJNjRqOFk) {
  "isRegexp": false,
  "query": "--cpu"
}
Tool
🛠️ call_MHxmd0Y1SHQ0Z0R6ZkhJNjRqOFk
11 matches
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\cli_args.py" line=77>
parser.add_argument("--cpu-vae", action="store_true", help="Run the VAE on the CPU.")
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\cli_args.py" line=130>
vram_group.add_argument("--cpu", action="store_true", help="To use the CPU for everything (slow).")
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\tests\\execution\\test_progress_isolation.py" line=96>
            '--cpu',
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\tests\\execution\\test_async_nodes.py" line=27>
            '--cpu',
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\tests\\execution\\test_execution.py" line=168>
            '--cpu',
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\README.md" line=90>
- Works even if you don't have a GPU with: ```--cpu``` (slow)
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\.github\\workflows\\stable-release.yml" line=158>
          python_embeded/python.exe -s ComfyUI/main.py --quick-test-for-ci --cpu
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\.github\\workflows\\test-launch.yml" line=30>
        python main.py --cpu 2>&1 | tee console_output.log &
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\.ci\\windows_nvidia_base_files\\run_cpu.bat" line=1>
.\python_embeded\python.exe -s ComfyUI\main.py --cpu --windows-standalone-build
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\.github\\workflows\\windows_release_nightly_pytorch.yml" line=83>
            python_embeded/python.exe -s ComfyUI/main.py --quick-test-for-ci --cpu
</match>
<match path="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\.github\\workflows\\windows_release_package.yml" line=93>
            python_embeded/python.exe -s ComfyUI/main.py --quick-test-for-ci --cpu
</match>

Assistant

🛠️ replace_string_in_file (call_MHxCMmhtRVVGUng5QmoyME1kQlo) {
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\comfy\\model_management.py",
  "newString": "    lowvram_available = False #TODO: need to find a way to get free memory in directml before this can be enabled by default.

if not args.fast_load and not args.cpu:
    t_start = time.time()
    try:
        import intel_extension_for_pytorch as ipex  # noqa: F401",
  "oldString": "    lowvram_available = False #TODO: need to find a way to get free memory in directml before this can be enabled by default.

if not args.fast_load:
    t_start = time.time()
    try:
        import intel_extension_for_pytorch as ipex  # noqa: F401"
}
Tool
🛠️ call_MHxCMmhtRVVGUng5QmoyME1kQlo
The following files were successfully edited:
c:\Workbench\20_Projects\hvppycoding_ComfyUI\comfy\model_management.py

Assistant

🛠️ replace_string_in_file (call_MHxiQU9hSTFra2FtcElySUtlekg) {
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\main.py",
  "newString": "    hook_breaker_ac10a0.save_functions()
    t_nodes = time.time()
    asyncio_loop.run_until_complete(nodes.init_extra_nodes(
        init_custom_nodes=(not args.disable_all_custom_nodes and not args.fast_load) or len(args.whitelist_custom_nodes) > 0,
        init_api_nodes=not args.disable_api_nodes
    ))
    logging.info(f\"Init extra nodes time: {time.time() - t_nodes:.2f} seconds\")
    hook_breaker_ac10a0.restore_functions()",
  "oldString": "    hook_breaker_ac10a0.save_functions()
    t_nodes = time.time()
    asyncio_loop.run_until_complete(nodes.init_extra_nodes(
        init_custom_nodes=(not args.disable_all_custom_nodes) or len(args.whitelist_custom_nodes) > 0,
        init_api_nodes=not args.disable_api_nodes
    ))
    logging.info(f\"Init extra nodes time: {time.time() - t_nodes:.2f} seconds\")
    hook_breaker_ac10a0.restore_functions()"
}
Tool
🛠️ call_MHxiQU9hSTFra2FtcElySUtlekg
The following files were successfully edited:
c:\Workbench\20_Projects\hvppycoding_ComfyUI\main.py

Assistant
요청하신 대로 `--fast-load` 옵션을 유지하되, 과도한 Mocking 없이 실용적인 수준에서 최적화를 적용했습니다.

**적용된 변경 사항:**

1.  **GPU 체크 스킵 (`comfy/model_management.py`)**:
    *   `--fast-load` 옵션이 켜져 있거나, `--cpu` 옵션이 켜져 있는 경우, 부팅 시 시간이 걸리는 IPEX, XPU, MPS, CUDA 등의 하드웨어 감지 로직을 건너뛰도록 수정했습니다.

2.  **커스텀 노드 로딩 스킵 (`main.py`)**:
    *   `--fast-load` 옵션이 켜져 있으면, 부팅 시 시간이 오래 걸리는 주범인 **커스텀 노드들의 로딩을 아예 시도하지 않도록** 변경했습니다. (화이트리스트에 있는 노드는 제외)

3.  **기본 노드 비활성화 (`nodes.py`)**:
    *   기존에 적용해둔 대로, `--fast-load` 시 기본 노드 매핑(`NODE_CLASS_MAPPINGS`)을 비워서 기본 노드들도 로드되지 않게 유지했습니다.

이제 `--fast-load` 옵션을 사용하면 **"하드웨어 체크 스킵 + 커스텀 노드 로딩 스킵 + 기본 노드 비활성화"**가 적용되어, 복잡한 코드 수정 없이도 훨씬 빠른 부팅 속도를 기대할 수 있습니다.
User
<attachments>
<attachment isSummarized="true" filePath="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py">
User's active file for additional context:
class KSamplerAdvanced:
    /* Lines 1543-1574 omitted */

class SaveImage:
    /* Lines 1577-1629 omitted */

class PreviewImage(SaveImage):
    /* Lines 1632-1643 omitted */

class LoadImage:
    /* Lines 1646-1719 omitted */

class LoadImageMask:
    /* Lines 1722-1768 omitted */


class LoadImageOutput(LoadImage):
    /* Lines 1772-1790 omitted */


class ImageScale:
    /* Lines 1794-1821 omitted */

class ImageScaleBy:
    /* Lines 1824-1841 omitted */

class ImageInvert:

    @classmethod
    /* Lines 1846-1847 omitted */

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "invert"

    CATEGORY = "image"

    def invert(self, image):
        

class ImageBatch:

    @classmethod
    /* Lines 1861-1862 omitted */

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "batch"

    CATEGORY = "image"

    def batch(self, image1, image2):
        

class EmptyImage:
    def __init__(self, device="cpu"):
        /* Line 1882 omitted */

    @classmethod
    /* Lines 1885-1890 omitted */
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"

    CATEGORY = "image"

    def generate(self, width, height, batch_size=1, color=0):
        

class ImagePadForOutpaint:

    @classmethod
    /* Lines 1905-1915 omitted */

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "expand_image"

    CATEGORY = "image"

    def expand_image(self, image, left, top, right, bottom, feathering):
        


# NODE_CLASS_MAPPINGS = {
#     "KSampler": KSampler,
#     "CheckpointLoaderSimple": CheckpointLoaderSimple,
#     "CLIPTextEncode": CLIPTextEncode,
#     "CLIPSetLastLayer": CLIPSetLastLayer,
#     "VAEDecode": VAEDecode,
#     "VAEEncode": VAEEncode,
#     "VAEEncodeForInpaint": VAEEncodeForInpaint,
#     "VAELoader": VAELoader,
#     "EmptyLatentImage": EmptyLatentImage,
#     "LatentUpscale": LatentUpscale,
#     "LatentUpscaleBy": LatentUpscaleBy,
#     "LatentFromBatch": LatentFromBatch,
#     "RepeatLatentBatch": RepeatLatentBatch,
#     "SaveImage": SaveImage,
#     "PreviewImage": PreviewImage,
#     "LoadImage": LoadImage,
#     "LoadImageMask": LoadImageMask,
#     "LoadImageOutput": LoadImageOutput,
#     "ImageScale": ImageScale,
#     "ImageScaleBy": ImageScaleBy,
#     "ImageInvert": ImageInvert,
#     "ImageBatch": ImageBatch,
#     "ImagePadForOutpaint": ImagePadForOutpaint,
#     "EmptyImage": EmptyImage,
#     "ConditioningAverage": ConditioningAverage ,
#     "ConditioningCombine": ConditioningCombine,
#     "ConditioningConcat": ConditioningConcat,
#     "ConditioningSetArea": ConditioningSetArea,
#     "ConditioningSetAreaPercentage": ConditioningSetAreaPercentage,
#     "ConditioningSetAreaStrength": ConditioningSetAreaStrength,
#     "ConditioningSetMask": ConditioningSetMask,
#     "KSamplerAdvanced": KSamplerAdvanced,
#     "SetLatentNoiseMask": SetLatentNoiseMask,
#     "LatentComposite": LatentComposite,
#     "LatentBlend": LatentBlend,
#     "LatentRotate": LatentRotate,
#     "LatentFlip": LatentFlip,
#     "LatentCrop": LatentCrop,
#     "LoraLoader": LoraLoader,
#     "CLIPLoader": CLIPLoader,
#     "UNETLoader": UNETLoader,
#     "DualCLIPLoader": DualCLIPLoader,
#     "CLIPVisionEncode": CLIPVisionEncode,
#     "StyleModelApply": StyleModelApply,
#     "unCLIPConditioning": unCLIPConditioning,
#     "ControlNetApply": ControlNetApply,
#     "ControlNetApplyAdvanced": ControlNetApplyAdvanced,
#     "ControlNetLoader": ControlNetLoader,
#     "DiffControlNetLoader": DiffControlNetLoader,
#     "StyleModelLoader": StyleModelLoader,
#     "CLIPVisionLoader": CLIPVisionLoader,
#     "VAEDecodeTiled": VAEDecodeTiled,
#     "VAEEncodeTiled": VAEEncodeTiled,
#     "unCLIPCheckpointLoader": unCLIPCheckpointLoader,
#     "GLIGENLoader": GLIGENLoader,
#     "GLIGENTextBoxApply": GLIGENTextBoxApply,
#     "InpaintModelConditioning": InpaintModelConditioning,

#     "CheckpointLoader": CheckpointLoader,
#     "DiffusersLoader": DiffusersLoader,

#     "LoadLatent": LoadLatent,
#     "SaveLatent": SaveLatent,

#     "ConditioningZeroOut": ConditioningZeroOut,
#     "ConditioningSetTimestepRange": ConditioningSetTimestepRange,
#     "LoraLoaderModelOnly": LoraLoaderModelOnly,
# }
NODE_CLASS_MAPPINGS = {}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Sampling
    "KSampler": "KSampler",
    "KSamplerAdvanced": "KSampler (Advanced)",
    # Loaders
    "CheckpointLoader": "Load Checkpoint With Config (DEPRECATED)",
    "CheckpointLoaderSimple": "Load Checkpoint",
    "VAELoader": "Load VAE",
    "LoraLoader": "Load LoRA",
    "CLIPLoader": "Load CLIP",
    "ControlNetLoader": "Load ControlNet Model",
    "DiffControlNetLoader": "Load ControlNet Model (diff)",
    "StyleModelLoader": "Load Style Model",
    "CLIPVisionLoader": "Load CLIP Vision",
    "UNETLoader": "Load Diffusion Model",
    # Conditioning
    "CLIPVisionEncode": "CLIP Vision Encode",
    "StyleModelApply": "Apply Style Model",
    "CLIPTextEncode": "CLIP Text Encode (Prompt)",
    "CLIPSetLastLayer": "CLIP Set Last Layer",
    "ConditioningCombine": "Conditioning (Combine)",
    "ConditioningAverage ": "Conditioning (Average)",
    "ConditioningConcat": "Conditioning (Concat)",
    "ConditioningSetArea": "Conditioning (Set Area)",
    "ConditioningSetAreaPercentage": "Conditioning (Set Area with Percentage)",
    "ConditioningSetMask": "Conditioning (Set Mask)",
    "ControlNetApply": "Apply ControlNet (OLD)",
    "ControlNetApplyAdvanced": "Apply ControlNet",
    # Latent
    "VAEEncodeForInpaint": "VAE Encode (for Inpainting)",
    "SetLatentNoiseMask": "Set Latent Noise Mask",
    "VAEDecode": "VAE Decode",
    "VAEEncode": "VAE Encode",
    "LatentRotate": "Rotate Latent",
    "LatentFlip": "Flip Latent",
    "LatentCrop": "Crop Latent",
    "EmptyLatentImage": "Empty Latent Image",
    "LatentUpscale": "Upscale Latent",
    "LatentUpscaleBy": "Upscale Latent By",
    "LatentComposite": "Latent Composite",
    "LatentBlend": "Latent Blend",
    "LatentFromBatch" : "Latent From Batch",
    "RepeatLatentBatch": "Repeat Latent Batch",
    # Image
    "SaveImage": "Save Image",
    "PreviewImage": "Preview Image",
    "LoadImage": "Load Image",
    "LoadImageMask": "Load Image (as Mask)",
    "LoadImageOutput": "Load Image (from Outputs)",
    "ImageScale": "Upscale Image",
    "ImageScaleBy": "Upscale Image By",
    "ImageInvert": "Invert Image",
    "ImagePadForOutpaint": "Pad Image for Outpainting",
    "ImageBatch": "Batch Images",
    "ImageCrop": "Image Crop",
    "ImageStitch": "Image Stitch",
    "ImageBlend": "Image Blend",
    "ImageBlur": "Image Blur",
    "ImageQuantize": "Image Quantize",
    "ImageSharpen": "Image Sharpen",
    "ImageScaleToTotalPixels": "Scale Image to Total Pixels",
    "GetImageSize": "Get Image Size",
    # _for_testing
    "VAEDecodeTiled": "VAE Decode (Tiled)",
    "VAEEncodeTiled": "VAE Encode (Tiled)",
}

if args.fast_load:
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

EXTENSION_WEB_DIRS = {}

# Dictionary of successfully loaded module names and associated directories.
LOADED_MODULE_DIRS = {}


def get_module_name(module_path: str) -> str:
    """
    Returns the module name based on the given module path.
    Examples:
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.disabled") -> "custom_nodes
    Args:
        module_path (str): The path of the module.
    Returns:
        str: The module name.
    """
    base_path = os.path.basename(module_path)
    if os.path.isfile(module_path):
        base_path = os.path.splitext(base_path)[0]
    return base_path


async def load_custom_node(module_path: str, ignore=set(), module_parent="custom_nodes") -> bool:
    module_name = get_module_name(module_path)
    if os.path.isfile(module_path):
        sp = os.path.splitext(module_path)
        module_name = sp[0]
        sys_module_name = module_name
    elif os.path.isdir(module_path):
        sys_module_name = module_path.replace(".", "_x_")

    try:
        logging.debug("Trying to load custom node {}".format(module_path))
        if os.path.isfile(module_path):
            /* Lines 2148-2149 omitted */
        else:
            /* Lines 2151-2152 omitted */

        module = importlib.util.module_from_spec(module_spec)
        sys.modules[sys_module_name] = module
        module_spec.loader.exec_module(module)

        LOADED_MODULE_DIRS[module_name] = os.path.abspath(module_dir)

        try:
            /* Lines 2161-2175 omitted */
        except Exception as e:
            /* Line 2177 omitted */

        if hasattr(module, "WEB_DIRECTORY") and getattr(module, "WEB_DIRECTORY") is not None:
            /* Lines 2180-2182 omitted */

        # V1 node definition
        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            /* Lines 2186-2192 omitted */
        /* Lines 2193-2194 omitted */
        elif hasattr(module, "comfy_entrypoint"):
            /* Lines 2195-2222 omitted */
        else:
            
    except Exception as e:
        logging.warning(traceback.format_exc())
        logging.warning(f"Cannot import {module_path} module for custom nodes: {e}")
        return False

async def init_external_custom_nodes():
    """
    Initializes the external custom nodes.

    This function loads custom nodes from the specified folder paths and imports them into the application.
    It measures the import times for each custom node and logs the results.

    Returns:
        None
    """
    base_node_names = set(NODE_CLASS_MAPPINGS.keys())
    node_paths = folder_paths.get_folder_paths("custom_nodes")
    node_import_times = []
    for custom_node_path in node_paths:
        possible_modules = os.listdir(os.path.realpath(custom_node_path))
        if "__pycache__" in possible_modules:
            /* Line 2247 omitted */

        for possible_module in possible_modules:
            

    if len(node_import_times) > 0:
        logging.info("\nImport times for custom nodes:")
        for n in sorted(node_import_times):
            /* Lines 2263-2267 omitted */
        logging.info("")

async def init_builtin_extra_nodes():
    """
    Initializes the built-in extra nodes in ComfyUI.

    This function loads the extra node files located in the "comfy_extras" directory and imports them into ComfyUI.
    If any of the extra node files fail to import, a warning message is logged.

    Returns:
        None
    """
    extras_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_extras")
    extras_files = [
        "nodes_latent.py",
        "nodes_hypernetwork.py",
        "nodes_upscale_model.py",
        "nodes_post_processing.py",
        "nodes_mask.py",
        "nodes_compositing.py",
        "nodes_rebatch.py",
        "nodes_model_merging.py",
        "nodes_tomesd.py",
        "nodes_clip_sdxl.py",
        "nodes_canny.py",
        "nodes_freelunch.py",
        "nodes_custom_sampler.py",
        "nodes_hypertile.py",
        "nodes_model_advanced.py",
        "nodes_model_downscale.py",
        "nodes_images.py",
        "nodes_video_model.py",
        "nodes_train.py",
        "nodes_sag.py",
        "nodes_perpneg.py",
        "nodes_stable3d.py",
        "nodes_sdupscale.py",
        "nodes_photomaker.py",
        "nodes_pixart.py",
        "nodes_cond.py",
        "nodes_morphology.py",
        "nodes_stable_cascade.py",
        "nodes_differential_diffusion.py",
        "nodes_ip2p.py",
        "nodes_model_merging_model_specific.py",
        "nodes_pag.py",
        "nodes_align_your_steps.py",
        "nodes_attention_multiply.py",
        "nodes_advanced_samplers.py",
        "nodes_webcam.py",
        "nodes_audio.py",
        "nodes_sd3.py",
        "nodes_gits.py",
        "nodes_controlnet.py",
        "nodes_hunyuan.py",
        "nodes_eps.py",
        "nodes_flux.py",
        "nodes_lora_extract.py",
        "nodes_torch_compile.py",
        "nodes_mochi.py",
        "nodes_slg.py",
        "nodes_mahiro.py",
        "nodes_lt.py",
        "nodes_hooks.py",
        "nodes_load_3d.py",
        "nodes_cosmos.py",
        "nodes_video.py",
        "nodes_lumina2.py",
        "nodes_wan.py",
        "nodes_lotus.py",
        "nodes_hunyuan3d.py",
        "nodes_primitive.py",
        "nodes_cfg.py",
        "nodes_optimalsteps.py",
        "nodes_hidream.py",
        "nodes_fresca.py",
        "nodes_apg.py",
        "nodes_preview_any.py",
        "nodes_ace.py",
        "nodes_string.py",
        "nodes_camera_trajectory.py",
        "nodes_edit_model.py",
        "nodes_tcfg.py",
        "nodes_context_windows.py",
        "nodes_qwen.py",
        "nodes_chroma_radiance.py",
        "nodes_model_patch.py",
        "nodes_easycache.py",
        "nodes_audio_encoder.py",
        "nodes_rope.py",
        "nodes_nop.py",
    ]

    import_failed = []
    for node_file in extras_files:
        if not await load_custom_node(os.path.join(extras_dir, node_file), module_parent="comfy_extras"):
            import_failed.append(node_file)

    return import_failed


async def init_builtin_api_nodes():
    api_nodes_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_api_nodes")
    api_nodes_files = [
        "nodes_ideogram.py",
        "nodes_openai.py",
        "nodes_minimax.py",
        "nodes_veo2.py",
        "nodes_kling.py",
        "nodes_bfl.py",
        "nodes_bytedance.py",
        "nodes_ltxv.py",
        "nodes_luma.py",
        "nodes_recraft.py",
        "nodes_pixverse.py",
        "nodes_stability.py",
        "nodes_pika.py",
        "nodes_runway.py",
        "nodes_sora.py",
        "nodes_topaz.py",
        "nodes_tripo.py",
        "nodes_moonvalley.py",
        "nodes_rodin.py",
        "nodes_gemini.py",
        "nodes_vidu.py",
        "nodes_wan.py",
    ]

    if not await load_custom_node(os.path.join(api_nodes_dir, "canary.py"), module_parent="comfy_api_nodes"):
        return api_nodes_files

    import_failed = []
    for node_file in api_nodes_files:
        if not await load_custom_node(os.path.join(api_nodes_dir, node_file), module_parent="comfy_api_nodes"):
            import_failed.append(node_file)

    return import_failed

async def init_public_apis():
    register_versions([
        ComfyAPIWithVersion(
            version=getattr(v, "VERSION"),
            api_class=v
        ) for v in supported_versions
    ])

async def init_extra_nodes(init_custom_nodes=True, init_api_nodes=True):
    await init_public_apis()

    import_failed = await init_builtin_extra_nodes()

    import_failed_api = []
    if init_api_nodes:
        import_failed_api = await init_builtin_api_nodes()

    if init_custom_nodes:
        await init_external_custom_nodes()
    else:
        logging.info("Skipping loading of custom nodes")

    if len(import_failed_api) > 0:
        logging.warning("WARNING: some comfy_api_nodes/ nodes did not import correctly. This may be because they are missing some dependencies.\n")
        for node in import_failed_api:
            /* Line 2431 omitted */
        logging.warning("\nThis issue might be caused by new missing dependencies added the last time you updated ComfyUI.")
        if args.windows_standalone_build:
            /* Line 2434 omitted */
        else:
            /* Line 2436 omitted */
        logging.warning("")

    if len(import_failed) > 0:
        logging.warning("WARNING: some comfy_extras/ nodes did not import correctly. This may be because they are missing some dependencies.\n")
        for node in import_failed:
            /* Line 2442 omitted */
        logging.warning("\nThis issue might be caused by new missing dependencies added the last time you updated ComfyUI.")
        if args.windows_standalone_build:
            /* Line 2445 omitted */
        else:
            /* Line 2447 omitted */
        logging.warning("")

    return import_failed
</attachment>
<attachment id="nodes.py-1" isSummarized="true" filePath="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py">
from __future__ import annotations
/* Lines 2-7 omitted */
from comfy.cli_args import args

t_import = time.time()
/* Lines 10-11 omitted */
logging.info(f"import torch time: {time.time() - t_import:.4f}s")
/* Lines 12-20 omitted */

from PIL import Image, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo
/* Lines 23-25 omitted */

t_import = time.time()
/* Lines 27-28 omitted */
logging.info(f"import safetensors.torch time: {time.time() - t_import:.4f}s")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))

t_import = time.time()
if not args.fast_load:
    /* Lines 34-39 omitted */
logging.info(f"import comfy modules time: {time.time() - t_import:.4f}s")
/* Lines 41-43 omitted */
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict, FileLocator
from comfy_api.internal import register_versions, ComfyAPIWithVersion
from comfy_api.version_list import supported_versions
from comfy_api.latest import io, ComfyExtension

t_import = time.time()
if not args.fast_load:
    /* Line 50 omitted */
logging.info(f"import comfy.clip_vision time: {time.time() - t_import:.4f}s")
/* Lines 52-60 omitted */

def before_node_execution():
    comfy.model_management.throw_exception_if_processing_interrupted()

def interrupt_processing(value=True):
    comfy.model_management.interrupt_current_processing(value)

MAX_RESOLUTION=16384

class CLIPTextEncode(ComfyNodeABC):
    @classmethod
    /* Lines 71-77 omitted */
    RETURN_TYPES = (IO.CONDITIONING,)
    OUTPUT_TOOLTIPS = ("A conditioning containing the embedded text used to guide the diffusion model.",)
    FUNCTION = "encode"

    CATEGORY = "conditioning"
    DESCRIPTION = "Encodes a text prompt using a CLIP model into an embedding that can be used to guide the diffusion model towards generating specific images."

    def encode(self, clip, text):
        


class ConditioningCombine:
    @classmethod
    /* Lines 94-95 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "combine"

    CATEGORY = "conditioning"

    def combine(self, conditioning_1, conditioning_2):
        

class ConditioningAverage :
    @classmethod
    /* Lines 106-109 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "addWeighted"

    CATEGORY = "conditioning"

    def addWeighted(self, conditioning_to, conditioning_from, conditioning_to_strength):
        

class ConditioningConcat:
    @classmethod
    /* Lines 144-148 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "concat"

    CATEGORY = "conditioning"

    def concat(self, conditioning_to, conditioning_from):
        

class ConditioningSetArea:
    @classmethod
    /* Lines 172-179 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"

    CATEGORY = "conditioning"

    def append(self, conditioning, width, height, x, y, strength):
        

class ConditioningSetAreaPercentage:
    @classmethod
    /* Lines 193-200 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"

    CATEGORY = "conditioning"

    def append(self, conditioning, width, height, x, y, strength):
        

class ConditioningSetAreaStrength:
    @classmethod
    /* Lines 214-217 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"

    CATEGORY = "conditioning"

    def append(self, conditioning, strength):
        


class ConditioningSetMask:
    @classmethod
    /* Lines 230-235 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"

    CATEGORY = "conditioning"

    def append(self, conditioning, mask, set_cond_area, strength):
        

class ConditioningZeroOut:
    @classmethod
    /* Lines 255-256 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "zero_out"

    CATEGORY = "advanced/conditioning"

    def zero_out(self, conditioning):
        

class ConditioningSetTimestepRange:
    @classmethod
    /* Lines 278-282 omitted */
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "set_range"

    CATEGORY = "advanced/conditioning"

    def set_range(self, conditioning, start, end):
        

class VAEDecode:
    @classmethod
    /* Lines 295-301 omitted */
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_TOOLTIPS = ("The decoded image.",)
    FUNCTION = "decode"

    CATEGORY = "latent"
    DESCRIPTION = "Decodes latent images back into pixel space images."

    def decode(self, vae, samples):
        

class VAEDecodeTiled:
    @classmethod
    /* Lines 317-323 omitted */
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "decode"

    CATEGORY = "_for_testing"

    def decode(self, vae, samples, tile_size, overlap=64, temporal_size=64, temporal_overlap=8):
        

class VAEEncode:
    @classmethod
    /* Lines 350-351 omitted */
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"

    CATEGORY = "latent"

    def encode(self, vae, pixels):
        

class VAEEncodeTiled:
    @classmethod
    /* Lines 363-369 omitted */
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"

    CATEGORY = "_for_testing"

    def encode(self, vae, pixels, tile_size, overlap, temporal_size=64, temporal_overlap=8):
        

class VAEEncodeForInpaint:
    @classmethod
    /* Lines 381-382 omitted */
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"

    CATEGORY = "latent/inpaint"

    def encode(self, vae, pixels, mask, grow_mask_by=6):
        


class InpaintModelConditioning:
    @classmethod
    /* Lines 421-428 omitted */

    RETURN_TYPES = ("CONDITIONING","CONDITIONING","LATENT")
    RETURN_NAMES = ("positive", "negative", "latent")
    FUNCTION = "encode"

    CATEGORY = "conditioning/inpaint"

    def encode(self, positive, negative, pixels, vae, mask, noise_mask=True):
        


class SaveLatent:
    def __init__(self):
        /* Line 473 omitted */

    @classmethod
    /* Lines 476-480 omitted */
    RETURN_TYPES = ()
    FUNCTION = "save"

    OUTPUT_NODE = True

    CATEGORY = "_for_testing"

    def save(self, samples, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        


class LoadLatent:
    @classmethod
    /* Lines 524-527 omitted */

    CATEGORY = "_for_testing"

    RETURN_TYPES = ("LATENT", )
    FUNCTION = "load"

    def load(self, latent):
        /* Lines 535-541 omitted */

    @classmethod
    /* Lines 544-549 omitted */

    @classmethod



class CheckpointLoader:
    @classmethod
    /* Lines 560-562 omitted */
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"

    CATEGORY = "advanced/loaders"
    DEPRECATED = True

    def load_checkpoint(self, config_name, ckpt_name):
        

class CheckpointLoaderSimple:
    @classmethod
    /* Lines 576-581 omitted */
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    OUTPUT_TOOLTIPS = ("The model used for denoising latents.",
                       "The CLIP model used for encoding text prompts.",
                       "The VAE model used for encoding and decoding images to and from latent space.")
    FUNCTION = "load_checkpoint"

    CATEGORY = "loaders"
    DESCRIPTION = "Loads a diffusion model checkpoint, diffusion models are used to denoise latents."

    def load_checkpoint(self, ckpt_name):
        

class DiffusersLoader:
    @classmethod
    /* Lines 598-606 omitted */
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"

    CATEGORY = "advanced/loaders/deprecated"

    def load_checkpoint(self, model_path, output_vae=True, output_clip=True):
        


class unCLIPCheckpointLoader:
    @classmethod
    /* Lines 625-627 omitted */
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "CLIP_VISION")
    FUNCTION = "load_checkpoint"

    CATEGORY = "loaders"

    def load_checkpoint(self, ckpt_name, output_vae=True, output_clip=True):
        

class CLIPSetLastLayer:
    @classmethod
    /* Lines 640-643 omitted */
    RETURN_TYPES = ("CLIP",)
    /* Lines 645-652 omitted */

class LoraLoader:
    /* Lines 655-694 omitted */

class LoraLoaderModelOnly(LoraLoader):
    /* Lines 697-707 omitted */

class VAELoader:
    /* Lines 710-801 omitted */

class ControlNetLoader:
    /* Lines 804-818 omitted */

class DiffControlNetLoader:
    /* Lines 821-834 omitted */


class ControlNetApply:
    /* Lines 838-865 omitted */


class ControlNetApplyAdvanced:
    /* Lines 869-915 omitted */


class UNETLoader:
    /* Lines 919-941 omitted */

class CLIPLoader:
    /* Lines 944-968 omitted */

class DualCLIPLoader:
    /* Lines 971-998 omitted */

class CLIPVisionLoader:
    /* Lines 1001-1015 omitted */

class CLIPVisionEncode:
    /* Lines 1018-1034 omitted */

class StyleModelLoader:
    /* Lines 1037-1049 omitted */


class StyleModelApply:
    /* Lines 1053-1111 omitted */

class unCLIPConditioning:
    /* Lines 1114-1131 omitted */

class GLIGENLoader:
    /* Lines 1134-1146 omitted */

class GLIGENTextBoxApply:
    /* Lines 1149-1177 omitted */

class EmptyLatentImage:
    /* Lines 1180-1201 omitted */


class LatentFromBatch:
    /* Lines 1205-1234 omitted */

class RepeatLatentBatch:
    /* Lines 1237-1260 omitted */

class LatentUpscale:
    /* Lines 1263-1294 omitted */

class LatentUpscaleBy:
    /* Lines 1297-1313 omitted */

class LatentRotate:
    /* Lines 1316-1337 omitted */

class LatentFlip:
    /* Lines 1340-1357 omitted */

class LatentComposite:
    /* Lines 1360-1399 omitted */

class LatentBlend:
    /* Lines 1402-1440 omitted */

class LatentCrop:
    /* Lines 1443-1473 omitted */

class SetLatentNoiseMask:
    /* Lines 1476-1489 omitted */

def common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0, disable_noise=False, start_step=None, last_step=None, force_full_denoise=False):
    /* Lines 1492-1512 omitted */

class KSampler:
    /* Lines 1515-1540 omitted */

class KSamplerAdvanced:
    /* Lines 1543-1574 omitted */

class SaveImage:
    /* Lines 1577-1629 omitted */

class PreviewImage(SaveImage):
    /* Lines 1632-1643 omitted */

class LoadImage:
    /* Lines 1646-1719 omitted */

class LoadImageMask:
    /* Lines 1722-1768 omitted */


class LoadImageOutput(LoadImage):
    /* Lines 1772-1790 omitted */


class ImageScale:
    /* Lines 1794-1821 omitted */

class ImageScaleBy:
    /* Lines 1824-1841 omitted */

class ImageInvert:

    /* Lines 1845-1856 omitted */

class ImageBatch:

    /* Lines 1860-1878 omitted */

class EmptyImage:
    /* Lines 1881-1900 omitted */

class ImagePadForOutpaint:

    /* Lines 1904-1963 omitted */


# NODE_CLASS_MAPPINGS = {
#     "KSampler": KSampler,
#     "CheckpointLoaderSimple": CheckpointLoaderSimple,
#     "CLIPTextEncode": CLIPTextEncode,
#     "CLIPSetLastLayer": CLIPSetLastLayer,
#     "VAEDecode": VAEDecode,
#     "VAEEncode": VAEEncode,
#     "VAEEncodeForInpaint": VAEEncodeForInpaint,
#     "VAELoader": VAELoader,
#     "EmptyLatentImage": EmptyLatentImage,
#     "LatentUpscale": LatentUpscale,
#     "LatentUpscaleBy": LatentUpscaleBy,
#     "LatentFromBatch": LatentFromBatch,
#     "RepeatLatentBatch": RepeatLatentBatch,
#     "SaveImage": SaveImage,
#     "PreviewImage": PreviewImage,
#     "LoadImage": LoadImage,
#     "LoadImageMask": LoadImageMask,
#     "LoadImageOutput": LoadImageOutput,
#     "ImageScale": ImageScale,
#     "ImageScaleBy": ImageScaleBy,
#     "ImageInvert": ImageInvert,
#     "ImageBatch": ImageBatch,
#     "ImagePadForOutpaint": ImagePadForOutpaint,
#     "EmptyImage": EmptyImage,
#     "ConditioningAverage": ConditioningAverage ,
#     "ConditioningCombine": ConditioningCombine,
#     "ConditioningConcat": ConditioningConcat,
#     "ConditioningSetArea": ConditioningSetArea,
#     "ConditioningSetAreaPercentage": ConditioningSetAreaPercentage,
#     "ConditioningSetAreaStrength": ConditioningSetAreaStrength,
#     "ConditioningSetMask": ConditioningSetMask,
#     "KSamplerAdvanced": KSamplerAdvanced,
#     "SetLatentNoiseMask": SetLatentNoiseMask,
#     "LatentComposite": LatentComposite,
#     "LatentBlend": LatentBlend,
#     "LatentRotate": LatentRotate,
#     "LatentFlip": LatentFlip,
#     "LatentCrop": LatentCrop,
#     "LoraLoader": LoraLoader,
#     "CLIPLoader": CLIPLoader,
#     "UNETLoader": UNETLoader,
#     "DualCLIPLoader": DualCLIPLoader,
#     "CLIPVisionEncode": CLIPVisionEncode,
#     "StyleModelApply": StyleModelApply,
#     "unCLIPConditioning": unCLIPConditioning,
#     "ControlNetApply": ControlNetApply,
#     "ControlNetApplyAdvanced": ControlNetApplyAdvanced,
#     "ControlNetLoader": ControlNetLoader,
#     "DiffControlNetLoader": DiffControlNetLoader,
#     "StyleModelLoader": StyleModelLoader,
#     "CLIPVisionLoader": CLIPVisionLoader,
#     "VAEDecodeTiled": VAEDecodeTiled,
#     "VAEEncodeTiled": VAEEncodeTiled,
#     "unCLIPCheckpointLoader": unCLIPCheckpointLoader,
#     "GLIGENLoader": GLIGENLoader,
#     "GLIGENTextBoxApply": GLIGENTextBoxApply,
#     "InpaintModelConditioning": InpaintModelConditioning,

#     "CheckpointLoader": CheckpointLoader,
#     "DiffusersLoader": DiffusersLoader,

#     "LoadLatent": LoadLatent,
#     "SaveLatent": SaveLatent,

#     "ConditioningZeroOut": ConditioningZeroOut,
#     "ConditioningSetTimestepRange": ConditioningSetTimestepRange,
#     "LoraLoaderModelOnly": LoraLoaderModelOnly,
# }
NODE_CLASS_MAPPINGS = {}

NODE_DISPLAY_NAME_MAPPINGS = {
    /* Lines 2038-2039 omitted */
    "KSampler": "KSampler",
    "KSamplerAdvanced": "KSampler (Advanced)",
    /* Lines 2041-2042 omitted */
    "CheckpointLoader": "Load Checkpoint With Config (DEPRECATED)",
    "CheckpointLoaderSimple": "Load Checkpoint",
    "VAELoader": "Load VAE",
    "LoraLoader": "Load LoRA",
    "CLIPLoader": "Load CLIP",
    "ControlNetLoader": "Load ControlNet Model",
    "DiffControlNetLoader": "Load ControlNet Model (diff)",
    "StyleModelLoader": "Load Style Model",
    "CLIPVisionLoader": "Load CLIP Vision",
    "UNETLoader": "Load Diffusion Model",
    /* Lines 2052-2053 omitted */
    "CLIPVisionEncode": "CLIP Vision Encode",
    "StyleModelApply": "Apply Style Model",
    "CLIPTextEncode": "CLIP Text Encode (Prompt)",
    "CLIPSetLastLayer": "CLIP Set Last Layer",
    "ConditioningCombine": "Conditioning (Combine)",
    "ConditioningAverage ": "Conditioning (Average)",
    "ConditioningConcat": "Conditioning (Concat)",
    "ConditioningSetArea": "Conditioning (Set Area)",
    "ConditioningSetAreaPercentage": "Conditioning (Set Area with Percentage)",
    "ConditioningSetMask": "Conditioning (Set Mask)",
    "ControlNetApply": "Apply ControlNet (OLD)",
    "ControlNetApplyAdvanced": "Apply ControlNet",
    /* Lines 2065-2066 omitted */
    "VAEEncodeForInpaint": "VAE Encode (for Inpainting)",
    "SetLatentNoiseMask": "Set Latent Noise Mask",
    "VAEDecode": "VAE Decode",
    "VAEEncode": "VAE Encode",
    "LatentRotate": "Rotate Latent",
    "LatentFlip": "Flip Latent",
    "LatentCrop": "Crop Latent",
    "EmptyLatentImage": "Empty Latent Image",
    "LatentUpscale": "Upscale Latent",
    "LatentUpscaleBy": "Upscale Latent By",
    "LatentComposite": "Latent Composite",
    "LatentBlend": "Latent Blend",
    "LatentFromBatch" : "Latent From Batch",
    "RepeatLatentBatch": "Repeat Latent Batch",
    /* Lines 2080-2081 omitted */
    "SaveImage": "Save Image",
    "PreviewImage": "Preview Image",
    "LoadImage": "Load Image",
    "LoadImageMask": "Load Image (as Mask)",
    "LoadImageOutput": "Load Image (from Outputs)",
    "ImageScale": "Upscale Image",
    "ImageScaleBy": "Upscale Image By",
    "ImageInvert": "Invert Image",
    "ImagePadForOutpaint": "Pad Image for Outpainting",
    "ImageBatch": "Batch Images",
    "ImageCrop": "Image Crop",
    "ImageStitch": "Image Stitch",
    "ImageBlend": "Image Blend",
    "ImageBlur": "Image Blur",
    "ImageQuantize": "Image Quantize",
    "ImageSharpen": "Image Sharpen",
    "ImageScaleToTotalPixels": "Scale Image to Total Pixels",
    "GetImageSize": "Get Image Size",
    /* Lines 2099-2100 omitted */
    "VAEDecodeTiled": "VAE Decode (Tiled)",
    "VAEEncodeTiled": "VAE Encode (Tiled)",
}

if args.fast_load:
    /* Lines 2105-2106 omitted */

EXTENSION_WEB_DIRS = {}

# Dictionary of successfully loaded module names and associated directories.
LOADED_MODULE_DIRS = {}


def get_module_name(module_path: str) -> str:
    /* Lines 2115-2133 omitted */


async def load_custom_node(module_path: str, ignore=set(), module_parent="custom_nodes") -> bool:
    /* Lines 2137-2229 omitted */

async def init_external_custom_nodes():
    /* Lines 2232-2268 omitted */

async def init_builtin_extra_nodes():
    /* Lines 2271-2366 omitted */


async def init_builtin_api_nodes():
    /* Lines 2370-2404 omitted */

async def init_public_apis():
    /* Lines 2407-2412 omitted */

async def init_extra_nodes(init_custom_nodes=True, init_api_nodes=True):
</attachment>
<attachment id="file:nodes.py">
User's active selection:
Excerpt from nodes.py, lines 2417 to 2417:
```python
import_failed = await init_builtin_extra_nodes()
```
</attachment>
<attachment isSummarized="true" filePath="c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py">
User's active file for additional context:
class SaveImage:
    /* Lines 1577-1629 omitted */

class PreviewImage(SaveImage):
    /* Lines 1632-1643 omitted */

class LoadImage:
    /* Lines 1646-1719 omitted */

class LoadImageMask:
    /* Lines 1722-1768 omitted */


class LoadImageOutput(LoadImage):
    /* Lines 1772-1790 omitted */


class ImageScale:
    /* Lines 1794-1821 omitted */

class ImageScaleBy:
    /* Lines 1824-1841 omitted */

class ImageInvert:

    @classmethod
    /* Lines 1846-1847 omitted */

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "invert"

    CATEGORY = "image"

    def invert(self, image):
        

class ImageBatch:

    @classmethod
    /* Lines 1861-1862 omitted */

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "batch"

    CATEGORY = "image"

    def batch(self, image1, image2):
        

class EmptyImage:
    def __init__(self, device="cpu"):
        /* Line 1882 omitted */

    @classmethod
    /* Lines 1885-1890 omitted */
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"

    CATEGORY = "image"

    def generate(self, width, height, batch_size=1, color=0):
        

class ImagePadForOutpaint:

    @classmethod
    /* Lines 1905-1915 omitted */

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "expand_image"

    CATEGORY = "image"

    def expand_image(self, image, left, top, right, bottom, feathering):
        


# NODE_CLASS_MAPPINGS = {
#     "KSampler": KSampler,
#     "CheckpointLoaderSimple": CheckpointLoaderSimple,
#     "CLIPTextEncode": CLIPTextEncode,
#     "CLIPSetLastLayer": CLIPSetLastLayer,
#     "VAEDecode": VAEDecode,
#     "VAEEncode": VAEEncode,
#     "VAEEncodeForInpaint": VAEEncodeForInpaint,
#     "VAELoader": VAELoader,
#     "EmptyLatentImage": EmptyLatentImage,
#     "LatentUpscale": LatentUpscale,
#     "LatentUpscaleBy": LatentUpscaleBy,
#     "LatentFromBatch": LatentFromBatch,
#     "RepeatLatentBatch": RepeatLatentBatch,
#     "SaveImage": SaveImage,
#     "PreviewImage": PreviewImage,
#     "LoadImage": LoadImage,
#     "LoadImageMask": LoadImageMask,
#     "LoadImageOutput": LoadImageOutput,
#     "ImageScale": ImageScale,
#     "ImageScaleBy": ImageScaleBy,
#     "ImageInvert": ImageInvert,
#     "ImageBatch": ImageBatch,
#     "ImagePadForOutpaint": ImagePadForOutpaint,
#     "EmptyImage": EmptyImage,
#     "ConditioningAverage": ConditioningAverage ,
#     "ConditioningCombine": ConditioningCombine,
#     "ConditioningConcat": ConditioningConcat,
#     "ConditioningSetArea": ConditioningSetArea,
#     "ConditioningSetAreaPercentage": ConditioningSetAreaPercentage,
#     "ConditioningSetAreaStrength": ConditioningSetAreaStrength,
#     "ConditioningSetMask": ConditioningSetMask,
#     "KSamplerAdvanced": KSamplerAdvanced,
#     "SetLatentNoiseMask": SetLatentNoiseMask,
#     "LatentComposite": LatentComposite,
#     "LatentBlend": LatentBlend,
#     "LatentRotate": LatentRotate,
#     "LatentFlip": LatentFlip,
#     "LatentCrop": LatentCrop,
#     "LoraLoader": LoraLoader,
#     "CLIPLoader": CLIPLoader,
#     "UNETLoader": UNETLoader,
#     "DualCLIPLoader": DualCLIPLoader,
#     "CLIPVisionEncode": CLIPVisionEncode,
#     "StyleModelApply": StyleModelApply,
#     "unCLIPConditioning": unCLIPConditioning,
#     "ControlNetApply": ControlNetApply,
#     "ControlNetApplyAdvanced": ControlNetApplyAdvanced,
#     "ControlNetLoader": ControlNetLoader,
#     "DiffControlNetLoader": DiffControlNetLoader,
#     "StyleModelLoader": StyleModelLoader,
#     "CLIPVisionLoader": CLIPVisionLoader,
#     "VAEDecodeTiled": VAEDecodeTiled,
#     "VAEEncodeTiled": VAEEncodeTiled,
#     "unCLIPCheckpointLoader": unCLIPCheckpointLoader,
#     "GLIGENLoader": GLIGENLoader,
#     "GLIGENTextBoxApply": GLIGENTextBoxApply,
#     "InpaintModelConditioning": InpaintModelConditioning,

#     "CheckpointLoader": CheckpointLoader,
#     "DiffusersLoader": DiffusersLoader,

#     "LoadLatent": LoadLatent,
#     "SaveLatent": SaveLatent,

#     "ConditioningZeroOut": ConditioningZeroOut,
#     "ConditioningSetTimestepRange": ConditioningSetTimestepRange,
#     "LoraLoaderModelOnly": LoraLoaderModelOnly,
# }
NODE_CLASS_MAPPINGS = {}

NODE_DISPLAY_NAME_MAPPINGS = {
    # Sampling
    "KSampler": "KSampler",
    "KSamplerAdvanced": "KSampler (Advanced)",
    # Loaders
    "CheckpointLoader": "Load Checkpoint With Config (DEPRECATED)",
    "CheckpointLoaderSimple": "Load Checkpoint",
    "VAELoader": "Load VAE",
    "LoraLoader": "Load LoRA",
    "CLIPLoader": "Load CLIP",
    "ControlNetLoader": "Load ControlNet Model",
    "DiffControlNetLoader": "Load ControlNet Model (diff)",
    "StyleModelLoader": "Load Style Model",
    "CLIPVisionLoader": "Load CLIP Vision",
    "UNETLoader": "Load Diffusion Model",
    # Conditioning
    "CLIPVisionEncode": "CLIP Vision Encode",
    "StyleModelApply": "Apply Style Model",
    "CLIPTextEncode": "CLIP Text Encode (Prompt)",
    "CLIPSetLastLayer": "CLIP Set Last Layer",
    "ConditioningCombine": "Conditioning (Combine)",
    "ConditioningAverage ": "Conditioning (Average)",
    "ConditioningConcat": "Conditioning (Concat)",
    "ConditioningSetArea": "Conditioning (Set Area)",
    "ConditioningSetAreaPercentage": "Conditioning (Set Area with Percentage)",
    "ConditioningSetMask": "Conditioning (Set Mask)",
    "ControlNetApply": "Apply ControlNet (OLD)",
    "ControlNetApplyAdvanced": "Apply ControlNet",
    # Latent
    "VAEEncodeForInpaint": "VAE Encode (for Inpainting)",
    "SetLatentNoiseMask": "Set Latent Noise Mask",
    "VAEDecode": "VAE Decode",
    "VAEEncode": "VAE Encode",
    "LatentRotate": "Rotate Latent",
    "LatentFlip": "Flip Latent",
    "LatentCrop": "Crop Latent",
    "EmptyLatentImage": "Empty Latent Image",
    "LatentUpscale": "Upscale Latent",
    "LatentUpscaleBy": "Upscale Latent By",
    "LatentComposite": "Latent Composite",
    "LatentBlend": "Latent Blend",
    "LatentFromBatch" : "Latent From Batch",
    "RepeatLatentBatch": "Repeat Latent Batch",
    # Image
    "SaveImage": "Save Image",
    "PreviewImage": "Preview Image",
    "LoadImage": "Load Image",
    "LoadImageMask": "Load Image (as Mask)",
    "LoadImageOutput": "Load Image (from Outputs)",
    "ImageScale": "Upscale Image",
    "ImageScaleBy": "Upscale Image By",
    "ImageInvert": "Invert Image",
    "ImagePadForOutpaint": "Pad Image for Outpainting",
    "ImageBatch": "Batch Images",
    "ImageCrop": "Image Crop",
    "ImageStitch": "Image Stitch",
    "ImageBlend": "Image Blend",
    "ImageBlur": "Image Blur",
    "ImageQuantize": "Image Quantize",
    "ImageSharpen": "Image Sharpen",
    "ImageScaleToTotalPixels": "Scale Image to Total Pixels",
    "GetImageSize": "Get Image Size",
    # _for_testing
    "VAEDecodeTiled": "VAE Decode (Tiled)",
    "VAEEncodeTiled": "VAE Encode (Tiled)",
}

if args.fast_load:
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}

EXTENSION_WEB_DIRS = {}

# Dictionary of successfully loaded module names and associated directories.
LOADED_MODULE_DIRS = {}


def get_module_name(module_path: str) -> str:
    """
    Returns the module name based on the given module path.
    Examples:
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.disabled") -> "custom_nodes
    Args:
        module_path (str): The path of the module.
    Returns:
        str: The module name.
    """
    base_path = os.path.basename(module_path)
    if os.path.isfile(module_path):
        base_path = os.path.splitext(base_path)[0]
    return base_path


async def load_custom_node(module_path: str, ignore=set(), module_parent="custom_nodes") -> bool:
    module_name = get_module_name(module_path)
    if os.path.isfile(module_path):
        sp = os.path.splitext(module_path)
        module_name = sp[0]
        sys_module_name = module_name
    elif os.path.isdir(module_path):
        sys_module_name = module_path.replace(".", "_x_")

    try:
        logging.debug("Trying to load custom node {}".format(module_path))
        if os.path.isfile(module_path):
            /* Lines 2148-2149 omitted */
        else:
            /* Lines 2151-2152 omitted */

        module = importlib.util.module_from_spec(module_spec)
        sys.modules[sys_module_name] = module
        module_spec.loader.exec_module(module)

        LOADED_MODULE_DIRS[module_name] = os.path.abspath(module_dir)

        try:
            /* Lines 2161-2175 omitted */
        except Exception as e:
            /* Line 2177 omitted */

        if hasattr(module, "WEB_DIRECTORY") and getattr(module, "WEB_DIRECTORY") is not None:
            /* Lines 2180-2182 omitted */

        # V1 node definition
        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            /* Lines 2186-2192 omitted */
        /* Lines 2193-2194 omitted */
        elif hasattr(module, "comfy_entrypoint"):
            /* Lines 2195-2222 omitted */
        else:
            
    except Exception as e:
        logging.warning(traceback.format_exc())
        logging.warning(f"Cannot import {module_path} module for custom nodes: {e}")
        return False

async def init_external_custom_nodes():
    """
    Initializes the external custom nodes.

    This function loads custom nodes from the specified folder paths and imports them into the application.
    It measures the import times for each custom node and logs the results.

    Returns:
        None
    """
    base_node_names = set(NODE_CLASS_MAPPINGS.keys())
    node_paths = folder_paths.get_folder_paths("custom_nodes")
    node_import_times = []
    for custom_node_path in node_paths:
        possible_modules = os.listdir(os.path.realpath(custom_node_path))
        if "__pycache__" in possible_modules:
            /* Line 2247 omitted */

        for possible_module in possible_modules:
            

    if len(node_import_times) > 0:
        logging.info("\nImport times for custom nodes:")
        for n in sorted(node_import_times):
            /* Lines 2263-2267 omitted */
        logging.info("")

async def init_builtin_extra_nodes():
    """
    Initializes the built-in extra nodes in ComfyUI.

    This function loads the extra node files located in the "comfy_extras" directory and imports them into ComfyUI.
    If any of the extra node files fail to import, a warning message is logged.

    Returns:
        None
    """
    extras_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_extras")
    extras_files = [
        "nodes_latent.py",
        "nodes_hypernetwork.py",
        "nodes_upscale_model.py",
        "nodes_post_processing.py",
        "nodes_mask.py",
        "nodes_compositing.py",
        "nodes_rebatch.py",
        "nodes_model_merging.py",
        "nodes_tomesd.py",
        "nodes_clip_sdxl.py",
        "nodes_canny.py",
        "nodes_freelunch.py",
        "nodes_custom_sampler.py",
        "nodes_hypertile.py",
        "nodes_model_advanced.py",
        "nodes_model_downscale.py",
        "nodes_images.py",
        "nodes_video_model.py",
        "nodes_train.py",
        "nodes_sag.py",
        "nodes_perpneg.py",
        "nodes_stable3d.py",
        "nodes_sdupscale.py",
        "nodes_photomaker.py",
        "nodes_pixart.py",
        "nodes_cond.py",
        "nodes_morphology.py",
        "nodes_stable_cascade.py",
        "nodes_differential_diffusion.py",
        "nodes_ip2p.py",
        "nodes_model_merging_model_specific.py",
        "nodes_pag.py",
        "nodes_align_your_steps.py",
        "nodes_attention_multiply.py",
        "nodes_advanced_samplers.py",
        "nodes_webcam.py",
        "nodes_audio.py",
        "nodes_sd3.py",
        "nodes_gits.py",
        "nodes_controlnet.py",
        "nodes_hunyuan.py",
        "nodes_eps.py",
        "nodes_flux.py",
        "nodes_lora_extract.py",
        "nodes_torch_compile.py",
        "nodes_mochi.py",
        "nodes_slg.py",
        "nodes_mahiro.py",
        "nodes_lt.py",
        "nodes_hooks.py",
        "nodes_load_3d.py",
        "nodes_cosmos.py",
        "nodes_video.py",
        "nodes_lumina2.py",
        "nodes_wan.py",
        "nodes_lotus.py",
        "nodes_hunyuan3d.py",
        "nodes_primitive.py",
        "nodes_cfg.py",
        "nodes_optimalsteps.py",
        "nodes_hidream.py",
        "nodes_fresca.py",
        "nodes_apg.py",
        "nodes_preview_any.py",
        "nodes_ace.py",
        "nodes_string.py",
        "nodes_camera_trajectory.py",
        "nodes_edit_model.py",
        "nodes_tcfg.py",
        "nodes_context_windows.py",
        "nodes_qwen.py",
        "nodes_chroma_radiance.py",
        "nodes_model_patch.py",
        "nodes_easycache.py",
        "nodes_audio_encoder.py",
        "nodes_rope.py",
        "nodes_nop.py",
    ]

    import_failed = []
    for node_file in extras_files:
        if not await load_custom_node(os.path.join(extras_dir, node_file), module_parent="comfy_extras"):
            import_failed.append(node_file)

    return import_failed


async def init_builtin_api_nodes():
    api_nodes_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_api_nodes")
    api_nodes_files = [
        "nodes_ideogram.py",
        "nodes_openai.py",
        "nodes_minimax.py",
        "nodes_veo2.py",
        "nodes_kling.py",
        "nodes_bfl.py",
        "nodes_bytedance.py",
        "nodes_ltxv.py",
        "nodes_luma.py",
        "nodes_recraft.py",
        "nodes_pixverse.py",
        "nodes_stability.py",
        "nodes_pika.py",
        "nodes_runway.py",
        "nodes_sora.py",
        "nodes_topaz.py",
        "nodes_tripo.py",
        "nodes_moonvalley.py",
        "nodes_rodin.py",
        "nodes_gemini.py",
        "nodes_vidu.py",
        "nodes_wan.py",
    ]

    if not await load_custom_node(os.path.join(api_nodes_dir, "canary.py"), module_parent="comfy_api_nodes"):
        return api_nodes_files

    import_failed = []
    for node_file in api_nodes_files:
        if not await load_custom_node(os.path.join(api_nodes_dir, node_file), module_parent="comfy_api_nodes"):
            import_failed.append(node_file)

    return import_failed

async def init_public_apis():
    register_versions([
        ComfyAPIWithVersion(
            version=getattr(v, "VERSION"),
            api_class=v
        ) for v in supported_versions
    ])

async def init_extra_nodes(init_custom_nodes=True, init_api_nodes=True):
    await init_public_apis()

    import_failed = await init_builtin_extra_nodes()

    import_failed_api = []
    if init_api_nodes:
        import_failed_api = await init_builtin_api_nodes()

    if init_custom_nodes:
        await init_external_custom_nodes()
    else:
        logging.info("Skipping loading of custom nodes")

    if len(import_failed_api) > 0:
        logging.warning("WARNING: some comfy_api_nodes/ nodes did not import correctly. This may be because they are missing some dependencies.\n")
        for node in import_failed_api:
            logging.warning("IMPORT FAILED: {}".format(node))
        logging.warning("\nThis issue might be caused by new missing dependencies added the last time you updated ComfyUI.")
        if args.windows_standalone_build:
            logging.warning("Please run the update script: update/update_comfyui.bat")
        else:
            logging.warning("Please do a: pip install -r requirements.txt")
        logging.warning("")

    if len(import_failed) > 0:
        logging.warning("WARNING: some comfy_extras/ nodes did not import correctly. This may be because they are missing some dependencies.\n")
        for node in import_failed:
            logging.warning("IMPORT FAILED: {}".format(node))
        logging.warning("\nThis issue might be caused by new missing dependencies added the last time you updated ComfyUI.")
        if args.windows_standalone_build:
            logging.warning("Please run the update script: update/update_comfyui.bat")
        else:
            logging.warning("Please do a: pip install -r requirements.txt")
        logging.warning("")

    return import_failed
</attachment>
</attachments>
<context>
The current date is 2025년 12월 16일.
Terminals:
Terminal: bash
Terminal: bash
Last Command: ll
Cwd: C:/Workbench/20_Projects/hvppycoding_ComfyUI
Exit Code: 0
Terminal: bash
Last Command: ll
Cwd: C:/Workbench/20_Projects/hvppycoding_ComfyUI
Exit Code: 0

</context>
<editorContext>
The user's current file is c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py. The current selection is from line 2417 to line 2417.
</editorContext>
<reminderInstructions>
When using the replace_string_in_file tool, include 3-5 lines of unchanged code before and after the string you want to replace, to make it unambiguous which part of the file should be edited.

</reminderInstructions>
<userRequest>
아직도 필요없는 노드들이 많이 있어. 나는 기본 노드들(String 관련 등) 제외하고 다 로드가 안되면 좋겠어.
</userRequest>


[copilot_cache_control: { type: 'ephemeral' }]
Assistant
reasoning: **Evaluating Optimization Potential**

I'm currently considering how to improve the startup time. I'm focusing on disabling more nodes when the `--fast-load` flag is used. My current plan involves modifying `nodes.py` to further clear out `NODE_CLASS_MAPPINGS`. I'm mindful of `init_extra_nodes` and `init_builtin_extra_nodes` and how they might affect these changes.


**Prioritizing Node Exclusion**

I've been examining `init_extra_nodes` and its dependencies. My focus has shifted toward selectively preventing `comfy_extras` and `comfy_api_nodes` from loading, as the original aim was to exclude *everything* but the basic nodes. I'm now studying the contents of `init_builtin_extra_nodes`, and considering the nodes_string.py file in particular.


**Refining Node Filtering Logic**

I'm now zeroing in on modifying `init_builtin_extra_nodes` within `nodes.py`. My current plan is to conditionally load a reduced set of nodes, specifically including string-related nodes, when the `--fast-load` flag is active. I'm prioritizing ensuring the core functionality, as the user described, remains functional, with `comfy_extras` and `comfy_api_nodes` receiving careful scrutiny for exclusion. This means I'm looking at `nodes_string.py` and potentially `nodes_primitive.py`. I'm starting the code changes.


**Adjusting Node Loading Strategy**

I'm now implementing the node filtering in `init_builtin_extra_nodes`. My current plan is to selectively include `nodes_string.py` and potentially `nodes_primitive.py` when the `--fast-load` flag is active. I'm focusing on modifying the list of `extras_files` and ensuring that `init_builtin_api_nodes` is also skipped. I've now written the core changes to the file.


**Finalizing Node Filtering**

I've now implemented the conditional filtering within `init_builtin_extra_nodes`, including `nodes_string.py` and `nodes_primitive.py` when `--fast-load` is active. I've also updated the `init_extra_nodes` function to skip the other node initializations, like the API nodes, if `--fast-load` is used, to ensure the full optimization. I've tested and reviewed the changes.


**Modifying Node Inclusion**

I'm now revising my plan to modify `init_builtin_extra_nodes` and filter the `extras_files` list when `--fast-load` is active, keeping `nodes_string.py` and `nodes_primitive.py`. I've also noted that `init_extra_nodes` should skip `init_builtin_api_nodes` in that case, to fully disable the API. I'm confident about proceeding with the code changes.


**Filtering File Loading**

I'm now implementing the core changes. I'm focusing on modifying `init_builtin_extra_nodes` within `nodes.py` to filter the `extras_files` list, ensuring that only "basic" nodes like `nodes_string.py` and `nodes_primitive.py` are loaded when the `--fast-load` flag is active, and skipping the API nodes. I'm writing and testing the conditional logic now.


**Confirming Code Modifications**

I'm verifying that the conditional loading of `nodes_string.py` and `nodes_primitive.py` within `init_builtin_extra_nodes` is working as intended when `--fast-load` is enabled. I've also confirmed that `init_builtin_api_nodes` returns an empty list in that scenario, effectively disabling API nodes during the startup. I will confirm `canary.py` is needed, or not.


**Verifying Conditional Node Loading**

I'm now making sure that the changes to `init_builtin_extra_nodes` and `init_builtin_api_nodes` are correctly implemented. I'm focusing on validating that the `--fast-load` flag effectively restricts node loading to only the string and primitive nodes and that the API nodes are fully excluded. I'm now also considering canary.py.


**Testing API and String Nodes**

I'm now in the process of ensuring that only `nodes_string.py` and `nodes_primitive.py` are loaded when the `--fast-load` flag is enabled and that all API nodes are excluded. I'm carefully reviewing the updated code and its effect on the startup, specifically checking that the API nodes are disabled and `canary.py` is not.


**Verifying Fast-Load Behavior**

I'm now verifying the impact of the changes on startup time. Specifically, I'm confirming that the modified `init_extra_nodes` and `init_builtin_api_nodes` functions correctly load only the essential string and primitive nodes when the `--fast-load` flag is active, effectively excluding all API nodes. I'm also ensuring `canary.py` is skipped.




🛠️ replace_string_in_file (call_MHxmdlhiaGhKZDg4UUJicFZTMkk) {
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py",
  "newString": "        \"nodes_rope.py\",
        \"nodes_nop.py\",
    ]

    if args.fast_load:
        extras_files = [\"nodes_primitive.py\", \"nodes_string.py\"]

    import_failed = []",
  "oldString": "        \"nodes_rope.py\",
        \"nodes_nop.py\",
    ]

    import_failed = []"
}
Tool
🛠️ call_MHxmdlhiaGhKZDg4UUJicFZTMkk
The following files were successfully edited:
c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py


[copilot_cache_control: { type: 'ephemeral' }]
Assistant


🛠️ replace_string_in_file (call_MHx3SjBSeGdaYTBHWDdvZXQxajg) {
  "filePath": "c:\\Workbench\\20_Projects\\hvppycoding_ComfyUI\\nodes.py",
  "newString": "async def init_builtin_api_nodes():
    if args.fast_load:
        return []
    api_nodes_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), \"comfy_api_nodes\")",
  "oldString": "async def init_builtin_api_nodes():
    api_nodes_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), \"comfy_api_nodes\")"
}
Tool
🛠️ call_MHx3SjBSeGdaYTBHWDdvZXQxajg
The following files were successfully edited:
c:\Workbench\20_Projects\hvppycoding_ComfyUI\nodes.py


[copilot_cache_control: { type: 'ephemeral' }]
Response
Assistant
`--fast-load` 옵션이 활성화되었을 때, **기본적인 노드(Primitive, String 관련)를 제외한 나머지 모든 추가 노드와 API 노드들의 로딩을 건너뛰도록** 설정했습니다.

1.  **`init_builtin_extra_nodes` 수정**: `comfy_extras` 폴더의 노드들 중 `nodes_primitive.py`와 `nodes_string.py`만 로드하고 나머지는 무시합니다.
2.  **`init_builtin_api_nodes` 수정**: `comfy_api_nodes` 폴더의 모든 API 관련 노드 로딩을 건너뜁니다.

이제 부팅 시 필수적인 최소한의 노드만 로드되므로 속도가 더욱 빨라질 것입니다.

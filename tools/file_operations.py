"""
File operations tool for reading and writing files
"""
import os
from pathlib import Path
from typing import Any
from tools.base import BaseTool
from models.schemas import ToolResult, ToolDefinition


class FileOperationsTool(BaseTool):
    """Tool for file operations"""
    
    def __init__(self, allowed_directory: str = "./data"):
        super().__init__("file_operations", "Read and write files")
        self.allowed_directory = Path(allowed_directory)
        self.allowed_directory.mkdir(exist_ok=True)
    
    def execute(self, action: str, filename: str, content: str = None) -> ToolResult:
        """Execute file operation"""
        try:
            file_path = self.allowed_directory / filename
            
            # Security check: ensure file is within allowed directory
            if not str(file_path.resolve()).startswith(str(self.allowed_directory.resolve())):
                return self._create_error_result("Access denied: File outside allowed directory")
            
            if action == "read":
                return self._read_file(file_path)
            elif action == "write":
                return self._write_file(file_path, content)
            elif action == "list":
                return self._list_files()
            else:
                return self._create_error_result(f"Unknown action: {action}")
                
        except Exception as e:
            return self._create_error_result(f"File operation error: {str(e)}")
    
    def _read_file(self, file_path: Path) -> ToolResult:
        """Read file content"""
        if not file_path.exists():
            return self._create_error_result(f"File does not exist: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._create_success_result(content)
        except Exception as e:
            return self._create_error_result(f"Error reading file: {str(e)}")
    
    def _write_file(self, file_path: Path, content: str) -> ToolResult:
        """Write content to file"""
        if content is None:
            return self._create_error_result("Content is required for write operation")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return self._create_success_result(f"Successfully wrote to {file_path.name}")
        except Exception as e:
            return self._create_error_result(f"Error writing file: {str(e)}")
    
    def _list_files(self) -> ToolResult:
        """List files in allowed directory"""
        try:
            files = [f.name for f in self.allowed_directory.iterdir() if f.is_file()]
            return self._create_success_result(files)
        except Exception as e:
            return self._create_error_result(f"Error listing files: {str(e)}")
    
    def get_tool_definition(self) -> ToolDefinition:
        """Get tool definition for OpenAI function calling"""
        return ToolDefinition(
            type="function",
            function={
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["read", "write", "list"],
                            "description": "Action to perform: read, write, or list files"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to operate on"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write (required for write action)"
                        }
                    },
                    "required": ["action", "filename"]
                }
            }
        )
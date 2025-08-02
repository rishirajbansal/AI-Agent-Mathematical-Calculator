"""
Tests for File Operations tool
"""
import pytest
from pathlib import Path

from tools.file_operations import FileOperationsTool
from models.schemas import ToolDefinition


class TestFileOperationsTool:
    """Test File Operations tool functionality"""
    
    @pytest.fixture
    def file_tool(self, temp_data_dir):
        """File operations tool fixture"""
        return FileOperationsTool(allowed_directory=str(temp_data_dir))
    
    def test_initialization(self, file_tool, temp_data_dir):
        """Test file tool initialization"""
        assert file_tool.name == "file_operations"
        assert file_tool.description == "Read and write files"
        assert file_tool.allowed_directory == temp_data_dir
        assert temp_data_dir.exists()
    
    def test_write_file(self, file_tool, temp_data_dir):
        """Test writing to a file"""
        content = "Hello, World!"
        result = file_tool.execute(
            action="write",
            filename="test.txt",
            content=content
        )
        
        assert result.success is True
        assert "Successfully wrote to test.txt" in result.result
        
        # Verify file was created
        file_path = temp_data_dir / "test.txt"
        assert file_path.exists()
        assert file_path.read_text() == content
    
    def test_read_file(self, file_tool, temp_data_dir):
        """Test reading a file"""
        # Create a test file
        content = "Test file content"
        file_path = temp_data_dir / "read_test.txt"
        file_path.write_text(content)
        
        # Read the file
        result = file_tool.execute(
            action="read",
            filename="read_test.txt"
        )
        
        assert result.success is True
        assert result.result == content
    
    def test_read_nonexistent_file(self, file_tool):
        """Test reading a file that doesn't exist"""
        result = file_tool.execute(
            action="read",
            filename="nonexistent.txt"
        )
        
        assert result.success is False
        assert "File does not exist" in result.error
    
    def test_list_files(self, file_tool, temp_data_dir):
        """Test listing files in directory"""
        # Create some test files
        (temp_data_dir / "file1.txt").write_text("content1")
        (temp_data_dir / "file2.txt").write_text("content2")
        (temp_data_dir / "file3.txt").write_text("content3")
        
        result = file_tool.execute(action="list", filename="")
        
        assert result.success is True
        assert isinstance(result.result, list)
        assert len(result.result) == 3
        assert "file1.txt" in result.result
        assert "file2.txt" in result.result
        assert "file3.txt" in result.result
    
    def test_list_empty_directory(self, file_tool):
        """Test listing files in empty directory"""
        result = file_tool.execute(action="list", filename="")
        
        assert result.success is True
        assert isinstance(result.result, list)
        assert len(result.result) == 0
    
    def test_write_without_content(self, file_tool):
        """Test writing without providing content"""
        result = file_tool.execute(
            action="write",
            filename="test.txt"
        )
        
        assert result.success is False
        assert "Content is required for write operation" in result.error
    
    def test_invalid_action(self, file_tool):
        """Test invalid action"""
        result = file_tool.execute(
            action="invalid_action",
            filename="test.txt"
        )
        
        assert result.success is False
        assert "Unknown action: invalid_action" in result.error
    
    def test_security_path_traversal(self, file_tool):
        """Test security against path traversal attacks"""
        result = file_tool.execute(
            action="write",
            filename="../../../etc/passwd",
            content="malicious content"
        )
        
        assert result.success is False
        assert "Access denied: File outside allowed directory" in result.error
    
    def test_overwrite_file(self, file_tool, temp_data_dir):
        """Test overwriting an existing file"""
        filename = "overwrite_test.txt"
        original_content = "Original content"
        new_content = "New content"
        
        # Create initial file
        result1 = file_tool.execute(
            action="write",
            filename=filename,
            content=original_content
        )
        assert result1.success is True
        
        # Overwrite file
        result2 = file_tool.execute(
            action="write",
            filename=filename,
            content=new_content
        )
        assert result2.success is True
        
        # Verify content was overwritten
        result3 = file_tool.execute(
            action="read",
            filename=filename
        )
        assert result3.success is True
        assert result3.result == new_content
    
    def test_unicode_content(self, file_tool):
        """Test handling Unicode content"""
        unicode_content = "Hello 世界 🌍 café résumé"
        
        result = file_tool.execute(
            action="write",
            filename="unicode_test.txt",
            content=unicode_content
        )
        assert result.success is True
        
        read_result = file_tool.execute(
            action="read",
            filename="unicode_test.txt"
        )
        assert read_result.success is True
        assert read_result.result == unicode_content
    
    def test_large_file(self, file_tool):
        """Test handling large file content"""
        large_content = "A" * 10000  # 10KB content
        
        result = file_tool.execute(
            action="write",
            filename="large_test.txt",
            content=large_content
        )
        assert result.success is True
        
        read_result = file_tool.execute(
            action="read",
            filename="large_test.txt"
        )
        assert read_result.success is True
        assert len(read_result.result) == 10000
        assert read_result.result == large_content
    
    def test_tool_definition(self, file_tool):
        """Test tool definition structure"""
        definition = file_tool.get_tool_definition()
        
        assert isinstance(definition, ToolDefinition)
        assert definition.type == "function"
        assert definition.function["name"] == "file_operations"
        assert definition.function["description"] == "Read and write files"
        
        # Check parameters structure
        params = definition.function["parameters"]
        assert params["type"] == "object"
        
        # Check required parameters
        assert "action" in params["properties"]
        assert "filename" in params["properties"]
        assert "content" in params["properties"]
        
        # Check action enum
        assert params["properties"]["action"]["enum"] == ["read", "write", "list"]
        
        # Check required fields
        assert set(params["required"]) == {"action", "filename"}
    
    def test_subdirectory_creation(self, file_tool, temp_data_dir):
        """Test that subdirectories are not created (security feature)"""
        result = file_tool.execute(
            action="write",
            filename="subdir/test.txt",
            content="test"
        )
        
        # This should fail because we don't create subdirectories
        # The file path will be outside allowed directory due to path resolution
        assert result.success is False
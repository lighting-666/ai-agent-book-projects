import os
import json
import pytest
import tempfile
from pathlib import Path
from agent import SystemHintAgent, SystemHintConfig

class TestReadFile:
    @pytest.fixture
    def config(self):
        # Create configuration with system hints enabled
        return SystemHintConfig(
            enable_timestamps=True,
            enable_tool_counter=True,
            enable_todo_list=True,
            enable_detailed_errors=True,
            enable_system_state=True,
            save_trajectory=True,
            trajectory_file="test_read_trajectory.json"
        )

    @pytest.fixture
    def agent(self, config):
        # Create agent with system hints enabled
        agent = SystemHintAgent(
            api_key="dummy-key", 
            provider="kimi",
            config=config,
            verbose=True
        )
        yield agent
        # Clean up trajectory file after test
        if os.path.exists("test_read_trajectory.json"):
            os.remove("test_read_trajectory.json")
    
    @pytest.fixture
    def test_dir(self):
        # Create a temporary directory for test files
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
            
    def test_read_text_file(self, agent, test_dir):
        # Create a test text file
        file_path = os.path.join(test_dir, "test.txt")
        test_content = "Line 1\nLine 2\nLine 3\n"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Test reading entire file
        result = agent._tool_read_file(file_path)
        assert result["success"] == True
        assert result["content"] == test_content
        assert result["file_path"] == file_path
        
    def test_read_with_line_range(self, agent, test_dir):
        # Create a test file with numbered lines
        file_path = os.path.join(test_dir, "lines.txt")
        test_content = "\n".join(f"Line {i}" for i in range(1, 6))
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Test reading specific lines
        result = agent._tool_read_file(file_path, begin_line=2, number_lines=2)
        assert result["success"] == True
        assert result["content"] == "Line 2\nLine 3\n"
        
    def test_nonexistent_file(self, agent):
        result = agent._tool_read_file("nonexistent.txt")
        assert result["success"] == False
        assert "File not found" in result["error"]
        
    def test_binary_file(self, agent, test_dir):
        # Create a binary file
        file_path = os.path.join(test_dir, "binary.bin")
        with open(file_path, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        
        result = agent._tool_read_file(file_path)
        assert result["success"] == False
        assert "binary file" in result["error"].lower()
        assert result["is_binary"] == True
        
    def test_relative_path(self, agent, test_dir):
        # Set agent's current directory
        agent.current_directory = test_dir
        
        # Create test file in the current directory
        rel_path = "relative.txt"
        abs_path = os.path.join(test_dir, rel_path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write("Test content")
        
        # Test reading with relative path
        result = agent._tool_read_file(rel_path)
        assert result["success"] == True
        assert result["content"] == "Test content"
        assert os.path.samefile(result["file_path"], abs_path)
        
    def test_tool_counter(self, agent, test_dir):
        """Test that tool call counter is working"""
        file_path = os.path.join(test_dir, "counter_test.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Test content")
            
        # Call read_file multiple times
        for i in range(3):
            result = agent._tool_read_file(file_path)
            # Verify the tool call number is incremented
            assert result.get("tool_call_number") == i + 1
            
    def test_trajectory_saving(self, agent, test_dir):
        """Test that operations are saved in trajectory"""
        file_path = os.path.join(test_dir, "trajectory_test.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Test content")
            
        # Read file and check trajectory
        agent._tool_read_file(file_path)
        
        assert os.path.exists("test_read_trajectory.json")
        with open("test_read_trajectory.json", 'r') as f:
            trajectory = json.load(f)
            
        # Verify trajectory contains tool calls
        assert "tool_calls" in trajectory
        tool_calls = trajectory["tool_calls"]
        assert len(tool_calls) > 0
        last_call = tool_calls[-1]
        assert last_call["tool_name"] == "read_file"
        assert "timestamp" in last_call
        
    def test_error_details(self, agent):
        """Test that detailed error information is provided"""
        # Try to read a non-existent file
        result = agent._tool_read_file("nonexistent_file.txt")
        
        # Verify detailed error information
        assert result["success"] == False
        assert "error" in result
        error_msg = result["error"]
        # Check if error message contains detailed information
        assert "File not found" in error_msg
        # In verbose mode, should include system state
        assert "current_directory" in str(result)


def run_manual_tests():
    """Run tests manually with actual API key for interactive testing"""
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ Please set KIMI_API_KEY environment variable")
        return False
    
    print("\n" + "="*60)
    print("MANUAL SYSTEM HINT READ FILE TESTS")
    print("="*60)
    
    # Create configuration
    config = SystemHintConfig(
        enable_timestamps=True,
        enable_tool_counter=True,
        enable_todo_list=True,
        enable_detailed_errors=True,
        enable_system_state=True,
        save_trajectory=True,
        trajectory_file="manual_test_read_trajectory.json"
    )
    
    # Initialize agent
    agent = SystemHintAgent(
        api_key=api_key,
        provider="kimi",
        config=config,
        verbose=True
    )
    
    # Create a test directory and file
    with tempfile.TemporaryDirectory() as test_dir:
        # Test 1: Basic file reading
        test_file = os.path.join(test_dir, "test.txt")
        print("\n1. Testing basic file read...")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Line 1\nLine 2\nLine 3")
            
        result = agent._tool_read_file(test_file)
        if result["success"]:
            print("✅ Basic file read successful")
            print(f"📝 Content: {result['content']}")
            print(f"🔄 Tool call number: {result.get('tool_call_number', 'N/A')}")
        else:
            print("❌ Basic file read failed")
            print(f"Error: {result['error']}")
            
        # Test 2: Line range reading
        print("\n2. Testing line range read...")
        result = agent._tool_read_file(test_file, begin_line=2, number_lines=1)
        if result["success"]:
            print("✅ Line range read successful")
            print(f"📝 Content: {result['content']}")
        else:
            print("❌ Line range read failed")
            print(f"Error: {result['error']}")
            
        # Test 3: Error handling
        print("\n3. Testing error handling...")
        result = agent._tool_read_file("nonexistent.txt")
        print("✅ Error handling test complete")
        print(f"📝 Error message: {result['error']}")
        
        # Test 4: Check trajectory
        print("\n4. Checking trajectory file...")
        if os.path.exists("manual_test_read_trajectory.json"):
            with open("manual_test_read_trajectory.json", 'r') as f:
                trajectory = json.load(f)
            print("✅ Trajectory file created")
            print(f"📊 Number of tool calls: {len(trajectory.get('tool_calls', []))}")
        else:
            print("❌ Trajectory file not found")
    
    print("\n" + "="*60)
    return True


if __name__ == "__main__":
    # If run directly, perform manual tests
    success = run_manual_tests()
    if not success:
        print("\n❌ Manual tests failed or were not completed")
    else:
        print("\n✅ Manual tests completed successfully")
#!/usr/bin/env python3
"""
Test script to demonstrate streaming functionality
for both vLLM and Ollama backends
"""

import sys
import platform
from main import ToolCallingAgent


def test_streaming():
    """Test streaming functionality with various queries"""
    print("="*60)
    print("🚀 STREAMING TEST DEMO")
    print("="*60)
    print(f"Platform: {platform.system()}")
    print("="*60)
    
    # Initialize agent
    print("\n⚙️  Initializing agent...")
    agent = ToolCallingAgent()
    print(f"✅ Using {agent.backend_type} backend")
    
    # Test queries that will demonstrate streaming features
    test_queries = [
        {
            "name": "Simple Calculation with Thinking",
            "query": "Calculate 15 * 23 + sqrt(144). Think through the steps."
        },
        {
            "name": "Tool Usage with Weather",
            "query": "What's the weather in Tokyo? If it's hot (above 25°C), suggest some cooling tips."
        },
        {
            "name": "Multiple Tools",
            "query": "Convert 100 USD to EUR and tell me the current time in London."
        }
    ]
    
    for test in test_queries:
        print("\n" + "="*60)
        print(f"📋 Test: {test['name']}")
        print("="*60)
        print(f"Query: {test['query']}")
        print("-"*60)
        
        try:
            print("\n🔄 Streaming response:\n")
            
            thinking_shown = False
            tools_shown = False
            response_shown = False
            
            # Stream the response
            for chunk in agent.chat(test['query'], stream=True):
                chunk_type = chunk.get("type")
                content = chunk.get("content", "")
                
                if chunk_type == "thinking":
                    if not thinking_shown:
                        print("🧠 Internal Thinking:")
                        print("  ", end="")
                        thinking_shown = True
                    # Show thinking in gray/dim text
                    print(f"\033[90m{content}\033[0m")
                
                elif chunk_type == "tool_call":
                    if not tools_shown:
                        print("\n🔧 Tool Calls:")
                        tools_shown = True
                    tool_info = content
                    print(f"  📦 Calling: {tool_info.get('name', 'unknown')}")
                    print(f"     Arguments: {tool_info.get('arguments', {})}")
                
                elif chunk_type == "tool_result":
                    result_str = str(content)
                    print(f"     ✓ Result: {result_str}")
                
                elif chunk_type == "content":
                    if not response_shown:
                        print("\n🤖 Assistant Response:")
                        print("  ", end="")
                        response_shown = True
                    # Stream the content character by character
                    print(content, end="", flush=True)
                
                elif chunk_type == "error":
                    print(f"\n❌ Error: {content}")
            
            print("\n")  # New line after response
            
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
        
        # Reset conversation for next test
        agent.reset_conversation()
        
        # Ask user if they want to continue
        if test != test_queries[-1]:
            cont = input("\nPress Enter to continue to next test (or 'q' to quit): ")
            if cont.lower() == 'q':
                break
    
    print("\n" + "="*60)
    print("✅ Streaming test completed!")
    print("="*60)


def compare_streaming_vs_regular():
    """Compare streaming vs regular responses"""
    print("="*60)
    print("📊 STREAMING VS REGULAR COMPARISON")
    print("="*60)
    
    # Initialize agent
    agent = ToolCallingAgent()
    
    test_query = "What's the weather in Paris and convert 20°C to Fahrenheit?"
    
    print(f"\n📋 Test Query: {test_query}")
    print("="*60)
    
    # Regular mode
    print("\n1️⃣ REGULAR MODE (No Streaming):")
    print("-"*40)
    print("⏳ Processing...")
    response = agent.chat(test_query, stream=False)
    print(f"🤖 Response: {response}")
    
    agent.reset_conversation()
    
    # Streaming mode
    print("\n2️⃣ STREAMING MODE:")
    print("-"*40)
    print("⏳ Processing (you'll see content as it arrives)...\n")
    
    for chunk in agent.chat(test_query, stream=True):
        chunk_type = chunk.get("type")
        content = chunk.get("content", "")
        
        if chunk_type == "thinking":
            # print(f"[THINKING] \033[90m{content}\033[0m") #这样子会出现一个每个字符一行 （原先代码是这个）出现了：
                    # [THINKING] n
                    # [THINKING] h
                    # [THINKING] e
                    # [THINKING] i
                    # [THINKING] t
                    # [THINKING] .
                    # [THINKING]

            print(f"\033[90m{content}\033[0m", end="", flush=True)
                # 在你的代码中，flush=True 主要用于：
                # 实现流式思考过程的实时显示
                # 确保每个字符立即显示，创造打字机效果
                # 提供更好的实时反馈体验
                # 没有 flush=True 时，内容可能会被缓存，不会立即显示
                # 使用 flush=True 时，每个字符都会立即显示
        elif chunk_type == "tool_call":
            print(f"[TOOL CALL] {content}")
        elif chunk_type == "tool_result":
            print(f"[TOOL RESULT] {content}")
        elif chunk_type == "content":
            print(content, end="", flush=True)
    
    print("\n\n" + "="*60)
    print("✅ Comparison complete!")
    print("💡 Streaming mode shows intermediate steps in real-time")
    print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test streaming functionality")
    parser.add_argument(
        "--mode",
        choices=["demo", "compare"],
        default="demo",
        help="Test mode: demo (full demo) or compare (streaming vs regular)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        test_streaming()
    else:
        compare_streaming_vs_regular()

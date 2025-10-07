##### Using in Your Code

# from main import ToolCallingAgent

# # Initialize (auto-detects best backend)
# agent = ToolCallingAgent()

# # Send a message
# response = agent.chat("What's the weather in Tokyo?")
# print(response)

# Disable tools for a query
# response = agent.chat("Tell me a joke", use_tools=False)
# print(response)

# Reset conversation
# agent.reset_conversation()



##### Adding Custom Tools
# from tools import ToolRegistry

# # Get the tool registry
# registry = ToolRegistry()

# # Define your tool function
# def my_custom_tool(param1: str, param2: int) -> str:
#     return f"Processed {param1} with {param2}"

# # Register it
# registry.register_tool(
#     name="my_custom_tool",
#     function=my_custom_tool,
#     description="My custom tool description",
#     parameters={
#         "type": "object",
#         "properties": {
#             "param1": {"type": "string", "description": "First parameter"},
#             "param2": {"type": "integer", "description": "Second parameter"}
#         },
#         "required": ["param1", "param2"]
#     }
# )
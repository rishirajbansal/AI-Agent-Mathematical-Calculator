"""
Main script to run the AI Agent
"""
import sys
from pathlib import Path
from core.agent import AIAgent
from models.schemas import Message, MessageRole


def main():
    """Main function to run the agent"""
    print("🤖 AI Agent - Built from Scratch")
    print("=" * 40)
    print("Type 'quit' or 'exit' to stop the agent")
    print("Type 'help' for available commands")
    print("=" * 40)
    
    # Initialize agent
    try:
        agent = AIAgent()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("Make sure you have set the OPENAI_API_KEY environment variable")
        return
    
    # Conversation history
    conversation_history = []
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            if user_input.lower() == 'clear':
                conversation_history.clear()
                print("🧹 Conversation history cleared!")
                continue
            
            if not user_input:
                continue
            
            # Get response from agent
            print("\n🤖 Agent: ", end="", flush=True)
            response = agent.run(user_input, conversation_history)
            print(response)
            
            # Update conversation history
            conversation_history.extend([
                Message(role=MessageRole.USER, content=user_input),
                Message(role=MessageRole.ASSISTANT, content=response)
            ])
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def show_help():
    """Show available commands and examples"""
    help_text = """
📋 Available Commands:
• quit/exit - Stop the agent
• clear - Clear conversation history
• help - Show this help message

🛠️ Available Tools:
• Calculator - Perform mathematical calculations
  Example: "Calculate 25 * 4 + sqrt(16)"
  
• File Operations - Read, write, and list files
  Example: "Write 'Hello World' to a file called greeting.txt"
  Example: "Read the contents of greeting.txt"
  Example: "List all files"

💡 Example Interactions:
• "What is 15% of 250?"
• "Calculate the area of a circle with radius 5"
• "Create a file with a list of programming languages"
• "Solve the equation: 2x + 5 = 15"
"""
    print(help_text)


if __name__ == "__main__":
    main()
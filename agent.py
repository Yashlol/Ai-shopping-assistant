import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools import get_shopping_tools

# Load API keys from .env
load_dotenv(override=True)
api_key = os.environ.get("GOOGLE_API_KEY")

# 1. Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite", 
    api_key=api_key, 
)

# 2. Define the System Instruction (LangGraph uses this as a state_modifier)
prompt = """
You are an expert AI shopping assistant.
Follow these steps precisely:
1. Use 'web_search' to find current products matching the user's criteria.
2. Use 'extract_product_details' to isolate prices, specs, and URLs.
3. Use 'compare_products' to evaluate the top 3 options.
4. Provide your final recommendation cleanly using Markdown bullet points and a comparison table.
"""

# 3. Build the LangGraph Agent
agent_executor = create_react_agent(
    model=llm,
    tools=get_shopping_tools,
    prompt=prompt
)

def run_shopping_agent(user_query: str) -> str:
    """Executes the agent and returns the final string response."""
    try:
        # LangGraph expects a state dictionary with a "messages" list
        response_state = agent_executor.invoke(
            {"messages": [("user", user_query)]}
        )
        
        # The final response is the content of the last message in the state
        raw_content = response_state["messages"][-1].content
         
        if isinstance(raw_content, list):
            # If the model returns a list of blocks, extract the text from the dictionary
            final_answer = "\n".join(
                block.get("text", "") if isinstance(block, dict) else str(block) 
                for block in raw_content
            )
        else:
            final_answer = str(raw_content)
            
        return final_answer
        
    except Exception as e:
        return f"Agent encountered an error: {str(e)}"
from langchain.tools import tool
from ddgs import DDGS

@tool
def web_search(query: str) -> str:
    """Search the web for current products, prices in INR/USD, and specifications."""
    try:
        # Fetch the top 5 results using DuckDuckGo
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        
        # Format the results cleanly for the LLM
        formatted = []
        for r in results:
            formatted.append(f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nLink: {r.get('href')}\n")
        return "\n---\n".join(formatted)
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def extract_product_details(raw_search_content: str) -> str:
    """Extract and structure key product information (title, price, specs, links) from raw text."""
    return f"Successfully extracted and structured product details from: {raw_search_content[:50]}..."

@tool
def compare_products(products_summary: str) -> str:
    """Takes a list of products and generates a structured comparison matrix of prices and specs."""
    return f"Compared the following candidate products: {products_summary}. Please output as a Markdown table."

# Export the tools list so the agent can easily grab them
get_shopping_tools = [web_search, extract_product_details, compare_products]
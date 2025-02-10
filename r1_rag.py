import requests
import json
import re
import time
import urllib.parse
from duckduckgo_search import DDGS

# Function to perform DuckDuckGo search using the duckduckgo_search library
def duckduckgo_search(query, num_results=3):
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=num_results)

        search_results = []
        for result in results:
            title = result.get('title', 'No title')
            link = result.get('href', 'No link')
            snippet = result.get('body', 'No snippet')
            search_results.append({"title": title, "link": link, "snippet": snippet})

        return search_results
    except Exception as e:
        print(f"Error fetching DuckDuckGo search results: {e}")
        return []

# Function to communicate with DeepSeek-R1 model
def query_llm(prompt):
    url = "http://localhost:5000/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"  # Replace with API key if needed
    }

    payload = {
        "model": "deepseek-reasoner",
        "messages": [{"role": "system", "content": "<think>\n"}, {"role": "user", "content": prompt}],
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 2000
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: API call failed with status code {response.status_code}")
        return None

# Extract relevant response from LLM output
def parse_llm_response(response_text):
    """Extracts CoT (<think> tags) and final answer separately."""
    start_index = response_text.find("<think>")
    end_index = response_text.find("</think>", start_index + len("<think>")) if start_index != -1 else -1

    if start_index != -1 and end_index != -1:
        cot_block = response_text[start_index + len("<think>"): end_index].strip()
        answer_part = response_text[end_index + len("</think>"):].strip()
        return cot_block, answer_part
    else:
        return "", response_text.strip()

def main():
    # 1. Get the user's input
    user_prompt = input("Enter your prompt: ")

    # **PASS 1: Generate proper search queries**
    print("\n[PASS 1] Generating search queries...\n")
    
    search_prompt = f"""
    Given the user's question below, generate **exactly 3** precise DuckDuckGo search queries that retrieve **real-time** information. 
    **Do NOT attempt to answer the question directly.** Just provide search queries.

    User Question: {user_prompt}

    Output format:
    - <search query 1>
    - <search query 2>
    - <search query 3>
    """
    
    llm_response_1 = query_llm(search_prompt)
    if not llm_response_1:
        return
    
    generated_text_1 = llm_response_1.get("choices", [{}])[0].get("message", {}).get("content", "")
    cot_block_1, search_queries = parse_llm_response(generated_text_1)

    # Extract clean search queries
    search_queries_list = [q.strip("- ").replace('"', '') for q in search_queries.split("\n") if q.strip()]
    print(f"\nIdentified search queries:\n{search_queries_list}")

    retrieved_search_results = []
    source_links = []

    # **Perform DuckDuckGo searches and extract search result summaries**
    for query in search_queries_list:
        print(f"\nSearching DuckDuckGo for: {query}...")
        search_results = duckduckgo_search(query, num_results=3)

        if search_results:
            retrieved_search_results.extend(search_results)
            source_links.extend([r["link"] for r in search_results])
        else:
            print(f"No results found for query: {query}")

    # **PASS 2: Pass retrieved search results + user query**
    print("\n[PASS 2] Processing final response...\n")

    if retrieved_search_results:
        search_results_text = "\n\n".join([f"{r['title']} - {r['link']}\nSnippet: {r['snippet']}" for r in retrieved_search_results])
        final_prompt = f"""
        Use the following **real-time** DuckDuckGo search results to **accurately answer** the user's question.

        ### Search Results:
        {search_results_text}

        ### User Query:
        {user_prompt}

        Provide a well-reasoned response based on these search results.
        """
    else:
        final_prompt = f"""
        No relevant search results were found.

        ### User Query:
        {user_prompt}

        Provide an informative answer based on prior knowledge instead.
        """

    llm_response_2 = query_llm(final_prompt)
    if not llm_response_2:
        return
    
    generated_text_2 = llm_response_2.get("choices", [{}])[0].get("message", {}).get("content", "")
    cot_block_2, final_answer = parse_llm_response(generated_text_2)

    # **Display final answer including formatted prompt**
    print("\n========================")
    print("Final Prompt Sent to LLM:")
    print("========================\n")
    print(final_prompt)

    print("\n========================")
    print("CoT Reasoning:")
    print("========================\n")
    print(cot_block_2)

    print("\n========================")
    print("Final Answer:")
    print("========================\n")
    print(final_answer)

    # **Display source links**
    if source_links:
        print("\n========================")
        print("Sources Used:")
        print("========================\n")
        for link in source_links:
            print(link)

if __name__ == "__main__":
    main()

import re
import os
import time
import datetime
import asyncio
import requests

from newsapi import NewsApiClient
from bs4 import BeautifulSoup
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from prompts.news_instruction_prompts import NEWS_API_AGENT_INSTRUCTION

MODEL = "gemini-2.0-flash"
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))


def fetch_full_article_text(url: str) -> str:
    """
    Fetches the full text content from a given URL using requests and BeautifulSoup.

    Args:
        url (str): The URL of the article to fetch.
    Returns:
        str: The extracted text content of the article, or an error message if fetching fails.
    """
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted elements (scripts, styles, ads, etc.)
        for element in soup(['script', 'style', 'footer', 'nav', 'header', 'iframe', 'aside']):
            element.decompose()

        # Extract text from relevant tags (e.g., <p>, <article>, <div>)
        article_content = soup.find('article') or soup.find('main') or soup
        paragraphs = article_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        # Combine text from paragraphs, cleaning up whitespace
        full_text = ' '.join([para.get_text(strip=True) for para in paragraphs])
        full_text = re.sub(r'\s+', ' ', full_text).strip()  # Normalize whitespace

        return full_text if full_text else "No content extracted from the article."

    except requests.RequestException as e:
        return f"Error fetching article: {str(e)}"
    except Exception as e:
        return f"Error parsing article: {str(e)}"


def news_api_tool(topic: str):
    """
    Extracts information using the News API for a given topic.
    This tool will be used to get top headlines and news information from the web articles for a given topic.

    Args:
        topic (str): The topic to search for using the News API.
    Returns:
        A list of dictionaries containing the extracted information.
    """
    res = {}
    one_month_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    top_headline_news_result = newsapi.get_top_headlines(
        q=topic,
        language="en",
        country="in",
        page_size=2
    )

    all_news_result = newsapi.get_everything(
        q=topic,
        from_param=one_month_ago,
        to=datetime.datetime.now().strftime('%Y-%m-%d'),
        language="en",
        sort_by="popularity",
        page_size=2,
    )

    def process_articles(articles):
        for article in articles:
            if article.get('url'):
                full_text = fetch_full_article_text(article['url'])
                article['content'] = full_text  # Replace or add the content field
                time.sleep(2) # Sleep to avoid hitting rate limits
        return articles

    res["top_headlines"] = process_articles(top_headline_news_result.get("articles", []))
    res["all_news"] = process_articles(all_news_result.get("articles", []))
    return res


news_agent = LlmAgent(
    name="news_agent",
    model=MODEL,
    instruction=NEWS_API_AGENT_INSTRUCTION,
    tools=[news_api_tool],
    output_key="news_api_results",
)


async def run_news_api_agent(topic: str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        session_id="news_api_agent_session_1",
        app_name="insights_extractor",
        user_id="user_eesh12345"
    )
    print(f"Session created successfully.: {session}")

    result = []
    tool_results = []
    content = types.Content(role='user', parts=[types.Part(text=topic)])
    runner = Runner(
        agent=news_agent,
        session_service=session_service,
        app_name="insights_extractor",
    )
    runner_events = runner.run_async(user_id="user_eesh12345", session_id="news_api_agent_session_1", new_message=content)
    async for event in runner_events:
        if event.content and event.content.parts:
            if event.is_final_response():
                result.append(event.content.parts[0].text)

            elif event.get_function_calls():
                for tool_call in event.get_function_calls():
                    print(f"--> Tool call: {tool_call.name} with args: {tool_call.args}")
            elif event.get_function_responses():
                for tool_response in event.get_function_responses():
                    print(f"--> Tool response: {tool_response.name} with result: {tool_response.response}")
                    tool_results.append(tool_response.response)

    return result, tool_results

if __name__ == "__main__":
    topic = "Apple wwdc 2025"
    loop = asyncio.get_event_loop()
    final_result, tool_results = loop.run_until_complete(run_news_api_agent(topic))

    print("------------------------Final Result:-------------------------------\n")
    for res in final_result:
        print(res)
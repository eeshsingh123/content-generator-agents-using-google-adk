import os
import datetime
import asyncio

from exa_py import Exa
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from prompts.exa_instruction_prompts import EXA_AGENT_INSTRUCTION

MODEL = "gemini-2.0-flash-lite"
exa = Exa(os.getenv('EXA_API_KEY'))
SEARCH_RESULTS_COUNT = 10


def exa_ai_tool(topic: str):
    """
        Extracts information using the Exa AI API for a given topic.
        This tool will be used to get information from the web for a given topic.

        Args:
            topic (str): The topic to search for using the Exa AI API.
        Returns:
            A list of dictionaries containing the extracted information. The dictionaries will include keys such as
            'title', 'url', 'publishedDate', 'text', 'author'.
        """
    combined_result = {}
    one_month_ago_as_str = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    result = exa.search_and_contents(
        topic,
        num_results=SEARCH_RESULTS_COUNT,
        start_crawl_date=one_month_ago_as_str,
        category="news"
    )

    twitter_results = exa.search_and_contents(
        topic,
        num_results=SEARCH_RESULTS_COUNT,
        include_domains=["https://x.com"],
        start_crawl_date=one_month_ago_as_str,
        category="tweet"
    )

    linkedin_results = exa.search_and_contents(
        topic,
        num_results=SEARCH_RESULTS_COUNT,
        include_domains=["https://www.linkedin.com/"],
    )

    combined_result["news"] = result.results
    combined_result["twitter"] = twitter_results.results
    combined_result["linkedin"] = linkedin_results.results
    return combined_result


exa_agent = LlmAgent(
    name="exa_agent",
    model=MODEL,
    description="An agent designed to extract web results from Exa AI API for a given topic.",
    instruction=EXA_AGENT_INSTRUCTION,
    tools=[exa_ai_tool],
    output_key="exa_results",
)


async def run_exa_agent(topic: str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        session_id="exa_agent_session_1",
        app_name="insights_extractor",
        user_id="user_eesh12345"
    )
    print(f"Session created successfully.: {session}")

    result = []
    tool_results = []
    content = types.Content(role='user', parts=[types.Part(text=topic)])
    runner = Runner(
        agent=exa_agent,
        session_service=session_service,
        app_name="insights_extractor",
    )
    runner_events = runner.run_async(user_id="user_eesh12345", session_id="exa_agent_session_1", new_message=content)
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
    topic = "apple wwdc 2025"
    loop = asyncio.get_event_loop()
    final_result, tool_results = loop.run_until_complete(run_exa_agent(topic))

    print("------------------------Final Result:-------------------------------\n")
    for res in final_result:
        print(res)
import os
import asyncio

import praw
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from prompts.reddit_instruction_prompts import REDDIT_AGENT_INSTRUCTION

MODEL = "gemini-2.0-flash"
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv('REDDIT_USER_AGENT', "google-adk-reddit-agent"),
)

print("Reddit client initialized successfully.")


def reddit_extractor_tool(topic: str, subreddits: str,  num_posts: int, num_comments: int) -> list:
    """
    Extracts information from Reddit for a given topic.
    It can be used to fetch posts title, post content, comments, and other relevant data from specified subreddits.

    Args:
        topic (str): The topic to search for on Reddit.
        subreddits (str): A string of subreddits for getting the best conversations on the given topic to search
        num_posts (int): The number of top posts to retrieve for the topic. Use any value between 5 and 10.
        num_comments (int): The number of comments to retrieve for each post. Use any value between 10 and 20.
    Returns:
        A list of dictionaries containing the extracted information. The dictionaries will include keys such as
        'title', 'text', 'score', 'subreddit', 'comments'.
        If no relevant posts are found, it returns a list with an "error" key and message.
    """
    subreddit = reddit.subreddit(subreddits)

    search_results = subreddit.search(
        topic, sort='hot', time_filter='month', limit=num_posts
    )

    insights = []
    # Process each post
    for submission in search_results:
        post_data = {
            'title': submission.title,
            'text': submission.selftext if submission.selftext else "[No text content]",
            'score': submission.score,
            'subreddit': submission.subreddit.display_name,
            'source': f"https://reddit.com{submission.permalink}",
            'comments': []
        }
        submission.comments.replace_more(limit=0)
        top_comments = sorted(
            submission.comments, key=lambda c: c.score, reverse=True
        )[:num_comments]

        # Collect comment data
        for comment in top_comments:
            post_data['comments'].append({
                'body': comment.body,
                'score': comment.score
            })

        insights.append(post_data)

    if not insights:
        return [{"error": "No relevant posts found for the given topic, or Reddit API error"}]

    return insights


reddit_agent = LlmAgent(
    name="reddit_agent",
    model=MODEL,
    description="""This agent is designed to interact with Reddit, explore subreddits, and provide insights
     for a given topic.""",
    instruction=REDDIT_AGENT_INSTRUCTION,
    tools=[reddit_extractor_tool],
    output_key="reddit_results",
)

print("Reddit agent initialized successfully.")


async def run_reddit_agent(topic: str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        session_id="reddit_agent_session_1",
        app_name="insights_extractor",
        user_id="user_eesh12345"
    )
    print(f"Session created successfully.: {session}")

    result = []
    tool_results = []
    content = types.Content(role='user', parts=[types.Part(text=topic)])
    runner = Runner(
        agent=reddit_agent,
        session_service=session_service,
        app_name="insights_extractor",
    )
    runner_events = runner.run_async(user_id="user_eesh12345", session_id="reddit_agent_session_1", new_message=content)
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
    final_result, tool_results = loop.run_until_complete(run_reddit_agent(topic))

    print("------------------------Final Result:-------------------------------\n")
    for res in final_result:
        print(res)
import asyncio

from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.report_generator_agents import combiner_agent
from eda_agents import eda_agent, trend_spotter_agent, network_and_relationship_agent
from exa_agent import exa_agent
from reddit_agent import reddit_agent
from news_agent import news_agent
from report_generator_agents import (report_generator_agent, reddit_post_generator_agent,
                                     blog_post_generator_agent, twitter_thread_generator_agent,
                                     linkedin_post_generator_agent)


class AnalysisWorkflow:
    def __init__(self, topic: str):
        self.topic = topic
        self.app_name = "AnalysisWorkflow"
        self.user_id = "TestUser1234"
        self.temp_session_id = "temp_workflow_session_1234"
        self.session_service = InMemorySessionService()

    async def create_runner_and_input(self, agent, topic):
        # create a session temporarily for the workflow
        session = await self.session_service.create_session(
            session_id=self.temp_session_id,
            app_name=self.app_name,
            user_id=self.user_id,
        )
        print(f"Session created successfully: {session}")

        # define the runner
        runner = Runner(
            agent=agent,
            session_service=self.session_service,
            app_name=self.app_name
        )
        # create the input content
        topic = f"Analyze the topic: {topic}"  # can also be a part of the state but keeping it simple here
        content = types.Content(role='user', parts=[types.Part(text=topic)])
        return runner, content

    async def run(self, topic: str):
        result = []
        # Step 1: Collect information from various sources in parallel
        information_gathering_agents = ParallelAgent(
            name="InformationGatheringAgents",
            sub_agents=[exa_agent, reddit_agent, news_agent],
            description="Runs in parallel and gathers information from various sources about the topic.",
        )

        # Step 2: Generate analysis with sequential agents
        analysis_pipeline_agents = SequentialAgent(
            name="AnalysisPipeline",
            sub_agents=[
                information_gathering_agents,
                eda_agent,
                trend_spotter_agent,
                network_and_relationship_agent
            ],
            description="Runs sequentially to analyze the topic and gather insights based on the information collected."
        )

        # Step 3: Generate a comprehensive report and visualizations
        result_creator_agents = SequentialAgent(
            name="ReportGeneratorAgents",
            sub_agents=[
                analysis_pipeline_agents, report_generator_agent,
                blog_post_generator_agent, twitter_thread_generator_agent,
                linkedin_post_generator_agent, reddit_post_generator_agent
            ],
            description="Generates a comprehensive report based on the analysis results."
        )

        # Step 4: Create a root agent that combines all the above agents
        root_agent = SequentialAgent(
            name="RootAnalysisAgent",
            sub_agents=[result_creator_agents, combiner_agent],
            description="Combines all agents to run the complete analysis workflow based on the output schema."
        )

        runner, content = await self.create_runner_and_input(root_agent, topic)
        runner_events = runner.run_async(
            user_id=self.user_id,
            session_id=self.temp_session_id,
            new_message=content
        )

        async for event in runner_events:
            if event.content and event.content.parts:
                if event.is_final_response():
                    result.append(event.content.parts[0].text.strip())
                    print(f"Final Response: {event.content.parts[0].text}")

                if event.get_function_calls():
                    for tool_call in event.get_function_calls():
                        print(f"--> Tool call: {tool_call.name} with args: {tool_call.args}")
                elif event.get_function_responses():
                    for tool_response in event.get_function_responses():
                        print(f"--> Tool response: {tool_response.name} with result: {tool_response.response}")

        return result[-1]


if __name__ == "__main__":
    input_topic = "Vijay Mallya podcast"
    workflow = AnalysisWorkflow(input_topic)

    loop = asyncio.get_event_loop()
    final_result = loop.run_until_complete(workflow.run(input_topic))

    print("------------------------Final Result:-------------------------------\n")
    print(final_result)

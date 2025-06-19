import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import streamlit as st

from google.adk.agents import ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.eda_agents import eda_agent, trend_spotter_agent, network_and_relationship_agent
from agents.exa_agent import exa_agent
from agents.reddit_agent import reddit_agent
from agents.news_agent import news_agent
from agents.report_generator_agents import (report_generator_agent,
                                            blog_post_generator_agent, twitter_thread_generator_agent,
                                            linkedin_post_generator_agent)

from agents.report_generator_agents import combiner_agent


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

    async def run(self, topic: str, tool_calls_placeholder=None):
        result = []
        tool_calls = []

        # Agent configuration remains the same...
        information_gathering_agents = ParallelAgent(
            name="InformationGatheringAgents",
            sub_agents=[exa_agent, reddit_agent, news_agent],
            description="Runs in parallel and gathers information from various sources about the topic.",
        )

        analysis_pipeline_agents = SequentialAgent(
            name="AnalysisPipeline",
            sub_agents=[
                eda_agent,
                trend_spotter_agent,
                network_and_relationship_agent
            ],
            description="Runs sequentially to analyze the topic and gather insights."
        )

        result_creator_agents = ParallelAgent(
            name="ReportGeneratorAgents",
            sub_agents=[
                report_generator_agent, blog_post_generator_agent, twitter_thread_generator_agent,
                linkedin_post_generator_agent
            ],
            description="Generates a comprehensive report based on the analysis results."
        )

        root_agent = SequentialAgent(
            name="RootAnalysisAgent",
            sub_agents=[
                information_gathering_agents,
                analysis_pipeline_agents,
                result_creator_agents,
                combiner_agent
            ],
            description="Combines all agents to run the complete analysis workflow."
        )

        runner, content = await self.create_runner_and_input(root_agent, topic)
        runner_events = runner.run_async(
            user_id=self.user_id,
            session_id=self.temp_session_id,
            new_message=content
        )

        tooL_name_map = {
            "exa_ai_tool": "Exa AI",
            "reddit_extractor_tool": "Reddit",
            "news_api_tool": "News API",
        }

        with st.spinner("Processing analysis workflow..."):
            counter = 1
            async for event in runner_events:
                if event.content and event.content.parts:
                    if event.is_final_response():
                        tool_text = f"✅ {counter} Intermediate result processed"
                        tool_calls.append(tool_text)
                        if tool_calls_placeholder:
                            tool_calls_placeholder.markdown("## 🤖 Analysis Progress\n" + "\n\n".join(tool_calls))
                        result.append(event.content.parts[0].text.strip())
                        counter += 1

                    if event.get_function_calls():
                        for tool_call in event.get_function_calls():
                            tool_text = f"🔍 **Searching** `{tooL_name_map.get(tool_call.name, tool_call.name)}`..."
                            tool_calls.append(tool_text)
                            if tool_calls_placeholder:
                                tool_calls_placeholder.markdown("## 🤖 Analysis Progress\n" + "\n\n".join(tool_calls))
                    elif event.get_function_responses():
                        for tool_response in event.get_function_responses():
                            if tool_response.name == "image_generator_tool":
                                image_dir = "generated_images"
                                if os.path.exists(image_dir):
                                    # Get latest generated image
                                    latest_image = max(
                                        [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))],
                                        key=lambda x: os.path.getctime(os.path.join(image_dir, x)))
                                    image_path = os.path.join(image_dir, latest_image)
                                    tool_calls.append(f"🖼️ Generated visualization: `{latest_image}`")

                                    if tool_calls_placeholder:
                                        tool_calls_placeholder.markdown(
                                            "## 🤖 Analysis Progress\n" + "\n\n".join(tool_calls))

                                        # Create/update image grid
                                        if 'generated_images' not in st.session_state:
                                            st.session_state.generated_images = []
                                        st.session_state.generated_images.append(image_path)

                                        # Display images in a 4-column grid
                                        image_placeholder = st.empty()
                                        with image_placeholder.container():
                                            for i in range(0, len(st.session_state.generated_images), 4):
                                                cols = st.columns(4)
                                                for j in range(4):
                                                    if i + j < len(st.session_state.generated_images):
                                                        with cols[j]:
                                                            st.image(st.session_state.generated_images[i + j],
                                                                     use_column_width=True,
                                                                     caption=f"Visual {i + j + 1}")
                            else:
                                sources_found = 0
                                if type(tool_response.response) is list:
                                    sources_found = len(tool_response.response)
                                elif type(tool_response.response) is dict:
                                    sources_found += sum([len(v) for v in tool_response.response.values()])

                                tool_text = f"✨ Found **{sources_found}** sources from `{tooL_name_map.get(tool_response.name, tool_response.name)}`"
                                tool_calls.append(tool_text)
                                if tool_calls_placeholder:
                                    tool_calls_placeholder.markdown(
                                        "## 🤖 Analysis Progress\n" + "\n\n".join(tool_calls))


        return result[-1]


def main():
    st.set_page_config(
        page_title="AI Research & Content Hub",
        page_icon="🎯",
        layout="wide"
    )

    st.title("🤖 AI Research & Social Media Content Generator")
    st.markdown("### Your All-in-One Research Assistant & Content Creation Engine using Google's Agent Development Kit (ADK)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🔍 Research Capabilities:
        - 🌐 Multi-source information gathering
        - 📊 Advanced trend analysis
        - 🔗 Key relationship mapping
        - 📈 Pattern recognition
        """)

    with col2:
        st.markdown("""
        #### 📱 Auto-Generated Content For:
        - 🔵 LinkedIn - Professional insights
        - 🐦 Twitter - Viral thread creation
        - 📝 Blog Posts - Detailed articles
        """)

    with st.expander("✨ Example Topics & Content Ideas"):
        st.markdown("""
        1. **Tech Industry Updates**
           - Google I/O 2025
           - Apple WWDC 2025
           - YC Summer 2025 Batch

        2. **Gaming & Entertainment**
           - Doom: The Dark Ages
           - Future of VR Gaming

        3. **Innovation & Research**
           - AI Agent Breakthroughs
           - MCP and its challenges
        """)

    topic = st.text_input(
        "🎯 Enter your research topic:",
        placeholder="e.g., Google I/O 2025",
        help="Enter any topic to get comprehensive research and auto-generated social media content"
    )

    if st.button("Analyze"):
        st.info("Analysis started... Please wait.")

        # Create placeholders for progress updates
        tool_calls_placeholder = st.empty()

        workflow = AnalysisWorkflow(topic)

        # Run the async workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            final_result = loop.run_until_complete(
                workflow.run(
                    topic,
                    tool_calls_placeholder,
                )
            )
            # Display the actual final result
            st.markdown("## Final Answer")
            st.markdown(final_result)
        finally:
            loop.close()


if __name__ == "__main__":
    main()

from google.adk.agents import LlmAgent

from prompts.eda_prompts import eda_prompt, trend_spotting_prompt, network_and_relationship_prompt


SUPERIOR_MODEL = "gemini-2.0-flash"

eda_agent = LlmAgent(
    name="exploratory_data_analysis_agent",
    model=SUPERIOR_MODEL,
    instruction=eda_prompt,
    description="An agent designed to perform exploratory data analysis (EDA) on a given dataset.",
    output_key="eda_results",
)

trend_spotter_agent = LlmAgent(
    name="trend_spotter_agent",
    model=SUPERIOR_MODEL,
    instruction=trend_spotting_prompt,
    description="An agent designed to identify trends and patterns in data from multiple sources.",
    output_key="trend_spotter_results",
)

network_and_relationship_agent = LlmAgent(
    name="network_and_relationship_agent",
    model=SUPERIOR_MODEL,
    instruction=network_and_relationship_prompt,
    description="An agent designed to analyze relationships and networks within data.",
    output_key="network_and_relationship_results",
)
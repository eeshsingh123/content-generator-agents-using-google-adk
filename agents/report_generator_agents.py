import os
import datetime
from PIL import Image

from google import genai
from google.genai import types
from io import BytesIO

from google.adk.agents import LlmAgent

from prompts.report_generator_prompts import (report_generator_prompt,
                                              combiner_agent_prompt, blog_post_generator_prompt,
                                              twitter_thread_generator_prompt, linkedin_post_generator_prompt,
                                              reddit_post_generator_prompt)

MODEL = "gemini-2.0-flash"


# Tools
def image_generator_tool(prompt: str):
    """
    Generates an image based on the provided prompt using the image generation API.
    Args:
        prompt (str): The description of the image to be generated.
    Returns:
        dict: {"text": str, "image": bytes} that contains the generated image and any accompanying text.
    """
    image_res = {}
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            image_res["text"] = part.text
        elif part.inline_data is not None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            root_dir_path = "C:\\Projects\\GoogleADKHackathon\\generated_images"
            image_path = f'{root_dir_path}\\image_{timestamp}_{prompt[:50]}.png'

            Image.open(BytesIO(part.inline_data.data)).save(image_path)
            image_res["image_path"] = image_path
    return image_res


# Agents
report_generator_agent = LlmAgent(
    name="report_generator_agent",
    model=MODEL,
    instruction=report_generator_prompt,
    description="An agent designed to generate comprehensive reports based on data analysis and insights.",
    output_key="generated_report",
)

blog_post_generator_agent = LlmAgent(
    name="blog_post_generator_agent",
    model=MODEL,
    instruction=blog_post_generator_prompt,
    description="An agent designed to generate a blog post summarizing the key findings from the report.",
    output_key="blog_post",
    tools=[image_generator_tool]
)

twitter_thread_generator_agent = LlmAgent(
    name="twitter_thread_generator_agent",
    model=MODEL,
    instruction=twitter_thread_generator_prompt,
    description="An agent designed to generate a Twitter thread summarizing the key findings from the report.",
    tools=[image_generator_tool],
    output_key="twitter_thread",
)

linkedin_post_generator_agent = LlmAgent(
    name="linkedin_post_generator_agent",
    model=MODEL,
    instruction=linkedin_post_generator_prompt,
    description="An agent designed to generate a LinkedIn post summarizing the key findings from the report.",
    tools=[image_generator_tool],
    output_key="linkedin_post",
)

reddit_post_generator_agent = LlmAgent(
    name="reddit_post_generator_agent",
    model=MODEL,
    instruction=reddit_post_generator_prompt,
    description="An agent designed to generate a Reddit post summarizing the key findings from the report.",
    tools=[image_generator_tool],
    output_key="reddit_post",
)

combiner_agent = LlmAgent(
    name="combiner_agent",
    model=MODEL,
    instruction=combiner_agent_prompt,
    description="An agent designed to combine various content formats into a comprehensive report.",
)

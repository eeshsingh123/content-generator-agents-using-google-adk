report_generator_prompt = """
Create a professional trend analysis report that transforms analytical insights into strategic intelligence.

## REPORT STRUCTURE (1500-2000 words)

### Executive Summary
Comprehensive overview of key findings and strategic implications

### Current Landscape Analysis  
Present state analysis with supporting data and metrics

### Emerging Trends & Patterns
Data-driven trend identification with quantified insights

### Impact Assessment
Stakeholder and market implications of identified trends

### Future Outlook & Recommendations
Evidence-based predictions and actionable strategic guidance

## ANALYTICAL DATA SOURCES

**Primary Computed Analysis:**
- **Data Insights**: {eda_results}
- **Trend Analysis**: {trend_spotter_results} 
- **Network Patterns**: {network_and_relationship_results}

**Supporting Evidence:**
- **Reddit Discussions**: {reddit_results}
- **Web Research**: {exa_results}
- **News Coverage**: {news_api_results}

## CONTENT REQUIREMENTS

**Data-Driven Approach:**
- Lead with quantified findings (percentages, growth rates, statistical significance)
- Support all claims with specific data points from computed analysis
- Highlight cross-source patterns and correlations
- Include relevant tables/charts when data supports visualization

**Professional Standards:**
- Executive-level language and presentation
- **Bold** key metrics and critical findings
- *Italicize* important nuances and implications
- Use markdown formatting for clear structure

**Citation Format:**
- Reference original sources with URLs: [Finding] (Source: Description)
- Source mapping: Reddit → "Reddit", Exa → "Web Research", News → "News Coverage"
- Do NOT cite computed analysis as sources - only original data

## ANALYSIS FOCUS

Transform your computed insights into strategic narrative by:
- Explaining significance of data patterns found in EDA results
- Contextualizing trend directions and momentum from trend analysis
- Interpreting network relationships and their implications
- Connecting findings to broader market/industry context
- Identifying actionable opportunities and risks

Include a comprehensive References section with all original source URLs organized by type.
"""

blog_post_generator_prompt = """
You are an expert content writer creating an SEO-optimized blog post. Write in a natural, human tone that engages readers.

## CONTENT REQUIREMENTS
- **Length**: 800-1200 words
- **Tone**: Professional yet conversational, avoid AI-generated language patterns
- **SEO**: Include relevant keywords naturally throughout the content
- **Structure**: Use clear H2/H3 subheadings for scannability

## POST STRUCTURE
1. **Compelling Headline**: Include primary keyword, create curiosity
2. **Hook Introduction**: Start with a surprising statistic or thought-provoking question
3. **Main Content**: 3-4 sections with actionable insights from the data
4. **Key Takeaways**: Bulleted list of main points
5. **Strong CTA**: Encourage engagement (comments, shares, newsletter signup)

## IMAGE GENERATION
Use the `image_generator_tool` ONCE to create a featured image. Keep the prompt simple and thematic (e.g., "modern data visualization dashboard" or "business trends infographic").

## DATA SOURCES
Transform these insights into engaging content:
- **Analysis Results**: {eda_results}
- **Trend Insights**: {trend_spotter_results}
- **Relationship Data**: {network_and_relationship_results}

Focus on the most compelling findings that provide value to your audience.
"""

twitter_thread_generator_prompt = """
Create a viral Twitter thread (5-8 tweets) with authentic, engaging content. Write like a human, not a bot.

## STYLE GUIDELINES
- **Tone**: Conversational, slightly edgy, use humor when appropriate
- **No emojis**: Keep it clean and text-focused
- **Hook**: Start with a compelling statistic, controversial take, or surprising insight
- **Format**: Use "1/🧵" for thread indicator

## THREAD STRUCTURE
1. **Hook Tweet**: Grab attention with data-driven insight or bold statement
2. **Context Tweets**: 3-5 tweets expanding on the main points
3. **Closing Tweet**: Strong CTA asking for engagement (retweets, thoughts, follows)

## CONTENT FOCUS
Extract the most interesting/surprising findings from:
- **Key Insights**: {eda_results}
- **Trending Patterns**: {trend_spotter_results}
- **Connections**: {network_and_relationship_results}

## IMAGE GENERATION
Use `image_generator_tool` ONCE for a simple, thread-relevant visual (e.g., "data trends chart" or "social media analytics").

## SENSITIVITY NOTE
If dealing with controversial topics, maintain respectful tone while keeping engagement high.

Output format: [Tweet 1/n], [Tweet 2/n], etc.
"""

linkedin_post_generator_prompt = """
Create a professional LinkedIn post that drives engagement and showcases thought leadership.

## CONTENT STRATEGY
- **Length**: 150-300 words (LinkedIn sweet spot)
- **Tone**: Professional but approachable, avoid corporate jargon
- **Value**: Share actionable insights, not just observations
- **Engagement**: End with a question to spark discussion

## POST STRUCTURE
1. **Hook**: Start with a bold statement, question, or surprising statistic
2. **Context**: Brief setup explaining why this matters
3. **Key Insights**: 3-4 bullet points with specific findings
4. **So What**: Explain the implications for professionals
5. **CTA**: Ask a thoughtful question to encourage comments

## FORMATTING
- Use line breaks for readability
- **Bold** key statistics and important findings
- Include 3-5 strategic bullet points
- Add relevant hashtags (3-5 max)

## DATA TO LEVERAGE
Focus on professional/business implications from:
- **Analysis Results**: {eda_results}
- **Market Trends**: {trend_spotter_results}
- **Industry Connections**: {network_and_relationship_results}

Transform data into career/business insights that professionals can act on.
"""


combiner_agent_prompt = """
Combine the provided content into a single, clean markdown document. Output ONLY the final markdown content without any code block wrapping or markdown tags.

**CONTENT TO COMBINE**
- **Research Report**: {generated_report}
- **Blog Post**: {blog_post}
- **Twitter Thread**: {twitter_thread}
- **LinkedIn Post**: {linkedin_post}

**OUTPUT FORMAT**
### 1. Executive Summary
Brief overview of the main findings and content package

### 2. Full Research Report
[Research Report content here]

### 3. Content Adaptations
#### Blog Post
[Blog content here] as a Markdown document no backticks

#### Social Media Content
**Twitter Thread:**
[Twitter content here]

**LinkedIn Post:**
[LinkedIn content here]

## CRITICAL INSTRUCTIONS
- Output clean markdown text ONLY
- Do NOT wrap output in ```markdown``` tags or any code blocks
- Do NOT add backticks around content sections
- Maintain all original formatting within each section
- Use proper markdown headers (##, ###) for structure
- Ensure clean line breaks between sections
"""
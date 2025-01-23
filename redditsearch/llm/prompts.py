system_prompt = \
"""
You are a reddit post summarization agent, with the objective of providing a well-rounded yet informative summary to the user
"""

post_summarize_prompt_tmpl = \
"""
You have been provided with the entire text of a reddit post under <<<<REDDIT POST>>>>.
This reddit post was retrieved when a user made the following google query: {query}
In the query, the user is seeking solutions to a problem they have or wants to get advice to make the best decision.
Given the context of the query, summarize the advice and solutions that people are saying in the thread.
OUTPUT THE SUMMARY BETWEEN <<<<SUMMARY>>>> and <<<</SUMMARY>>>>

After outputting the summary, output a python list of key words that can be verbs or nouns, which are solutions to the problem or advice provided in the thread.
For example, if the user has queried "Migraine relief", the list would be something like ["exedrin", "Magnesium Glycinate", "ibuprofen", "earplugs", "stretching", ...].
As another example, if the user has queried "Europe trip planning", the list would be something like ["Italy", "Budapest", "Barcelona", "Netherlands", ...]
YOU MUST ONLY USE WORDS THAT EXIST IN THE TEXT AS THEY ARE. OUTPUT THE LIST OF WORDS BETWEEN <KEYWORDS> and </KEYWORDS>

Follow the following chain of thought:
1. Identify the solutions or suggestions that are central to the discussion 
2. Determine the consensus about these solutions or suggestions. Is it good, or is it bad?
3. Identify unique solutions or suggestions that are not an integral part of the discussion, but could be worth trying out or exploring.
4. Provide a medium-length summary of the discussion, including the pros and cons of some of the discussed solutions or suggestions.
5. Output the key word list including the discussed solutions and suggestions.

Below are examples of the output that is expected:

{example_output}

Below is the reddit post for you to summarize:
<<<<REDDIT POST>>>>

{reddit_post}
"""

summary_summarize_prompt_tmpl = \
"""
You have been provided with a list of reddit post summaries under <<<<REDDIT POST SUMMARIES>>>>
These reddit posts were retrieved when a user made the following google query: {query}
In the query, the user is seeking solutions to a problem they have or wants to get advice to make the best decision.
Please create a very concise overarching summary of all the post summaries IN A FEW TINY PARAGRAPHS of similar length to the example below (not bullet points)
OUTPUT THE SUMMARY BETWEEN the tags <SUMMARY> and </SUMMARY>.

Follow the following chain of thought when thinking about the summary:
1. Which solutions or suggestions frequently come up in the discussion?
2. Do people have good or bad opinions about these solutions or suggestions?
3. Are there any unique solutions or suggestions that could be worth trying out or exploring?
4. How can I best summarize all all the info in a way that is wholistic yet concise?

Below are examples of the output that is expected:
{example_output}

Below are the summaries of the reddit posts for you to summarize:
<<<<REDDIT POST SUMMARIES>>>>

{reddit_post_summaries}
"""
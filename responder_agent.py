from datetime import datetime
import random
import dotenv
import os
import logging
from functools import lru_cache, partial
import requests
import json
from pydantic import Field
import praw

from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.core import Settings
# Import and initialize our tool spec
from llama_index.readers.wikipedia import WikipediaReader


dotenv.load_dotenv()

OLLAMA_MODEL='mistral'
OLLAMA_TIMEOUT=3000.00
OLLAMA_TEMP=0.0
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL")


fileHandler = logging.FileHandler("responder_agent.log")
responder_logger = logging.getLogger(__name__)
responder_logger.addHandler(fileHandler)
responder_logger.setLevel(logging.INFO)

def generate_answers(input: str = Field(description="A question posted in the r/explainitlikeimfive subreddit formatted like: <title> <question>"), llm=Ollama(model=OLLAMA_MODEL, request_timeout=OLLAMA_TIMEOUT, temperature=OLLAMA_TEMP, base_url=OLLAMA_BASE_URL), num_answers: int = 4):
    current_datetime = datetime.now()
    responder_logger.info(f"{current_datetime} Generating answers for: {input}")
    prompt = f"""Purpose: Generate {num_answers} answers to the question in the tone given in the examples.
    Example:
    Question: ELI5: How did American soldiers use napalm without harming themselves? I know napalm usage was quite common in wartime between WW2 and Vietnam, and I'm also very aware of just how damaging the substance was to the people affected. Internal damage, skin essentially melting, burning underwater (cue Phil Swift), etc. My question is, how were soldiers able to, for lack of a better word, safely use napalm without harming themselves as well as their targets?
    Answer 1: 
    You ever see one of those little cans with the pink gel in them that you light to keep a serving tray warm?

    Thats napalm and its fairly harmless until given oxygen and heated above its ingition point.
    Answer 2:
    Napalm was powerful but I think the main culprit of chemicals they were exposed to that left lasting health damage was Agent Orange. My grandfather had a grapefruit sized tumor in his lung when he died on the operating table from the surgeon accidently cutting an artery. That wasn't his only health problem, either. He started to hunch over with arthritis in his neck and spine to the point it affected his height, and it didn't look like normal aging stuff anyway. He was maybe in his 50s but his health was like 20-30 years older seeming. I don't know more details because he died before I was born but his health spiraled from exposure to that stuff.
    Answer 3:
    napalm was generally dropped from planes.   It would harm friendly targets if it was dropped on them.  
    Answer 4:
    Basically the pilots would come down low, sometimes withing a few hundred feet. They would drop as close as possible usually withing 300 meters of the frontline. Many times they would fly over the spot to get a bearing and then fly the second pass where they would drop the ordnance. The pilots where well trained and determined to save their comrades
    Question: """
    response =  llm.complete(prompt+input)
    current_datetime = datetime.now()
    responder_logger.info(f"{current_datetime} Answers: {response}")
    return response

def get_top_k_wiki_pages(input: str = Field(description="A topic to search for on Wikipedia"), k: int = 5):
    current_datetime = datetime.now()
    responder_logger.info(f"{current_datetime} Searching Wikipedia for: {input}")
    url = f"https://api.wikimedia.org/core/v1/wikipedia/en/search/page?q={input}&limit={k}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        titles = []
        for page in data["pages"]:
            titles.append(page["title"])
        current_datetime = datetime.now()
        responder_logger.info(f"{current_datetime} Wikipedia pages found: {titles}")
        return titles
    else:
        return None
@lru_cache
def retrieve_wikipedia(input: str = Field(description="A topic to search for on Wikipedia")):
    top_k_pages = get_top_k_wiki_pages(input, k=5)
    responder_logger.info(f"Top 5 Wikipedia Pages: {top_k_pages}")
    if top_k_pages is None:
        return "No wikipedia pages found for the given input."
    reader = WikipediaReader()
    # Load data from Wikipedia
    documents = reader.load_data(pages=top_k_pages)
    # build a vectorstore index and query tool
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    query_engine=index.as_query_engine(llm=Ollama(model=OLLAMA_MODEL, request_timeout=OLLAMA_TIMEOUT, temperature=OLLAMA_TEMP, base_url=OLLAMA_BASE_URL), verbose=True)
    # retrieve a summary of the top 5 wikipedia pages
    summary = query_engine.chat("summarize the documents")
    current_datetime = datetime.now()
    responder_logger.info(f"{current_datetime} Wikipedia Summary: {summary}")
    return summary

def build_agent():
    current_datetime = datetime.now()
    responder_logger.info(f"{current_datetime} Building Responder Agent")
    llm = Ollama(
        model=OLLAMA_MODEL,
        request_timeout=OLLAMA_TIMEOUT,
        temperature=OLLAMA_TEMP,
        base_url=OLLAMA_BASE_URL
    )

    tools = [
        FunctionTool(
            partial(generate_answers, num_answers=4, llm=llm), ToolMetadata(
            name="response_generator",
            description="Generates responses to a question.",
        )
        ),
        # FunctionTool(
        #     retrieve_wikipedia, ToolMetadata(
        #         name="retrieve_wikipedia",
        #         description="Retrieves a summary of the top 5 wikipedia pages for a given input. only use if you cannot answer the question using the other tools",
        #     )
        # )
    ]

    agent = ReActAgent.from_tools(tools, llm=llm, context="""You are to craft a clear concise and factual answer to a question posted in the r/explainitlikeimfive subreddit. Example: Question: ELI5: How did American soldiers use napalm without harming themselves?  Answer: The soldiers used napalm by dropping it from planes. They would fly low to the ground and drop the napalm as close as possible to the frontline. The pilots were well trained and determined to save their comrades.""", max_iterations=100)

    return agent
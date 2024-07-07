from datetime import datetime
import random
import dotenv
import os
import logging
from functools import partial
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


dotenv.load_dotenv("./.env")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL")
OLLAMA_TIMEOUT=3000.00
OLLAMA_TEMP=0.0
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL")

fileHandler = logging.FileHandler("evaluator_agent.log")
evaluator_logger = logging.getLogger(__name__)
evaluator_logger.addHandler(fileHandler)
evaluator_logger.setLevel(logging.INFO)

def evaluate_answer(input: str = Field(description="A question-answer pair formatted: Question: <question> Answer: <answer>"), llm=Ollama(model=OLLAMA_MODEL, request_timeout=OLLAMA_TIMEOUT, temperature=OLLAMA_TEMP, base_url=OLLAMA_BASE_URL)):
    current_datetime = datetime.now()
    evaluator_logger.info(f"{current_datetime} Evaluating: {input}")
    prompt = f"""Purpose: Evaluate the quality of the answer given the question on a scale of 1-10 and explain your reasoning. {input}"""
    response =  llm.complete(prompt)
    current_datetime = datetime.now()
    evaluator_logger.info(f"{current_datetime} Evaluation: {response}")
    return response

def build_agent():
    current_datetime = datetime.now()
    evaluator_logger.info(f"{current_datetime} Building Evaluator Agent")
    llm=Ollama(model=OLLAMA_MODEL, request_timeout=OLLAMA_TIMEOUT, temperature=OLLAMA_TEMP, base_url=OLLAMA_BASE_URL)

    tool = FunctionTool(partial(evaluate_answer, llm=llm), ToolMetadata(name="evaluate_answer",
        description="Evaluate the quality of the answer given the question on a scale of 1-10 and explain your reasoning.",)
    )

    agent = ReActAgent.from_tools([tool], llm=llm, context="""Respond to the question, answer, and evaluation in typical reddit comment fashion.""", max_iterations=100)

    return agent

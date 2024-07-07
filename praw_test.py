import random
import dotenv
import os
import logging
from functools import partial
import requests
import json
from pydantic import Field
import praw

from responder_agent import build_agent as responder_agent
from evaluator_agent import build_agent as evaluator_agent


dotenv.load_dotenv()

fileHandler = logging.FileHandler("praw_test.log")
logger = logging.getLogger()
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)


client_secret = os.getenv("REDDIT_CLIENT_SECRET")
client_id = os.getenv("REDDIT_CLIENT_ID")
user_name = os.getenv("REDDIT_USERNAME")
password = os.getenv("REDDIT_PASSWORD")
code = os.getenv("REDDIT_CODE")
reddit = praw.Reddit(
    username=user_name,
    password=password,
    client_id=client_id,
    client_secret=client_secret,
    user_agent="An LLM that responds to ELI5 posts",
    redirect_uri="http://localhost:8999",
)

print(reddit.user.me())


ELI5Submissions = reddit.subreddit("explainlikeimfive").hot(limit=5)

print("ELI5 Subreddit Comments")


# make a tool that generates ten answers to a question
# and then pass it to the agent

responder = responder_agent()
evaluator = evaluator_agent()
skip=False
for submission in ELI5Submissions:
    if not submission.stickied:
        if skip:
            skip = False
            continue
        print(submission.title)
        print(submission.selftext)
        question =  submission.title + submission.selftext.replace("\n", " ")
        answer = responder.chat(question)
        print(answer)
        # reply to the submission
        comment = submission.reply(answer)
        evaluation = evaluator.chat(f"Question: {question} Answer: {answer}")
        print(evaluation)
        # reply to the comment
        comment.reply(evaluation)

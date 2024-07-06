# ELI5 LLM Agent

This project leverages the amazing tools that are coming out in the large language model space to engage the community on the r/explainitlikeimfive subreddit. 

 - I use PRAW to read posts and comment the agent's response
 - I use LlamaIndex and Ollama to power the LLM agent (surprisingly easy!)

## Installation

### Prerequisites

 - Python 3 (I use 3.10, but I think most versions will do)
 - [Ollama](https://ollama.com/download)

### Steps

 1. Clone the repository
    
    `git clone https://github.com/Steffanic/ELI5Bot/`
 
 2. Create a virtualenv

    `python3 -m venv ELI5`

 3. Activate the environment

    `source ELI5/bin/activate`
    
 5. Install the requirements

    `pip install -r requirements.txt`

 6. Install and serve Ollama

    `curl -fsSL https://ollama.com/install.sh | sh`

 7. Make a reddit app

    ``

### Usage

Running praw_test.py will retrieve the most recent "hot" posts on r/explainitlikeimfive and generate a response to the question.
    

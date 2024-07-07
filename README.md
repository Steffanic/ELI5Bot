# ELI5 LLM Agent

This project leverages the amazing tools that are coming out in the large language model space to engage the community on the r/explainitlikeimfive subreddit. 

 - I use PRAW to read posts and comment the agent's response
 - I use LlamaIndex and Ollama to power the LLM agent (surprisingly easy!)

 Check out the [notebook](ELI5LLM.ipynb) to get started right away! I recommend opening it up in colab, there is a link when you open the notebook in github. I cannot guarantee that the dependencies pre-loaded in colab are present in my requirements.txt file.

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
    
 4. Install the requirements

    `pip install -r requirements.txt`

    Note: There are a few extra requirements in the requirements.txt file that are not strictly necessary. I will clean this up in the future but you should really look through it yourself. If you want to use other LLMs or embedding solutions you will need to install the appropriate packages.

 5. Install and serve Ollama

    `curl -fsSL https://ollama.com/install.sh | sh`

 6. Make a reddit app

    It seems like there are two methods for making an app on reddit. The ['old' way](https://old.reddit.com/prefs/apps/) that I used. Just create a new personal use script, pick any redirect uri(I used http://localhost:8999), and get the client_id below the words "personal use script" and client_secret called "secret". The ['new' way](https://developers.reddit.com/my/apps), which I did not use, seems to entail creating a TypeScript app that interfaces with reddit's API. I recommend the old way because it interfaces seamlessly with praw.

 7. Create a .env file in the root directory of the project with the following variables:

   ```
   REDDIT_CLIENT_SECRET=<'secret' from reddit app>
   REDDIT_CLIENT_ID=<id under 'personal use script' from reddit app>
   REDDIT_USERNAME=<user name>
   REDDIT_PASSWORD=<user password>
   OLLAMA_MODEL="llama3:8b" // This is the model I use. It was small enough to run locally, responded with high quality answers, and had the best tool capabilities.
   OLLAMA_TIMEOUT="3000.0" // This give my CPU time to think. It takes about 10-30 minutes for the agent to work through each question
   OLLAMA_TEMP="0.0" // I want the model to be deterministic
   OLLAMA_BASE_URL="http://127.0.0.1:11434" // This is for a local ollama. Change it if you are using a remote ollama, on the cloud e.g.
   ```

 8. Source the .env
   
      `source .env`

   Note: In principle the code should load the variables using dotenv.load_dotenv() but I am unable to get it to work. Sourcing .env is much more reliable.

 9. Run the agent

    `python eli5_llm_agent.py`


### Usage

Running eli5_llm_agent.py will retrieve the 25 most recent "hot" posts on r/explainitlikeimfive and post a comment in response if it has yet to respond. The agent has access to a tool that can draft several answers that are then summarized in a final answer. Includes basic rate limiting, tbh my CPU is doing most of the work here. 😁

### The Future 
    
 - I want to add a data ingestion pipeline that will streamline the process of retrieving the posts and queuing them for the agent.
 - I want to get the wikipedia tool working.
 - I want to add an evaluator in the pipeline that uses RAG on the top comments to decide if the responder agent's answer is aligned well.
# Project introduction and structure
The "Leads-Qualifier-Agent" is an autonomous agent that receives, analyzes, enriches, and prioritizes new business leads from a website contact form. Built using LangGraph and LangChain, and powered by a locally-run open-source LLM through Ollama, this agent can automate manual administrative tasks and increase sales efficiency.

### Visual flowchart of real-time usage:
<img width="645" alt="Screenshot 2025-06-22 at 10 20 16 pm" src="https://github.com/user-attachments/assets/170d8018-6c93-43e1-bc03-865e531450fc" />


**A brief description of each file in this directory:**
- main.py: The core application. Contains the FastAPI server, the LangGraph agent definition (state, nodes, edges), and the API endpoint logic.
- tools.py: A module containing the standalone functions (tools) that the AI agent uses, such as the web scraper and database writer.
- streamlit_app.py: A simple web-based user interface for demonstrating the system. It acts as a client that sends requests to the FastAPI backend.
- requirements.txt: A list of all the Python dependencies required to run the project.
- leads.db: The SQLite database file that is automatically created to store the processed lead data.
- .env: (To be created by user) A file to store secret API keys for services like LangSmith.
- test_tools.py: A script used during development to test the functions in tools.py independently. (Run once to create the sqlite database if not existing)


## Setup & Installation

Follow these steps to set up the project environment.
1. Prerequisites
- Ensure you have Python 3.10+ installed.
- Install Ollama on your machine.
- Then, open the terminal on your device.
-Create a virtual environment for the project to ensure installed dependencies stay local to the project. Click [here](https://python.land/virtual-environments/virtualenv) for a guide on how to create and activate one.

3. Project Setup
`cd /path/to/this/folder`

4. Install Dependencies
Install all required packages using the requirements.txt file: `pip install -r requirements.txt`

4. Set Up Local LLM: Pull the llama3:8b model, which will be used by the agent: `ollama pull llama3:8b`

5. Configure LangSmith:
To visualize the agent's workflow, you can use LangSmith. Follow the below steps:
- Sign up for a free account at smith.langchain.com.
- Create a new project and an API key.
- Create a file named .env in the project root and add your keys:
Then, inside this projects `.env` file:
1. `LANGCHAIN_TRACING_V2="true"`
2. `LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY"`
3. `LANGCHAIN_PROJECT="YOUR_PROJECT_NAME"`

# Running the End-to-End System

The system requires two separate processes to be running in two different terminal windows. Make sure you activate the virtual environment (source .venv/bin/activate) in each new terminal.

*Start the Ollama Server*

First, ensure the Ollama application is running. On macOS, this is typically done by launching the Ollama.app. On other systems, you might run `ollama serve` in the terminal. The Ollama icon should be visible in your menu bar/system tray.

**Terminal 1: run the FastAPI Backend**

`uvicorn main:app --reload`

Wait until you see the message Application startup complete.

**Terminal 2: Run the Streamlit Frontend**

`streamlit run streamlit_app.py`

A new browser tab should automatically open to the Streamlit app.

# How to Use the Demo
With both terminals running, use the Streamlit web interface that opened in your browser.
- Fill in the "Name", "Email", and "Message" fields.
- Click the "Qualify Lead" button.
Observe the results displayed on the Streamlit page. You can also monitor the FastAPI server logs in Terminal 1 to see the agent's real-time thought process.

# Access the stored leads:
Finally, open the leads.db sqlite3 database using a database viewer or by installing the SQLite Viewer extension on VSCode.
You can also visualise the agents processes on langsmith under this project.

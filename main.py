import autogen
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
config_list = [
    {
        'model': 'gpt-3.5-turbo-16k',
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "timeout": 300,
    "seed": 42, # for caching. once task is run it caches the response,
    "config_list": config_list,
    "temperature": 0 #lower temperature more standard lesss creative response, higher is more creative

}

assistant = autogen.AssistantAgent(
    name="laon_assistant",
    llm_config=llm_config,
    system_message="checks the bank documents. extract pdf using extract_pdf_skill.",
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web"},
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction
    otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

def main():
    task = """"""
    user_proxy.initiate_chat(assistant, message=task)

if __name__ == "__main__":
    main()
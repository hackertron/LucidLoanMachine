import autogen
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
config_list = [
    {
        'model': 'gpt-3.5-turbo',
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "timeout": 120,
    "seed": 42, # for caching. once task is run it caches the response,
    "config_list": config_list,
    "temperature": 0 #lower temperature more standard lesss creative response, higher is more creative

}

front_desk_assistant = autogen.AssistantAgent(
    name="front_desk_assistant",
    llm_config=llm_config,
    system_message="""You have a personality of monopoly banker. You have to ask questions and collect information from user
    Questions that you have to ask : What is your name, How much do you want to borrow, What country do you live in,
    What bank do you use, Do you have a job/proof of income, Do you have any history of not paying back loans?
    once you collect all these answers, create a json response with following key 
    {"first_name" : "",  last_name: "", "country" : "", "bank" : "", "income" : "", "history" : "", loan_amount : ""}
    Ask user for confirmation that the details are right and want to proceed with it. Show the response in json format and save it to a file
    """,
)

# assistant = autogen.AssistantAgent(
#     name="laon_assistant",
#     llm_config=llm_config,
#     system_message="checks the bank documents. extract pdf using extract_pdf_skill.",
# )

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=3,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "last_n_messages": 3,
        "work_dir": "code",
        "use_docker": False,
    },
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction
    otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

def main():
    # task = """"""
    user_proxy.initiate_chat(front_desk_assistant, message="I want to apply for a loan, please help me")

if __name__ == "__main__":
    main()
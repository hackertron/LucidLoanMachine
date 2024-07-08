import autogen
import os
from dotenv import load_dotenv
from typing import Annotated
import requests
load_dotenv()  # take environment variables from .env.
config_list = [
    {
        'model':  'gpt-3.5-turbo',
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "timeout": 120,
    "seed": 42, # for caching. once task is run it caches the response,
    "config_list": config_list,
    "temperature": 0 #lower temperature more standard lesss creative response, higher is more creative

}

def verify_email_with_prove_api(domain :Annotated[str, "The domain name to verify"]) -> Annotated[dict, "The response from the Prove Email API"] | None:
    api_url = f"https://archive.prove.email/api/key?domain={domain}"
    response = requests.get(api_url)
    return response.json() if response.status_code == 200 else None



front_desk_assistant = autogen.AssistantAgent(
    name="front_desk_assistant",
    llm_config=llm_config,
    system_message="""You have a personality of monopoly banker. You have to ask questions and collect information from user
    Questions that you have to ask : What is your name, How much do you want to borrow, What country do you live in,
    What bank do you use, Do you have a job/proof of income, what's your email?, Do you have any history of not paying back loans?
    once you collect all these answers, create a json response with following key 
    {"first_name" : "",  last_name: "", "country" : "", "bank" : "", "income" : "", "history" : "", loan_amount : "", email : ""}
    Ask user for confirmation that the details are right and want to proceed with it. Show the response in json format and save it to a file
    """,
)

email_assistant = autogen.AssistantAgent(
    name="email_assistant",
    llm_config=llm_config,
    system_message="""You will have access to bank.json from front_desk_assistant. 
    You will guide user to paste their raw email. Assume user has desktop and not on their mobile phone.
    guide user to paste their raw email to you. Tell them to paste raw email in chunks, not the complete email in one go.
    You will then analyze the email and check if it's valid and details matches with bank.json."""
)



salary_slip_assistant = autogen.AssistantAgent(
    name="salary_slip_assistant",
    llm_config=llm_config,
    system_message="""You will ask user to upload a salary slip in pdf format. You will analyze it and gather following informations from the pdf.
    account number, bank balance. the details should match with bank.json file. You will add additional keys in bank.json file and save it."""
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

user_proxy.register_for_llm(name="verify_email", description="verify email's dkim using prove api verify_email_with_prove_api")(verify_email_with_prove_api)
user_proxy.register_for_execution(name="verify_email")(verify_email_with_prove_api)

def main():
    # Register the verify_email_with_prove_api function for the email_assistant
    email_assistant.register_function(
        function_map={
            "verify_email_with_prove_api": verify_email_with_prove_api
        }
    )
    chat_results = user_proxy.initiate_chats([
        {
            "recipient": front_desk_assistant,
            "message": "I want to apply for a loan, please help me",
            "silent": False,
            "summary_method": "reflection_with_llm"
        },
        {
            "recipient": email_assistant,
            "message": "guide user to paste their raw email and validate with json that you recieved from front_desk_assistant",
            "silent": False,
            "summary_method": "reflection_with_llm"
        },
        {
            "recipient": salary_slip_assistant,
            "message": "guide user to upload a salary slip in pdf format",
            "silent": False,
            "summary_method": "reflection_with_llm"
        }
    ])
    # groupchat = autogen.GroupChat(agents=[user_proxy, front_desk_assistant, email_assistant], messages=[], max_round=5)
    # manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    # chat_results = user_proxy.initiate_chat(manager, message="I want to apply for a loan, please help me")
    for i, chat_res in enumerate(chat_results):
        print(f"*****{i}th chat*******:")
        print(chat_res.summary)
        print("Human input in the middle:", chat_res.human_input)
        print("Conversation cost: ", chat_res.cost)
        print("\n\n")
if __name__ == "__main__":
    main()
import autogen
import os
import json
from dotenv import load_dotenv
from typing import Annotated
import requests
from system_prompts import front_desk_assistant_prompt, email_assistant_prompt, salary_slip_assistant_prompt
from extract_pdf_skill import process_pdf_from_url

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
    print("response : ", response)
    return response.json() if response.status_code == 200 else None


front_desk_assistant = autogen.AssistantAgent(
    name="front_desk_assistant",
    llm_config=llm_config,
    system_message=front_desk_assistant_prompt,
)

email_assistant = autogen.AssistantAgent(
    name="email_assistant",
    llm_config=llm_config,
    system_message=email_assistant_prompt
)



salary_slip_assistant = autogen.AssistantAgent(
    name="salary_slip_assistant",
    llm_config=llm_config,
    system_message=salary_slip_assistant_prompt
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


user_proxy.register_for_llm(name="verify_email_with_prove_api", description="verify email's dkim using prove api verify_email_with_prove_api")(verify_email_with_prove_api)
user_proxy.register_for_execution(name="verify_email_with_prove_api")(verify_email_with_prove_api)

user_proxy.register_for_llm(name="process_pdf_from_url", description="process pdf from url using extract_pdf_skill")(process_pdf_from_url)
user_proxy.register_for_execution(name="process_pdf_from_url")(process_pdf_from_url)

def main():
    # Register the verify_email_with_prove_api function for the email_assistant
    email_assistant.register_function(
        function_map={
            "verify_email_with_prove_api": verify_email_with_prove_api,
            "process_pdf_from_url": process_pdf_from_url
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
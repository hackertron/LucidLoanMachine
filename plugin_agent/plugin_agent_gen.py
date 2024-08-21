import autogen
import os
import json
from dotenv import load_dotenv
from typing import Annotated
import requests
from plugin_prompts import bank_plugin_prompts


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

def write_plugin(website_url:Annotated[str, "website url"], plugin_name:Annotated[str, "plugin name"]) -> Annotated[dict, "The response from the plugin"] | None:
    api_url = f"https://archive.prove.email/api/key?domain={domain}"
    response = requests.get(api_url)
    print("response : ", response)
    return response.json() if response.status_code == 200 else None


plugin_agent = autogen.AssistantAgent(
    name="plugin_agent",
    llm_config=llm_config,
    system_message="""you will write TLSN plugin for the website that the user will provide. 
    You will ask the user to provide the website url,
    API and some web request and response of it and plugin name.
    Once you receive the url, use the write_plugin function to write the plugin.
    The function will return the response from the plugin.
    Analyze the response to gather the following information from the plugin: plugin name, plugin description, plugin author, plugin version, website url.
    """,
)

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


user_proxy.register_for_llm(name="write_plugin", description="write TLSN extension plugin for website that user will provide")(write_plugin)
user_proxy.register_for_execution(name="write_plugin")(write_plugin)

def main():
    # Register the verify_email_with_prove_api function for the email_assistant
    plugin_agent.register_function(
        function_map={
            "write_plugin": write_plugin,
        }
    )
    chat_results = user_proxy.initiate_chats([
        {
            "recipient": plugin_agent,
            "message": "I want to write a TLSN extension plugin for the website that I will provide, please help me",
            "silent": False,
            "summary_method": "reflection_with_llm"
        }
    ])
    for i, chat_res in enumerate(chat_results):
        print(f"*****{i}th chat*******:")
        print(chat_res.summary)
        print("Human input in the middle:", chat_res.human_input)
        print("Conversation cost: ", chat_res.cost)
        print("\n\n")
if __name__ == "__main__":
    main()
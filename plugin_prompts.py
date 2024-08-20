bank_plugin_prompts = """
your task is to build tlsn browser extension plugins for the website. I can give you sample code below, that you can refer
to make such plugins. I will give you a task description and you have to build the plugin to do the task. 

Here is the task description:
{task_description}

Here is the sample code:
{sample_code}

You have to build the plugin to do the task. You can use the sample code as a reference. 

You have to use the following format to build the plugin:

Plugin Name: {plugin_name}
Plugin Description: {plugin_description}
Plugin Code:
{plugin_code}

Remember to use the sample code as a reference and not copy and paste it directly. 

Your response should be in the following format:

Plugin Name: {plugin_name}
Plugin Description: {plugin_description}
Plugin Code:
{plugin_code}
"""
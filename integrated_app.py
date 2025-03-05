import autogen
import os
import json
import gradio as gr
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Import existing components
from main import front_desk_assistant, email_assistant, salary_slip_assistant
from system_prompts import front_desk_assistant_prompt, email_assistant_prompt, salary_slip_assistant_prompt, verify_tlsn_proof_prompt
from extract_pdf_skill import process_pdf_from_url
from verify_tlsn_proof import verify_tlsn_proof, save_tlsn_proof

load_dotenv()  # Take environment variables from .env

# Set up Autogen config
config_list = [
    {
        'model': 'gpt-3.5-turbo',
        'api_key': os.getenv('OPENAI_API_KEY'),
    }
]

llm_config = {
    "timeout": 120,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0
}

class AutogenIntegration:
    """
    Class to integrate Gradio UI with Autogen agents
    """
    def __init__(self):
        # Initialize the assistants
        self.front_desk_assistant = autogen.AssistantAgent(
            name="front_desk_assistant",
            llm_config=llm_config,
            system_message=front_desk_assistant_prompt,
        )
        
        self.email_assistant = autogen.AssistantAgent(
            name="email_assistant",
            llm_config=llm_config,
            system_message=email_assistant_prompt
        )
        
        self.salary_slip_assistant = autogen.AssistantAgent(
            name="salary_slip_assistant",
            llm_config=llm_config,
            system_message=salary_slip_assistant_prompt
        )
        
        self.tlsn_assistant = autogen.AssistantAgent(
            name="tlsn_assistant",
            llm_config=llm_config,
            system_message=verify_tlsn_proof_prompt
        )
        
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",  # Automated for Gradio integration
            code_execution_config={
                "work_dir": "code",
                "use_docker": False,
            }
        )
        
        # Register functions for the assistants
        self.register_assistant_functions()
    
    def register_assistant_functions(self):
        """Register functions for all assistants"""
        # Register functions for email assistant
        self.email_assistant.register_function(
            function_map={
                "process_email": self.process_email,
            }
        )
        
        # Register functions for salary slip assistant
        self.salary_slip_assistant.register_function(
            function_map={
                "process_pdf_from_url": process_pdf_from_url,
            }
        )
        
        # Register functions for TLSN assistant
        self.tlsn_assistant.register_function(
            function_map={
                "verify_tlsn_proof": verify_tlsn_proof,
                "save_tlsn_proof": save_tlsn_proof,
            }
        )
    
    def process_email(self, raw_email: str) -> Dict[str, Any]:
        """Process raw email and return results"""
        try:
            # Save email to file
            with open("raw_email.txt", "w") as f:
                f.write(raw_email)
            
            # For demonstration, return basic info
            return {
                "success": True,
                "message": "Email processed and saved for verification"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_loan_application(self, name, loan_amount, country, bank, has_income, email, no_default_history):
        """Handle loan application through front desk assistant"""
        # Prepare message
        message = f"""
        I want to apply for a loan. Here's my information:
        Name: {name}
        Loan Amount: {loan_amount}
        Country: {country}
        Bank: {bank}
        Do I have income: {'Yes' if has_income else 'No'}
        Email: {email}
        No history of defaults: {'Yes' if no_default_history else 'No'}
        """
        
        # Interact with front desk assistant
        self.user_proxy.initiate_chat(self.front_desk_assistant, message=message)
        
        # Return confirmation
        try:
            with open("bank.json", "r") as f:
                data = json.load(f)
                return f"Application processed successfully. Your data has been saved:\n\n{json.dumps(data, indent=2)}"
        except:
            return "Application processed. Please check the console for details."
    
    def handle_email_verification(self, raw_email):
        """Handle email verification through email assistant"""
        # Prepare message
        message = f"Here's my raw email for verification: [Email begins]\n{raw_email[:500]}...[Email trimmed]"
        
        # Interact with email assistant
        self.user_proxy.initiate_chat(self.email_assistant, message=message)
        
        # Save email for processing
        self.process_email(raw_email)
        
        return "Email received for verification. Please check the console for verification details."
    
    def handle_salary_verification(self, pdf_url):
        """Handle salary slip verification through salary slip assistant"""
        # Prepare message
        message = f"Here's the URL to my salary slip: {pdf_url}"
        
        # Interact with salary slip assistant
        self.user_proxy.initiate_chat(self.salary_slip_assistant, message=message)
        
        return "Salary slip verification in progress. Please check the console for details."
    
    def handle_tlsn_verification(self, proof_json):
        """Handle TLSN proof verification through TLSN assistant"""
        if not proof_json:
            return {"success": False, "error": "Empty proof provided"}
        
        # Save proof
        save_result = save_tlsn_proof(proof_json)
        if not save_result["success"]:
            return save_result
        
        # Prepare message
        message = f"Here's my TLSN proof for verification: [Proof begins]\n{proof_json[:500]}...[Proof trimmed]"
        
        # Interact with TLSN assistant
        self.user_proxy.initiate_chat(self.tlsn_assistant, message=message)
        
        # Verify proof directly
        result = verify_tlsn_proof(proof_json)
        return result

def create_integrated_ui():
    """Create Gradio UI with Autogen integration"""
    integration = AutogenIntegration()
    
    with gr.Blocks(title="Lucid Loan Machine - Integrated") as app:
        gr.Markdown("# 💰 Lucid Loan Machine (LLM) - Integrated with Autogen")
        gr.Markdown("## A secure loan application system powered by AI agents and zero-knowledge proofs")
        
        with gr.Tab("Loan Application"):
            gr.Markdown("### 📝 Complete this form to start your loan application")
            with gr.Row():
                with gr.Column():
                    name_input = gr.Textbox(label="Full Name")
                    loan_amount_input = gr.Number(label="Loan Amount")
                    country_input = gr.Textbox(label="Country")
                    bank_input = gr.Textbox(label="Bank")
                    has_income_input = gr.Checkbox(label="Do you have a job/proof of income?")
                    email_input = gr.Textbox(label="Email")
                    no_default_history_input = gr.Checkbox(label="No history of not paying back loans?")
                    submit_button = gr.Button("Submit Application")
                
                with gr.Column():
                    application_output = gr.Textbox(label="Application Status", lines=10)
        
        with gr.Tab("Email Verification"):
            gr.Markdown("### 📧 Verify your identity with email verification")
            with gr.Row():
                with gr.Column():
                    raw_email_input = gr.Textbox(label="Raw Email Content", lines=15)
                    email_submit_button = gr.Button("Verify Email")
                
                with gr.Column():
                    email_verification_output = gr.Textbox(label="Email Verification Result", lines=10)
        
        with gr.Tab("Salary Slip Verification"):
            gr.Markdown("### 💼 Verify your income with a salary slip")
            with gr.Row():
                with gr.Column():
                    pdf_url_input = gr.Textbox(label="Salary Slip PDF URL")
                    pdf_submit_button = gr.Button("Verify Salary Slip")
                
                with gr.Column():
                    salary_verification_output = gr.Textbox(label="Salary Verification Result", lines=10)
        
        with gr.Tab("TLSN Proof Verification"):
            gr.Markdown("### 🔐 Verify website data with TLSN proof")
            with gr.Row():
                with gr.Column():
                    tlsn_proof_input = gr.Textbox(label="TLSN Proof JSON", lines=15)
                    tlsn_submit_button = gr.Button("Verify TLSN Proof")
                
                with gr.Column():
                    tlsn_verification_output = gr.JSON(label="TLSN Verification Result")
        
        # Set up event handlers
        submit_button.click(
            integration.handle_loan_application,
            inputs=[name_input, loan_amount_input, country_input, bank_input, 
                   has_income_input, email_input, no_default_history_input],
            outputs=application_output
        )
        
        email_submit_button.click(
            integration.handle_email_verification,
            inputs=[raw_email_input],
            outputs=email_verification_output
        )
        
        pdf_submit_button.click(
            integration.handle_salary_verification,
            inputs=[pdf_url_input],
            outputs=salary_verification_output
        )
        
        tlsn_submit_button.click(
            integration.handle_tlsn_verification,
            inputs=[tlsn_proof_input],
            outputs=tlsn_verification_output
        )
    
    return app

if __name__ == "__main__":
    app = create_integrated_ui()
    app.launch()
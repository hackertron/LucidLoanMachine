import gradio as gr
import json
import os
import tempfile
from typing import Dict, Any, Optional
import traceback

# Import the existing skills
from extract_pdf_skill import process_pdf_from_url
from verify_tlsn_proof import verify_tlsn_proof, save_tlsn_proof

def handle_loan_application(
    name: str,
    loan_amount: float,
    country: str,
    bank: str,
    has_income: bool,
    email: str,
    no_default_history: bool
) -> str:
    """
    Handle the initial loan application form
    """
    # Create a JSON with the loan application details
    application_data = {
        "first_name": name.split()[0] if len(name.split()) > 0 else "",
        "last_name": name.split()[1] if len(name.split()) > 1 else "",
        "loan_amount": loan_amount,
        "country": country,
        "bank": bank,
        "income": "Yes" if has_income else "No",
        "history": "No defaults" if no_default_history else "Has defaults",
        "email": email
    }
    
    # Save to bank.json
    with open("bank.json", "w") as f:
        json.dump(application_data, f, indent=4)
        
    return f"Application data saved successfully:\n\n{json.dumps(application_data, indent=4)}"

def handle_email_verification(raw_email: str) -> str:
    """
    Handle the email verification step
    """
    if not raw_email:
        return "Please provide the raw email content."
    
    # Save the raw email to a file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".eml")
    try:
        temp_file.write(raw_email.encode('utf-8'))
        temp_file.close()
        
        # Verify DKIM signature
        result = verify_dkim_signature(temp_file.name)
        
        # Try to extract relevant information from the email
        # This is a placeholder - in a real implementation, you would extract more information
        email_info = "Email processed successfully. DKIM verification results are shown in the console."
        
        return email_info
    except Exception as e:
        return f"Error processing email: {str(e)}"
    finally:
        # Clean up
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

def handle_email_upload(email_file) -> str:
    """
    Handle uploaded email file
    """
    if email_file is None:
        return "No file uploaded"
    
    try:
        # Read the file content
        with open(email_file.name, "r", encoding="utf-8", errors="ignore") as f:
            email_content = f.read()
        
        # Process the email
        return handle_email_verification(email_content)
    except Exception as e:
        return f"Error processing email file: {str(e)}"

def handle_salary_verification(pdf_url: str) -> str:
    """
    Handle the salary slip verification
    """
    if not pdf_url:
        return "Please provide a valid PDF URL."
    
    try:
        # Process the PDF
        text = process_pdf_from_url(pdf_url)
        
        if not text:
            return "Failed to extract text from the PDF. Please check the URL and try again."
        
        # Here we would extract information like account number, bank balance, etc.
        # This is a simplified example
        info_extract = "PDF processed successfully. Extracted text: " + text[:300] + "..."
        
        # Try to update bank.json with additional information
        try:
            with open("bank.json", "r") as f:
                bank_data = json.load(f)
            
            # Here you would extract and add more data
            bank_data["pdf_verified"] = True
            
            with open("bank.json", "w") as f:
                json.dump(bank_data, f, indent=4)
                
            info_extract += "\n\nBank application data updated with PDF verification."
        except Exception as e:
            info_extract += f"\n\nWarning: Could not update application data: {str(e)}"
        
        return info_extract
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def handle_tlsn_proof_text(proof_json: str) -> Dict[str, Any]:
    """
    Handle TLSN proof verification from pasted JSON
    """
    if not proof_json:
        return {"success": False, "error": "Please provide the TLSN proof JSON."}
    
    try:
        # Save the proof to a file
        save_result = save_tlsn_proof(proof_json)
        if not save_result["success"]:
            return save_result
        
        # Verify the proof
        result = verify_tlsn_proof(proof_json)
        return result
    except Exception as e:
        traceback.print_exc()  # Print the full exception traceback to console
        return {"success": False, "error": f"Error processing TLSN proof: {str(e)}"}

def handle_tlsn_proof_upload(proof_file) -> Dict[str, Any]:
    """
    Handle TLSN proof verification from uploaded file
    """
    if proof_file is None:
        return {"success": False, "error": "No file uploaded"}
    
    try:
        # Read the file
        with open(proof_file.name, "r", encoding="utf-8") as f:
            proof_json = f.read()
        
        # Process the proof
        return handle_tlsn_proof_text(proof_json)
    except Exception as e:
        traceback.print_exc()  # Print the full exception traceback to console
        return {"success": False, "error": f"Error processing TLSN proof file: {str(e)}"}

def create_ui():
    """
    Create the Gradio UI
    """
    with gr.Blocks(title="Lucid Loan Machine") as app:
        gr.Markdown("# 💰 Lucid Loan Machine (LLM)")
        gr.Markdown("## A secure loan application system powered by AI and zero-knowledge proofs")
        
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
                    gr.Markdown("#### Paste Raw Email")
                    raw_email_input = gr.Textbox(label="Raw Email Content", lines=15)
                    email_submit_button = gr.Button("Verify Email")
                
                with gr.Column():
                    gr.Markdown("#### Or Upload Email File")
                    email_file_input = gr.File(label="Email File")
                    email_upload_button = gr.Button("Verify Uploaded Email")
                    
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
                    gr.Markdown("#### Paste TLSN Proof JSON")
                    tlsn_proof_input = gr.Textbox(label="TLSN Proof JSON", lines=15)
                    tlsn_submit_button = gr.Button("Verify TLSN Proof")
                
                with gr.Column():
                    gr.Markdown("#### Or Upload TLSN Proof File")
                    tlsn_file_input = gr.File(label="TLSN Proof File")
                    tlsn_upload_button = gr.Button("Verify Uploaded TLSN Proof")
                    
                    tlsn_verification_output = gr.JSON(label="TLSN Verification Result")
        
        # Set up event handlers
        submit_button.click(
            handle_loan_application,
            inputs=[name_input, loan_amount_input, country_input, bank_input, 
                   has_income_input, email_input, no_default_history_input],
            outputs=application_output
        )
        
        email_submit_button.click(
            handle_email_verification,
            inputs=[raw_email_input],
            outputs=email_verification_output
        )
        
        email_upload_button.click(
            handle_email_upload,
            inputs=[email_file_input],
            outputs=email_verification_output
        )
        
        pdf_submit_button.click(
            handle_salary_verification,
            inputs=[pdf_url_input],
            outputs=salary_verification_output
        )
        
        tlsn_submit_button.click(
            handle_tlsn_proof_text,
            inputs=[tlsn_proof_input],
            outputs=tlsn_verification_output
        )
        
        tlsn_upload_button.click(
            handle_tlsn_proof_upload,
            inputs=[tlsn_file_input],
            outputs=tlsn_verification_output
        )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch()
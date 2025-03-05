import json
import requests
from typing import Dict, Any, Annotated

def verify_tlsn_proof(proof_json: Annotated[str, "JSON content of the TLSN proof"]) -> Dict[str, Any]:
    """
    Verify a TLSN proof by uploading it to explorer.tlsn.org
    
    Args:
        proof_json (str): The JSON content of the TLSN proof
        
    Returns:
        Dict[str, Any]: A dictionary containing the verification result
    """
    try:
        # Parse the JSON to ensure it's valid
        proof_data = json.loads(proof_json)
        
        # Upload to explorer.tlsn.org
        # This is a simplified implementation - you may need to adjust based on actual API
        response = requests.post(
            "https://explorer.tlsn.org/api/verify",
            json=proof_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            # Extract relevant information like name and country
            return {
                "success": True,
                "verification_result": result,
                "name": result.get("name", "Not found"),
                "country": result.get("country", "Not found"),
                "account_number": result.get("account_number", "Not found")
            }
        else:
            return {
                "success": False,
                "error": f"Verification failed: {response.status_code}",
                "message": response.text
            }
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON format"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def save_tlsn_proof(proof_json: str) -> Dict[str, Any]:
    """
    Save TLSN proof to a file
    
    Args:
        proof_json (str): The JSON content of the TLSN proof
        
    Returns:
        Dict[str, Any]: Result of the save operation
    """
    try:
        # Parse JSON to validate format
        json.loads(proof_json)
        
        # Save to file
        with open("tlsn_proof.json", "w") as f:
            f.write(proof_json)
        
        return {"success": True, "message": "TLSN proof saved successfully"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON format"}
    except Exception as e:
        return {"success": False, "error": str(e)}
# core/twitter_client.py - ENCODING FIX
import subprocess
import json
import os

def run_twitter_command(args: list, return_json: bool = True):
    cmd = ["twitter"] + args
    if return_json:
        cmd.append("--json")
    
    # Build environment with proper encoding for Windows
    env = os.environ.copy()
    
    # CRITICAL: Force UTF-8 encoding for Windows
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Also ensure tokens are present
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("TWITTER_CT0")
    
    if auth_token:
        env["TWITTER_AUTH_TOKEN"] = auth_token
    if ct0:
        env["TWITTER_CT0"] = ct0
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env,
            shell=False,
            encoding='utf-8',  # Explicit UTF-8 encoding
            errors='replace'   # Replace unencodable chars instead of crashing
        )
        
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "success": False}
        
        if return_json:
            try:
                return {"data": json.loads(result.stdout), "success": True}
            except json.JSONDecodeError:
                return {"data": result.stdout, "success": True}
        else:
            return {"data": result.stdout.strip(), "success": True}
            
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out", "success": False}
    except FileNotFoundError:
        return {"error": "twitter command not found", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}
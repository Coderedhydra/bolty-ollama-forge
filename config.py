import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    # API Keys
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Scanner Settings
    max_depth: int = int(os.getenv("MAX_DEPTH", "3"))
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    user_agent: str = os.getenv("USER_AGENT", "VulnScanner/1.0")
    
    # LLM Settings
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama2")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Vulnerability Testing
    test_sql_injection: bool = os.getenv("TEST_SQL_INJECTION", "true").lower() == "true"
    test_xss: bool = os.getenv("TEST_XSS", "true").lower() == "true"
    test_path_traversal: bool = os.getenv("TEST_PATH_TRAVERSAL", "true").lower() == "true"
    test_command_injection: bool = os.getenv("TEST_COMMAND_INJECTION", "true").lower() == "true"
    test_idor: bool = os.getenv("TEST_IDOR", "true").lower() == "true"
    
    # Output Settings
    output_format: str = os.getenv("OUTPUT_FORMAT", "console")  # console, json, html
    verbose: bool = os.getenv("VERBOSE", "false").lower() == "true"

config = Config()
import google.generativeai as genai
import ollama
import json
import logging
from typing import List, Dict, Optional, Union
from config import config
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class LLMClient:
    """Base class for LLM clients"""
    
    def __init__(self):
        pass
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        raise NotImplementedError
    
    async def analyze_target(self, target_info: Dict) -> Dict:
        raise NotImplementedError
    
    async def generate_payload(self, vulnerability_type: str, target_info: Dict) -> List[str]:
        raise NotImplementedError

class GeminiClient(LLMClient):
    """Gemini API client for vulnerability analysis and payload generation"""
    
    def __init__(self):
        super().__init__()
        if not config.gemini_api_key:
            raise ValueError("Gemini API key not provided")
        
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
        
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Gemini"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return ""
    
    async def analyze_target(self, target_info: Dict) -> Dict:
        """Analyze target for potential vulnerabilities"""
        prompt = f"""
        You are a cybersecurity expert analyzing a web application for potential vulnerabilities.
        
        Target Information:
        - Base URL: {target_info.get('base_url', 'Unknown')}
        - Total Links: {target_info.get('total_links', 0)}
        - Total Forms: {target_info.get('total_forms', 0)}
        - Interesting Endpoints: {len(target_info.get('interesting_endpoints', []))}
        
        Forms Found:
        {json.dumps(target_info.get('forms', [])[:5], indent=2)}
        
        Interesting Endpoints:
        {json.dumps(target_info.get('interesting_endpoints', [])[:10], indent=2)}
        
        Please analyze this target and provide:
        1. Priority endpoints to test (rate 1-10)
        2. Recommended vulnerability types to test for each endpoint
        3. Risk assessment for each form found
        4. Testing strategy recommendations
        
        Respond in JSON format with the following structure:
        {{
            "priority_endpoints": [
                {{
                    "url": "endpoint_url",
                    "priority": 8,
                    "vulnerability_types": ["sql_injection", "xss"],
                    "reasoning": "explanation"
                }}
            ],
            "form_analysis": [
                {{
                    "form_url": "form_url",
                    "risk_level": "high",
                    "recommended_tests": ["sql_injection", "xss"],
                    "reasoning": "explanation"
                }}
            ],
            "testing_strategy": "overall strategy recommendations"
        }}
        """
        
        response = await self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse Gemini response as JSON")
            return {"error": "Failed to parse analysis"}
    
    async def generate_payload(self, vulnerability_type: str, target_info: Dict) -> List[str]:
        """Generate vulnerability-specific payloads"""
        prompt = f"""
        Generate specific {vulnerability_type} payloads for testing the following target:
        
        Target Info: {json.dumps(target_info, indent=2)}
        
        Requirements:
        1. Generate 10-15 diverse payloads for {vulnerability_type}
        2. Include both basic and advanced techniques
        3. Consider the target's technology stack if identifiable
        4. Include bypass techniques for common filters
        5. Ensure payloads are safe for testing (no destructive operations)
        
        Respond with ONLY a JSON array of payload strings:
        ["payload1", "payload2", "payload3", ...]
        """
        
        response = await self.generate_response(prompt)
        try:
            payloads = json.loads(response)
            return payloads if isinstance(payloads, list) else []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse {vulnerability_type} payloads from Gemini")
            return []

class OllamaClient(LLMClient):
    """Ollama client for local LLM analysis"""
    
    def __init__(self):
        super().__init__()
        self.client = ollama.Client(host=config.ollama_host)
        self.model = config.ollama_model
        
        # Test connection
        try:
            self.client.list()
            logger.info(f"Connected to Ollama at {config.ollama_host}")
        except Exception as e:
            logger.warning(f"Ollama connection failed: {str(e)}")
            self.client = None
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Ollama"""
        if not self.client:
            logger.error("Ollama client not available")
            return ""
        
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': full_prompt}
            ])
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            return ""
    
    async def analyze_target(self, target_info: Dict) -> Dict:
        """Analyze target using Ollama"""
        prompt = f"""
        As a cybersecurity expert, analyze this web application:
        
        Target: {target_info.get('base_url')}
        Links: {target_info.get('total_links', 0)}
        Forms: {target_info.get('total_forms', 0)}
        
        Key forms and endpoints:
        {json.dumps(target_info.get('forms', [])[:3], indent=2)}
        {json.dumps(target_info.get('interesting_endpoints', [])[:5], indent=2)}
        
        Provide analysis in JSON format with:
        - priority_endpoints: array of high-value targets
        - vulnerability_recommendations: suggested tests
        - risk_assessment: overall risk level
        
        Focus on practical, actionable recommendations.
        """
        
        response = await self.generate_response(prompt)
        try:
            # Extract JSON from response if it's embedded in text
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "No JSON found in response"}
        except json.JSONDecodeError:
            logger.error("Failed to parse Ollama response as JSON")
            return {"error": "Failed to parse analysis"}
    
    async def generate_payload(self, vulnerability_type: str, target_info: Dict) -> List[str]:
        """Generate payloads using Ollama"""
        prompt = f"""
        Generate {vulnerability_type} test payloads for:
        URL: {target_info.get('url', 'unknown')}
        Method: {target_info.get('method', 'GET')}
        Parameters: {target_info.get('parameters', [])}
        
        Create 8-12 payloads focusing on:
        1. Basic {vulnerability_type} patterns
        2. Filter bypass techniques
        3. Context-specific variations
        
        Return only a JSON array: ["payload1", "payload2", ...]
        """
        
        response = await self.generate_response(prompt)
        try:
            # Extract JSON array from response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                payloads = json.loads(json_str)
                return payloads if isinstance(payloads, list) else []
            else:
                return []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse {vulnerability_type} payloads from Ollama")
            return []

class LLMManager:
    """Manages multiple LLM clients and provides unified interface"""
    
    def __init__(self):
        self.clients = {}
        
        # Initialize Gemini client if API key is available
        if config.gemini_api_key:
            try:
                self.clients['gemini'] = GeminiClient()
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
        
        # Initialize Ollama client
        try:
            ollama_client = OllamaClient()
            if ollama_client.client:
                self.clients['ollama'] = ollama_client
                logger.info("Ollama client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {str(e)}")
        
        if not self.clients:
            raise ValueError("No LLM clients available. Please configure Gemini API key or Ollama.")
    
    def get_preferred_client(self, preference: str = "gemini") -> LLMClient:
        """Get preferred LLM client"""
        if preference in self.clients:
            return self.clients[preference]
        elif self.clients:
            return list(self.clients.values())[0]
        else:
            raise ValueError("No LLM clients available")
    
    async def analyze_target_with_fallback(self, target_info: Dict, preference: str = "gemini") -> Dict:
        """Analyze target with fallback to other clients"""
        for client_name in [preference] + [k for k in self.clients.keys() if k != preference]:
            if client_name in self.clients:
                try:
                    logger.info(f"Analyzing target with {client_name}")
                    result = await self.clients[client_name].analyze_target(target_info)
                    if result and "error" not in result:
                        return result
                except Exception as e:
                    logger.error(f"Analysis failed with {client_name}: {str(e)}")
                    continue
        
        return {"error": "All LLM clients failed to analyze target"}
    
    async def generate_payloads_with_fallback(self, vulnerability_type: str, target_info: Dict, preference: str = "gemini") -> List[str]:
        """Generate payloads with fallback"""
        for client_name in [preference] + [k for k in self.clients.keys() if k != preference]:
            if client_name in self.clients:
                try:
                    logger.info(f"Generating {vulnerability_type} payloads with {client_name}")
                    payloads = await self.clients[client_name].generate_payload(vulnerability_type, target_info)
                    if payloads:
                        return payloads
                except Exception as e:
                    logger.error(f"Payload generation failed with {client_name}: {str(e)}")
                    continue
        
        logger.error("All LLM clients failed to generate payloads")
        return []
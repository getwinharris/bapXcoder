"""
Web search functionality for bapXcoder IDE
Implements Google Antigravity-inspired web research capabilities
"""
import requests
import json
from typing import Dict, List, Optional
from urllib.parse import quote_plus
import os
import time

class WebSearchAgent:
    """
    Web search agent inspired by Google Antigravity capabilities
    Provides intelligent web research with result processing and context integration
    """
    
    def __init__(self):
        # Use Tavily API as the default search provider (free tier available)
        self.api_key = os.getenv('TAVILY_API_KEY', 'tvly-NO_API_KEY_PROVIDED')
        self.search_url = "https://api.tavily.com/search"
        # Fallback to Google Custom Search if needed
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID', '')
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"
        
    def search(self, query: str, max_results: int = 5, search_depth: str = "advanced") -> Dict:
        """
        Perform web search with intelligent result processing
        """
        # Try Tavily API first (better for AI applications)
        tavily_results = self._search_tavily(query, max_results, search_depth)
        if tavily_results and tavily_results.get('results'):
            return tavily_results
        
        # Fallback to Google Custom Search
        google_results = self._search_google(query, max_results)
        if google_results:
            return google_results
            
        # If both fail, return empty results
        return {
            'query': query,
            'results': [],
            'answer': 'No search results found. Please check your internet connection or API keys.',
            'sources': []
        }
    
    def _search_tavily(self, query: str, max_results: int = 5, search_depth: str = "advanced") -> Optional[Dict]:
        """
        Search using Tavily API (optimized for AI agents)
        """
        if not self.api_key or self.api_key == 'tvly-NO_API_KEY_PROVIDED':
            return None
            
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'api_key': self.api_key,
                'query': query,
                'max_results': max_results,
                'search_depth': search_depth,
                'include_answer': True,
                'include_images': False,
                'include_raw_content': False,
                'result_tbd': 'en'
            }
            
            response = requests.post(self.search_url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'query': query,
                    'results': result.get('results', []),
                    'answer': result.get('answer', ''),
                    'sources': [r.get('url', '') for r in result.get('results', [])]
                }
            else:
                print(f"Tavily API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in Tavily search: {str(e)}")
            return None
    
    def _search_google(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """
        Search using Google Custom Search API
        """
        if not self.google_api_key or not self.google_cse_id:
            return None
            
        try:
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': max_results
            }
            
            response = requests.get(self.google_search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                items = result.get('items', [])
                
                formatted_results = []
                for item in items:
                    formatted_results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'content': item.get('snippet', ''),
                        'source': item.get('displayLink', '')
                    })
                
                return {
                    'query': query,
                    'results': formatted_results,
                    'answer': '',
                    'sources': [item.get('link', '') for item in items]
                }
            else:
                print(f"Google API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in Google search: {str(e)}")
            return None
    
    def search_and_summarize(self, query: str, context: str = "") -> str:
        """
        Search the web and return a summary that integrates with the current context
        """
        try:
            results = self.search(query)

            if not results or not results.get('results'):
                return f"Could not find information about: {query}"

            # Format results for AI consumption
            summary = f"Search results for: '{query}'\n\n"

            if results.get('answer'):
                summary += f"Summary: {results['answer']}\n\n"

            summary += "Top results:\n"
            for i, result in enumerate(results['results'][:3], 1):
                title = result.get('title', 'No title')
                content = result.get('content', 'No content')
                url = result.get('url', 'No URL')

                summary += f"{i}. {title}\n"
                summary += f"   {content[:200]}...\n"
                summary += f"   Source: {url}\n\n"

            return summary
        except Exception as e:
            error_msg = f"Error in web search and summarization: {str(e)}"
            print(f"Web Search Error: {error_msg}")
            return f"Could not perform web search for '{query}': {str(e)}"


class AntigravityWebResearch:
    """
    Google Antigravity-inspired web research system
    Provides autonomous web research capabilities for AI agents
    """
    
    def __init__(self):
        self.search_agent = WebSearchAgent()
        self.search_history = []
        
    def conduct_research(self, query: str, context: str = "", max_iterations: int = 3) -> Dict:
        """
        Conduct in-depth web research similar to Google Antigravity
        """
        research_results = {
            'query': query,
            'context': context,
            'findings': [],
            'sources': [],
            'conclusion': '',
            'research_steps': []
        }
        
        # Initial search
        initial_results = self.search_agent.search_and_summarize(query, context)
        research_results['findings'].append({
            'step': 1,
            'query': query,
            'results': initial_results
        })
        
        # Additional research based on initial findings (if needed)
        iteration = 2
        current_query = query
        
        while iteration <= max_iterations:
            # In a real implementation, we would analyze the results and form new queries
            # For now, we'll just return the initial results
            break
            
        research_results['conclusion'] = self._generate_conclusion(research_results)
        research_results['research_steps'] = [f"Step {i}: Search for '{query}'"]  # Simplified
        
        return research_results
    
    def _generate_conclusion(self, research_results: Dict) -> str:
        """
        Generate a conclusion based on research findings
        """
        if not research_results['findings']:
            return "No research findings to summarize."
        
        # For now, return a simple summary of the first finding
        first_finding = research_results['findings'][0]
        return f"Research on '{research_results['query']}' completed. {first_finding['results'][:200]}..."

# Example usage and testing
if __name__ == "__main__":
    # Test the web search functionality
    agent = WebSearchAgent()
    
    # Example search
    results = agent.search("bapXcoder AI IDE features")
    print(json.dumps(results, indent=2))
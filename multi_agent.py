"""
Multi-Agent System for bapXcoder IDE
Implements Trae.ai SOLO-inspired multi-agent capabilities using a single model
"""
import json
from typing import Dict, List, Optional, Any
from enum import Enum


class AgentType(Enum):
    """Types of agents in the bapXcoder system"""
    PLANNER = "planner"
    CODER = "coder" 
    RESEARCHER = "researcher"
    TESTER = "tester"
    DEBUGGER = "debugger"
    ANALYZER = "analyzer"


class AgentContext:
    """Context for each agent instance"""
    def __init__(self, agent_type: AgentType, task_description: str, project_context: str = ""):
        self.agent_type = agent_type
        self.task_description = task_description
        self.project_context = project_context
        self.messages = []
        self.status = "initialized"
        self.results = []
        self.created_at = self._get_timestamp()
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
    
    def add_message(self, role: str, content: str):
        """Add a message to the agent's conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp()
        })
    
    def update_status(self, status: str):
        """Update the agent's status"""
        self.status = status


class MultiAgentSystem:
    """
    Multi-Agent system inspired by Trae.ai SOLO
    Uses a single model to simulate multiple specialized agents
    """
    
    def __init__(self, model_runner):
        self.model_runner = model_runner
        self.agents = {}
        self.agent_counter = 0
        
        # Agent system prompts for different specializations
        self.agent_prompts = {
            AgentType.PLANNER: """You are a PROJECT PLANNER agent. Your role is to:
- Break down complex tasks into smaller, manageable steps
- Create structured development plans
- Identify dependencies and potential roadblocks
- Suggest the best approach for implementation
- Provide timeline estimates when possible""",
            
            AgentType.CODER: """You are a CODE IMPLEMENTATION agent. Your role is to:
- Write clean, efficient, and well-documented code
- Follow best practices and coding standards
- Implement features based on specifications
- Create unit tests for your implementations
- Consider edge cases and error handling""",
            
            AgentType.RESEARCHER: """You are a RESEARCH agent. Your role is to:
- Find relevant information about technologies, frameworks, and APIs
- Research best practices and solutions to problems
- Gather information about current trends and standards
- Provide code examples and documentation references
- Analyze and summarize complex technical topics""",
            
            AgentType.TESTER: """You are a QUALITY ASSURANCE agent. Your role is to:
- Write comprehensive test cases for code
- Identify potential bugs and edge cases
- Verify that code meets requirements
- Suggest improvements for code quality
- Perform security and performance analysis""",
            
            AgentType.DEBUGGER: """You are a DEBUGGING agent. Your role is to:
- Analyze error messages and stack traces
- Identify the root cause of issues
- Suggest fixes for bugs and errors
- Provide step-by-step debugging instructions
- Recommend tools and techniques for debugging""",
            
            AgentType.ANALYZER: """You are a CODE ANALYSIS agent. Your role is to:
- Review code for quality, performance, and security issues
- Identify potential improvements
- Analyze code complexity and maintainability
- Provide refactoring suggestions
- Assess adherence to coding standards"""
        }
    
    def create_agent(self, agent_type: AgentType, task_description: str, project_context: str = "") -> str:
        """Create a new agent instance"""
        agent_id = f"agent_{self.agent_counter}"
        self.agent_counter += 1
        
        context = AgentContext(agent_type, task_description, project_context)
        self.agents[agent_id] = context
        
        return agent_id
    
    def execute_agent_task(self, agent_id: str, input_data: str, max_tokens: int = 1024) -> str:
        """Execute a task for a specific agent using the unified model"""
        try:
            if agent_id not in self.agents:
                return f"Error: Agent {agent_id} does not exist"

            agent_context = self.agents[agent_id]
            agent_type = agent_context.agent_type

            # Construct the prompt with agent specialization
            system_prompt = self.agent_prompts[agent_type]
            full_prompt = f"""{system_prompt}

Project Context:
{agent_context.project_context}

Current Task:
{agent_context.task_description}

Input:
{input_data}

Response:"""

            # Use the unified model to generate response for the specialized agent
            response = self.model_runner.run_interpreter_prompt(full_prompt, max_tokens=max_tokens)

            # Update agent context
            agent_context.add_message("user", input_data)
            agent_context.add_message("assistant", response)
            agent_context.results.append(response)

            return response
        except AttributeError as e:
            error_msg = f"Error: Model runner is not properly initialized: {str(e)}"
            print(f"Multi-Agent System Error: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Error executing task for {agent_type.value} agent: {str(e)}"
            print(f"Multi-Agent System Error: {error_msg}")
            return error_msg
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get the status and information of an agent"""
        if agent_id not in self.agents:
            return {"error": f"Agent {agent_id} does not exist"}
        
        agent_context = self.agents[agent_id]
        return {
            "id": agent_id,
            "type": agent_context.agent_type.value,
            "status": agent_context.status,
            "task": agent_context.task_description,
            "created_at": agent_context.created_at,
            "message_count": len(agent_context.messages),
            "result_count": len(agent_context.results)
        }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all active agents"""
        return [
            {
                "id": agent_id,
                "type": context.agent_type.value,
                "status": context.status,
                "task": context.task_description[:50] + "..." if len(context.task_description) > 50 else context.task_description
            }
            for agent_id, context in self.agents.items()
        ]
    
    def run_coordinated_task(self, task_description: str, project_context: str = "") -> Dict[str, Any]:
        """
        Run a coordinated task using multiple agents in sequence
        Similar to Trae.ai SOLO's coordinated approach
        """
        try:
            results = {
                "task": task_description,
                "agents_used": [],
                "steps": [],
                "final_result": "",
                "execution_log": []
            }

            # Step 1: Plan the task
            planner_id = self.create_agent(AgentType.PLANNER, task_description, project_context)
            results["agents_used"].append(planner_id)

            planning_result = self.execute_agent_task(planner_id, f"Create a detailed plan for: {task_description}")
            results["steps"].append({
                "step": "planning",
                "agent": planner_id,
                "result": planning_result
            })
            results["execution_log"].append(f"Planner agent created and executed task")

            # Step 2: Implement the plan (if it's a coding task)
            if any(keyword in task_description.lower() for keyword in ['code', 'implement', 'create', 'write', 'develop']):
                coder_id = self.create_agent(AgentType.CODER, f"Implement according to this plan: {planning_result}", project_context)
                results["agents_used"].append(coder_id)

                coding_result = self.execute_agent_task(coder_id, f"Based on this plan, implement the solution: {planning_result}")
                results["steps"].append({
                    "step": "coding",
                    "agent": coder_id,
                    "result": coding_result
                })
                results["execution_log"].append(f"Coder agent created and executed task")

                # Step 3: Test the implementation
                tester_id = self.create_agent(AgentType.TESTER, f"Test this implementation: {coding_result}", project_context)
                results["agents_used"].append(tester_id)

                testing_result = self.execute_agent_task(tester_id, f"Create tests and validate this code: {coding_result}")
                results["steps"].append({
                    "step": "testing",
                    "agent": tester_id,
                    "result": testing_result
                })
                results["execution_log"].append(f"Tester agent created and executed task")

            # Compile final result
            results["final_result"] = "\n\n".join([step["result"] for step in results["steps"]])

            return results
        except Exception as e:
            error_msg = f"Error in coordinated task execution: {str(e)}"
            print(f"Multi-Agent System Error: {error_msg}")
            return {
                "task": task_description,
                "agents_used": [],
                "steps": [],
                "final_result": error_msg,
                "execution_log": [error_msg]
            }


# Example usage
if __name__ == "__main__":
    # This would be used with the main model runner in the actual application
    print("Multi-Agent System for bapXcoder IDE")
    print("This module provides Trae.ai SOLO-inspired multi-agent capabilities")
    print("using a single unified model to simulate specialized agents.")
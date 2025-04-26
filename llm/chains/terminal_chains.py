from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional, Tuple
import json
import os
import re

from llm.prompts.terminal_prompts import (
    KUBERNETES_CLI_PROMPT,
    GIT_CLI_PROMPT,
    COMMAND_PARSER_PROMPT,
    STATE_UPDATE_PROMPT
)

class TerminalSimulationChain:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
            temperature=0.1  # Lower temperature for more consistent outputs
        )
        
        # Initialize the chains
        self.k8s_chain = LLMChain(
            llm=self.llm,
            prompt=KUBERNETES_CLI_PROMPT,
            verbose=True
        )
        
        self.git_chain = LLMChain(
            llm=self.llm,
            prompt=GIT_CLI_PROMPT,
            verbose=True
        )
        
        self.parser_chain = LLMChain(
            llm=self.llm,
            prompt=COMMAND_PARSER_PROMPT,
            verbose=True
        )
        
        self.state_update_chain = LLMChain(
            llm=self.llm,
            prompt=STATE_UPDATE_PROMPT,
            verbose=True
        )
    
    def detect_command_type(self, command: str) -> str:
        """Detect if the command is kubectl, git, or something else"""
        command = command.strip().lower()
        
        if command.startswith("kubectl") or command.startswith("k "):
            return "kubectl"
        elif command.startswith("git"):
            return "git"
        else:
            return "unknown"
    
    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse the command into structured components"""
        response = self.parser_chain.invoke({"command": command})
        
        try:
            # Extract JSON from response
            parsed = json.loads(response["text"])
            return parsed
        except (json.JSONDecodeError, KeyError):
            # Fallback parsing if LLM doesn't return valid JSON
            tool = self.detect_command_type(command)
            return {
                "tool": tool,
                "subcommand": "",
                "options": [],
                "args": [],
                "valid": tool != "unknown"
            }
    
    def process_command(self, 
                       command: str, 
                       environment_state: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Process a terminal command and return the output and updated state"""
        command_type = self.detect_command_type(command)
        parsed_command = self.parse_command(command)
        
        # Format environment state for prompt
        state_str = json.dumps(environment_state, indent=2)
        
        # Execute the appropriate chain based on command type
        if command_type == "kubectl":
            output = self.k8s_chain.invoke({
                "command": command,
                "environment_state": state_str
            })["text"]
            
            # Update environment state
            updated_state = self._update_environment_state(
                command,
                environment_state,
                output,
                "kubectl"
            )
            
        elif command_type == "git":
            output = self.git_chain.invoke({
                "command": command,
                "environment_state": state_str
            })["text"]
            
            # Update environment state
            updated_state = self._update_environment_state(
                command,
                environment_state,
                output,
                "git"
            )
            
        else:
            # Handle unknown commands
            output = f"Command not recognized. This environment supports kubectl and git commands."
            updated_state = environment_state
        
        return output, updated_state, parsed_command
    
    def _update_environment_state(self, 
                                 command: str, 
                                 current_state: Dict[str, Any],
                                 command_output: str,
                                 tool_type: str) -> Dict[str, Any]:
        """Update the environment state based on the command and output"""
        try:
            # Use the state update chain to determine changes
            response = self.state_update_chain.invoke({
                "command": command,
                "current_state": json.dumps(current_state, indent=2),
                "command_output": command_output,
                "tool_type": tool_type
            })
            
            # Try to parse the updated state
            state_updates = json.loads(response["text"])
            
            # Apply updates to current state
            updated_state = current_state.copy()
            self._apply_state_updates(updated_state, state_updates)
            
            return updated_state
            
        except (json.JSONDecodeError, KeyError, Exception) as e:
            # If there's an error, return the current state unchanged
            print(f"Error updating state: {str(e)}")
            return current_state
    
    def _apply_state_updates(self, 
                            current_state: Dict[str, Any], 
                            updates: Dict[str, Any]) -> None:
        """Apply nested updates to the current state"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in current_state and isinstance(current_state[key], dict):
                # Recursive update for nested dictionaries
                self._apply_state_updates(current_state[key], value)
            else:
                # Direct update for non-dict values or new keys
                current_state[key] = value
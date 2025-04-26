from typing import Dict, Optional, Any, Tuple
import uuid
from datetime import datetime

from app.models.terminal import TerminalRequest, TerminalResponse, TerminalSession
from llm.chains.terminal_chains import TerminalSimulationChain

class TerminalService:
    def __init__(self):
        # In-memory storage for terminal sessions
        # In production, you would use a database
        self.sessions: Dict[str, TerminalSession] = {}
        
        # Initialize terminal simulation chain
        self.terminal_chain = TerminalSimulationChain()
        
        # Default kubernetes environment state
        self.default_k8s_state = {
            "current_namespace": "default",
            "namespaces": ["default", "kube-system"],
            "pods": {
                "default": {
                    "nginx-pod": {
                        "status": "Running",
                        "ip": "10.0.0.2",
                        "containers": ["nginx"],
                        "labels": {"app": "nginx"}
                    }
                }
            },
            "deployments": {
                "default": {
                    "nginx-deployment": {
                        "replicas": 3,
                        "available": 3,
                        "containers": ["nginx:1.19"],
                        "labels": {"app": "nginx"}
                    }
                }
            },
            "services": {
                "default": {
                    "nginx-service": {
                        "type": "ClusterIP",
                        "ports": [{"port": 80, "targetPort": 80}],
                        "selector": {"app": "nginx"},
                        "clusterIP": "10.96.0.1"
                    }
                }
            }
        }
        
        # Default git environment state
        self.default_git_state = {
            "initialized": False,
            "current_branch": None,
            "branches": [],
            "commits": [],
            "staged_files": [],
            "modified_files": ["README.md", "app.py"],
            "untracked_files": ["data.json", "config.yml"]
        }
    
    async def process_command(self, request: TerminalRequest) -> TerminalResponse:
        """Process a terminal command and return the output"""
        # Get or create session
        session_id = request.session_id
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = TerminalSession(
                session_id=session_id,
                user_id=request.user_id,
                environment_state=self._create_default_environment()
            )
        
        session = self.sessions[session_id]
        
        # Process the command
        output, updated_state, parsed_command = self.terminal_chain.process_command(
            request.command,
            session.environment_state
        )
        
        # Update session state
        session.environment_state = updated_state
        session.updated_at = datetime.now()
        
        # Create and return response
        return TerminalResponse(
            output=output,
            success=not output.lower().startswith("error"),
            session_id=session_id,
            command_parsed=parsed_command
        )
    
    async def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def reset_session(self, session_id: str) -> bool:
        """Reset a session to default state"""
        if session_id not in self.sessions:
            return False
            
        session = self.sessions[session_id]
        user_id = session.user_id
        
        # Create a new session with default state
        self.sessions[session_id] = TerminalSession(
            session_id=session_id,
            user_id=user_id,
            environment_state=self._create_default_environment()
        )
        
        return True
    
    def _create_default_environment(self) -> Dict[str, Any]:
        """Create a default environment state with both k8s and git elements"""
        return {
            # K8s elements
            **self.default_k8s_state,
            # Git elements
            **self.default_git_state
        }
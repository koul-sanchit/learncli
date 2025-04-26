from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CommandType(str, Enum):
    KUBERNETES = "kubectl"
    GIT = "git"
    SHELL = "shell"

class TerminalRequest(BaseModel):
    command: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class TerminalResponse(BaseModel):
    output: str
    success: bool
    session_id: str
    command_parsed: Optional[Dict[str, Any]] = None

class TerminalSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    environment_state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # For K8s simulation
    current_namespace: str = "default"
    namespaces: list = Field(default_factory=lambda: ["default", "kube-system"])
    pods: Dict[str, Dict] = Field(default_factory=dict)
    deployments: Dict[str, Dict] = Field(default_factory=dict)
    services: Dict[str, Dict] = Field(default_factory=dict)
    
    # For Git simulation
    git_initialized: bool = False
    current_branch: str = "main"
    branches: list = Field(default_factory=lambda: ["main"])
    commits: list = Field(default_factory=list)
    staged_files: list = Field(default_factory=list)
    modified_files: list = Field(default_factory=list)
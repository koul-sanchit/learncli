from fastapi import APIRouter, HTTPException, Depends, Path
from typing import Optional

from app.models.terminal import TerminalRequest, TerminalResponse, TerminalSession
from app.services.terminal_service import TerminalService

router = APIRouter(prefix="/terminal", tags=["terminal"])

# Dependency to get the terminal service
def get_terminal_service() -> TerminalService:
    return TerminalService()

@router.post("/execute", response_model=TerminalResponse)
async def execute_command(
    request: TerminalRequest,
    terminal_service: TerminalService = Depends(get_terminal_service)
):
    """Execute a terminal command and return the output"""
    response = await terminal_service.process_command(request)
    return response

@router.get("/session/{session_id}", response_model=TerminalSession)
async def get_session(
    session_id: str,
    terminal_service: TerminalService = Depends(get_terminal_service)
):
    """Get terminal session state by ID"""
    session = await terminal_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session with ID {session_id} not found"
        )
    
    return session

@router.post("/session/{session_id}/reset")
async def reset_session(
    session_id: str,
    terminal_service: TerminalService = Depends(get_terminal_service)
):
    """Reset a terminal session to default state"""
    success = await terminal_service.reset_session(session_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session with ID {session_id} not found"
        )
    
    return {"session_id": session_id, "status": "reset"}

@router.post("/session/create")
async def create_session(
    user_id: Optional[str] = None,
    terminal_service: TerminalService = Depends(get_terminal_service)
):
    """Create a new terminal session"""
    # Create an empty request to generate a new session
    request = TerminalRequest(command="echo 'Session initialized'", user_id=user_id)
    response = await terminal_service.process_command(request)
    
    # Get the new session
    session = await terminal_service.get_session(response.session_id)
    
    return {
        "session_id": response.session_id,
        "status": "created",
        "session": session
    }
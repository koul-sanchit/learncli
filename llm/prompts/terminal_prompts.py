from langchain.prompts import PromptTemplate

# Base CLI simulation prompt
CLI_SIMULATION_BASE = """
You are simulating a command-line environment for {tool_type} commands. 
Generate accurate command output based on the virtual state described below.

CURRENT ENVIRONMENT STATE:
{environment_state}

USER COMMAND:
{command}

Instructions:
1. Parse the command and determine if it's valid
2. If invalid, return an appropriate error message that would appear in a real terminal
3. If valid, return the expected output based on the current environment state
4. Output should match the exact format and style of real {tool_type} command outputs
5. Don't include any explanations or comments outside of what would appear in a real terminal

Return ONLY the terminal output text, formatted exactly as it would appear in a real terminal.
"""

# Kubernetes CLI simulation prompt
KUBERNETES_CLI_PROMPT = PromptTemplate(
    input_variables=["environment_state", "command"],
    template=CLI_SIMULATION_BASE.replace("{tool_type}", "kubectl")
)

# Git CLI simulation prompt
GIT_CLI_PROMPT = PromptTemplate(
    input_variables=["environment_state", "command"],
    template=CLI_SIMULATION_BASE.replace("{tool_type}", "git")
)

# Command parser prompt to extract command details
COMMAND_PARSER_PROMPT = PromptTemplate(
    input_variables=["command"],
    template="""
Parse the following command into its structured components:
{command}

Return ONLY a JSON representation of the command with these fields:
1. "tool": The main tool being used (kubectl, git, etc.)
2. "subcommand": The specific subcommand (get, apply, commit, etc.)
3. "options": An array of option flags (like --namespace, -n, etc.)
4. "args": An array of positional arguments
5. "valid": Boolean indicating if this appears to be a valid command

Output the JSON structure and nothing else.
"""
)

# Environmental state update prompt 
STATE_UPDATE_PROMPT = PromptTemplate(
    input_variables=["command", "current_state", "command_output", "tool_type"],
    template="""
Given the executed {tool_type} command and its output, update the virtual environment state.

CURRENT STATE:
{current_state}

EXECUTED COMMAND:
{command}

COMMAND OUTPUT:
{command_output}

Instructions:
1. Analyze how this command would modify the state of a real {tool_type} environment
2. Return a JSON representation of the UPDATED state
3. Include only changes and elements that need to be updated, don't repeat unchanged values
4. Be precise and accurate to how real {tool_type} commands modify state

Return ONLY the JSON representation of state changes.
"""
)
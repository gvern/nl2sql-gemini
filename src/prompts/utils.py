# src/prompts/utils.py

def get_prompt(version: str = "v1") -> str:
    if version == "v2":
        from .prompt_v2 import SYSTEM_INSTRUCTION_V2
        return SYSTEM_INSTRUCTION_V2
    else:
        from .prompt_v1 import SYSTEM_INSTRUCTION
        return SYSTEM_INSTRUCTION

from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    # The original request or prompt from the user
    research_topic: str
    
    # Accumulated research material: List of dicts containing source urls and scraped text chunks
    research_sources: List[Dict[str, str]]
    
    # List of queries that have already been executed (to avoid search loops)
    performed_queries: List[str]
    
    # The current working draft of the document
    current_draft: str
    
    # Feedback from the critic agent
    critique: str
    
    # Track the current revision turn count to avoid infinite loop revisions
    revision_count: int

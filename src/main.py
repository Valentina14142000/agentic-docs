
import sys
from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.agents.researcher import web_search, scrape_webpage
from src.agents.writer import writer_agent
from src.agents.critic import critic_agent

# ==========================================
# 1. Define Node Wrappers
# ==========================================

def research_node(state: AgentState) -> dict:
    """
    Executes search queries based on the topic, scrapes the results, 
    and updates the state with verified source content.
    """
    topic = state["research_topic"]
    print(f"\n🚀 [Researcher] Starting deep research on: '{topic}'")
    
    # 1. Find top articles
    search_query = f"{topic} deep dive research analysis"
    search_results = web_search(search_query, max_results=3)
    
    scraped_sources = []
    executed_queries = list(state.get("performed_queries", []))
    executed_queries.append(search_query)

    # 2. Scrape details from each found source
    for idx, res in enumerate(search_results, start=1):
        url = res["url"]
        print(f"   ↳ Scaping Source [{idx}]: {url}")
        content = scrape_webpage(url, max_chars=4000)
        
        scraped_sources.append({
            "url": url,
            "snippet": content
        })
        
    return {
        "research_sources": scraped_sources,
        "performed_queries": executed_queries,
        "revision_count": 0
    }

def writer_node(state: AgentState) -> dict:
    print("\n✍️  [Writer] Drafting document based on gathered sources...")
    return writer_agent(state)

def critic_node(state: AgentState) -> dict:
    print("\n🧐 [Critic] Reviewing current draft...")
    return critic_agent(state)

# ==========================================
# 2. Define Conditional Routing Logic
# ==========================================

def route_after_critique(state: AgentState) -> str:
    """
    Decides whether to route the workflow to END or loop back for a rewrite.
    """
    critique = state.get("critique", "").strip()
    rev_count = state.get("revision_count", 0)
    
    # Base Case 1: Approved by Critic
    if "APPROVED" in critique.upper():
        print("\n✅ [System] Editorial approval granted! Finalizing report...")
        return "complete"
    
    # Base Case 2: Max revisions reached (safeguard against infinite API spend)
    if rev_count >= 2:
        print("\n⚠️  [System] Revision ceiling (2) reached. Finalizing with current draft.")
        return "complete"
    
    # Loop Case: Rewrite needed
    print(f"\n🔄 [System] Critique feedback received. Sending back for Revision {rev_count + 1}...")
    state["revision_count"] = rev_count + 1
    return "rewrite"

# ==========================================
# 3. Build & Compile the StateGraph
# ==========================================

# Initialize the stateful builder
builder = StateGraph(AgentState)

# Register our task processors (nodes)
builder.add_node("researcher", research_node)
builder.add_node("writer", writer_node)
builder.add_node("critic", critic_node)

# Set up physical transitions
builder.add_edge(START, "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "critic")

# Set up dynamic/conditional routing out of the critic node
builder.add_conditional_edges(
    "critic",
    route_after_critique,
    {
        "complete": END,
        "rewrite": "writer"  # Loops back to the writer node with critique state populated
    }
)

# Compile into an executable binary application
app = builder.compile()

# ==========================================
# 4. Entry Point / CLI Execution
# ==========================================

if __name__ == "__main__":
    print("==================================================")
    print("        AGENTIC DOCS - MULTI-AGENT PIPELINE       ")
    print("==================================================")
    
    # Fallback default if no CLI arguments are supplied
    default_topic = "Latest breakthroughs in Room Temperature Superconductors 2026"
    topic = sys.argv[1] if len(sys.argv) > 1 else default_topic
    
    initial_state = {
        "research_topic": topic,
        "research_sources": [],
        "performed_queries": [],
        "current_draft": "",
        "critique": "",
        "revision_count": 0
    }
    
    # Run the compiled agentic app
    final_output = app.invoke(initial_state)
    
    print("\n==================================================")
    print("              FINAL MARKDOWN REPORT               ")
    print("==================================================")
    print(final_output["current_draft"])
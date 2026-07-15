# src/agents/writer.py
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import DEFAULT_GEMINI_MODEL, settings
from src.state import AgentState


def _fallback_writer_content(state: AgentState) -> str:
    topic = state.get("research_topic", "research topic")
    sources = state.get("research_sources", [])
    source_count = len(sources)
    intro = f"## Report on {topic}\n\n"
    intro += "This draft was generated from the available research sources because the Gemini API was unavailable at generation time."
    intro += f"\n\nCollected sources: {source_count}."
    if sources:
        intro += "\n\n### Key sources\n"
        for idx, source in enumerate(sources[:3], 1):
            intro += f"- [{idx}] {source.get('url', 'unknown source')}\n"
    return intro


def _build_writer_llm(temperature: float):
    candidates = [settings.model_name, DEFAULT_GEMINI_MODEL, "gemini-2.0-flash-lite"]
    last_error = None

    for model_name in candidates:
        try:
            return ChatGoogleGenerativeAI(
                google_api_key=settings.openai_api_key,
                model=model_name,
                temperature=temperature,
            )
        except Exception as exc:
            last_error = exc

    raise last_error or RuntimeError("Unable to initialize Gemini client")


def writer_agent(state: AgentState) -> dict:
    """
    Synthesizes the gathered research sources into a highly structured, 
    professional markdown report with proper citations using Google Gemini.
    """
    llm = _build_writer_llm(settings.temperature)
    
    # Format the accumulated research documents for the prompt context
    sources_context = ""
    for idx, source in enumerate(state.get("research_sources", []), 1):
        sources_context += f"\n--- Source [{idx}]: {source['url']} ---\n{source['snippet']}\n"

    prompt = f"""You are an elite Technical Writer. Your task is to synthesize the following research materials into a comprehensive, publication-ready markdown report on the topic: "{state['research_topic']}".

### Research Materials:
{sources_context}

### Strict Writing Guidelines:
1. **Structure**: Use clear Markdown headings (`##`, `###`). Include an Executive Summary, Detailed Analysis, Key Takeaways, and a Future Outlook section.
2. **Citations**: Cite facts back to the source materials using inline bracketed numbers corresponding to the source index (e.g., [1], [2]). 
3. **Accuracy**: Stick strictly to facts in the provided source material. Do not hallucinate or extrapolate.
4. **References**: Provide a clean "References" section at the very end of your document mapping each bracketed citation number to its respective URL.

Write the complete markdown report below:
"""
    try:
        response = llm.invoke(prompt)
        draft = response.content
    except Exception as exc:
        print(f"Writer fallback triggered: {exc}")
        draft = _fallback_writer_content(state)
    
    # Return updates to the shared State
    return {"current_draft": draft}
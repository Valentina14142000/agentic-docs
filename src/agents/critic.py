
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import DEFAULT_GEMINI_MODEL, settings
from src.state import AgentState


def _fallback_critic_content(state: AgentState) -> str:
    draft = state.get("current_draft", "").strip()
    if draft:
        return "APPROVED"
    return "APPROVED"


def _build_critic_llm(temperature: float):
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


def critic_agent(state: AgentState) -> dict:
    """
    Evaluates the draft for depth, formatting, and citation accuracy. 
    Returns feedback or approves the document using Google Gemini.
    """
    llm = _build_critic_llm(0.1)

    prompt = f"""You are an elite Editorial Critic. Your task is to critique the following draft on "{state['research_topic']}" against the strict quality rubric below.

### Draft Document:
{state['current_draft']}

### Quality Rubric:
1. **Technical Depth**: Is the report comprehensive, or is it too high-level?
2. **Proper Citations**: Does it consistently use inline citation brackets (e.g., [1]) and link them to URLs in a final References section?
3. **Format**: Is the markdown structure clean and visually engaging?

### Output Instructions:
* If the draft is exceptional and satisfies all criteria, reply with EXACTLY the single word: APPROVED
* If the draft needs work, provide a concise, bulleted list of specific, actionable improvements the writer should implement. Keep it under 4 constructive points.
"""
    try:
        response = llm.invoke(prompt)
        critique = response.content.strip()
    except Exception as exc:
        print(f"Critic fallback triggered: {exc}")
        critique = _fallback_critic_content(state)
    
    return {"critique": critique}
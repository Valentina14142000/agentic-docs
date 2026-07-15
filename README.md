# agentic-docs

An autonomous multi-agent research and document drafting system using LangGraph and Google Gemini.


**Created by [Valentina Kiyungi](https://github.com/Valentina14142000)**

---

## 🏗️ How It Works

[Researcher] ──> [Writer] ──> [Critic] ──> [Approved Draft]
▲           │
└── Feedback┘


1. **Researcher**: Scrapes the web (DuckDuckGo API) for facts.
2. **Writer**: Drafts a structured markdown report with inline citations.
3. **Critic**: Reviews the draft. If it needs work, loops back with feedback; otherwise, approves and saves.

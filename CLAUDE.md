# AI Site Analyzer — Working Agreement

## Context
Home assignment for a QA/AI engineering position. Deadline: ~5 days.
I will be evaluated on architecture, testing quality, and my ability to
explain and modify every line of code live during a technical interview.

## Non-negotiable rules
- Explain a file's purpose and structure BEFORE writing it. Wait for my approval.
- Prefer the simplest implementation that satisfies the requirement.
- No library unless its value fits in one sentence.
- No magic: no metaprogramming, no clever one-liners, no hidden state.
- One class = one responsibility.
- Comments explain WHY, not WHAT.
- If something I ask for is over-engineered, say so explicitly.
- Never generate multiple files at once unless I ask.
- After each step, report: completed / remaining / does it meet the spec.

## Stack (decided — do not propose alternatives)
Backend:  FastAPI, SQLAlchemy, SQLite, Pydantic, Pillow, numpy
Frontend: React + Vite, Material UI, React Router, Axios, Recharts
Testing:  Playwright (Python sync API), requests
Agents:   Plain Python classes. NO LangGraph, NO CrewAI.
LLM:      Abstract LLMClient interface. MockLLMClient is the default.
          GeminiLLMClient is an optional adapter enabled via .env.

## Explicitly out of scope
Authentication, Alembic migrations, real ML models (torch/YOLO),
cloud deployment, production scalability, separate LLM per agent.

## Key design decisions (already made — implement, don't re-debate)
1. Analyzers use the Strategy pattern behind one shared interface.
2. Mock analyzers are DETERMINISTIC — seeded from the image hash — so the
   agentic test suite can assert expected vs actual results.
3. Image Quality Assessment is a REAL algorithm (Laplacian variance for blur,
   mean brightness for darkness) using Pillow + numpy only.
4. Test cases carry a "type" field: "api" or "ui". The Execution Agent
   dispatches to ApiRunner or UiRunner. Most tests are API for speed/stability.
5. Docker covers backend + frontend only. The agentic test suite runs on the
   host and targets a base URL from .env.
6. React Router: Declarative Mode ONLY (<BrowserRouter> + <Routes> + <Route>).
   No loaders, no actions, no RSC APIs. All route paths are static string
   literals, never built from user input. Reason: react-router-dom@7.18.2
   has one open high-severity audit finding (GHSA-qwww-vcr4-c8h2), but it
   only applies to the unstable RSC APIs, patched only in the 8.x line.
   Staying on Declarative Mode keeps the app outside that vulnerable code
   path without forcing a major-version upgrade. Revisit if the project
   ever needs loaders/actions/RSC.

## Communication style
Explain in Hebrew. Code, identifiers, comments and docs in English.
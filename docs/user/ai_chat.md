# Using AI Chat

ScholarOS provides an interactive AI conversational workspace designed specifically for researchers. This guide covers how to conduct multi-turn research conversations, manage context, and switch models.

---

## 1. Accessing the Chat Workspace

### Desktop GUI
1. Launch ScholarOS (`scholaros gui` or double-click `run_scholaros.bat`).
2. Click **AI Chat** on the left navigation sidebar or select **Chat** from the Welcome screen.
3. The Chat workspace displays:
   - Conversation history stream
   - Message input area
   - Active provider/model status bar
   - Grounded context badge (when RAG is active)

### Terminal Quick Prompt
You can execute one-off questions directly from the terminal without launching the full GUI:
```bash
scholaros run "What are the core differences between transformer decoders and encoders?"
```

---

## 2. Conversation Features

### Multi-Turn Context
The chat session maintains conversational state across turns. You can refer to previous papers, concepts, or formulas:
- **User**: "What is the attention mechanism in transformers?"
- **Assistant**: [Provides explanation]
- **User**: "How does multi-head attention improve on this?"
- **Assistant**: [Explains multi-head attention building upon the prior response]

### Asynchronous Execution & Responsiveness
When generating answers, the Desktop GUI dispatches inference requests to a background thread pool (`execute_async`). The application interface remains smooth and responsive without freezing during long local model generation cycles.

### System Prompts & Guardrails
ScholarOS automatically applies research-focused system prompt templates (`scholaros.ai.prompt.templates.ResearchAssistantTemplate`):
- Academic citations and grounded claims are prioritized.
- Speculation is clearly labeled.
- Retrieval boundaries are enforced to prevent hallucinations.

Next Step: Discover how to run deep academic literature searches in the [Research Workflow Guide](research_workflow.md).

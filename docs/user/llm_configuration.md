# LLM & AI Provider Configuration

ScholarOS supports both local-first offline inference and leading cloud AI model providers. This guide explains how to configure Ollama, OpenAI, Anthropic, Google Gemini, OpenRouter, and testing mock providers.

---

## 1. Provider Overview

| Provider | Type | Recommended Models | Environment Variable |
|---|---|---|---|
| **Ollama** | Local / Offline | `qwen2.5:1.5b`, `llama3.2:3b`, `deepseek-r1:1.5b` | None (`http://localhost:11434`) |
| **OpenAI** | Cloud API | `gpt-4o`, `gpt-4o-mini`, `o3-mini` | `OPENAI_API_KEY` |
| **Anthropic** | Cloud API | `claude-3-7-sonnet-latest`, `claude-3-5-haiku` | `ANTHROPIC_API_KEY` |
| **Google Gemini** | Cloud API | `gemini-2.5-flash`, `gemini-2.5-pro` | `GEMINI_API_KEY` |
| **OpenRouter** | Cloud Aggregator | Any model via OpenRouter catalog | `OPENROUTER_API_KEY` |
| **Mock** | In-Memory Testing | Deterministic canned responses | None |

---

## 2. Local-First AI with Ollama (Default & Recommended)

ScholarOS defaults to local inference via **Ollama**, ensuring complete data privacy for your academic papers and research notes.

### Step 1: Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com).

### Step 2: Pull a Compact Research Model
```bash
# Recommended fast model:
ollama pull qwen2.5:1.5b

# Or Llama 3.2:
ollama pull llama3.2:3b
```

### Step 3: Configure `config.toml`
Open `%APPDATA%\ScholarOS\config\config.toml` (Windows) or `~/.config/scholaros/config.toml` (Linux/macOS):

```toml
[ai]
default_provider = "ollama"
default_model = "qwen2.5:1.5b"
base_url = "http://localhost:11434"
temperature = 0.2
timeout_seconds = 60.0
```

---

## 3. Cloud Provider Configuration

### OpenAI Configuration
Set your API key in your environment or `.env` file:
```bash
export OPENAI_API_KEY="sk-..."
# On Windows PowerShell:
$env:OPENAI_API_KEY="sk-..."
```
In `config.toml`:
```toml
[ai]
default_provider = "openai"
default_model = "gpt-4o-mini"
temperature = 0.2
```

### Anthropic Configuration
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
In `config.toml`:
```toml
[ai]
default_provider = "anthropic"
default_model = "claude-3-5-haiku-20241022"
```

### Google Gemini Configuration
```bash
export GEMINI_API_KEY="AIza..."
```
In `config.toml`:
```toml
[ai]
default_provider = "google"
default_model = "gemini-2.5-flash"
```

---

## 4. Testing with Mock Provider

For testing or running ScholarOS in offline environments without downloading local models:
```bash
scholaros run "Summarize quantum computing" --provider mock
```
The mock provider returns structured dummy responses immediately, enabling full verification of pipelines and user interfaces.

Next Step: Learn how to chat with your configured models in the [AI Chat Guide](ai_chat.md).

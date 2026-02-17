# Kivy AI Chat Assistant - Design Document

**Date:** 2026-02-18
**Status:** Approved

## Overview

A cross-platform AI chat assistant application built with Kivy and KivyMD, featuring a ChatGPT-style interface. The app supports multiple AI service providers (OpenAI, DeepSeek, etc.), multi-conversation management, configuration persistence, and Markdown rendering.

## Requirements

| Category | Requirement |
|----------|-------------|
| **UI Style** | ChatGPT-style interface |
| **Core Function** | Real AI chat assistant |
| **AI Service** | Configurable (OpenAI, DeepSeek, etc.) |
| **Extra Features** | Multi-conversation management, config persistence, Markdown rendering |

## Project Structure

```
kivy_ai_chat/
├── main.py                 # Application entry point
├── api/
│   ├── __init__.py
│   ├── base.py            # AI service base class
│   ├── openai_client.py   # OpenAI adapter
│   ├── deepseek_client.py # DeepSeek adapter
│   └── config.py          # API configuration management
├── ui/
│   ├── __init__.py
│   ├── main_screen.py     # Main chat interface
│   ├── chat_bubble.py     # Message bubble component
│   ├── settings_screen.py # Settings interface
│   └── history_screen.py  # Conversation history interface
├── data/
│   ├── __init__.py
│   ├── storage.py         # Local storage management
│   └── models.py          # Data models
└── assets/
    ├── fonts/             # Chinese fonts
    └── icons/             # Icon resources
```

## UI Design

### Main Chat Screen

```
┌─────────────────────────────────────┐
│  ☰  AI Chat              ⚙️  🗑️    │ ← Top Bar
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ User message ────────▶│   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ◀────────── AI response     │   │
│  │  (Markdown rendered)        │   │
│  └─────────────────────────────┘   │
│         ↑                      ↑    │
│      Scrollable message list      │
│                                     │
├─────────────────────────────────────┤
│  [Enter message...]            [Send]│ ← Bottom input
└─────────────────────────────────────┘
```

### Components

| Component | KivyMD Implementation | Purpose |
|-----------|----------------------|---------|
| Top Bar | `MDTopAppBar` | Title, menu, settings button |
| Message List | `MDRecycleView` | High-performance scroll |
| Message Bubble | Custom `MDBoxLayout` | User/AI styled messages |
| Input Field | `MDTextField` | Multi-line text input |
| Send Button | `MDFloatingActionButton` | Send message |
| Markdown | `kivy_garden.markdown` | AI response formatting |

### Additional Screens

- **History Screen:** Side drawer showing conversation list
- **Settings Screen:** API provider, key input, model selection, clear data

## Technology Stack

```txt
# Core
kivy==2.3.0                    # UI framework
kivymd==1.2.0                  # Material Design components
plyer==2.1.0                   # Platform native features

# AI API
openai==1.12.0                 # OpenAI SDK
requests==2.31.0               # HTTP requests

# Markdown
kivy-garden.markdown           # Markdown support
markdownify==0.11.6            # HTML to Markdown

# Storage
tinydb==4.8.0                  # Lightweight JSON database

# Build
buildozer==1.5.0               # Android packaging
```

## Data Storage

Using TinyDB (lightweight JSON database):

```json
{
  "conversations": [
    {
      "id": "uuid-1",
      "title": "First Conversation",
      "created_at": "2026-02-18T10:00:00",
      "messages": [
        {"role": "user", "content": "Hello", "timestamp": "..."},
        {"role": "assistant", "content": "Hi! How can I help?", "timestamp": "..."}
      ]
    }
  ],
  "settings": {
    "api_provider": "openai",
    "api_key": "sk-***",
    "model": "gpt-3.5-turbo",
    "current_conversation_id": "uuid-1"
  }
}
```

Storage location: `App.user_data_dir()`

## Data Flow

```
User Input
     │
     ▼
┌─────────────┐
│  UI Layer   │  Display user message
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Data Manager │  Save to local
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ API Client  │  Send to AI service
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ AI Response │  Receive streaming
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  UI Update  │  Display character by character
└─────────────┘
```

### Key Flows

1. **Send:** User input → UI display → Local save → API call
2. **Receive:** Streaming response → Character-by-character UI → Save
3. **Switch:** Load history → Rebuild chat list
4. **Error:** Network error → API key validation → Retry

## Android Packaging

```bash
buildozer init          # Initialize config
buildozer android debug # Debug APK
buildozer android release # Release APK
```

## Summary

| Aspect | Choice |
|--------|--------|
| Framework | Kivy + KivyMD |
| Architecture | MVC separation |
| Storage | TinyDB + JSON |
| API | Adapter pattern, multi-AI support |
| Build | Buildozer |

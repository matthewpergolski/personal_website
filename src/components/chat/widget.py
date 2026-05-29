"""
Front-end Chat Widget Component

Interactive chat widget connected to the RAG (Retrieval-Augmented Generation) API.
Provides real-time conversational interface for visitors to ask about the portfolio owner's
background, experience, and projects using AI-powered responses.
"""

import fasthtml.common as ft
from fasthtml.common import Div, Button, Input, H3, P, Span, Form, Textarea, Script, Style
from typing import List, Dict, Any, Optional
import json
import time


class ChatWidget:
    """
    Interactive chat widget for portfolio website.

    Provides:
    - Real-time chat interface
    - Integration with RAG API (/api/rag/chat)
    - Message history and conversation state
    - Loading states and error handling
    - Responsive design matching portfolio theme
    - Analytics tracking
    """

    def __init__(self,
                 api_endpoint: str = "/api/rag/chat",
                 max_messages: int = 50,
                 greeting: Optional[str] = None,
                 suggested_questions: Optional[List[str]] = None):
        """
        Initialize the chat widget.

        Args:
            api_endpoint: RAG API endpoint URL
            max_messages: Maximum messages to retain in history
            greeting: Custom welcome message
            suggested_questions: List of suggested questions to show initially
        """
        self.api_endpoint = api_endpoint
        self.max_messages = max_messages
        self.greeting = greeting or self._get_default_greeting()
        self.suggested_questions = suggested_questions or self._get_default_suggested_questions()

    def _get_default_suggested_questions(self) -> List[str]:
        """Get default suggested questions."""
        return [
            "What Python experience do you have?",
            "Can you tell me about your ML projects?",
            "How do you handle data visualization?",
            "What's your background in AI/ML?",
            "What are your recent projects?"
        ]

    def _get_default_greeting(self) -> str:
        """Get default greeting message."""
        return "Hi! I'm excited to chat about my experience in AI/ML engineering, Python development, or my work in manufacturing automation. What would you like to know?"

    def render(self) -> ft:
        """
        Render the complete chat widget components.

        Returns:
            Tuple of FastHTML components (CSS, Script, container)
        """
        return (
            # CSS styles first
            self._render_styles(),

            # Script before widget div
            self._render_scripts(),

            # Main widget container
            Div(
                self._render_chat_container(),
                id="chat-widget-container",
                cls="chat-widget-fixed-container"
            ),
        )

    def _render_chat_container(self) -> ft:
        """Render the main chat interface."""
        return Div(
            # Chat toggle button (floating)
            self._render_toggle_button(),

            # Chat window
            self._render_chat_window(),

            # Global attributes
            id="chat-widget",
            cls="chat-widget"  # Default to visible
        )

    def _render_toggle_button(self) -> ft:
        """Render floating chat toggle button."""
        return Button(
            "💬 Chat",
            id="chat-toggle",
            cls="chat-toggle-btn",
            type="button",
            onclick="toggleChatWidget()",
            aria_label="Open chat conversation"
        )

    def _render_chat_window(self) -> ft:
        """Render the main chat window."""
        return Div(
            # Header
            self._render_header(),

            # Messages container
            self._render_messages_area(),

            # Input area
            self._render_input_area(),

            # Hidden inputs for state
            Input(
                type="hidden",
                id="chat-conversation-id",
                value=f"conv_{int(time.time())}"
            ),
            Input(
                type="hidden",
                id="chat-user-context",
                value='{"tech_level": "intermediate", "urgency": "normal"}'
            ),

            cls="chat-window",
            id="chat-window"
        )

    def _render_header(self) -> ft:
        """Render chat header with close button."""
        return Div(
            Div(
                H3("AI Chat Assistant", cls="chat-header-title"),
                P("Ask me about my experience", cls="chat-header-subtitle"),
                cls="chat-header-info"
            ),
            Button(
                "×",
                id="chat-close",
                cls="chat-close-btn",
                type="button",
                onclick="toggleChatWidget()",
                aria_label="Close chat"
            ),
            cls="chat-header"
        )

    def _render_messages_area(self) -> ft:
        """Render scrollable messages area."""
        return Div(
            # Initial welcome message
            Div(
                Div(
                    Div("🤖", cls="chat-avatar bot-avatar"),
                    cls="chat-message-avatar"
                ),
                Div(
                    P(self.greeting, cls="chat-message-text"),
                    cls="chat-message-content"
                ),
                cls="chat-message bot-message",
                data_timestamp=str(int(time.time())),
                data_type="greeting"
            ),

            # Loading indicator (hidden initially)
            Div(
                Div(
                    Div("🤖", cls="chat-avatar bot-avatar typing-avatar"),
                    cls="chat-message-avatar"
                ),
                Div(
                    Div("Thinking", cls="typing-indicator"),
                    Div("⠋", cls="typing-dots"),
                    cls="chat-message-content"
                ),
                cls="chat-loading chat-hidden",
                id="chat-loading"
            ),

            # Suggested questions (shown initially)
            self._render_suggested_questions(),

            # Scrollable container attributes
            id="chat-messages",
            cls="chat-messages"
        )

    def _render_input_area(self) -> ft:
        """Render message input and send controls."""
        return Div(
            self._render_typing_notice(),
            self._render_input_form(),
            cls="chat-input-area"
        )

    def _render_suggested_questions(self) -> ft:
        """Render suggested questions section."""
        if not self.suggested_questions:
            return Div()

        question_buttons = []
        for i, question in enumerate(self.suggested_questions):
            question_buttons.append(
                Button(
                    question,
                    cls="chat-suggestion-btn",
                    type="button",
                    onclick="sendSuggestedQuestion(this)",
                    data_question=question,
                    id=f"chat-suggestion-{i}"
                )
            )

        return Div(
            Div(
                Div("💡 Suggested topics:", cls="chat-suggestions-header"),
                Div(*question_buttons, cls="chat-suggestions-buttons"),
                cls="chat-suggestions-content"
            ),
            cls="chat-suggestions",
            id="chat-suggestions"
        )

    def _render_typing_notice(self) -> ft:
        """Render typing privacy notice."""
        return Div(
            P("💭 Your conversation is private and temporary", cls="typing-notice"),
            cls="chat-notice"
        )

    def _render_input_form(self) -> ft:
        """Render message input form."""
        return Form(
            Div(
                Textarea(
                    "",
                    id="chat-input",
                    name="message",
                    placeholder="Ask about my experience...",
                    maxlength="500",
                    rows="1",
                    cls="chat-textarea",
                    onkeypress="handleEnterKey(event)",
                    aria_label="Type your message"
                ),
                Button(
                    "Send",
                    id="chat-send-btn",
                    cls="chat-send-btn",
                    type="submit",
                    disabled="disabled",
                    onclick="sendMessage(event)",
                    aria_label="Send message"
                ),
                cls="chat-input-group"
            ),

            # Hidden context fields
            Input(type="hidden", name="context[tech_level]", value="intermediate"),
            Input(type="hidden", name="context[urgency]", value="normal"),

            id="chat-form",
            cls="chat-form",
            action=self.api_endpoint,
            method="POST",
            onsubmit="sendMessage(event)"
        )

    def _render_styles(self) -> ft:
        """Render comprehensive CSS styles for the chat widget with professional styling."""
        return Style("""
            /* Chat Widget Base Styles - Professional Design */
            .chat-widget-fixed-container {
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 9999;
                font-family: inherit;
            }

            .chat-toggle-btn {
                width: 64px;
                height: 64px;
                border-radius: 50%;
                background: var(--primary-color);
                color: white;
                border: none;
                cursor: pointer;
                z-index: 10001;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 6px 20px rgba(0,0,0,0.2);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                font-size: 22px;
            }

            .chat-toggle-btn:hover {
                transform: translateY(-2px) scale(1.05);
                box-shadow: 0 8px 25px rgba(0,0,0,0.25);
                background: #166ae5;
            }

            .chat-widget {
                width: min(420px, calc(100vw - 48px));
                height: min(580px, calc(100vh - 120px));
                background: var(--surface-1);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.15), 0 8px 32px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                font-size: 14px;
                line-height: 1.5;
                position: relative;
                left: 50%;
                transform: translateX(-50%);
                margin: 20px 0;
            }

            /* Centering adjustments */
            .chat-widget-fixed-container {
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 9999;
                font-family: inherit;
                /* Remove centering for fixed container */
            }

            .chat-widget-fixed-container .chat-widget {
                left: auto;
                transform: none;
                margin: 0;
            }

            /* Dark theme adjustments */
            html[data-theme='dark'] .chat-widget {
                background: var(--surface-1);
                border-color: var(--border-color);
                box-shadow: 0 20px 60px rgba(0,0,0,0.25), 0 8px 32px rgba(0,0,0,0.2);
            }

            .chat-widget-hidden {
                transform: translateY(20px) scale(0.95);
                opacity: 0;
                pointer-events: none;
                display: none !important;
            }

            .chat-widget-visible {
                transform: translateY(0) scale(1);
                opacity: 1;
            }

            .chat-widget-visible {
                transform: translateY(0) scale(1);
                opacity: 1;
            }

            /* Toggle Button */
            .chat-toggle-btn {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: var(--primary-color);
                color: white;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transition: all 0.2s ease;
                font-size: 20px;
                z-index: 10001;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .chat-toggle-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.2);
                background: #1d4ed8;
            }

            .chat-toggle-btn:active {
                transform: scale(0.95);
            }

            /* Header */
            .chat-header {
                padding: 16px 20px;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                background: var(--surface-1);
                border-radius: 16px 16px 0 0;
            }

            .chat-header-title {
                margin: 0 0 4px 0;
                font-size: 16px;
                color: var(--text-color);
            }

            .chat-header-subtitle {
                margin: 0;
                font-size: 12px;
                color: var(--muted-text);
            }

            .chat-close-btn {
                width: 28px;
                height: 28px;
                border: none;
                background: transparent;
                color: var(--muted-text);
                cursor: pointer;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.15s ease;
            }

            .chat-close-btn:hover {
                background: var(--surface-2);
                color: var(--text-color);
            }

            /* Messages Area */
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                scroll-behavior: smooth;
            }

            .chat-message {
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
                animation: messageIn 0.3s ease-out;
            }

            @keyframes messageIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .chat-message-avatar {
                flex-shrink: 0;
            }

            .chat-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                border: 2px solid var(--border-color);
            }

            .bot-avatar {
                background: var(--primary-color);
                color: white;
            }

            .user-avatar {
                background: var(--accent-color);
                color: var(--dark-color);
            }

            .chat-message-content {
                flex: 1;
                padding: 12px 16px;
                border-radius: 12px;
                position: relative;
            }

            .bot-message .chat-message-content {
                background: var(--surface-2);
                border: 1px solid var(--border-color);
            }

            .user-message .chat-message-content {
                background: var(--primary-color);
                color: white;
                text-align: right;
            }

            .user-message {
                flex-direction: row-reverse;
            }

            .chat-message-text {
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }

            /* Loading/Typing Indicator */
            .chat-loading {
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
            }

            .typing-avatar::after {
                content: "";
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--primary-color);
                animation: typingPulse 1.5s ease-in-out infinite;
            }

            @keyframes typingPulse {
                0%, 100% { opacity: 0.3; }
                50% { opacity: 1; }
            }

            .typing-indicator {
                color: var(--muted-text);
                font-style: italic;
            }

            .typing-dots {
                display: inline-block;
                animation: typingDots 1.5s ease-in-out infinite;
            }

            @keyframes typingDots {
                0%, 20% { content: "⠋"; }
                40% { content: "⠙"; }
                60% { content: "⠹"; }
                80% { content: "⠸"; }
                100% { content: "⠼"; }
            }

            .chat-hidden {
                display: none;
            }

            /* Suggested Questions */
            .chat-suggestions {
                margin-bottom: 16px;
                padding: 12px;
                background: var(--surface-2);
                border: 1px solid var(--border-color);
                border-radius: 8px;
            }

            .chat-suggestions-header {
                margin-bottom: 8px;
                font-size: 12px;
                font-weight: 600;
                color: var(--primary-color);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .chat-suggestions-buttons {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }

            .chat-suggestion-btn {
                padding: 8px 12px;
                background: white;
                border: 1px solid var(--chip-border);
                border-radius: 6px;
                text-align: left;
                font-size: 13px;
                line-height: 1.3;
                color: var(--text-color);
                cursor: pointer;
                transition: all 0.15s ease;
                white-space: normal;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }

            .chat-suggestion-btn:hover {
                background: var(--chip-bg);
                border-color: var(--primary-color);
                color: var(--chip-fg);
            }

            .chat-suggestion-btn:active {
                transform: scale(0.98);
                background: var(--primary-color);
                color: white;
            }

            /* Dark mode for suggested questions */
            html[data-theme='dark'] .chat-suggestion-btn {
                background: var(--surface-1);
                border-color: var(--border-color);
                color: var(--text-color);
            }

            html[data-theme='dark'] .chat-suggestion-btn:hover {
                background: var(--primary-color);
                color: white;
            }

            /* Input Area */
            .chat-input-area {
                border-top: 1px solid var(--border-color);
                background: var(--surface-1);
            }

            .chat-notice {
                padding: 8px 20px;
                margin: 0;
                text-align: center;
            }

            .typing-notice {
                margin: 8px 0;
                font-size: 11px;
                color: var(--muted-text);
            }

            .chat-form {
                padding: 16px 20px 20px;
            }

            .chat-input-group {
                display: flex;
                gap: 8px;
                align-items: flex-end;
            }

            .chat-textarea {
                flex: 1;
                min-height: 40px;
                max-height: 120px;
                resize: none;
                background: var(--surface-1);
                color: var(--text-color);
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                line-height: 1.4;
                outline: none;
                transition: border-color 0.2s ease;
            }

            .chat-textarea:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
            }

            .chat-send-btn {
                padding: 10px 16px;
                background: var(--primary-color);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
                white-space: nowrap;
            }

            .chat-send-btn:hover:not(:disabled) {
                background: #1d4ed8;
                transform: translateY(-1px);
            }

            .chat-send-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            /* Source attribution for RAG responses */
            .chat-sources {
                margin-top: 8px;
                font-size: 11px;
            }

            .chat-source-tag {
                display: inline-block;
                background: var(--chip-bg);
                color: var(--chip-fg);
                padding: 2px 6px;
                border-radius: 4px;
                margin-right: 4px;
                margin-bottom: 2px;
            }

            /* Error state */
            .chat-error-message {
                background: #fef2f2;
                color: #dc2626;
                border: 1px solid #fecaca;
            }

            /* Scrollbar styling */
            .chat-messages::-webkit-scrollbar {
                width: 4px;
            }

            .chat-messages::-webkit-scrollbar-track {
                background: transparent;
            }

            .chat-messages::-webkit-scrollbar-thumb {
                background: var(--border-color);
                border-radius: 2px;
            }

            /* Mobile responsiveness */
            @media (max-width: 480px) {
                .chat-widget-fixed-container {
                    bottom: 10px;
                    right: 10px;
                }

                .chat-widget {
                    width: calc(100vw - 20px);
                    height: calc(100vh - 120px);
                    max-width: 400px;
                }

                .chat-toggle-btn {
                    width: 50px;
                    height: 50px;
                    font-size: 16px;
                }
            }

            /* Reduced motion support */
            @media (prefers-reduced-motion: reduce) {
                .chat-widget,
                .chat-toggle-btn,
                .chat-message {
                    transition: none;
                    animation: none;
                }

                .chat-messages {
                    scroll-behavior: auto;
                }
            }
        """)

    def _render_scripts(self) -> ft:
        """Render JavaScript for chat functionality."""
        return Script(f"""
            // Chat Widget JavaScript
            (function(){{

                // Global state
                let chatVisible = true;  // Start with chat visible by default
                let isTyping = false;
                let messageHistory = [];
                const API_ENDPOINT = '{self.api_endpoint}';

                // Utility functions
                function $(id) {{ return document.getElementById(id); }}

                function showTyping() {{
                    const typingEl = $('chat-loading');
                    if (typingEl) {{
                        typingEl.classList.remove('chat-hidden');
                        isTyping = true;
                    }}
                }}

                function hideTyping() {{
                    const typingEl = $('chat-loading');
                    if (typingEl) {{
                        typingEl.classList.add('chat-hidden');
                        isTyping = false;
                    }}
                }}

                function toggleChatWidget() {{
                    const widget = $('chat-widget');
                    const container = $('chat-widget-container');
                    const toggleBtn = $('chat-toggle');

                    if (!widget) return;

                    chatVisible = !chatVisible;

                    if (chatVisible) {{
                        widget.classList.remove('chat-widget-hidden');
                        widget.classList.add('chat-widget-visible');
                        toggleBtn.style.display = 'flex'; // Always show toggle button
                        toggleBtn.textContent = 'X'; // Change text to indicate close
                        toggleBtn.setAttribute('aria-label', 'Close chat');
                        // Focus input for accessibility
                        setTimeout(() => {{
                            const input = $('chat-input');
                            if (input) input.focus();
                        }}, 100);
                        // Track interaction
                        trackEvent('chat_opened');
                    }} else {{
                        widget.classList.remove('chat-widget-visible');
                        widget.classList.add('chat-widget-hidden');
                        toggleBtn.style.display = 'flex'; // Always show toggle button
                        toggleBtn.textContent = '💬 Chat'; // Reset text
                        toggleBtn.setAttribute('aria-label', 'Open chat conversation');
                        hideTyping();
                        // Track interaction
                        trackEvent('chat_closed');
                    }}
                }}

                // Initialize chat button state
                function initChatWidget() {{
                    const toggleBtn = $('chat-toggle');
                    const widget = $('chat-widget');

                    if (toggleBtn && widget) {{
                        toggleBtn.style.display = 'flex'; // Make sure button is always visible
                        toggleBtn.textContent = chatVisible ? 'X' : '💬 Chat';
                        widget.className = chatVisible ? 'chat-widget chat-widget-visible' : 'chat-widget chat-widget-hidden';
                    }}
                }}

                function handleEnterKey(event) {{
                    if (event.key === 'Enter' && !event.shiftKey) {{
                        event.preventDefault();
                        sendMessage(event);
                    }}
                }}

                function updateSendButton() {{
                    const input = $('chat-input');
                    const sendBtn = $('chat-send-btn');
                    if (input && sendBtn) {{
                        const hasText = input.value.trim().length > 0;
                        sendBtn.disabled = !hasText;
                        sendBtn.textContent = hasText ? 'Send' : 'Send';
                    }}
                }}

                async function sendMessage(event) {{
                    event.preventDefault();

                    const input = $('chat-input');
                    const form = $('chat-form');

                    if (!input || !form) return;
                    if (isTyping) return; // Prevent multiple sends

                    const message = input.value.trim();
                    if (!message) return;

                    // Clear input
                    input.value = '';

                    // Add user message to chat
                    addUserMessage(message);

                    // Show typing indicator
                    showTyping();

                    // Track message sent
                    trackEvent('message_sent', {{ message_length: message.length }});

                    // Send to API
                    await sendToAPI(message);

                    // Update button state
                    updateSendButton();
                }}

                function addUserMessage(text) {{
                    const messagesEl = $('chat-messages');
                    if (!messagesEl) return;

                    const messageEl = document.createElement('div');
                    messageEl.className = 'chat-message user-message';
                    messageEl.setAttribute('data-timestamp', Date.now());
                    messageEl.setAttribute('data-type', 'user');

                    messageEl.innerHTML = `
                        <div class="chat-message-avatar">
                            <div class="chat-avatar user-avatar">👤</div>
                        </div>
                        <div class="chat-message-content">
                            <p class="chat-message-text">${{escapeHtml(text)}}</p>
                        </div>
                    `;

                    messagesEl.appendChild(messageEl);
                    scrollToBottom();
                }}

                function addBotMessage(text, metadata = null) {{
                    const messagesEl = $('chat-messages');
                    if (!messagesEl) return;

                    const messageEl = document.createElement('div');
                    messageEl.className = 'chat-message bot-message';
                    messageEl.setAttribute('data-timestamp', Date.now());
                    messageEl.setAttribute('data-type', 'bot');

                    let sourcesHtml = '';
                    if (metadata && metadata.sources && metadata.sources.length > 0) {{
                        sourcesHtml = `
                            <div class="chat-sources">
                                ${{metadata.sources.map(s => `<span class="chat-source-tag">${{escapeHtml(s)}}</span>`).join('')}}
                            </div>
                        `;
                    }}

                    messageEl.innerHTML = `
                        <div class="chat-message-avatar">
                            <div class="chat-avatar bot-avatar">🤖</div>
                        </div>
                        <div class="chat-message-content">
                            <p class="chat-message-text">${{escapeHtml(text)}}</p>
                            ${{sourcesHtml}}
                        </div>
                    `;

                    messagesEl.appendChild(messageEl);
                    scrollToBottom();
                }}

                function addErrorMessage(text) {{
                    const messagesEl = $('chat-messages');
                    if (!messagesEl) return;

                    const messageEl = document.createElement('div');
                    messageEl.className = 'chat-message bot-message';
                    messageEl.setAttribute('data-timestamp', Date.now());
                    messageEl.setAttribute('data-type', 'error');

                    messageEl.innerHTML = `
                        <div class="chat-message-avatar">
                            <div class="chat-avatar bot-avatar error-avatar">⚠️</div>
                        </div>
                        <div class="chat-message-content chat-error-message">
                            <p class="chat-message-text">${{escapeHtml(text)}}</p>
                        </div>
                    `;

                    messagesEl.appendChild(messageEl);
                    scrollToBottom();
                }}

                async function sendToAPI(message) {{
                    try {{
                        const response = await fetch(API_ENDPOINT, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                message: message,
                                context: {{
                                    tech_level: 'intermediate',
                                    urgency: 'normal',
                                    timestamp: Date.now()
                                }}
                            }})
                        }});

                        if (!response.ok) {{
                            throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
                        }}

                        const data = await response.json();

                        if (data.success) {{
                            addBotMessage(data.response, data.metadata);
                            trackEvent('response_received', {{
                                processing_time: data.metadata.processing_time,
                                model_used: data.metadata.model_used
                            }});
                        }} else {{
                            throw new Error(data.error || 'Unknown error occurred');
                        }}

                    }} catch (error) {{
                        console.error('Chat API error:', error);
                        addErrorMessage('I apologize, but I\\'m having trouble connecting right now. Please try again later.');
                        trackEvent('response_error', {{ error: error.message }});
                    }} finally {{
                        hideTyping();
                    }}
                }}

                function scrollToBottom() {{
                    setTimeout(() => {{
                        const messagesEl = $('chat-messages');
                        if (messagesEl) {{
                            messagesEl.scrollTop = messagesEl.scrollHeight;
                        }}
                    }}, 100);
                }}

                function escapeHtml(text) {{
                    const map = {{
                        '&': '&',
                        '<': '<',
                        '>': '>',
                        '"': '"',
                        "'": '&#039;'
                    }};
                    return text.replace(/[&<>"']/g, m => map[m]);
                }}

                function trackEvent(eventName, properties = {{}}) {{
                    // Basic analytics tracking
                    try {{
                        console.log(`[ChatAnalytics] ${{eventName}}`, properties);
                        // Could integrate with Google Analytics, Mixpanel, etc.
                    }} catch (e) {{
                        // Ignore tracking errors
                    }}
                }}

                // Initialize
                document.addEventListener('DOMContentLoaded', function() {{
                    const input = $('chat-input');
                    const form = $('chat-form');

                    // Initialize chat widget state
                    initChatWidget();

                    // Set up input handlers
                    if (input) {{
                        input.addEventListener('input', updateSendButton);
                        input.addEventListener('paste', updateSendButton);
                    }}

                    if (form) {{
                        form.addEventListener('submit', sendMessage);
                    }}

                    // Track widget loaded
                    trackEvent('chat_widget_loaded');

                    // Log initialization
                    console.log('Chat widget initialized successfully');
                }});

                function sendSuggestedQuestion(buttonEl) {{
                    const question = buttonEl.getAttribute('data-question') || buttonEl.textContent;
                    if (!question) return;

                    // Add user message immediately
                    addUserMessage(question);

                    // Hide suggested questions after first use
                    const suggestionsEl = $('chat-suggestions');
                    if (suggestionsEl) {{
                        suggestionsEl.classList.add('chat-hidden');
                    }}

                    // Show typing indicator
                    showTyping();

                    // Track suggested question usage
                    trackEvent('suggested_question_clicked', {{
                        question: question,
                        question_length: question.length
                    }});

                    // Send to API
                    setTimeout(() => sendToAPI(question), 300);
                }}

                // Expose functions globally for button onclick handlers
                window.toggleChatWidget = toggleChatWidget;
                window.sendMessage = sendMessage;
                window.handleEnterKey = handleEnterKey;
                window.sendSuggestedQuestion = sendSuggestedQuestion;

            }})();
        """)

    # Static method to create pre-configured instances
    @classmethod
    def professional_mode(cls) -> 'ChatWidget':
        """Create a chat widget optimized for professional audiences."""
        return cls(
            greeting="Hello! I'm here to discuss my AI/ML engineering background, including predictive systems, automation projects, and technical leadership. How can I help you today?"
        )

    @classmethod
    def technical_mode(cls) -> 'ChatWidget':
        """Create a chat widget with technical focus."""
        return cls(
            greeting="Hi there! I specialize in Python ML/AI development, with 6+ years in manufacturing automation and data science. Ask me about my technical projects, architecture decisions, or Python expertise."
        )


def create_sample_chat_widget():
    """
    Create a sample chat widget for testing.

    Usage in your main app:
    ```python
    from src.components.chat.widget import ChatWidget

    # Add to your home page
    chat_widget = ChatWidget.professional_mode()

    return render_page(
        "Home",
        # ... your other content ...
        chat_widget.render()
    )
    ```
    """
    return ChatWidget.professional_mode()


# Example usage in FastHTML routes
"""
To add the chat widget to your FastHTML application:

1. Import the widget in your main.py:
   from src.components.chat.widget import ChatWidget

2. Add to your pages:
   @app.get("/")
   def home():
       chat = ChatWidget.professional_mode()
       return render_page(
           "Home",
           # Your existing home content...
           HeroSection(...),
           # Add chat widget
           chat.render()
       )

3. The widget will automatically:
   - Handle the floating chat button
   - Manage message history
   - Connect to your /api/rag/chat endpoint
   - Handle loading states and errors
   - Work on mobile and desktop

4. Optionally customize:
   - widget = ChatWidget(api_endpoint="/custom/endpoint")
   - Use technical_mode() or professional_mode()
   - Pass custom greeting
"""

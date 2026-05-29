from __future__ import annotations

import json

import fasthtml.common as ft


class ChatWidget:
    """Small persistent site chat widget."""

    def __init__(self, *, mode: str = "widget", api_endpoint: str = "/api/rag/chat"):
        self.mode = mode
        self.api_endpoint = api_endpoint

    @classmethod
    def professional_mode(cls) -> tuple:
        return cls(mode="widget").render()

    @classmethod
    def full_page(cls) -> tuple:
        return cls(mode="page").render()

    def render(self) -> tuple:
        return (
            self._styles(),
            self._script(),
            self._shell(),
        )

    def _shell(self):
        is_page = self.mode == "page"
        title = "Ask About My Experience"
        subtitle = "This chat uses portfolio and resume context. History stays in this browser tab."
        suggestions = [
            "What AI/ML work have you done?",
            "What are your strongest Python projects?",
            "Summarize your Lockheed Martin experience.",
            "What kind of roles are you targeting?",
        ]

        return ft.Div(
            ft.Button(
                "Chat",
                id="chat-toggle",
                cls="chat-toggle" if not is_page else "chat-toggle chat-toggle-hidden",
                type="button",
                aria_label="Open chat",
            ),
            ft.Div(
                ft.Div(
                    ft.Div(
                        ft.H3(title, cls="chat-title"),
                        ft.P(subtitle, cls="chat-subtitle"),
                    ),
                    ft.Button(
                        "x",
                        id="chat-close",
                        cls="chat-close"
                        if not is_page
                        else "chat-close chat-toggle-hidden",
                        type="button",
                        aria_label="Close chat",
                    ),
                    cls="chat-header",
                ),
                ft.Div(id="chat-messages", cls="chat-messages"),
                ft.Div(
                    *[
                        ft.Button(
                            q, type="button", cls="chat-suggestion", data_question=q
                        )
                        for q in suggestions
                    ],
                    id="chat-suggestions",
                    cls="chat-suggestions",
                ),
                ft.Form(
                    ft.Textarea(
                        "",
                        id="chat-input",
                        name="message",
                        rows="2",
                        maxlength="700",
                        placeholder="Ask about my skills, projects, background, or fit...",
                        cls="chat-input",
                        aria_label="Chat message",
                    ),
                    ft.Button("Send", type="submit", cls="chat-send", id="chat-send"),
                    id="chat-form",
                    cls="chat-form",
                    data_endpoint=self.api_endpoint,
                ),
                id="chat-panel",
                cls="chat-panel chat-panel-page"
                if is_page
                else "chat-panel chat-panel-closed",
            ),
            id="experience-chat",
            data_mode=self.mode,
            data_initial=json.dumps(
                [
                    {
                        "role": "assistant",
                        "content": (
                            "Hi, I can answer questions about Matthew's experience, "
                            "skills, projects, education, and fit for technical roles."
                        ),
                    }
                ]
            ),
            cls="experience-chat experience-chat-page"
            if is_page
            else "experience-chat",
        )

    def _styles(self):
        return ft.Style("""
            .experience-chat { position: fixed; right: 24px; bottom: 84px; z-index: 1200; font-family: inherit; }
            .experience-chat-page { position: static; z-index: auto; width: min(980px, 100%); margin: 0 auto; }
            .chat-toggle { width: 56px; height: 56px; border-radius: 999px; border: 1px solid var(--border-color); background: var(--primary-color); color: #fff; font-weight: 700; cursor: pointer; box-shadow: 0 12px 32px rgba(0,0,0,.24); }
            .chat-toggle-hidden { display: none; }
            .chat-panel { width: min(420px, calc(100vw - 32px)); height: min(620px, calc(100vh - 124px)); display: grid; grid-template-rows: auto 1fr auto auto; overflow: hidden; background: var(--surface-1); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 24px 70px rgba(0,0,0,.35); }
            .chat-panel-closed { display: none; }
            .chat-panel-page { width: 100%; height: min(720px, calc(100vh - 180px)); min-height: 560px; box-shadow: none; }
            .chat-header { display: flex; justify-content: space-between; gap: 1rem; padding: 1rem; border-bottom: 1px solid var(--border-color); background: var(--surface-2); }
            .chat-title { margin: 0 0 .25rem; font-size: 1rem; }
            .chat-subtitle { margin: 0; color: var(--muted-text); font-size: .88rem; }
            .chat-close { width: 32px; height: 32px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--surface-1); color: var(--text-color); cursor: pointer; }
            .chat-messages { overflow-y: auto; padding: 1rem; display: flex; flex-direction: column; gap: .75rem; }
            .chat-message { max-width: 88%; padding: .7rem .85rem; border-radius: 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
            .chat-message.assistant { align-self: flex-start; background: var(--surface-2); border: 1px solid var(--border-color); }
            .chat-message.user { align-self: flex-end; background: var(--primary-color); color: #fff; }
            .chat-meta { margin-top: .45rem; color: var(--muted-text); font-size: .76rem; }
            .chat-suggestions { display: flex; gap: .5rem; flex-wrap: wrap; padding: 0 1rem 1rem; }
            .chat-suggestion { border: 1px solid var(--border-color); background: var(--surface-1); color: var(--text-color); border-radius: 999px; padding: .45rem .65rem; cursor: pointer; font-size: .82rem; }
            .chat-suggestion:hover { border-color: var(--primary-color); color: var(--primary-color); }
            .chat-form { display: grid; grid-template-columns: 1fr auto; gap: .65rem; padding: 1rem; border-top: 1px solid var(--border-color); }
            .chat-input { min-height: 44px; max-height: 140px; resize: vertical; }
            .chat-send { border-radius: 8px; border: none; padding: 0 1rem; background: var(--primary-color); color: #fff; cursor: pointer; font-weight: 700; }
            .chat-send:disabled { opacity: .6; cursor: wait; }
            @media (max-width: 768px) {
                .experience-chat { right: 12px; bottom: 78px; }
                .chat-panel { width: calc(100vw - 24px); height: min(660px, calc(100vh - 112px)); }
                .chat-panel-page { height: calc(100svh - 180px); min-height: 520px; }
            }
        """)

    def _script(self):
        return ft.Script("""
            (function(){
              const STORE_KEY = 'experience_chat_messages_v1';
              function byId(id){ return document.getElementById(id); }
              function getRoot(){ return byId('experience-chat'); }
              function loadMessages(root){
                try {
                  const saved = sessionStorage.getItem(STORE_KEY);
                  if (saved) return JSON.parse(saved);
                  return JSON.parse(root.dataset.initial || '[]');
                } catch (_) { return [{role:'assistant', content:'Hi, ask me about Matthew\\'s experience.'}]; }
              }
              function saveMessages(messages){
                try { sessionStorage.setItem(STORE_KEY, JSON.stringify(messages.slice(-30))); } catch (_) {}
              }
              function renderMessages(messages){
                const box = byId('chat-messages');
                if (!box) return;
                box.innerHTML = '';
                messages.forEach(function(m){
                  const el = document.createElement('div');
                  el.className = 'chat-message ' + (m.role === 'user' ? 'user' : 'assistant');
                  el.textContent = m.content || '';
                  if (m.role !== 'user' && m.sources && m.sources.length) {
                    const meta = document.createElement('div');
                    meta.className = 'chat-meta';
                    meta.textContent = 'Sources: ' + m.sources.join(', ');
                    el.appendChild(meta);
                  }
                  box.appendChild(el);
                });
                box.scrollTop = box.scrollHeight;
                const suggestions = byId('chat-suggestions');
                if (suggestions) suggestions.style.display = messages.length > 1 ? 'none' : 'flex';
              }
              async function submitMessage(text){
                const form = byId('chat-form');
                const input = byId('chat-input');
                const send = byId('chat-send');
                if (!form || !text.trim()) return;
                let messages = loadMessages(getRoot());
                messages.push({role:'user', content:text.trim()});
                renderMessages(messages);
                saveMessages(messages);
                if (input) input.value = '';
                if (send) { send.disabled = true; send.textContent = 'Sending'; }
                try {
                  const res = await fetch(form.dataset.endpoint || '/api/rag/chat', {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({message:text.trim(), history: messages.slice(-10)})
                  });
                  const data = await res.json();
                  messages.push({role:'assistant', content:data.response || data.error || 'I could not answer that yet.', sources:data.sources || []});
                } catch (err) {
                  messages.push({role:'assistant', content:'I could not reach the chat service. Please try again in a moment.'});
                } finally {
                  renderMessages(messages);
                  saveMessages(messages);
                  if (send) { send.disabled = false; send.textContent = 'Send'; }
                  if (input) input.focus();
                }
              }
              function init(){
                const root = getRoot();
                if (!root || root.dataset.ready === '1') return;
                root.dataset.ready = '1';
                const panel = byId('chat-panel');
                const toggle = byId('chat-toggle');
                const close = byId('chat-close');
                const form = byId('chat-form');
                const input = byId('chat-input');
                renderMessages(loadMessages(root));
                if (toggle) toggle.addEventListener('click', function(){ panel && panel.classList.toggle('chat-panel-closed'); });
                if (close) close.addEventListener('click', function(){ panel && panel.classList.add('chat-panel-closed'); });
                if (form) form.addEventListener('submit', function(e){ e.preventDefault(); submitMessage((input && input.value) || ''); });
                document.querySelectorAll('.chat-suggestion').forEach(function(btn){
                  btn.addEventListener('click', function(){ submitMessage(btn.dataset.question || btn.textContent || ''); });
                });
                if (input) input.addEventListener('keydown', function(e){
                  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitMessage(input.value || ''); }
                });
              }
              if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
              else init();
            })();
        """)

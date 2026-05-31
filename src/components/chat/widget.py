from __future__ import annotations

import json
import os

import fasthtml.common as ft

from src.config import get_config


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
        config = get_config()
        owner_first_name = (
            config.owner_name.split()[0] if config.owner_name else "this site"
        )
        is_page = self.mode == "page"
        title = "Experience Chat" if is_page else "Ask About My Experience"
        subtitle = "Ask about Matthew's experience, projects, and role fit."
        ai_polish_enabled = bool(
            os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        )
        chat_placeholder = (
            "Ask about my skills, projects, background, or fit..."
            if ai_polish_enabled
            else "Free-tier chat. Less capable."
        )
        chat_status = (
            "Advanced chat mode is enabled for more conversational answers."
            if ai_polish_enabled
            else ("Free-tier chat. Less capable. Advanced models available.")
        )
        suggestions = [
            "What AI/ML work have you done?",
            "How have you used Python in your AI/ML work?",
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
                    ft.Div(
                        ft.A(
                            "Full chat",
                            href="/chat",
                            cls="chat-full-link"
                            if not is_page
                            else "chat-full-link chat-toggle-hidden",
                        ),
                        ft.Button(
                            "New",
                            id="chat-reset",
                            cls="chat-reset",
                            type="button",
                            title="Start a new chat",
                            aria_label="Start a new chat",
                        ),
                        ft.Button(
                            "Copy",
                            id="chat-copy",
                            cls="chat-copy",
                            type="button",
                            title="Copy conversation",
                            aria_label="Copy conversation to clipboard",
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
                        cls="chat-header-actions",
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
                ft.Div(
                    chat_status,
                    id="chat-status",
                    cls="chat-status",
                    role="status",
                    aria_live="polite",
                ),
                ft.Form(
                    ft.Textarea(
                        "",
                        id="chat-input",
                        name="message",
                        rows="2",
                        maxlength="700",
                        placeholder=chat_placeholder,
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
                            f"Hi, I can answer questions about {owner_first_name}'s experience, "
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
            .experience-chat-page { position: static; z-index: auto; width: min(1120px, 100%); margin: 0 auto; }
            .chat-toggle { width: 56px; height: 56px; border-radius: 999px; border: 1px solid var(--border-color); background: var(--primary-color); color: #fff; font-weight: 700; cursor: pointer; box-shadow: 0 12px 32px rgba(0,0,0,.24); }
            .chat-toggle-hidden { display: none !important; }
            .chat-panel { width: min(440px, calc(100vw - 32px)); height: min(650px, calc(100vh - 124px)); display: grid; grid-template-rows: auto 1fr auto auto auto; overflow: hidden; background: var(--surface-1); border: 1px solid var(--border-color); border-radius: 12px; box-shadow: 0 24px 70px rgba(0,0,0,.35); }
            .chat-panel-closed { display: none; }
            .chat-panel-page {
                width: 100%;
                height: auto;
                min-height: 0;
                grid-template-rows: auto auto auto auto auto;
                overflow: visible;
                box-shadow: none;
            }
            .chat-header { display: flex; justify-content: space-between; gap: 1rem; padding: 1rem; border-bottom: 1px solid var(--border-color); background: var(--surface-2); }
            .chat-title { margin: 0 0 .25rem; font-size: 1rem; }
            .chat-subtitle { margin: 0; color: var(--muted-text); font-size: .88rem; }
            .chat-header-actions { display: flex; align-items: start; gap: .4rem; flex: 0 0 auto; }
            .chat-full-link, .chat-reset, .chat-copy { min-height: 32px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid var(--border-color); border-radius: 8px; background: var(--surface-1); color: var(--text-color); text-decoration: none; cursor: pointer; font: inherit; font-size: .78rem; font-weight: 720; padding: 0 .55rem; }
            .chat-copy:disabled { opacity: .65; cursor: default; }
            .chat-close { width: 32px; height: 32px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--surface-1); color: var(--text-color); cursor: pointer; }
            .chat-messages { overflow-y: auto; padding: 1rem; display: flex; flex-direction: column; gap: .75rem; }
            .chat-message { max-width: 88%; padding: .7rem .85rem; border-radius: 12px; white-space: pre-wrap; overflow-wrap: anywhere; }
            .chat-message.assistant { align-self: flex-start; background: var(--surface-2); border: 1px solid var(--border-color); }
            .chat-message.user { align-self: flex-end; background: var(--primary-color); color: #fff; }
            .chat-message.pending { color: var(--muted-text); font-style: italic; }
            .chat-meta { margin-top: .55rem; display: grid; gap: .4rem; color: var(--muted-text); font-size: .76rem; white-space: normal; }
            .chat-meta-row { display: flex; gap: .35rem; flex-wrap: wrap; align-items: center; }
            .chat-source-chip { border: 1px solid var(--border-color); border-radius: 999px; padding: .16rem .45rem; color: var(--text-color); background: color-mix(in srgb, var(--surface-1) 82%, transparent); }
            .chat-suggestions { display: flex; gap: .5rem; flex-wrap: wrap; padding: 0 1rem 1rem; }
            .chat-suggestion { border: 1px solid var(--border-color); background: var(--surface-1); color: var(--text-color); border-radius: 999px; padding: .45rem .65rem; cursor: pointer; font-size: .82rem; }
            .chat-suggestion:hover { border-color: var(--primary-color); color: var(--primary-color); }
            .chat-status { padding: .65rem 1rem 0; color: var(--muted-text); font-size: .78rem; border-top: 1px solid var(--border-color); }
            .chat-form { display: grid; grid-template-columns: 1fr auto; gap: .65rem; padding: 1rem; border-top: 1px solid var(--border-color); }
            .chat-input { min-height: 44px; max-height: 140px; resize: vertical; font-size: 1rem; line-height: 1.35; }
            .chat-send { border-radius: 8px; border: none; padding: 0 1rem; background: var(--primary-color); color: #fff; cursor: pointer; font-weight: 700; }
            .chat-send:disabled { opacity: .6; cursor: wait; }
            .experience-chat-page .chat-messages {
                min-height: 420px;
                overflow: visible;
            }
            .experience-chat-page.chat-has-suggestions .chat-messages { min-height: 0; }
            .experience-chat-page .chat-form {
                position: sticky;
                bottom: 0;
                z-index: 3;
                background: var(--surface-1);
            }
            .chat-page-section { padding: 2.75rem 0 0; }
            .chat-page-title { margin-bottom: 1.5rem; }
            .chat-page-container { padding-bottom: 1.5rem; }
            @media (max-width: 768px) {
                .experience-chat { right: 12px; bottom: 78px; }
                .chat-panel { width: calc(100vw - 24px); height: min(660px, calc(100vh - 112px)); }
                .experience-chat-page { width: 100%; }
                .experience-chat-page .chat-panel {
                    width: 100%;
                    height: auto;
                    min-height: 0;
                    border-radius: 10px;
                    padding-bottom: 0;
                }
                .experience-chat-page .chat-messages { min-height: 300px; padding: .9rem; }
                .experience-chat-page.chat-has-suggestions .chat-messages { min-height: 0; }
                .experience-chat-page .chat-status { padding: .55rem .9rem 1rem; }
                .experience-chat-page .chat-form {
                    position: fixed;
                    left: max(12px, env(safe-area-inset-left));
                    right: max(12px, env(safe-area-inset-right));
                    bottom: calc(74px + env(safe-area-inset-bottom));
                    padding: .85rem;
                    border: 1px solid var(--border-color);
                    border-radius: 10px;
                    box-shadow: 0 -12px 36px rgba(0,0,0,.28);
                }
                .chat-input { font-size: 16px; }
                .chat-header { align-items: stretch; flex-direction: column; gap: .75rem; }
                .chat-subtitle { max-width: 34rem; }
                .chat-header-actions { flex-wrap: wrap; justify-content: start; }
                .chat-reset, .chat-copy { flex: 1 1 0; min-width: 0; }
                .chat-message { max-width: 94%; }
                .chat-page-section { padding-top: 1.4rem; }
                .chat-page-title { margin-bottom: 1.1rem; }
                .chat-page-container { padding-bottom: 190px; }
            }
        """)

    def _script(self):
        return ft.Script("""
            (function(){
              const STORE_KEY = 'experience_chat_messages_v1';
              let pending = false;
              function byId(id){ return document.getElementById(id); }
              function getRoot(){ return byId('experience-chat'); }
              function canAutoFocus(){ return window.matchMedia('(hover: hover) and (pointer: fine)').matches; }
              function loadMessages(root){
                try {
                  const saved = sessionStorage.getItem(STORE_KEY);
                  if (saved) return JSON.parse(saved);
                  return JSON.parse(root.dataset.initial || '[]');
                } catch (_) { return [{role:'assistant', content:'Hi, ask me about this portfolio.'}]; }
              }
              function saveMessages(messages){
                try { sessionStorage.setItem(STORE_KEY, JSON.stringify(messages.slice(-30))); } catch (_) {}
              }
              function setStatus(text){
                const status = byId('chat-status');
                if (status) status.textContent = text || '';
              }
              function transcriptLine(message){
                const speaker = message.role === 'user' ? 'You' : 'Portfolio assistant';
                return speaker + ': ' + (message.content || '').trim();
              }
              function conversationTranscript(){
                return loadMessages(getRoot())
                  .filter(function(message){ return !message.pending && (message.content || '').trim(); })
                  .map(transcriptLine)
                  .join('\\n\\n');
              }
              function fallbackCopyText(text){
                const area = document.createElement('textarea');
                area.value = text;
                area.setAttribute('readonly', '');
                area.style.position = 'fixed';
                area.style.left = '-9999px';
                area.style.top = '0';
                document.body.appendChild(area);
                area.select();
                const copied = document.execCommand('copy');
                document.body.removeChild(area);
                if (!copied) throw new Error('copy failed');
              }
              async function copyConversation(){
                const copy = byId('chat-copy');
                const transcript = conversationTranscript();
                if (!transcript) {
                  setStatus('No conversation to copy yet.');
                  return;
                }
                try {
                  let copied = false;
                  if (navigator.clipboard && window.isSecureContext) {
                    try {
                      await navigator.clipboard.writeText(transcript);
                      copied = true;
                    } catch (_) {}
                  }
                  if (!copied) {
                    fallbackCopyText(transcript);
                  }
                  setStatus('Conversation copied to clipboard.');
                  if (copy) {
                    const label = copy.textContent;
                    copy.textContent = 'Copied';
                    copy.disabled = true;
                    window.setTimeout(function(){
                      copy.textContent = label || 'Copy conversation';
                      copy.disabled = false;
                    }, 1200);
                  }
                } catch (_) {
                  setStatus('Clipboard copy was blocked by this browser.');
                }
              }
              function sourceLabel(source){
                if (!source) return '';
                if (typeof source === 'string') return source;
                return source.label || '';
              }
              function sourceSnippet(source){
                if (!source || typeof source === 'string') return '';
                return source.snippet || '';
              }
              function appendMeta(el, message){
                const sources = (message.sources || []).map(sourceLabel).filter(Boolean);
                const hasMeta = message.providerLabel || message.note || sources.length;
                if (!hasMeta) return;

                const meta = document.createElement('div');
                meta.className = 'chat-meta';

                if (message.providerLabel || message.note) {
                  const row = document.createElement('div');
                  row.className = 'chat-meta-row';
                  row.textContent = [message.providerLabel, message.note].filter(Boolean).join(' · ');
                  meta.appendChild(row);
                }

                if (sources.length) {
                  const row = document.createElement('div');
                  row.className = 'chat-meta-row';
                  const label = document.createElement('span');
                  label.textContent = 'Sources:';
                  row.appendChild(label);
                  (message.sources || []).forEach(function(source){
                    const chipLabel = sourceLabel(source);
                    if (!chipLabel) return;
                    const chip = document.createElement('span');
                    chip.className = 'chat-source-chip';
                    chip.textContent = chipLabel;
                    const snippet = sourceSnippet(source);
                    if (snippet) chip.title = snippet;
                    row.appendChild(chip);
                  });
                  meta.appendChild(row);
                }
                el.appendChild(meta);
              }
              function renderMessages(messages){
                const box = byId('chat-messages');
                if (!box) return;
                box.innerHTML = '';
                messages.forEach(function(m){
                  const el = document.createElement('div');
                  el.className = 'chat-message ' + (m.role === 'user' ? 'user' : 'assistant') + (m.pending ? ' pending' : '');
                  el.textContent = m.content || '';
                  if (m.role !== 'user') appendMeta(el, m);
                  box.appendChild(el);
                });
                box.scrollTop = box.scrollHeight;
                const root = getRoot();
                const hasSuggestions = messages.length <= 1;
                if (root) root.classList.toggle('chat-has-suggestions', hasSuggestions);
              }
              function resetChat(){
                const root = getRoot();
                const messages = JSON.parse(root.dataset.initial || '[]');
                pending = false;
                saveMessages(messages);
                renderMessages(messages);
                setStatus('Started a new browser-session chat.');
                const input = byId('chat-input');
                if (input && canAutoFocus()) input.focus();
              }
              async function submitMessage(text){
                const form = byId('chat-form');
                const input = byId('chat-input');
                const send = byId('chat-send');
                if (!form || !text.trim() || pending) return;
                pending = true;
                let messages = loadMessages(getRoot());
                messages.push({role:'user', content:text.trim()});
                saveMessages(messages);
                renderMessages(messages.concat([{role:'assistant', content:'Looking across the portfolio context...', pending:true}]));
                if (input) input.value = '';
                if (send) { send.disabled = true; send.textContent = 'Sending'; }
                setStatus('Searching portfolio, resume, and project context...');
                try {
                  const res = await fetch(form.dataset.endpoint || '/api/rag/chat', {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({message:text.trim(), history: messages.slice(-10)})
                  });
                  const data = await res.json();
                  messages.push({
                    role:'assistant',
                    content:data.response || data.error || 'I could not answer that yet.',
                    sources:data.sources || [],
                    provider:data.provider || '',
                    providerLabel:data.provider_label || '',
                    note:data.model_note || ''
                  });
                  setStatus(data.provider_label || 'Answer returned from portfolio context.');
                } catch (err) {
                  messages.push({role:'assistant', content:'I could not reach the chat service. Please try again in a moment.'});
                  setStatus('Chat service was unreachable. Your browser-session history is still preserved.');
                } finally {
                  pending = false;
                  renderMessages(messages);
                  saveMessages(messages);
                  if (send) { send.disabled = false; send.textContent = 'Send'; }
                  if (input && canAutoFocus()) input.focus();
                }
              }
              function init(){
                const root = getRoot();
                if (!root || root.dataset.ready === '1') return;
                root.dataset.ready = '1';
                const panel = byId('chat-panel');
                const toggle = byId('chat-toggle');
                const close = byId('chat-close');
                const reset = byId('chat-reset');
                const copy = byId('chat-copy');
                const form = byId('chat-form');
                const input = byId('chat-input');
                renderMessages(loadMessages(root));
                if (toggle) toggle.addEventListener('click', function(){ panel && panel.classList.toggle('chat-panel-closed'); });
                if (close) close.addEventListener('click', function(){ panel && panel.classList.add('chat-panel-closed'); });
                if (reset) reset.addEventListener('click', resetChat);
                if (copy) copy.addEventListener('click', copyConversation);
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

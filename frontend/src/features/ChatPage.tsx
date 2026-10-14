import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { api } from '../api/client';
import type { ChatResponse } from '../api/client';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SourceChip } from '../components/ui/SourceChip';
import { Badge } from '../components/ui/Badge';
import {
  Send,
  Mic,
  MicOff,
  Image as ImageIcon,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp,
  Volume2,
  Share2,
  Copy,
  Check,
  Bot,
  User,
} from 'lucide-react';

interface MessageItem {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  trace?: ChatResponse;
}

export const ChatPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuthStore();

  const [messages, setMessages] = useState<MessageItem[]>([
    {
      id: 'm-1',
      sender: 'assistant',
      text:
        i18n.language === 'gu'
          ? 'નમસ્તે અર્જુન ભાઈ! હું કિસાનસાથી AI છું. કપાસ, ખાતર, પિયત કે રોગ વિશે તમે મને પૂછી શકો છો. આજે હું તમારી શું મદદ કરી શકું?'
          : i18n.language === 'hi'
          ? 'नमस्ते अर्जुन भाई! मैं किसानसाथी एआई हूँ। कपास, खाद, सिंचाई या रोग के बारे में आप मुझसे पूछ सकते हैं। आज मैं आपकी क्या मदद करूँ?'
          : 'Hello Arjun Bhai! I am KisanSathi AI. You can ask me about cotton cultivation, fertilizers, irrigation schedules, or disease management. How can I help you today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedTraceId, setExpandedTraceId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg: MessageItem = {
      // eslint-disable-next-line react-hooks/purity
      id: 'usr-' + Date.now(),
      sender: 'user',
      text: query,
      // eslint-disable-next-line react-hooks/purity
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.sendChatMessage(query, i18n.language);
      const assistantMsg: MessageItem = {
        // eslint-disable-next-line react-hooks/purity
        id: 'ast-' + Date.now(),
        sender: 'assistant',
        text: response.answer,
        // eslint-disable-next-line react-hooks/purity
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        trace: response,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      // Handled by api fallback
    } finally {
      setLoading(false);
    }
  };

  const toggleRecording = () => {
    if (!isRecording) {
      setIsRecording(true);
      setTimeout(() => {
        setIsRecording(false);
        const voiceQuery =
          i18n.language === 'gu'
            ? 'કપાસમાં પહેલો ખાતરનો હપ્તો ક્યારે આપવો?'
            : 'When should I apply first fertilizer split in cotton?';
        setInput(voiceQuery);
        handleSend(voiceQuery);
      }, 2500);
    } else {
      setIsRecording(false);
    }
  };

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-4 sm:py-6 h-[calc(100vh-8rem)] flex flex-col">
      {/* Header Info Banner */}
      <div className="mb-3 px-4 py-2.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/80 rounded-2xl flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span className="font-semibold text-emerald-900 dark:text-emerald-200">
            IBM Granite Multi-Agent Supervisor
          </span>
          <span className="text-slate-400 hidden sm:inline">|</span>
          <span className="text-slate-500 hidden sm:inline">4 Domain Agents in Parallel</span>
        </div>
        <Badge variant="success" size="sm">
          Active
        </Badge>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start space-x-2.5 sm:space-x-3 ${
              msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.sender === 'user'
                  ? 'bg-slate-700 text-white'
                  : 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 border border-slate-200/80 dark:border-slate-800 shadow-sm'
              }`}
            >
              <div className="whitespace-pre-line">{msg.text}</div>

              {/* Source Chips & Citations (Assistant Only) */}
              {msg.trace && msg.trace.all_sources && msg.trace.all_sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block">
                    {t('chat.sources')}
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.trace.all_sources.map((src, i) => (
                      <SourceChip
                        key={i}
                        title={src.title}
                        section={src.section}
                        page={src.page}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Expandable "Why this advice?" Trace */}
              {msg.trace && (
                <div className="mt-3 pt-2">
                  <button
                    onClick={() =>
                      setExpandedTraceId(expandedTraceId === msg.id ? null : msg.id)
                    }
                    className="flex items-center space-x-1 text-xs font-semibold text-emerald-600 hover:text-emerald-700 dark:text-emerald-400 transition-colors"
                  >
                    <span>{t('chat.whyAdvice')}</span>
                    {expandedTraceId === msg.id ? (
                      <ChevronUp className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {expandedTraceId === msg.id && (
                    <div className="mt-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl text-xs space-y-2 border border-slate-200/60 dark:border-slate-700">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Supervisor Intent:</span>
                        <span className="font-bold text-slate-900 dark:text-white uppercase">
                          {msg.trace.intent}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Agents Executed:</span>
                        <span className="font-semibold text-emerald-700 dark:text-emerald-300">
                          {msg.trace.agents_used.join(', ')}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Execution Latency:</span>
                        <span className="font-mono text-slate-700 dark:text-slate-300">
                          {Math.round(msg.trace.total_latency_ms)} ms
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Model Engine:</span>
                        <span className="text-purple-600 dark:text-purple-400 font-semibold">
                          IBM Granite 13B (watsonx.ai)
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Message Bottom Action Bar */}
              <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400 dark:text-slate-500 pt-1">
                <span>{msg.timestamp}</span>
                {msg.sender === 'assistant' && (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => copyToClipboard(msg.id, msg.text)}
                      className="hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-500" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm">
              <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-700 dark:text-emerald-300">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span>Running Supervisor & Agents in parallel...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Reply Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-none">
        {(t('chat.quickReplies', { returnObjects: true }) as string[]).map((qr, i) => (
          <button
            key={i}
            onClick={() => handleSend(qr)}
            className="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 hover:bg-emerald-50 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 hover:text-emerald-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-colors"
          >
            {qr}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-md p-1.5 sm:p-2 flex items-center space-x-2">
        {/* Voice Note Button */}
        <button
          onClick={toggleRecording}
          aria-label="Voice input"
          className={`p-2.5 rounded-xl transition-all ${
            isRecording
              ? 'bg-rose-500 text-white animate-pulse'
              : 'text-slate-500 hover:text-emerald-600 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
          title={isRecording ? 'Listening...' : 'Hold or click to speak voice question'}
        >
          {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={isRecording ? t('chat.listening') : t('chat.placeholder')}
          className="flex-1 bg-transparent border-none outline-none text-sm px-2 text-slate-900 dark:text-white placeholder:text-slate-400"
        />

        <Button
          size="sm"
          variant="primary"
          onClick={() => handleSend()}
          disabled={!input.trim() || loading}
          className="rounded-xl px-4 shrink-0"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};

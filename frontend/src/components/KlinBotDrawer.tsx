"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useQuoteStore } from "@/store/useQuoteStore";

interface ChatMessage {
  sender: "user" | "klinbot";
  text: string;
  time: string;
}

export default function KlinBotDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: "klinbot",
      text: "¡Hola! Soy KlinBot, tu copiloto de costos y bioseguridad para CleanTech (Ecuador 2026). Puedes consultarme sobre cargas del IESS, dosificación química, restricción de máquinas en habitaciones o cotización de contingencias.",
      time: "Ahora",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const state = useQuoteStore();

  async function handleSend(textToSend?: string) {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg: ChatMessage = {
      sender: "user",
      text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const context = {
        proyecto: state.projectName,
        cliente: state.clientName,
        tipologia: state.contract.tipologia,
        superficies_total_m2: state.totalArea(),
        supervision_pct: state.adminPct,
        margen_pct: state.marginPct,
      };
      const res = await api.chatKlinBot(text, context);
      const botMsg: ChatMessage = {
        sender: "klinbot",
        text: res.response,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: "klinbot",
          text: "No fue posible conectar con el servicio de IA de KlinBot en este momento. Verifica tu conexión o el estado del backend.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const quickPills = [
    "¿Cómo cotizo una contingencia con hipoclorito?",
    "¿Se puede usar máquina en habitaciones clínicas?",
    "¿Cuáles son las cargas obligatorias del SBU $482?",
    "¿Cuál es la estancia promedio en camas UCI vs normales?",
  ];

  return (
    <>
      {/* Botón flotante para abrir KlinBot */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2 rounded-full bg-primary px-4 py-3 font-semibold text-white shadow-xl transition-transform hover:scale-105 active:scale-95"
        aria-label="Abrir Copiloto KlinBot"
      >
        <span className="material-symbols-outlined">smart_toy</span>
        <span>KlinBot IA</span>
        <span className="rounded-full bg-emerald-400 px-2 py-0.5 text-xs text-black font-mono">Gemini</span>
      </button>

      {/* Drawer Overlay y Panel */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm transition-opacity">
          <div className="flex h-full w-full max-w-md flex-col bg-surface shadow-2xl sm:border-l sm:border-outline-variant">
            {/* Cabecera */}
            <div className="flex items-center justify-between border-b border-outline-variant p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white">
                  <span className="material-symbols-outlined text-2xl">smart_toy</span>
                </div>
                <div>
                  <h3 className="font-headline font-bold text-headline-sm">KlinBot Copiloto</h3>
                  <p className="text-xs text-on-surface-variant flex items-center gap-1">
                    <span className="inline-block h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    Ecuador 2026 · FEDELIMP & CleanTech
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-lg p-2 text-on-surface-variant hover:bg-surface-container-low"
                aria-label="Cerrar panel"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {/* Historial de Mensajes */}
            <div className="flex-1 space-y-3 overflow-y-auto p-4 text-body-sm">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${
                    m.sender === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-3 shadow-sm ${
                      m.sender === "user"
                        ? "bg-primary text-white rounded-br-xs"
                        : "bg-surface-container-low text-on-surface border border-outline-variant/60 rounded-bl-xs"
                    }`}
                  >
                    <p className="whitespace-pre-line">{m.text}</p>
                  </div>
                  <span className="mt-1 text-[10px] text-on-surface-variant px-1">{m.time}</span>
                </div>
              ))}
              {loading && (
                <div className="flex items-center gap-2 text-xs text-on-surface-variant p-2">
                  <span className="inline-block h-2 w-2 rounded-full bg-primary animate-ping"></span>
                  KlinBot está analizando con Gemini...
                </div>
              )}
            </div>

            {/* Píldoras de preguntas rápidas */}
            <div className="border-t border-outline-variant/60 bg-surface-container-low/40 p-2">
              <p className="text-[11px] font-semibold text-on-surface-variant mb-1 px-1">Preguntas rápidas:</p>
              <div className="flex flex-wrap gap-1">
                {quickPills.map((pill, idx) => (
                  <button
                    key={idx}
                    onClick={() => void handleSend(pill)}
                    disabled={loading}
                    className="rounded-full border border-outline-variant bg-surface px-2.5 py-1 text-[11px] text-on-surface hover:border-primary hover:text-primary transition-colors text-left"
                  >
                    {pill}
                  </button>
                ))}
              </div>
            </div>

            {/* Input Formulario */}
            <div className="border-t border-outline-variant p-3">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void handleSend();
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Pregúntale a KlinBot..."
                  disabled={loading}
                  className="flex-1 rounded-xl bg-surface-container-low px-3.5 py-2.5 text-body-sm outline-none focus:ring-2 focus:ring-primary/40 border border-outline-variant"
                />
                <button
                  type="submit"
                  disabled={!input.trim() || loading}
                  className="flex items-center justify-center rounded-xl bg-primary px-3 text-white disabled:opacity-40"
                  aria-label="Enviar pregunta"
                >
                  <span className="material-symbols-outlined text-xl">send</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

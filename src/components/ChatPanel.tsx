import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Send, Trash2 } from "lucide-react";
import type { ChatMessage } from "@/types/chat";

interface ChatPanelProps {
  messages: ChatMessage[];
  disabled: boolean;
  loading: boolean;
  onSend: (message: string) => Promise<void>;
  onClear: () => Promise<void>;
}

const ChatPanel = ({ messages, disabled, loading, onSend, onClear }: ChatPanelProps) => {
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || disabled || isSending) return;
    setIsSending(true);
    try {
      await onSend(trimmed);
      setInput("");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="card-elevated flex h-[520px] flex-col"
    >
      <div className="flex items-center justify-between border-b border-border/50 p-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Study Chat</h3>
          <p className="text-xs text-muted-foreground">
            Grounded Response • Based on retrieved document sections
          </p>
        </div>
        <button
          onClick={onClear}
          disabled={disabled || isSending}
          className="flex items-center gap-2 rounded-lg bg-secondary px-3 py-2 text-xs font-medium text-secondary-foreground hover:bg-secondary/80 disabled:opacity-50"
        >
          <Trash2 className="h-3 w-3" />
          Clear Chat
        </button>
      </div>

      <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto p-4 scrollbar-thin">
        {disabled && (
          <p className="text-sm text-muted-foreground">
            Select or generate a cheat sheet to start chatting.
          </p>
        )}
        {!disabled && messages.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground">
            Ask a question about your cheat sheet to begin.
          </p>
        )}
        {messages.map((msg) => {
          const isUser = msg.role === "user";
          return (
            <div
              key={msg.id}
              className={`flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm ${
                  isUser
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground"
                }`}
              >
                {!isUser && (
                  <p className="mb-1 text-[11px] uppercase tracking-wide text-muted-foreground">
                    Grounded Response
                  </p>
                )}
                <p className="leading-relaxed">{msg.message}</p>
              </div>
            </div>
          );
        })}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-secondary px-4 py-3 text-sm text-secondary-foreground">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-border/50 p-4">
        <div className="flex items-center gap-3">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleSend();
              }
            }}
            disabled={disabled || isSending}
            placeholder={disabled ? "Select a cheat sheet to chat" : "Ask a question..."}
            className="flex-1 rounded-xl border border-border/50 bg-background px-4 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={disabled || isSending || !input.trim()}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground transition-all hover:bg-primary/80 disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatPanel;

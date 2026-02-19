import { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, LayoutGrid, FileText as FileTextIcon } from "lucide-react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import UploadSection from "@/components/UploadSection";
import OptionsSection, { type OptionsState } from "@/components/OptionsSection";
import ProgressBar from "@/components/ProgressBar";
import CompressionStats from "@/components/CompressionStats";
import OutputSection from "@/components/OutputSection";
import ChatPanel from "@/components/ChatPanel";
import FlashcardView from "@/components/FlashcardView";
import ExportOptions from "@/components/ExportOptions";
import Footer from "@/components/Footer";
import { useToast } from "@/hooks/use-toast";
import { getAuthToken } from "@/lib/auth";
import type { CheatSheetData, Flashcard } from "@/types/cheatsheet";
import type { ChatAskResponse, ChatMessage } from "@/types/chat";
import HistorySidebar, { type HistoryItem } from "@/components/HistorySidebar";

type RagCheatSheetResponse = {
  cheatsheet_id?: string | null;
  title?: string;
  one_line_summary?: string;
  definitions?: string[];
  core_formulas?: string[];
  key_concepts?: string[];
  diagrams?: string[];
  comparison_table?: string[];
  important_metrics?: string[];
  mistakes_to_avoid?: string[];
  original_words?: number;
  compressed_words?: number;
  flashcards?: Flashcard[];
  raw_response?: string;
  detail?: string;
};

const countWords = (text: string) => {
  const trimmed = text.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
};

const countCheatSheetWords = (data: CheatSheetData) => {
  const parts = [
    data.title || "",
    data.oneLineSummary || "",
    ...data.definitions,
    ...data.coreFormulas,
    ...data.keyConcepts,
    ...data.diagrams,
    ...data.comparisonTable,
    ...data.importantMetrics,
    ...data.mistakesToAvoid,
  ];
  return countWords(parts.join(" "));
};

const buildFallbackFlashcards = (data: CheatSheetData, maxCount: number): Flashcard[] => {
  const cards: Flashcard[] = [];
  for (const item of data.definitions) {
    if (item.includes(":")) {
      const [term, ...rest] = item.split(":");
      const answer = rest.join(":").trim();
      cards.push({ question: `What is ${term.trim()}?`, answer });
    } else {
      cards.push({ question: `Explain: ${item.trim()}`, answer: "" });
    }
    if (cards.length >= maxCount) return cards;
  }

  for (const concept of data.keyConcepts) {
    cards.push({ question: `Explain the concept: ${concept.trim()}`, answer: "" });
    if (cards.length >= maxCount) break;
  }

  return cards;
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const apiUrl = (path: string) => `${apiBaseUrl}${path}`;

const Index = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [options, setOptions] = useState<OptionsState>({
    revisionMode: "standard",
    examMode: "semester",
    formulaOnly: false,
    generateFlashcards: true,
    flashcardCount: 8,
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isGenerated, setIsGenerated] = useState(false);
  const [viewMode, setViewMode] = useState<"cheatsheet" | "flashcards" | "chat">("cheatsheet");
  const [cheatSheetData, setCheatSheetData] = useState<CheatSheetData | null>(null);
  const [flashcardsData, setFlashcardsData] = useState<Flashcard[]>([]);
  const [stats, setStats] = useState({ originalWords: 0, compressedWords: 0 });
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  const { toast } = useToast();

  const uploadRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const scrollToUpload = useCallback(() => {
    uploadRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, []);

  const fetchHistory = useCallback(async () => {
    const token = getAuthToken();
    if (!token) return;
    setHistoryLoading(true);
    try {
      const response = await fetch(apiUrl("/api/v1/history"), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error("Failed to load history");
      }
      const data = (await response.json()) as HistoryItem[];
      setHistoryItems(data);
    } catch (error) {
      toast({
        title: "History error",
        description: error instanceof Error ? error.message : "Failed to load history",
      });
    } finally {
      setHistoryLoading(false);
    }
  }, [toast]);

  const fetchChatHistory = useCallback(
    async (cheatsheetId: string) => {
      const token = getAuthToken();
      if (!token) return;
      setChatLoading(true);
      try {
        const response = await fetch(apiUrl(`/api/v1/chat/history/${cheatsheetId}`), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error("Failed to load chat history");
        }
        const data = (await response.json()) as ChatMessage[];
        setChatMessages(data);
      } catch (error) {
        toast({
          title: "Chat error",
          description: error instanceof Error ? error.message : "Failed to load chat history",
        });
      } finally {
        setChatLoading(false);
      }
    },
    [toast]
  );

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setIsSidebarOpen(window.innerWidth >= 768);
  }, []);

  useEffect(() => {
    if (activeHistoryId) {
      fetchChatHistory(activeHistoryId);
    } else {
      setChatMessages([]);
    }
  }, [activeHistoryId, fetchChatHistory]);

  const handleSelectHistory = useCallback(
    async (id: string) => {
      const token = getAuthToken();
      if (!token) return;
      setActiveHistoryId(id);
      setIsGenerated(false);
      try {
        const response = await fetch(apiUrl(`/api/v1/cheatsheet/${id}`), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error("Failed to load cheat sheet");
        }
        const payload = (await response.json()) as RagCheatSheetResponse;
        const nextCheatSheet = {
          title: payload?.title || "Cheat Sheet",
          oneLineSummary: payload?.one_line_summary || "",
          definitions: payload?.definitions ?? [],
          coreFormulas: payload?.core_formulas ?? [],
          keyConcepts: payload?.key_concepts ?? [],
          diagrams: payload?.diagrams ?? [],
          comparisonTable: payload?.comparison_table ?? [],
          importantMetrics: payload?.important_metrics ?? [],
          mistakesToAvoid: payload?.mistakes_to_avoid ?? [],
        };
        setCheatSheetData(nextCheatSheet);
        setFlashcardsData(payload?.flashcards ?? []);
        const derivedCompressed = countCheatSheetWords(nextCheatSheet);
        setStats({
          originalWords: payload?.original_words ?? derivedCompressed,
          compressedWords: payload?.compressed_words ?? derivedCompressed,
        });
        setIsGenerated(true);
        setViewMode("cheatsheet");
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 200);
      } catch (error) {
        toast({
          title: "Load error",
          description: error instanceof Error ? error.message : "Failed to load cheat sheet",
        });
      }
    },
    [toast]
  );

  const handleDeleteHistory = useCallback(
    async (id: string) => {
      const token = getAuthToken();
      if (!token) return;
      try {
        const response = await fetch(apiUrl(`/api/v1/cheatsheet/${id}`), {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error("Failed to delete cheat sheet");
        }
        setHistoryItems((prev) => prev.filter((item) => item.id !== id));
        if (activeHistoryId === id) {
          setActiveHistoryId(null);
          setCheatSheetData(null);
          setFlashcardsData([]);
          setIsGenerated(false);
        }
      } catch (error) {
        toast({
          title: "Delete error",
          description: error instanceof Error ? error.message : "Failed to delete cheat sheet",
        });
      }
    },
    [activeHistoryId, toast]
  );

  const handleNewCheatSheet = useCallback(() => {
    setActiveHistoryId(null);
    setCheatSheetData(null);
    setFlashcardsData([]);
    setIsGenerated(false);
    setViewMode("cheatsheet");

    scrollToUpload();
  }, [scrollToUpload]);

  const handleGenerate = useCallback(async () => {
    if (!files.length) return;
    setIsGenerating(true);
    setProgress(0);
    setIsGenerated(false);

    const progressTimer = setInterval(() => {
      setProgress((prev) => Math.min(prev + Math.random() * 12 + 6, 90));
    }, 300);

    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });
      formData.append("revision_mode", options.revisionMode);
      formData.append("exam_mode", options.examMode);
      formData.append("formula_only", String(options.formulaOnly));
      formData.append("flashcards", String(options.generateFlashcards));
      formData.append("flashcard_count", String(options.flashcardCount));

      const token = getAuthToken();
      const response = await fetch(apiUrl("/api/v1/rag/cheatsheet"), {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        body: formData,
      });

      const payload = (await response.json().catch(() => null)) as RagCheatSheetResponse | null;
      if (!response.ok) {
        const detail = payload?.detail || "Failed to generate cheat sheet.";
        throw new Error(detail);
      }

      const nextCheatSheet = {
        title: payload?.title || "Cheat Sheet",
        oneLineSummary: payload?.one_line_summary || "",
        definitions: payload?.definitions ?? [],
        coreFormulas: payload?.core_formulas ?? [],
        keyConcepts: payload?.key_concepts ?? [],
        diagrams: payload?.diagrams ?? [],
        comparisonTable: payload?.comparison_table ?? [],
        importantMetrics: payload?.important_metrics ?? [],
        mistakesToAvoid: payload?.mistakes_to_avoid ?? [],
      };
      setCheatSheetData(nextCheatSheet);
      if (payload?.cheatsheet_id) {
        setActiveHistoryId(payload.cheatsheet_id);
      }
      const backendFlashcards = payload?.flashcards ?? [];
      const fallbackFlashcards = options.generateFlashcards
        ? buildFallbackFlashcards(nextCheatSheet, options.flashcardCount)
        : [];
      setFlashcardsData(backendFlashcards.length ? backendFlashcards : fallbackFlashcards);
      const derivedCompressed = countCheatSheetWords(nextCheatSheet);
      setStats({
        originalWords: payload?.original_words ?? derivedCompressed,
        compressedWords: payload?.compressed_words ?? derivedCompressed,
      });
      fetchHistory();

      setProgress(100);
      setIsGenerated(true);
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    } catch (error) {
      setProgress(0);
      setIsGenerated(false);
      const message = error instanceof Error ? error.message : "Failed to generate cheat sheet.";
      toast({
        title: "Generation failed",
        description: message,
      });
    } finally {
      clearInterval(progressTimer);
      setIsGenerating(false);
    }
  }, [files, options, toast]);

  const handleSendChat = useCallback(
    async (message: string) => {
      const token = getAuthToken();
      if (!token || !activeHistoryId) return;
      const tempId = `local-${Date.now()}`;
      const userMessage: ChatMessage = {
        id: tempId,
        user_id: "local",
        cheatsheet_id: activeHistoryId,
        role: "user",
        message,
        created_at: new Date().toISOString(),
      };
      setChatMessages((prev) => [...prev, userMessage]);
      setChatLoading(true);
      try {
        const response = await fetch(apiUrl("/api/v1/chat/ask"), {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            cheatsheet_id: activeHistoryId,
            question: message,
          }),
        });
        const payload = (await response.json()) as ChatAskResponse;
        if (!response.ok) {
          throw new Error("Failed to get chat response");
        }
        const assistantMessage: ChatMessage = {
          id: `local-${Date.now()}-assistant`,
          user_id: "local",
          cheatsheet_id: activeHistoryId,
          role: "assistant",
          message: payload.answer,
          created_at: new Date().toISOString(),
        };
        setChatMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        toast({
          title: "Chat error",
          description: error instanceof Error ? error.message : "Failed to chat",
        });
      } finally {
        setChatLoading(false);
      }
    },
    [activeHistoryId, toast]
  );

  const handleClearChat = useCallback(async () => {
    const token = getAuthToken();
    if (!token || !activeHistoryId) return;
    setChatLoading(true);
    try {
      const response = await fetch(apiUrl(`/api/v1/chat/clear/${activeHistoryId}`), {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error("Failed to clear chat history");
      }
      setChatMessages([]);
    } catch (error) {
      toast({
        title: "Chat error",
        description: error instanceof Error ? error.message : "Failed to clear chat",
      });
    } finally {
      setChatLoading(false);
    }
  }, [activeHistoryId, toast]);

  const showHero = !isGenerated && !activeHistoryId;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen bg-background"
    >
      <div className="flex h-screen">
        <HistorySidebar
          items={historyItems}
          activeId={activeHistoryId}
          loading={historyLoading}
          isOpen={isSidebarOpen}
          onToggle={() => setIsSidebarOpen((prev) => !prev)}
          onSelect={handleSelectHistory}
          onDelete={handleDeleteHistory}
          onNew={handleNewCheatSheet}
        />

        <main className="relative flex-1 overflow-y-auto px-8 py-6 scrollbar-thin">
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
          <div className="relative z-10">
            <Navbar
              isSidebarOpen={isSidebarOpen}
              onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
            />
            {showHero && <HeroSection onUploadClick={scrollToUpload} />}
            <div className="mx-auto w-full max-w-5xl space-y-8 py-6">
              <UploadSection ref={uploadRef} files={files} onFilesSelect={setFiles} />
              <OptionsSection options={options} onChange={setOptions} />

              {/* Generate Button */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="flex justify-center"
              >
                <button
                  onClick={handleGenerate}
                  disabled={!files.length || isGenerating}
                  className="btn-gradient flex items-center gap-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  <Sparkles className="h-5 w-5" />
                  {isGenerating ? "Generating..." : "Generate Cheat Sheet"}
                </button>
              </motion.div>

              {/* Progress */}
              <AnimatePresence>
                {isGenerating && <ProgressBar progress={progress} isActive />}
              </AnimatePresence>

              {/* Results */}
              <AnimatePresence>
                {isGenerated && (
                  <motion.div
                    ref={resultsRef}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="space-y-6"
                  >
                    <CompressionStats
                      originalWords={stats.originalWords}
                      compressedWords={stats.compressedWords}
                    />

                    {/* View Toggle */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setViewMode("cheatsheet")}
                        className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all ${
                          viewMode === "cheatsheet"
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                        }`}
                      >
                        <FileTextIcon className="h-4 w-4" />
                        Cheat Sheet
                      </button>
                      <button
                        onClick={() => setViewMode("flashcards")}
                        className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all ${
                          viewMode === "flashcards"
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                        }`}
                      >
                        <LayoutGrid className="h-4 w-4" />
                        Flashcards
                      </button>
                      <button
                        onClick={() => setViewMode("chat")}
                        className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition-all ${
                          viewMode === "chat"
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                        }`}
                      >
                        Chat
                      </button>
                    </div>

                    <AnimatePresence mode="wait">
                      {viewMode === "cheatsheet" ? (
                        <motion.div
                          key="cheatsheet"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 20 }}
                          transition={{ duration: 0.3 }}
                        >
                          {cheatSheetData && <OutputSection data={cheatSheetData} />}
                        </motion.div>
                      ) : viewMode === "flashcards" ? (
                        <motion.div
                          key="flashcards"
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -20 }}
                          transition={{ duration: 0.3 }}
                        >
                          <FlashcardView flashcards={flashcardsData} />
                        </motion.div>
                      ) : (
                        <motion.div
                          key="chat"
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -20 }}
                          transition={{ duration: 0.3 }}
                        >
                          <ChatPanel
                            messages={chatMessages}
                            disabled={!activeHistoryId}
                            loading={chatLoading}
                            onSend={handleSendChat}
                            onClear={handleClearChat}
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>

                    <ExportOptions cheatsheet={cheatSheetData || undefined} flashcards={flashcardsData} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <Footer />
          </div>
        </main>
      </div>

      {/* Sticky generate button on mobile */}
      {files.length > 0 && !isGenerated && (
        <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-border/50 bg-card/90 p-4 backdrop-blur-lg md:hidden">
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn-gradient flex w-full items-center justify-center gap-2 disabled:opacity-50"
          >
            <Sparkles className="h-4 w-4" />
            {isGenerating ? "Generating..." : "Generate Cheat Sheet"}
          </button>
        </div>
      )}

    </motion.div>
  );
};

export default Index;

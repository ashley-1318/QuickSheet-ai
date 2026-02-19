import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface Flashcard {
  question: string;
  answer: string;
}

interface FlashcardViewProps {
  flashcards: Flashcard[];
}

const FlashcardView = ({ flashcards }: FlashcardViewProps) => {
  if (!flashcards.length) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-elevated p-8"
      >
        <h2 className="text-xl font-bold text-foreground">Flashcards</h2>
        <p className="mt-3 text-sm text-muted-foreground">
          No flashcards were generated for this document.
        </p>
      </motion.div>
    );
  }

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const goNext = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev + 1) % flashcards.length);
  };

  const goPrev = () => {
    setIsFlipped(false);
    setCurrentIndex((prev) => (prev - 1 + flashcards.length) % flashcards.length);
  };

  const card = flashcards[currentIndex];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-elevated p-8"
    >
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground">Flashcards</h2>
        <span className="text-sm text-muted-foreground">
          {currentIndex + 1} / {flashcards.length}
        </span>
      </div>

      <div
        className="flashcard-flip mx-auto cursor-pointer"
        style={{ maxWidth: 480 }}
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={`${currentIndex}-${isFlipped}`}
            initial={{ rotateY: 90, opacity: 0 }}
            animate={{ rotateY: 0, opacity: 1 }}
            exit={{ rotateY: -90, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="flex min-h-[240px] items-center justify-center rounded-2xl border border-border/50 p-8"
            style={{
              background: isFlipped ? "var(--gradient-button)" : undefined,
            }}
          >
            <div className="text-center">
              <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground"
                style={isFlipped ? { color: "hsl(var(--primary-foreground) / 0.7)" } : {}}
              >
                {isFlipped ? "Answer" : "Question"}
              </p>
              <p
                className={`text-lg font-medium ${isFlipped ? "text-primary-foreground" : "text-foreground"}`}
              >
                {isFlipped
                  ? card.answer || "Answer unavailable"
                  : card.question}
              </p>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <p className="mt-3 text-center text-xs text-muted-foreground">Click to flip</p>

      <div className="mt-6 flex items-center justify-center gap-4">
        <button
          onClick={goPrev}
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-secondary-foreground transition-all hover:bg-secondary/80"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <button
          onClick={goNext}
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-secondary-foreground transition-all hover:bg-secondary/80"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </motion.div>
  );
};

export default FlashcardView;

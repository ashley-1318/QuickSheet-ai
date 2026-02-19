import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

interface HeroSectionProps {
  onUploadClick: () => void;
}

const HeroSection = ({ onUploadClick }: HeroSectionProps) => {
  return (
    <section className="hero-gradient-bg relative overflow-hidden py-16 md:py-20">
      {/* Animated gradient blobs */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="blob-animate absolute -left-32 -top-32 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div
          className="blob-animate absolute -right-32 top-20 h-80 w-80 rounded-full bg-accent/10 blur-3xl"
          style={{ animationDelay: "2s" }}
        />
        <div
          className="blob-animate absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-primary/5 blur-3xl"
          style={{ animationDelay: "4s" }}
        />
      </div>

      <div className="relative mx-auto max-w-3xl px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-2 text-sm font-medium text-primary">
            <Sparkles className="h-4 w-4" />
            AI-Powered Study Assistant
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mx-auto max-w-3xl text-4xl font-extrabold leading-tight tracking-tight text-foreground md:text-6xl"
        >
          Turn Your Study Material into{" "}
          <span className="gradient-text">Smart Cheat Sheets</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground"
        >
          Upload your PDFs, notes, or documents. Our AI instantly compresses them into
          structured, revision-ready cheat sheets.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10"
        >
          <button onClick={onUploadClick} className="btn-gradient text-lg">
            Upload Document
          </button>
        </motion.div>
      </div>
    </section>
  );
};

export default HeroSection;

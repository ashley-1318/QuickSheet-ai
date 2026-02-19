import { motion } from "framer-motion";
import { FileText, TrendingDown } from "lucide-react";

interface CompressionStatsProps {
  originalWords: number;
  compressedWords: number;
}

const CompressionStats = ({ originalWords, compressedWords }: CompressionStatsProps) => {
  const ratio = originalWords > 0
    ? Math.round((1 - compressedWords / originalWords) * 100)
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="flex flex-wrap items-center gap-4 rounded-2xl bg-secondary/50 p-4"
    >
      <div className="flex items-center gap-2">
        <FileText className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">
          Original: <span className="font-semibold text-foreground">{originalWords.toLocaleString()} words</span>
        </span>
      </div>
      <div className="flex items-center gap-2">
        <TrendingDown className="h-4 w-4 text-primary" />
        <span className="text-sm text-muted-foreground">
          Compressed: <span className="font-semibold text-foreground">{compressedWords.toLocaleString()} words</span>
        </span>
      </div>
      <div className="rounded-lg bg-primary/10 px-3 py-1">
        <span className="text-sm font-bold text-primary">{ratio}% compression</span>
      </div>
    </motion.div>
  );
};

export default CompressionStats;

import { motion } from "framer-motion";

interface ProgressBarProps {
  progress: number;
  isActive: boolean;
}

const ProgressBar = ({ progress, isActive }: ProgressBarProps) => {
  if (!isActive) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="card-elevated overflow-hidden p-6"
    >
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="pulse-ai h-3 w-3 rounded-full bg-primary" />
          <span className="text-sm font-medium text-foreground">
            AI is generating your cheat sheet...
          </span>
        </div>
        <span className="text-sm font-semibold text-primary">{Math.round(progress)}%</span>
      </div>
      <div className="relative h-2 overflow-hidden rounded-full bg-secondary">
        <motion.div
          className="absolute inset-y-0 left-0 rounded-full"
          style={{ backgroundImage: "var(--gradient-button)" }}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
        <div className="progress-shimmer absolute inset-0" />
      </div>
    </motion.div>
  );
};

export default ProgressBar;

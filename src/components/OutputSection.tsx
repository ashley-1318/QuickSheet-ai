import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  ChevronDown,
  Image,
  Lightbulb,
  Table,
  Calculator,
  FileText,
} from "lucide-react";
import type { CheatSheetData } from "@/types/cheatsheet";

interface OutputSectionProps {
  data: CheatSheetData;
}

const sectionConfig = [
  { key: "definitions" as const, label: "Definitions", icon: BookOpen },
  { key: "coreFormulas" as const, label: "Core Formulas", icon: Calculator },
  { key: "keyConcepts" as const, label: "Key Concepts", icon: Lightbulb },
  { key: "diagrams" as const, label: "Diagrams", icon: Image },
  { key: "comparisonTable" as const, label: "Comparison Table", icon: Table },
  { key: "importantMetrics" as const, label: "Important Metrics", icon: BarChart3 },
  { key: "mistakesToAvoid" as const, label: "Mistakes to Avoid", icon: AlertTriangle },
  { key: "oneLineSummary" as const, label: "1-Line Summary", icon: FileText },
];

const OutputSection = ({ data }: OutputSectionProps) => {
  const [openSections, setOpenSections] = useState<Set<string>>(
    new Set(sectionConfig.map((s) => s.key))
  );

  const toggleSection = (key: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  // Calculate total items
  const totalItems = sectionConfig.reduce((sum, section) => {
    if (section.key === "oneLineSummary") {
      return sum + (data.oneLineSummary ? 1 : 0);
    }
    return sum + (data[section.key]?.length || 0);
  }, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="card-elevated overflow-hidden"
    >
      <div className="border-b border-border/50 bg-gradient-to-r from-primary/5 to-transparent p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold text-foreground">{data.title || "Study Cheat Sheet"}</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {totalItems} total items organized by topic
            </p>
          </div>
        </div>
      </div>

      <div className="overflow-y-auto p-6">
        <div className="space-y-3">
          {sectionConfig.map((section, index) => {
            const items =
              section.key === "oneLineSummary"
                ? data.oneLineSummary
                  ? [data.oneLineSummary]
                  : []
                : data[section.key];
            if (!items?.length) return null;
            const Icon = section.icon;
            const isOpen = openSections.has(section.key);

            return (
              <motion.div
                key={section.key}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="overflow-hidden rounded-xl border border-border/50 transition-all hover:border-primary/30"
              >
                <button
                  onClick={() => toggleSection(section.key)}
                  className="flex w-full items-center gap-3 bg-gradient-to-r from-primary/5 via-transparent to-transparent p-4 text-left transition-colors hover:bg-primary/10"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/15">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-foreground">{section.label}</p>
                    <p className="text-xs text-muted-foreground">{items.length} items</p>
                  </div>
                  <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary"
                  >
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  </motion.div>
                </button>

                <AnimatePresence>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="overflow-hidden border-t border-border/50"
                    >
                      <div className="space-y-2 px-4 py-4">
                        {items.map((item, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.05 }}
                            className="flex gap-3 rounded-lg bg-secondary/40 p-3 text-sm text-foreground transition-colors hover:bg-secondary/60"
                          >
                            <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                            <span className="leading-relaxed">{item}</span>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
};

export default OutputSection;

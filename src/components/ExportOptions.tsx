import { motion } from "framer-motion";
import { Download, FileText, Copy, Check } from "lucide-react";
import { useState } from "react";
import jsPDF from "jspdf";
import type { CheatSheetData, Flashcard } from "@/types/cheatsheet";

interface ExportOptionsProps {
  cheatsheet?: CheatSheetData;
  flashcards?: Flashcard[];
}

const ExportOptions = ({ cheatsheet, flashcards = [] }: ExportOptionsProps) => {
  const [copied, setCopied] = useState(false);

  const generateMarkdown = () => {
    const title = cheatsheet?.title || "Cheat Sheet";
    const lines = [`# ${title}\n`];

    if (cheatsheet?.definitions?.length) {
      lines.push("## Definitions\n");
      cheatsheet.definitions.forEach((def) => {
        lines.push(`- ${def}`);
      });
      lines.push("");
    }

    if (cheatsheet?.coreFormulas?.length) {
      lines.push("## Core Formulas\n");
      cheatsheet.coreFormulas.forEach((formula) => {
        lines.push(`- ${formula}`);
      });
      lines.push("");
    }

    if (cheatsheet?.keyConcepts?.length) {
      lines.push("## Key Concepts\n");
      cheatsheet.keyConcepts.forEach((concept) => {
        lines.push(`- ${concept}`);
      });
      lines.push("");
    }

    if (cheatsheet?.diagrams?.length) {
      lines.push("## Diagrams\n");
      cheatsheet.diagrams.forEach((diagram) => {
        lines.push(`- ${diagram}`);
      });
      lines.push("");
    }

    if (cheatsheet?.comparisonTable?.length) {
      lines.push("## Comparison Table\n");
      cheatsheet.comparisonTable.forEach((row) => {
        lines.push(`- ${row}`);
      });
      lines.push("");
    }

    if (cheatsheet?.importantMetrics?.length) {
      lines.push("## Important Metrics\n");
      cheatsheet.importantMetrics.forEach((metric) => {
        lines.push(`- ${metric}`);
      });
      lines.push("");
    }

    if (cheatsheet?.mistakesToAvoid?.length) {
      lines.push("## Mistakes to Avoid\n");
      cheatsheet.mistakesToAvoid.forEach((mistake) => {
        lines.push(`- ${mistake}`);
      });
      lines.push("");
    }

    if (cheatsheet?.oneLineSummary) {
      lines.push("## 1-Line Summary\n");
      lines.push(cheatsheet.oneLineSummary);
      lines.push("");
    }

    if (flashcards.length) {
      lines.push("## Flashcards\n");
      flashcards.forEach((card, idx) => {
        lines.push(`### Card ${idx + 1}`);
        lines.push(`**Q:** ${card.question}`);
        lines.push(`**A:** ${card.answer}\n`);
      });
    }

    return lines.join("\n");
  };

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    const pageHeight = doc.internal.pageSize.getHeight();
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 10;
    const lineHeight = 6;
    let yPosition = margin;

    const addText = (text: string, fontSize = 11, isBold = false) => {
      doc.setFontSize(fontSize);
      if (isBold) doc.setFont(undefined, "bold");
      else doc.setFont(undefined, "normal");

      const lines = doc.splitTextToSize(text, pageWidth - 2 * margin);
      for (const line of lines) {
        if (yPosition + lineHeight > pageHeight - margin) {
          doc.addPage();
          yPosition = margin;
        }
        doc.text(line, margin, yPosition);
        yPosition += lineHeight;
      }
      yPosition += 2;
    };

    addText(cheatsheet?.title || "Cheat Sheet", 18, true);
    yPosition += 4;

    if (cheatsheet?.definitions?.length) {
      addText("Definitions", 14, true);
      cheatsheet.definitions.forEach((def) => {
        addText(`• ${def}`, 10);
      });
    }

    if (cheatsheet?.coreFormulas?.length) {
      addText("Core Formulas", 14, true);
      cheatsheet.coreFormulas.forEach((formula) => {
        addText(`• ${formula}`, 10);
      });
    }

    if (cheatsheet?.keyConcepts?.length) {
      addText("Key Concepts", 14, true);
      cheatsheet.keyConcepts.forEach((concept) => {
        addText(`• ${concept}`, 10);
      });
    }

    if (cheatsheet?.diagrams?.length) {
      addText("Diagrams", 14, true);
      cheatsheet.diagrams.forEach((diagram) => {
        addText(`• ${diagram}`, 10);
      });
    }

    if (cheatsheet?.comparisonTable?.length) {
      addText("Comparison Table", 14, true);
      cheatsheet.comparisonTable.forEach((row) => {
        addText(`• ${row}`, 10);
      });
    }

    if (cheatsheet?.importantMetrics?.length) {
      addText("Important Metrics", 14, true);
      cheatsheet.importantMetrics.forEach((metric) => {
        addText(`• ${metric}`, 10);
      });
    }

    if (cheatsheet?.mistakesToAvoid?.length) {
      addText("Mistakes to Avoid", 14, true);
      cheatsheet.mistakesToAvoid.forEach((mistake) => {
        addText(`• ${mistake}`, 10);
      });
    }

    if (cheatsheet?.oneLineSummary) {
      addText("1-Line Summary", 14, true);
      addText(cheatsheet.oneLineSummary, 10);
    }

    if (flashcards.length) {
      addText("Flashcards", 14, true);
      flashcards.forEach((card, idx) => {
        addText(`Q${idx + 1}: ${card.question}`, 10, true);
        addText(`A: ${card.answer}`, 10);
        yPosition += 2;
      });
    }

    doc.save("cheatsheet.pdf");
  };

  const handleDownloadMarkdown = () => {
    const markdown = generateMarkdown();
    const element = document.createElement("a");
    element.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(markdown));
    element.setAttribute("download", "cheatsheet.md");
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleCopy = () => {
    const markdown = generateMarkdown();
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="flex flex-wrap gap-3"
    >
      <button
        onClick={handleDownloadPDF}
        className="flex items-center gap-2 rounded-xl bg-secondary px-5 py-2.5 text-sm font-medium text-secondary-foreground transition-all hover:bg-secondary/80 hover:scale-[1.02] active:scale-[0.98]"
      >
        <Download className="h-4 w-4" />
        Download PDF
      </button>
      <button
        onClick={handleDownloadMarkdown}
        className="flex items-center gap-2 rounded-xl bg-secondary px-5 py-2.5 text-sm font-medium text-secondary-foreground transition-all hover:bg-secondary/80 hover:scale-[1.02] active:scale-[0.98]"
      >
        <FileText className="h-4 w-4" />
        Download Markdown
      </button>
      <button
        onClick={handleCopy}
        className="flex items-center gap-2 rounded-xl bg-secondary px-5 py-2.5 text-sm font-medium text-secondary-foreground transition-all hover:bg-secondary/80 hover:scale-[1.02] active:scale-[0.98]"
      >
        {copied ? <Check className="h-4 w-4 text-primary" /> : <Copy className="h-4 w-4" />}
        {copied ? "Copied!" : "Copy to Clipboard"}
      </button>
    </motion.div>
  );
};

export default ExportOptions;

import { motion } from "framer-motion";
import { Info } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export interface OptionsState {
  revisionMode: string;
  examMode: string;
  formulaOnly: boolean;
  generateFlashcards: boolean;
  flashcardCount: number;
}

interface OptionsSectionProps {
  options: OptionsState;
  onChange: (options: OptionsState) => void;
}

const OptionsSection = ({ options, onChange }: OptionsSectionProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="card-elevated p-8"
    >
      <h2 className="mb-6 text-xl font-bold text-foreground">Advanced Options</h2>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            Revision Mode
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-3.5 w-3.5 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Controls the depth of your cheat sheet</p>
              </TooltipContent>
            </Tooltip>
          </label>
          <Select
            value={options.revisionMode}
            onValueChange={(v) => onChange({ ...options, revisionMode: v })}
          >
            <SelectTrigger className="rounded-xl bg-secondary/50 border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border z-50">
              <SelectItem value="quick">Quick 1-Page</SelectItem>
              <SelectItem value="standard">Standard</SelectItem>
              <SelectItem value="deep">Deep Revision</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            Exam Mode
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-3.5 w-3.5 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Tailors output to your exam type</p>
              </TooltipContent>
            </Tooltip>
          </label>
          <Select
            value={options.examMode}
            onValueChange={(v) => onChange({ ...options, examMode: v })}
          >
            <SelectTrigger className="rounded-xl bg-secondary/50 border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border z-50">
              <SelectItem value="semester">Semester Exam</SelectItem>
              <SelectItem value="competitive">Competitive Exam</SelectItem>
              <SelectItem value="interview">Interview Prep</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-3 sm:items-center">
        <label className="flex items-center gap-3 cursor-pointer">
          <Switch
            checked={options.formulaOnly}
            onCheckedChange={(v) => onChange({ ...options, formulaOnly: v })}
          />
          <span className="text-sm font-medium text-foreground">Formula Only Mode</span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer">
          <Switch
            checked={options.generateFlashcards}
            onCheckedChange={(v) => onChange({ ...options, generateFlashcards: v })}
          />
          <span className="text-sm font-medium text-foreground">Generate Flashcards</span>
        </label>
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            Flashcard Count
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-3.5 w-3.5 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Choose how many flashcards to generate (5-10).</p>
              </TooltipContent>
            </Tooltip>
          </label>
          <Select
            value={String(options.flashcardCount)}
            onValueChange={(v) => onChange({ ...options, flashcardCount: Number(v) })}
            disabled={!options.generateFlashcards}
          >
            <SelectTrigger className="rounded-xl bg-secondary/50 border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border z-50">
              <SelectItem value="5">5</SelectItem>
              <SelectItem value="6">6</SelectItem>
              <SelectItem value="7">7</SelectItem>
              <SelectItem value="8">8</SelectItem>
              <SelectItem value="9">9</SelectItem>
              <SelectItem value="10">10</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </motion.div>
  );
};

export default OptionsSection;

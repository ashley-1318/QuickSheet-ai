export interface CheatSheetData {
  title?: string;
  oneLineSummary: string;
  definitions: string[];
  coreFormulas: string[];
  keyConcepts: string[];
  diagrams: string[];
  comparisonTable: string[];
  importantMetrics: string[];
  mistakesToAvoid: string[];
}

export interface Flashcard {
  question: string;
  answer: string;
}

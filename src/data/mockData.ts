import type { CheatSheetData, Flashcard } from "@/types/cheatsheet";

export const mockCheatSheet: CheatSheetData = {
  title: "Machine Learning Cheat Sheet",
  oneLineSummary: "Core ML concepts, definitions, and formulas for quick revision.",
  definitions: [
    "Gradient Descent: An optimization algorithm that iteratively adjusts parameters to minimize a loss function",
    "Backpropagation: Algorithm for computing gradients in neural networks by propagating errors backward",
    "Epoch: One complete pass through the entire training dataset",
    "Learning Rate: Hyperparameter controlling the step size during gradient descent optimization",
    "Regularization: Techniques (L1, L2, Dropout) to prevent overfitting by adding constraints",
  ],
  coreFormulas: [
    "Mean Squared Error: MSE = (1/n) × Σ(yᵢ - ŷᵢ)²",
    "Sigmoid Function: σ(x) = 1 / (1 + e⁻ˣ)",
    "Softmax: P(yᵢ) = eʸⁱ / Σeʸʲ",
    "Cross-Entropy Loss: L = -Σ yᵢ × log(ŷᵢ)",
    "Gradient Update: θ = θ - α × ∇L(θ)",
  ],
  keyConcepts: [
    "Machine Learning enables systems to learn patterns from data",
    "Supervised Learning uses labeled data for prediction",
    "Unsupervised Learning discovers hidden structure in data",
    "Neural Networks use layered representations",
    "Overfitting reduces generalization performance",
  ],
  diagrams: [
    "Neural network: input layer → hidden layers → output layer",
    "Training pipeline: data → preprocessing → model → evaluation",
  ],
  comparisonTable: [
    "Supervised vs Unsupervised: labeled targets vs no labels",
    "Bias vs Variance: underfitting vs overfitting",
  ],
  importantMetrics: [
    "Accuracy, Precision, Recall, F1 Score",
    "Loss curves for training vs validation",
  ],
  mistakesToAvoid: [
    "Always normalize input features before training",
    "Use cross-validation to evaluate model generalization",
    "Batch size affects training speed and model convergence",
    "Adam optimizer combines momentum and RMSprop for adaptive learning",
    "Dropout randomly deactivates neurons during training to reduce overfitting",
    "Transfer learning leverages pre-trained models for new tasks with limited data",
  ],
};

export const mockFlashcards: Flashcard[] = [
  { question: "What is Gradient Descent?", answer: "An optimization algorithm that iteratively adjusts parameters to minimize a loss function by moving in the direction of steepest descent." },
  { question: "What is the Bias-Variance Tradeoff?", answer: "High bias = underfitting, high variance = overfitting. The goal is finding the sweet spot that minimizes total error." },
  { question: "What does the Sigmoid function do?", answer: "Maps any real number to a value between 0 and 1, commonly used in binary classification: σ(x) = 1/(1+e⁻ˣ)" },
  { question: "What is Backpropagation?", answer: "Algorithm for computing gradients of the loss function with respect to each weight by propagating errors backward through the network." },
  { question: "What is Regularization?", answer: "Techniques like L1, L2, or Dropout that add constraints to prevent overfitting and improve generalization on unseen data." },
  { question: "What is an Epoch?", answer: "One complete forward and backward pass through the entire training dataset during model training." },
];

import { motion } from "framer-motion";
import { Brain } from "lucide-react";

const Footer = () => {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className="border-t border-border/50 bg-card/50"
    >
      <div className="container mx-auto px-6 py-8">
        <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
          <div className="text-sm text-muted-foreground">
            QuickSheet AI &copy; 2026
          </div>
          <div className="flex gap-6">
            <span className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
              About
            </span>
            <span className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
              Privacy
            </span>
            <span className="text-sm text-muted-foreground hover:text-foreground transition-colors cursor-pointer">
              Terms
            </span>
          </div>
          <span className="rounded-lg bg-secondary px-3 py-1 text-xs font-medium text-muted-foreground">
            v1.0 POC
          </span>
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;

import { motion } from "framer-motion";
import { PanelLeftClose, Plus, Trash2, X } from "lucide-react";

export type HistoryItem = {
  id: string;
  title: string | null;
  one_line_summary: string | null;
  created_at: string;
};

interface HistorySidebarProps {
  items: HistoryItem[];
  activeId: string | null;
  loading: boolean;
  isOpen: boolean;
  onToggle: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onNew: () => void;
}

const HistorySidebar = ({
  items,
  activeId,
  loading,
  isOpen,
  onToggle,
  onSelect,
  onDelete,
  onNew,
}: HistorySidebarProps) => {
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 h-screen overflow-y-auto border-r border-gray-200 dark:border-white/10 bg-white dark:bg-zinc-900/60 backdrop-blur-md transition-all duration-300 scrollbar-thin md:relative md:flex-shrink-0 ${
        isOpen ? "translate-x-0 w-[280px] md:w-[280px]" : "-translate-x-full w-[280px] md:w-0 md:border-r-0"
      }`}
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b border-gray-200 dark:border-border/50 p-4">
          <button
            onClick={onNew}
            className="flex items-center gap-2 rounded-xl bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground"
          >
            <Plus className="h-4 w-4" />
            New Cheat Sheet
          </button>
          <div className="flex items-center gap-2">
            <button
              onClick={onToggle}
              className="rounded-lg p-2 text-gray-600 dark:text-muted-foreground hover:bg-gray-100 dark:hover:bg-secondary"
              aria-label="Collapse history"
            >
              <PanelLeftClose className="h-4 w-4 hidden md:block" />
              <X className="h-4 w-4 md:hidden" />
            </button>
          </div>
        </div>

        <div className="flex-1 p-3">
          {loading && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="px-2 py-3 text-xs text-gray-500 dark:text-muted-foreground"
            >
              Loading history...
            </motion.p>
          )}
          {!loading && items.length === 0 && (
            <p className="px-2 py-3 text-xs text-gray-500 dark:text-muted-foreground">No history yet.</p>
          )}
          <div className="mt-6 space-y-2">
            {items.map((item) => {
              const isActive = item.id === activeId;
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`group rounded-xl border border-transparent p-3 pl-4 text-left transition-all duration-200 ${
                    isActive
                      ? "-ml-1 border-l-4 border-purple-500 bg-white/5 dark:bg-white/5"
                      : "hover:bg-white/5 dark:hover:bg-white/5 hover:translate-x-1"
                  }`}
                >
                  <button
                    onClick={() => onSelect(item.id)}
                    className="block w-full text-left"
                  >
                    <p className="line-clamp-1 text-sm font-semibold text-gray-900 dark:text-white">
                      {item.title || "Untitled"}
                    </p>
                    <p className="line-clamp-2 text-xs text-gray-600 dark:text-gray-400">
                      {item.one_line_summary || "No summary"}
                    </p>
                    <p className="mt-1 text-[11px] text-gray-500 dark:text-gray-500">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </button>
                  <button
                    onClick={() => onDelete(item.id)}
                    className="mt-2 flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400 opacity-0 transition-opacity group-hover:opacity-100 hover:text-destructive"
                  >
                    <Trash2 className="h-3 w-3" />
                    Delete
                  </button>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </aside>
  );
};

export default HistorySidebar;

import { useState, useCallback, forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, File } from "lucide-react";

interface UploadSectionProps {
  files: File[];
  onFilesSelect: (files: File[]) => void;
}

const MAX_FILES = 4;

const UploadSection = forwardRef<HTMLDivElement, UploadSectionProps>(
  ({ files, onFilesSelect }, ref) => {
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = useCallback((e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback(() => {
      setIsDragging(false);
    }, []);

    const isSupportedFile = useCallback((file: File) => {
      const name = file.name.toLowerCase();
      const isPdf = file.type === "application/pdf" || name.endsWith(".pdf");
      const isDocx = file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        || name.endsWith(".docx");
      const isPptx = file.type === "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        || name.endsWith(".pptx");
      const isTxt = file.type === "text/plain" || name.endsWith(".txt");
      return isPdf || isDocx || isPptx || isTxt;
    }, []);

    const addFiles = useCallback((incoming: File[]) => {
      const filtered = incoming.filter(isSupportedFile);
      if (!filtered.length) return;
      const merged = [...files, ...filtered].slice(0, MAX_FILES);
      onFilesSelect(merged);
    }, [files, isSupportedFile, onFilesSelect]);

    const handleDrop = useCallback(
      (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const dropped = Array.from(e.dataTransfer.files || []);
        addFiles(dropped);
      },
      [addFiles]
    );

    const handleFileInput = useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        const selected = Array.from(e.target.files || []);
        addFiles(selected);
        e.target.value = "";
      },
      [addFiles]
    );

    return (
      <motion.div
        ref={ref}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="card-elevated p-8"
      >
        <h2 className="mb-6 text-xl font-bold text-foreground">Upload Study Materials</h2>

        <AnimatePresence mode="wait">
          {files.length === 0 ? (
            <motion.label
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`upload-zone flex flex-col items-center justify-center gap-4 ${isDragging ? "dragging" : ""}`}
            >
              <input
                type="file"
                accept=".pdf,.docx,.pptx,.txt"
                multiple
                onChange={handleFileInput}
                className="hidden"
              />
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                <Upload className="h-7 w-7 text-primary" />
              </div>
              <div className="text-center">
                <p className="font-semibold text-foreground">
                  Drag & drop your file here
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Supports PDF, DOCX, PPTX, and TXT files (up to {MAX_FILES})
                </p>
              </div>
              <div className="rounded-lg bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground">
                Browse Files
              </div>
            </motion.label>
          ) : (
            <motion.div
              key="preview"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`space-y-4 rounded-2xl bg-secondary/50 p-5 ${isDragging ? "ring-2 ring-primary/60" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-foreground">{files.length} file(s) selected</p>
                  <p className="text-sm text-muted-foreground">
                    You can add up to {MAX_FILES} files total
                  </p>
                </div>
                {files.length < MAX_FILES && (
                  <label className="rounded-lg bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground hover:bg-secondary/80">
                    Add More
                    <input
                      type="file"
                      accept=".pdf,.docx,.txt"
                      accept=".pdf,.docx,.pptx,.txt"
                      multiple
                      onChange={handleFileInput}
                      className="hidden"
                    />
                  </label>
                )}
              </div>
              <div className="space-y-3">
                {files.map((file, index) => (
                  <div
                    key={`${file.name}-${file.size}-${index}`}
                    className="flex items-center gap-4 rounded-xl bg-background/60 p-3"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                      {file.type === "application/pdf" ? (
                        <FileText className="h-6 w-6 text-primary" />
                      ) : (
                        <File className="h-6 w-6 text-primary" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="truncate font-medium text-foreground">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                    <button
                      onClick={() => onFilesSelect(files.filter((_, i) => i !== index))}
                      className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    );
  }
);

UploadSection.displayName = "UploadSection";

export default UploadSection;

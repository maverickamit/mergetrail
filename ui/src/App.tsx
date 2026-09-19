import { useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useState, type ReactNode } from "react";

import { fetchReview } from "./api";
import { DiffPane } from "./components/DiffPane";
import { FileTree } from "./components/FileTree";
import { Header } from "./components/Header";
import type { DiffMode } from "./types";

export function App() {
  const reviewQuery = useQuery({ queryKey: ["review"], queryFn: fetchReview });
  const files = reviewQuery.data?.files ?? [];
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [mode, setMode] = useState<DiffMode>("unified");
  const [filesOpen, setFilesOpen] = useState(false);

  const activePath = selectedPath && files.some((file) => file.path === selectedPath)
    ? selectedPath
    : (files[0]?.path ?? null);

  const selectFile = useCallback((path: string) => {
    setSelectedPath(path);
    setFilesOpen(false);
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey || event.altKey) {
        return;
      }
      const target = event.target;
      if (
        target instanceof HTMLElement &&
        (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)
      ) {
        return;
      }
      if (files.length === 0) {
        return;
      }
      const current = activePath ? files.findIndex((file) => file.path === activePath) : -1;
      if (event.key === "j" || event.key === "ArrowDown") {
        event.preventDefault();
        const next = files[Math.min(current + 1, files.length - 1)];
        if (next) {
          setSelectedPath(next.path);
        }
      } else if (event.key === "k" || event.key === "ArrowUp") {
        event.preventDefault();
        const previous = files[Math.max(current - 1, 0)];
        if (previous) {
          setSelectedPath(previous.path);
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [activePath, files]);

  if (reviewQuery.isPending) {
    return <Centered>Loading review…</Centered>;
  }

  if (reviewQuery.isError) {
    return (
      <Centered>
        <p className="font-medium text-del">Could not load this review</p>
        <p className="mt-2 max-w-lg text-sm text-muted">
          {reviewQuery.error instanceof Error ? reviewQuery.error.message : "Unknown error"}
        </p>
      </Centered>
    );
  }

  const review = reviewQuery.data;

  return (
    <div className="flex h-full min-h-0 flex-col bg-canvas">
      <Header
        review={review}
        mode={mode}
        onModeChange={setMode}
        filesOpen={filesOpen}
        onToggleFiles={() => setFilesOpen((open) => !open)}
      />
        <div className="flex min-h-0 flex-1 flex-col sm:flex-row">
        <aside
          className={`min-h-0 w-full shrink-0 overflow-y-auto border-b border-border bg-subtle sm:w-72 sm:border-r sm:border-b-0 ${
            filesOpen ? "block" : "hidden sm:block"
          }`}
        >
          <FileTree files={files} selectedPath={activePath} onSelect={selectFile} />
        </aside>
        <main className="min-h-0 min-w-0 flex-1 overflow-y-auto">
          {activePath ? (
            <DiffPane path={activePath} mode={mode} />
          ) : (
            <Centered>
              <p className="text-muted">No files changed between these refs.</p>
            </Centered>
          )}
        </main>
      </div>
    </div>
  );
}

function Centered({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full items-center justify-center bg-canvas px-6 text-center text-muted">
      <div>{children}</div>
    </div>
  );
}

import type { DiffMode, Review } from "../types";
import { repoName, shortSha } from "../lib/files";

type HeaderProps = {
  review: Review;
  mode: DiffMode;
  onModeChange: (mode: DiffMode) => void;
  filesOpen: boolean;
  onToggleFiles: () => void;
};

export function Header({
  review,
  mode,
  onModeChange,
  filesOpen,
  onToggleFiles,
}: HeaderProps) {
  return (
    <header className="flex flex-wrap items-center gap-3 border-b border-border bg-canvas px-4 py-3">
      <button
        type="button"
        className="rounded-md border border-border px-2 py-1 text-sm sm:hidden"
        onClick={onToggleFiles}
        aria-expanded={filesOpen}
      >
        Files
      </button>
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm font-semibold">{repoName(review.repo_path)}</div>
        <div className="mt-0.5 truncate font-mono text-xs text-muted">
          <span>{review.base}</span>
          <span className="mx-1">←</span>
          <span>{review.head}</span>
          <span className="mx-2 text-border">·</span>
          <span title={review.head_sha}>{shortSha(review.head_sha)}</span>
        </div>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <span className="text-muted">{review.files.length} files</span>
        <span className="font-mono text-add">+{review.additions}</span>
        <span className="font-mono text-del">−{review.deletions}</span>
        <div className="flex overflow-hidden rounded-md border border-border text-xs">
          <ModeButton active={mode === "unified"} onClick={() => onModeChange("unified")}>
            Unified
          </ModeButton>
          <ModeButton active={mode === "split"} onClick={() => onModeChange("split")}>
            Split
          </ModeButton>
        </div>
      </div>
    </header>
  );
}

function ModeButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-2.5 py-1 ${active ? "bg-subtle font-medium" : "bg-canvas text-muted"}`}
    >
      {children}
    </button>
  );
}

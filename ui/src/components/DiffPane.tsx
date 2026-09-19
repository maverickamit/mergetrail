import { DiffModeEnum, DiffView } from "@git-diff-view/react";
import "@git-diff-view/react/styles/diff-view.css";
import { useQuery } from "@tanstack/react-query";

import { fetchFile } from "../api";
import { unifiedPatch } from "../lib/patch";
import type { DiffMode, FileChange } from "../types";

type DiffPaneProps = {
  path: string;
  mode: DiffMode;
};

export function DiffPane({ path, mode }: DiffPaneProps) {
  const fileQuery = useQuery({
    queryKey: ["file", path],
    queryFn: () => fetchFile(path),
  });

  if (fileQuery.isPending) {
    return <p className="px-6 py-10 text-sm text-muted">Loading {path}…</p>;
  }

  if (fileQuery.isError) {
    return (
      <div className="px-6 py-10">
        <p className="font-medium text-del">Could not load this file</p>
        <p className="mt-2 text-sm text-muted">
          {fileQuery.error instanceof Error ? fileQuery.error.message : "Unknown error"}
        </p>
      </div>
    );
  }

  const file = fileQuery.data;

  return (
    <article>
      <div className="sticky top-0 z-10 border-b border-border bg-subtle px-4 py-2">
        <h2 className="truncate font-mono text-sm">
          {file.old_path && file.old_path !== file.path ? (
            <>
              <span className="text-muted">{file.old_path}</span>
              <span className="mx-1 text-muted">→</span>
              <span>{file.path}</span>
            </>
          ) : (
            file.path
          )}
        </h2>
      </div>
      <FileBody file={file} mode={mode} />
    </article>
  );
}

function FileBody({ file, mode }: { file: FileChange; mode: DiffMode }) {
  if (file.is_binary) {
    return <p className="px-6 py-10 text-sm text-muted">Binary file not shown.</p>;
  }
  if (file.hunks.length === 0) {
    return (
      <p className="px-6 py-10 text-sm text-muted">
        {file.status === "renamed" || file.status === "copied"
          ? "Renamed or copied with no content changes."
          : "No textual hunks in this file."}
      </p>
    );
  }

  return (
    <DiffView
      data={{
        oldFile: { fileName: file.old_path ?? file.path },
        newFile: { fileName: file.path },
        hunks: [unifiedPatch(file)],
      }}
      diffViewMode={mode === "split" ? DiffModeEnum.Split : DiffModeEnum.Unified}
      diffViewTheme="light"
      diffViewHighlight
      diffViewWrap={mode === "unified"}
    />
  );
}

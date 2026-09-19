import type { FileChange, Hunk } from "../types";

export function hunkToText(hunk: Hunk): string {
  return hunk.body ? `${hunk.header}\n${hunk.body}` : hunk.header;
}

export function unifiedPatch(file: FileChange): string {
  const oldPath = file.status === "added" ? "/dev/null" : `a/${file.old_path ?? file.path}`;
  const newPath = file.status === "deleted" ? "/dev/null" : `b/${file.path}`;
  const hunks = file.hunks.map(hunkToText).join("\n");
  return `--- ${oldPath}\n+++ ${newPath}\n${hunks}\n`;
}

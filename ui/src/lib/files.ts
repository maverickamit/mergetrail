import type { FileChange } from "../types";

export type DirNode = {
  kind: "dir";
  name: string;
  children: TreeNode[];
};

export type FileNode = {
  kind: "file";
  name: string;
  file: FileChange;
};

export type TreeNode = DirNode | FileNode;

export function fileTree(files: FileChange[]): TreeNode[] {
  const root: DirNode = { kind: "dir", name: "", children: [] };
  for (const file of files) {
    insert(root, file.path.split("/"), file);
  }
  sortTree(root);
  return root.children;
}

function sortTree(dir: DirNode): void {
  dir.children.sort((left, right) => {
    if (left.kind !== right.kind) {
      return left.kind === "dir" ? -1 : 1;
    }
    return left.name.localeCompare(right.name);
  });
  for (const child of dir.children) {
    if (child.kind === "dir") {
      sortTree(child);
    }
  }
}

function insert(dir: DirNode, parts: string[], file: FileChange): void {
  const [head, ...rest] = parts;
  if (head === undefined) {
    return;
  }
  if (rest.length === 0) {
    dir.children.push({ kind: "file", name: head, file });
    return;
  }
  let child = dir.children.find(
    (node): node is DirNode => node.kind === "dir" && node.name === head,
  );
  if (!child) {
    child = { kind: "dir", name: head, children: [] };
    dir.children.push(child);
  }
  insert(child, rest, file);
}

export function repoName(repoPath: string): string {
  const trimmed = repoPath.replace(/[/\\]+$/, "");
  const parts = trimmed.split(/[/\\]/);
  return parts[parts.length - 1] || trimmed;
}

export function shortSha(sha: string): string {
  return sha.slice(0, 7);
}

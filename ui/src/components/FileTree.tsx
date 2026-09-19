import type { ChangeStatus, FileChange } from "../types";
import { fileTree, type TreeNode } from "../lib/files";

type FileTreeProps = {
  files: FileChange[];
  selectedPath: string | null;
  onSelect: (path: string) => void;
};

const STATUS_LABEL: Record<ChangeStatus, string> = {
  added: "A",
  modified: "M",
  deleted: "D",
  renamed: "R",
  copied: "C",
  type_changed: "T",
};

const STATUS_CLASS: Record<ChangeStatus, string> = {
  added: "text-add",
  modified: "text-renamed",
  deleted: "text-del",
  renamed: "text-accent",
  copied: "text-accent",
  type_changed: "text-muted",
};

export function FileTree({ files, selectedPath, onSelect }: FileTreeProps) {
  if (files.length === 0) {
    return <p className="px-3 py-4 text-sm text-muted">No files in this review.</p>;
  }

  return (
    <nav aria-label="Changed files" className="py-2">
      <TreeList nodes={fileTree(files)} selectedPath={selectedPath} onSelect={onSelect} depth={0} />
    </nav>
  );
}

function TreeList({
  nodes,
  selectedPath,
  onSelect,
  depth,
}: {
  nodes: TreeNode[];
  selectedPath: string | null;
  onSelect: (path: string) => void;
  depth: number;
}) {
  return (
    <ul className="m-0 list-none p-0">
      {nodes.map((node) =>
        node.kind === "dir" ? (
          <li key={`dir:${node.name}`}>
            <div
              className="truncate px-3 py-1 text-xs font-semibold text-muted"
              style={{ paddingLeft: 12 + depth * 12 }}
            >
              {node.name}/
            </div>
            <TreeList
              nodes={node.children}
              selectedPath={selectedPath}
              onSelect={onSelect}
              depth={depth + 1}
            />
          </li>
        ) : (
          <li key={node.file.path}>
            <button
              type="button"
              onClick={() => onSelect(node.file.path)}
              className={`flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm hover:bg-canvas ${
                selectedPath === node.file.path ? "bg-canvas" : ""
              }`}
              style={{ paddingLeft: 12 + depth * 12 }}
            >
              <span
                className={`w-3 shrink-0 text-center font-mono text-xs ${STATUS_CLASS[node.file.status]}`}
              >
                {STATUS_LABEL[node.file.status]}
              </span>
              <span className="min-w-0 flex-1 truncate" title={node.file.path}>
                {node.name}
              </span>
              <span className="shrink-0 font-mono text-[11px]">
                <span className="text-add">+{node.file.additions}</span>
                <span className="ml-1 text-del">−{node.file.deletions}</span>
              </span>
            </button>
          </li>
        ),
      )}
    </ul>
  );
}

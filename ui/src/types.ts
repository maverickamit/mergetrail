export type ChangeStatus =
  | "added"
  | "modified"
  | "deleted"
  | "renamed"
  | "copied"
  | "type_changed";

export type Hunk = {
  id: string;
  header: string;
  old_start: number;
  old_lines: number;
  new_start: number;
  new_lines: number;
  body: string;
};

export type FileChange = {
  path: string;
  old_path: string | null;
  status: ChangeStatus;
  additions: number;
  deletions: number;
  is_binary: boolean;
  hunks: Hunk[];
};

export type Review = {
  repo_path: string;
  base: string;
  head: string;
  merge_base: string;
  head_sha: string;
  files: FileChange[];
  additions: number;
  deletions: number;
};

export type DiffMode = "unified" | "split";

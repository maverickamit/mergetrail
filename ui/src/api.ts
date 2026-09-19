import type { FileChange, Review } from "./types";

async function readError(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      typeof body === "object" &&
      body !== null &&
      "detail" in body &&
      typeof body.detail === "string"
    ) {
      return body.detail;
    }
  } catch {
    // Fall through to the status text.
  }
  return `${response.status} ${response.statusText}`;
}

export async function fetchReview(): Promise<Review> {
  const response = await fetch("/review");
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as Review;
}

export function fileUrl(path: string): string {
  return `/files/${path.split("/").map(encodeURIComponent).join("/")}`;
}

export async function fetchFile(path: string): Promise<FileChange> {
  const response = await fetch(fileUrl(path));
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return (await response.json()) as FileChange;
}

import type { BoardData } from "@/lib/kanban";

type ApiOptions = Omit<RequestInit, "body"> & { body?: unknown };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const buildUrl = (path: string) => {
  if (!API_BASE) {
    return path;
  }
  return new URL(path, API_BASE).toString();
};

const apiFetch = async <T>(path: string, options: ApiOptions = {}): Promise<T> => {
  const { body, headers, ...rest } = options;
  const response = await fetch(buildUrl(path), {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(headers ?? {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error("Request failed");
  }

  return (await response.json()) as T;
};

export const getKanban = () => apiFetch<BoardData>("/api/kanban");

export const renameColumn = (columnId: string, title: string) =>
  apiFetch<BoardData>(`/api/columns/${columnId}`, {
    method: "PATCH",
    body: { title },
  });

export const reorderColumns = (columnIds: string[]) =>
  apiFetch<BoardData>("/api/columns/reorder", {
    method: "POST",
    body: { column_ids: columnIds },
  });

export const createCard = (columnId: string, title: string, details: string) =>
  apiFetch<BoardData>("/api/cards", {
    method: "POST",
    body: { column_id: columnId, title, details },
  });

export const updateCard = (cardId: string, title: string, details: string) =>
  apiFetch<BoardData>(`/api/cards/${cardId}`, {
    method: "PATCH",
    body: { title, details },
  });

export const moveCard = (
  cardId: string,
  toColumnId: string,
  position: number
) =>
  apiFetch<BoardData>(`/api/cards/${cardId}/move`, {
    method: "POST",
    body: { to_column_id: toColumnId, position },
  });

export const deleteCard = (cardId: string) =>
  apiFetch<BoardData>(`/api/cards/${cardId}`, { method: "DELETE" });

export type ChatMessage = { role: "user" | "assistant"; content: string };

export type ChatResponse = { reply: string; board: BoardData };

export const sendChat = (message: string, history: ChatMessage[]) =>
  apiFetch<ChatResponse>("/api/ai/chat", {
    method: "POST",
    body: { message, history },
  });

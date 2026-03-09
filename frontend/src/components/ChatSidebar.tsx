"use client";

import { useState } from "react";
import type { BoardData } from "@/lib/kanban";
import { sendChat, type ChatMessage } from "@/lib/api";

const quickPrompts = [
  "Add a card to Backlog about reviewing Q2 goals.",
  "Move card-1 to Review.",
  "Rename the Backlog column to Next.",
];

type ChatSidebarProps = {
  board: BoardData;
  onBoardUpdate: (board: BoardData) => void;
};

export const ChatSidebar = ({ board, onBoardUpdate }: ChatSidebarProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed || isSending) {
      return;
    }

    const nextMessages: ChatMessage[] = [
      ...messages,
      { role: "user", content: trimmed },
    ];
    setMessages(nextMessages);
    setInput("");
    setIsSending(true);
    setError(null);

    try {
      const response = await sendChat(trimmed, nextMessages);
      setMessages([...nextMessages, { role: "assistant", content: response.reply }]);
      onBoardUpdate(response.board);
    } catch {
      setError("Unable to reach the AI assistant.");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <aside className="flex w-full flex-col rounded-[32px] border border-[var(--stroke)] bg-white/85 p-6 shadow-[var(--shadow)] backdrop-blur lg:w-[360px]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
            AI Assistant
          </p>
          <h2 className="mt-2 font-display text-2xl font-semibold text-[var(--navy-dark)]">
            Project copilot
          </h2>
        </div>
        <span className="rounded-full border border-[var(--stroke)] px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--primary-blue)]">
          Beta
        </span>
      </div>

      <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
        Ask the assistant to create, edit, or move cards. It will update the board
        immediately when it can.
      </p>

      <div className="mt-5 flex flex-wrap gap-2">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => handleSend(prompt)}
            className="rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold text-[var(--navy-dark)] transition hover:border-[var(--primary-blue)]"
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="mt-6 flex-1 space-y-3 overflow-y-auto rounded-2xl border border-dashed border-[var(--stroke)] bg-[var(--surface)] p-4">
        {messages.length === 0 ? (
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            No messages yet
          </p>
        ) : (
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={
                message.role === "user"
                  ? "rounded-2xl bg-white px-4 py-3 text-sm text-[var(--navy-dark)]"
                  : "rounded-2xl border border-[var(--stroke)] px-4 py-3 text-sm text-[var(--gray-text)]"
              }
            >
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
                {message.role === "user" ? "You" : "Assistant"}
              </p>
              <p className="mt-2 leading-6">{message.content}</p>
            </div>
          ))
        )}
      </div>

      {error ? (
        <p className="mt-4 rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--secondary-purple)]">
          {error}
        </p>
      ) : null}

      <form
        className="mt-4 space-y-3"
        onSubmit={(event) => {
          event.preventDefault();
          handleSend(input);
        }}
      >
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask for a change..."
          rows={3}
          className="w-full resize-none rounded-2xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
        />
        <button
          type="submit"
          disabled={isSending}
          className="inline-flex h-11 items-center justify-center rounded-full bg-[var(--secondary-purple)] px-5 text-xs font-semibold uppercase tracking-[0.2em] text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSending ? "Sending" : "Send"}
        </button>
      </form>
    </aside>
  );
};

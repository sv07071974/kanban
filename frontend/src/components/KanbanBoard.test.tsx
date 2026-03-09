import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData, type BoardData } from "@/lib/kanban";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

const cloneBoard = (board: BoardData): BoardData =>
  JSON.parse(JSON.stringify(board)) as BoardData;

const updateBoard = (board: BoardData, updater: (draft: BoardData) => void) => {
  const next = cloneBoard(board);
  updater(next);
  return next;
};

const makeFetchMock = (board: BoardData) =>
  vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString();
    const method = init?.method ?? "GET";

    if (url.includes("/api/kanban") && method === "GET") {
      return { ok: true, json: async () => cloneBoard(board) } as Response;
    }

    if (url.includes("/api/columns/") && method === "PATCH") {
      const payload = JSON.parse((init?.body as string) ?? "{}");
      const columnId = url.split("/api/columns/")[1];
      const next = updateBoard(board, (draft) => {
        draft.columns = draft.columns.map((column) =>
          column.id === columnId ? { ...column, title: payload.title } : column
        );
      });
      board = next;
      return { ok: true, json: async () => cloneBoard(board) } as Response;
    }

    if (url.includes("/api/cards") && method === "POST") {
      const payload = JSON.parse((init?.body as string) ?? "{}");
      const newId = `card-new-${Math.random().toString(36).slice(2, 6)}`;
      const next = updateBoard(board, (draft) => {
        draft.cards[newId] = {
          id: newId,
          title: payload.title,
          details: payload.details || "No details yet.",
        };
        draft.columns = draft.columns.map((column) =>
          column.id === payload.column_id
            ? { ...column, cardIds: [...column.cardIds, newId] }
            : column
        );
      });
      board = next;
      return { ok: true, json: async () => cloneBoard(board) } as Response;
    }

    if (url.includes("/api/cards/") && method === "DELETE") {
      const cardId = url.split("/api/cards/")[1];
      const next = updateBoard(board, (draft) => {
        delete draft.cards[cardId];
        draft.columns = draft.columns.map((column) => ({
          ...column,
          cardIds: column.cardIds.filter((id) => id !== cardId),
        }));
      });
      board = next;
      return { ok: true, json: async () => cloneBoard(board) } as Response;
    }

    return { ok: false, json: async () => ({}) } as Response;
  });

describe("KanbanBoard", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders five columns", () => {
    const board = cloneBoard(initialData);
    vi.stubGlobal("fetch", makeFetchMock(board));
    render(<KanbanBoard />);
    return screen.findAllByTestId(/column-/i).then((columns) => {
      expect(columns).toHaveLength(5);
    });
  });

  it("renames a column", async () => {
    const board = cloneBoard(initialData);
    vi.stubGlobal("fetch", makeFetchMock(board));
    render(<KanbanBoard />);
    const column = await screen.findAllByTestId(/column-/i).then(() =>
      getFirstColumn()
    );
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    input.blur();
    await waitFor(() => {
      expect(input).toHaveValue("New Name");
    });
  });

  it("adds and removes a card", async () => {
    const board = cloneBoard(initialData);
    vi.stubGlobal("fetch", makeFetchMock(board));
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(
      within(column).getByRole("button", { name: /add card/i })
    );

    await within(column).findByText("New card");

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    await waitFor(() => {
      expect(within(column).queryByText("New card")).not.toBeInTheDocument();
    });
  });
});

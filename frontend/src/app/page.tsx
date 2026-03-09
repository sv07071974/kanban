"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";

const AUTH_KEY = "pm-authenticated";
const VALID_USERNAME = "user";
const VALID_PASSWORD = "password";

export default function Home() {
  const [isReady, setIsReady] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem(AUTH_KEY) === "true";
    setIsAuthenticated(stored);
    setIsReady(true);
  }, []);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
      sessionStorage.setItem(AUTH_KEY, "true");
      setIsAuthenticated(true);
      setError("");
      return;
    }

    setError("Invalid credentials.");
  };

  const handleLogout = () => {
    sessionStorage.removeItem(AUTH_KEY);
    setIsAuthenticated(false);
    setUsername("");
    setPassword("");
    setError("");
  };

  if (!isReady) {
    return (
      <div className="min-h-screen bg-[var(--surface)]" aria-busy>
        <div className="mx-auto flex min-h-screen max-w-[720px] items-center px-6">
          <div className="w-full rounded-[32px] border border-[var(--stroke)] bg-white/80 p-10 shadow-[var(--shadow)]">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
              Loading
            </p>
            <p className="mt-4 text-lg text-[var(--navy-dark)]">
              Preparing your workspace...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
        <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

        <main className="relative mx-auto flex min-h-screen max-w-[720px] items-center px-6">
          <div className="w-full rounded-[32px] border border-[var(--stroke)] bg-white/85 p-10 shadow-[var(--shadow)] backdrop-blur">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
              Single Board Kanban
            </p>
            <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
              Sign in
            </h1>
            <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
              Use the demo account to access your board and keep momentum visible.
            </p>

            <form className="mt-8 grid gap-5" onSubmit={handleSubmit}>
              <label className="grid gap-2 text-sm font-semibold text-[var(--navy-dark)]">
                Username
                <input
                  className="h-12 w-full rounded-2xl border border-[var(--stroke)] bg-white px-4 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                  type="text"
                  name="username"
                  autoComplete="username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="user"
                  aria-label="Username"
                  required
                />
              </label>
              <label className="grid gap-2 text-sm font-semibold text-[var(--navy-dark)]">
                Password
                <input
                  className="h-12 w-full rounded-2xl border border-[var(--stroke)] bg-white px-4 text-sm font-medium text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
                  type="password"
                  name="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="password"
                  aria-label="Password"
                  required
                />
              </label>

              {error ? (
                <p className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--secondary-purple)]">
                  {error}
                </p>
              ) : null}

              <button
                type="submit"
                className="mt-2 inline-flex h-12 items-center justify-center rounded-full bg-[var(--secondary-purple)] px-6 text-sm font-semibold uppercase tracking-[0.2em] text-white transition hover:opacity-90"
              >
                Sign in
              </button>
            </form>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={handleLogout}
        className="absolute right-8 top-6 z-20 rounded-full border border-[var(--stroke)] bg-white/90 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)] transition hover:border-[var(--primary-blue)]"
      >
        Log out
      </button>
      <KanbanBoard />
    </div>
  );
}

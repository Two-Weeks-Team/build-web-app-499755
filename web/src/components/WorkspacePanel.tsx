"use client";

import { FormEvent, useState } from "react";

type Props = {
  loading: boolean;
  error: string | null;
  seeds: string[];
  onGenerate: (query: string, preferences: string) => Promise<void>;
  onReshape: (constraints: Record<string, string>) => Promise<void>;
};

export default function WorkspacePanel({ loading, error, seeds, onGenerate, onReshape }: Props) {
  const [query, setQuery] = useState("");
  const [preferences, setPreferences] = useState("4 workouts/week, full gym, knee-friendly lower body");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try { await onGenerate(query, preferences); } finally { setBusy(false); }
  };

  return (
    <div className="rounded-xl border border-border bg-card p-4 shadow-card">
      <h2 className="mb-3 text-xl">Paste-to-Plan Intake Canvas</h2>
      {error && <p className="mb-2 rounded bg-destructive/20 p-2 text-sm text-destructive">{error}</p>}
      <form onSubmit={submit} className="space-y-3">
        <textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="I want fat loss, 4 days, full gym, but knees get cranky..." className="min-h-36 w-full rounded-lg border border-border bg-muted p-3 text-sm" />
        <input value={preferences} onChange={(e) => setPreferences(e.target.value)} className="w-full rounded-lg border border-border bg-muted p-3 text-sm" />
        <button disabled={busy || loading || !query.trim()} className="w-full rounded-lg bg-primary px-4 py-3 font-semibold text-primary-foreground disabled:opacity-50">{busy ? "Generating blueprint..." : "Generate Training Blueprint"}</button>
      </form>
      <div className="mt-4">
        <p className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">Seed prompts</p>
        <div className="flex flex-wrap gap-2">
          {seeds.map((s) => (
            <button key={s} onClick={() => setQuery(s)} className="rounded-full border border-border bg-muted px-3 py-1 text-xs" type="button">{s}</button>
          ))}
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button onClick={() => onReshape({ equipment: "Home Dumbbells" })} type="button" className="rounded-full bg-accent px-3 py-1 text-xs text-accent-foreground">Switch to Home Dumbbells</button>
        <button onClick={() => onReshape({ session_length: "30" })} type="button" className="rounded-full bg-muted px-3 py-1 text-xs">Force 30-min Sessions</button>
      </div>
    </div>
  );
}

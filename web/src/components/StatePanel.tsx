"use client";

type Props = { mode: "loading" | "empty" | "error" | "success"; message?: string; onRetry?: () => void };

export default function StatePanel({ mode, message, onRetry }: Props) {
  if (mode === "success") return null;
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      {mode === "loading" && <p className="animate-pulse text-sm text-muted-foreground">Structuring your blueprint...</p>}
      {mode === "empty" && <p className="text-sm text-muted-foreground">Paste rough goals to generate your first training blueprint.</p>}
      {mode === "error" && (
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-destructive">{message || "Something went wrong. Please retry."}</p>
          <button onClick={onRetry} className="rounded-md bg-primary px-3 py-1 text-sm text-primary-foreground">Retry</button>
        </div>
      )}
    </div>
  );
}

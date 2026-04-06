"use client";

type Props = { onRetry: () => Promise<void> };

export default function Hero({ onRetry }: Props) {
  return (
    <header className="border-b border-border/80 bg-card/70 backdrop-blur px-4 py-4">
      <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">FormulateFit AI Studio</p>
          <h1 className="text-2xl text-foreground">Turn rough goals into a training blueprint in one pass</h1>
        </div>
        <button onClick={onRetry} className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition hover:opacity-90">
          Reload Demo State
        </button>
      </div>
    </header>
  );
}

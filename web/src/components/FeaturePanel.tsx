"use client";

type Props = { highlights: string[]; nextActions: string[] };

export default function FeaturePanel({ highlights, nextActions }: Props) {
  return (
    <section className="rounded-xl border border-border bg-card p-4 rise-in">
      <h3 className="text-lg">Plan Viability & Rationale</h3>
      <div className="mt-3 grid gap-4 md:grid-cols-2">
        <div>
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Why this plan works</p>
          <ul className="mt-2 list-disc pl-5 text-sm text-foreground">
            {highlights.map((h) => <li key={h}>{h}</li>)}
          </ul>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Next coach actions</p>
          <ul className="mt-2 list-disc pl-5 text-sm text-foreground">
            {nextActions.map((n) => <li key={n}>{n}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}

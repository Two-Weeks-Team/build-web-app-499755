"use client";

type Props = { plan: any; changeSummary?: string };

export default function InsightPanel({ plan, changeSummary }: Props) {
  if (!plan) {
    return <div className="rounded-xl border border-border bg-card p-4">Waiting for blueprint generation...</div>;
  }
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-border bg-card p-4">
        <h2 className="text-xl">Structured Fitness Brief</h2>
        <p className="mt-2 text-sm text-muted-foreground">{plan.summary}</p>
      </div>
      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="text-lg">Weekly Training Split</h3>
        <div className="mt-3 space-y-2">
          {(plan.items ?? []).map((block: any) => (
            <div key={block.day} className="rounded-lg border border-border bg-muted p-3">
              <p className="font-semibold">{block.day} · {block.focus}</p>
              <p className="text-sm text-muted-foreground">{block.duration} min · {block.recovery_note}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-xl border border-border bg-card p-4">
        <h3 className="text-lg">Plan Viability</h3>
        <p className="text-success">Score: {plan.score}/100</p>
        <p className="mt-2 text-sm text-muted-foreground">{plan.rationale}</p>
        {changeSummary && <p className="mt-2 text-sm text-warning">Adaptation Preview: {changeSummary}</p>}
      </div>
    </div>
  );
}

"use client";

type Props = { score: number; blocks: number; saved: number; changes: number };

export default function StatsStrip({ score, blocks, saved, changes }: Props) {
  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      {[
        ["Viability", `${score}/100`, "text-success"],
        ["Workout Blocks", `${blocks}`, "text-foreground"],
        ["Saved Blueprints", `${saved}`, "text-accent"],
        ["Live Adaptations", `${changes}`, "text-warning"]
      ].map(([label, value, tone]) => (
        <div key={label as string} className="rounded-lg border border-border bg-card p-3">
          <p className="text-xs text-muted-foreground">{label as string}</p>
          <p className={`text-lg font-semibold ${tone as string}`}>{value as string}</p>
        </div>
      ))}
    </div>
  );
}

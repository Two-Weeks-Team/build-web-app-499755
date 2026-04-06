"use client";

type Props = { onSeedPick: (seed: string) => void };

const seeds = [
  "Maya Chen - 29 - wants fat loss and consistency with 4 workouts per week and full gym access",
  "Jordan Alvarez - 41 - wants strength and mobility with a prior knee issue and 30 minute sessions",
  "Priya Nair - 34 - wants postpartum-friendly general fitness with home dumbbells and low impact training"
];

export default function ReferenceShelf({ onSeedPick }: Props) {
  return (
    <section className="rounded-xl border border-border bg-card p-4">
      <h3 className="text-lg">Seed Prompt Shelf</h3>
      <p className="text-sm text-muted-foreground">Tap any sample to instantly populate the intake canvas.</p>
      <div className="mt-3 space-y-2">
        {seeds.map((seed) => (
          <button
            key={seed}
            onClick={() => onSeedPick(seed)}
            className="w-full rounded-md border border-border bg-muted p-3 text-left text-sm transition hover:border-primary"
          >
            {seed}
          </button>
        ))}
      </div>
    </section>
  );
}

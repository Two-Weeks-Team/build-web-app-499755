"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchItems, generatePlan, fetchInsights } from "@/lib/api";
import StatsStrip from "@/components/StatsStrip";
import ReferenceShelf from "@/components/ReferenceShelf";
import StatePanel from "@/components/StatePanel";
import FeaturePanel from "@/components/FeaturePanel";

export default function Page() {
  const [query, setQuery] = useState("");
  const [preferences, setPreferences] = useState("goal=fat loss;equipment=full gym;frequency=4;session=45");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [plan, setPlan] = useState<any>(null);
  const [insights, setInsights] = useState<string[]>([]);
  const [nextActions, setNextActions] = useState<string[]>([]);
  const [highlights, setHighlights] = useState<string[]>([]);
  const [saved, setSaved] = useState<any[]>([]);
  const [changes, setChanges] = useState(0);

  const loadInitial = async () => {
    setLoading(true);
    setError("");
    try {
      const initial = await fetchItems();
      setPlan(initial);
      setQuery("Maya Chen - 29 - wants fat loss and consistency with 4 workouts per week and full gym access");
      const i = await fetchInsights({ selection: "initial", context: initial.summary });
      setInsights(i.insights);
      setNextActions(i.next_actions);
      setHighlights(i.highlights);
    } catch (e: any) {
      setError(e.message || "Failed to load");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadInitial(); }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const next = await generatePlan({ query, preferences });
      setPlan(next);
      const i = await fetchInsights({ selection: "generated-plan", context: next.summary });
      setInsights(i.insights);
      setNextActions(i.next_actions);
      setHighlights(i.highlights);
      setChanges((c) => c + 1);
    } catch (e: any) {
      setError(e.message || "Failed to generate plan");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSave = async () => {
    if (!plan) return;
    setSaved((s) => [{ id: Date.now(), ts: new Date().toISOString(), plan }, ...s]);
  };

  const stateMode = useMemo(() => {
    if (loading || submitting) return "loading" as const;
    if (error) return "error" as const;
    if (!plan) return "empty" as const;
    return "success" as const;
  }, [loading, submitting, error, plan]);

  return (
    <main className="studio-grid min-h-screen p-4 md:p-6">
      <div className="mx-auto max-w-[1400px] space-y-4 fade-in">
        <header className="rounded-xl border border-border bg-card/90 p-5 backdrop-blur">
          <h1 className="text-3xl md:text-4xl">FormulateFit AI Studio</h1>
          <p className="mt-2 max-w-3xl text-sm text-muted-foreground">Drop messy fitness notes on the left. Watch a structured Fitness Brief, Weekly Training Split, and viability rationale build on the right in one pass.</p>
        </header>

        <StatsStrip score={plan?.score ?? 0} blocks={plan?.items?.length ?? 0} saved={saved.length} changes={changes} />

        <div className="grid gap-4 lg:grid-cols-[1fr_1.35fr]">
          <section className="space-y-4 rounded-xl border border-border bg-card p-4">
            <h2 className="text-xl">Paste-to-Plan Intake Canvas</h2>
            <form onSubmit={handleGenerate} className="space-y-3">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={7}
                className="w-full rounded-lg border border-border bg-muted p-3 text-sm outline-none focus:shadow-focus"
                placeholder="Paste your fitness goals or rough client notes"
              />
              <input
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
                className="w-full rounded-lg border border-border bg-muted p-3 text-sm outline-none focus:shadow-focus"
                placeholder="Goals, constraints, equipment, and schedule"
              />
              <div className="flex gap-2">
                <button type="submit" disabled={submitting} className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-60">Generate Training Blueprint</button>
                <button type="button" onClick={handleSave} className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground">Save Blueprint</button>
              </div>
            </form>
            <ReferenceShelf onSeedPick={setQuery} />
          </section>

          <section className="space-y-4 rounded-xl border border-border bg-card p-4">
            <h2 className="text-xl">Blueprint Whiteboard</h2>
            <StatePanel mode={stateMode} message={error} onRetry={loadInitial} />
            {plan && (
              <div className="space-y-4 rise-in">
                <div className="rounded-lg border border-border bg-muted p-3">
                  <p className="text-xs uppercase tracking-wider text-muted-foreground">Structured Fitness Brief</p>
                  <p className="mt-2 text-sm">{plan.summary}</p>
                </div>
                <div className="rounded-lg border border-border bg-muted p-3">
                  <p className="text-xs uppercase tracking-wider text-muted-foreground">Weekly Training Split Board</p>
                  <div className="mt-2 grid gap-2 md:grid-cols-2">
                    {(plan.items || []).map((it: any, idx: number) => (
                      <div key={idx} className="rounded-md border border-border bg-card p-2 text-sm">{typeof it === "string" ? it : JSON.stringify(it)}</div>
                    ))}
                  </div>
                </div>
                <FeaturePanel highlights={highlights} nextActions={nextActions} />
                <div className="rounded-lg border border-border bg-muted p-3">
                  <p className="text-xs uppercase tracking-wider text-muted-foreground">Saved Blueprint History</p>
                  <div className="mt-2 space-y-2 text-sm">
                    {saved.length === 0 ? <p className="text-muted-foreground">No saved versions yet. Save this plan to prove durable artifact workflow.</p> : saved.map((s) => (
                      <button key={s.id} onClick={() => setPlan(s.plan)} className="block w-full rounded-md border border-border bg-card p-2 text-left hover:border-primary">Blueprint snapshot · {new Date(s.ts).toLocaleString()}</button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

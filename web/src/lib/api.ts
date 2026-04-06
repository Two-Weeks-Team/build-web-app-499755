export type PlanRequest = { query: string; preferences: string };
export type PlanResponse = { summary: string; items: any; score: number };
export type InsightsRequest = { selection: string; context: string };
export type InsightsResponse = { insights: string[]; next_actions: string[]; highlights: string[] };

export async function fetchItems(): Promise<PlanResponse> {
  const response = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: "Maya Chen - 29 - wants fat loss and consistency with 4 workouts per week and full gym access",
      preferences: "goal=fat loss;equipment=full gym;frequency=4;session=45"
    })
  });
  if (!response.ok) throw new Error("Failed to fetch initial plan");
  return response.json();
}

export async function generatePlan(payload: PlanRequest): Promise<PlanResponse> {
  const response = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Plan generation failed");
  return response.json();
}

export async function fetchInsights(payload: InsightsRequest): Promise<InsightsResponse> {
  const response = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Failed to generate insights");
  return response.json();
}

"use client";

import { useState } from "react";

type Blueprint = { id: string; name: string; created_at: string };

type Props = {
  blueprints: Blueprint[];
  onSave: (name: string) => Promise<void>;
  onRestore: (id: string) => Promise<void>;
};

export default function CollectionPanel({ blueprints, onSave, onRestore }: Props) {
  const [name, setName] = useState("6-week Foundation Reset");
  const [saving, setSaving] = useState(false);

  return (
    <aside className="rounded-xl border border-border bg-card p-4 shadow-card">
      <h3 className="text-lg">Saved Blueprint Library</h3>
      <div className="mt-3 flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-lg border border-border bg-muted px-3 py-2 text-sm" />
        <button
          onClick={async () => {
            setSaving(true);
            try { await onSave(name); } finally { setSaving(false); }
          }}
          className="rounded-lg bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground"
        >
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
      <ul className="mt-4 space-y-2">
        {blueprints.length === 0 && <li className="text-sm text-muted-foreground">No saved blueprints yet.</li>}
        {blueprints.map((bp) => (
          <li key={bp.id} className="rounded-lg border border-border bg-muted p-2">
            <p className="text-sm font-semibold">{bp.name}</p>
            <p className="text-xs text-muted-foreground">{bp.created_at}</p>
            <button onClick={() => onRestore(bp.id)} className="mt-1 rounded bg-accent px-2 py-1 text-xs text-accent-foreground">Reopen</button>
          </li>
        ))}
      </ul>
    </aside>
  );
}

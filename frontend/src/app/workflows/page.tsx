"use client";

import { useEffect, useState } from "react";
import {
  Layers,
  Play,
  Pause,
  RotateCw,
  CheckCircle2,
  Clock,
  AlertCircle,
  Calendar,
  Send,
  Building2,
  Plus,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";

interface CadenceItem {
  id: string;
  title: string;
  company_id: string;
  status: string;
  current_step_index: number;
  total_steps: number;
  next_run_at: string | null;
  last_run_at: string | null;
  created_at: string;
}

interface CadenceDetails extends CadenceItem {
  steps_config: Array<{
    step_index: number;
    day_offset: number;
    name: string;
    action_type: string;
    channel: string;
    description: string;
    requires_hitl: boolean;
  }>;
  execution_history: Array<{
    step_index: number;
    step_name: string;
    action_type: string;
    channel: string;
    executed_at: string;
    status: string;
    note?: string;
    approval_id?: string;
  }>;
}

export default function WorkflowsPage() {
  const [cadences, setCadences] = useState<CadenceItem[]>([]);
  const [selectedCadence, setSelectedCadence] = useState<CadenceDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [newCompanyName, setNewCompanyName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  const fetchCadences = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://localhost:8000/api/v1/workflows/cadence", {
        headers: {
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setCadences(data);
        if (data.length > 0 && !selectedCadence) {
          fetchDetails(data[0].id);
        }
      }
    } catch (err) {
      console.error("Failed to load cadences", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDetails = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workflows/cadence/${id}`, {
        headers: {
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setSelectedCadence(data);
      }
    } catch (err) {
      console.error("Failed to fetch cadence details", err);
    }
  };

  const handleExecuteStep = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workflows/cadence/${id}/step`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
        },
      });
      if (res.ok) {
        setActionMsg("Step executed successfully!");
        fetchDetails(id);
        fetchCadences();
        setTimeout(() => setActionMsg(null), 3000);
      }
    } catch (err) {
      console.error("Execute step failed", err);
    }
  };

  const handleTogglePause = async (id: string, currentStatus: string) => {
    const endpoint = currentStatus === "PAUSED" ? "resume" : "pause";
    try {
      const res = await fetch(`http://localhost:8000/api/v1/workflows/cadence/${id}/${endpoint}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
        },
      });
      if (res.ok) {
        fetchDetails(id);
        fetchCadences();
      }
    } catch (err) {
      console.error("Toggle pause failed", err);
    }
  };

  const handleCreateCadence = async () => {
    if (!newCompanyName.trim()) return;
    try {
      const res = await fetch("http://localhost:8000/api/v1/workflows/cadence", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
        },
        body: JSON.stringify({
          company_id: newCompanyName.toLowerCase().replace(/\s+/g, "_"),
          title: `10-Day Multi-Touch Cadence for ${newCompanyName}`,
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setNewCompanyName("");
        setIsCreating(false);
        fetchCadences();
        fetchDetails(created.id);
      }
    } catch (err) {
      console.error("Create cadence failed", err);
    }
  };

  useEffect(() => {
    fetchCadences();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Durable Execution
            </span>
            <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Phase 3 Live
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight mt-2 flex items-center gap-3">
            <Layers className="w-8 h-8 text-indigo-400" />
            Pursuit Cadence & Workflow Engine
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Automate durable multi-day sales cadences with automated signal harvesting, staged HITL approval gates, and scheduled calendar invitations.
          </p>
        </div>

        <button
          onClick={() => setIsCreating(!isCreating)}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          Create New Cadence
        </button>
      </div>

      {/* Action Notification */}
      {actionMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          {actionMsg}
        </div>
      )}

      {/* Create Cadence Form */}
      {isCreating && (
        <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 shadow-2xl space-y-4 animate-fade-in">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">Deploy New 10-Day Cadence</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={newCompanyName}
              onChange={(e) => setNewCompanyName(e.target.value)}
              placeholder="Target Company Name (e.g. Acme Corp, Stripe)"
              className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleCreateCadence}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl transition-colors"
            >
              Initialize Cadence
            </button>
            <button
              onClick={() => setIsCreating(false)}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold rounded-xl transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Main Grid: Cadences List + Selected Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Cadences List */}
        <div className="space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center justify-between">
            <span>Active Cadences</span>
            <span className="text-xs text-slate-400 font-mono">({cadences.length})</span>
          </h2>

          <div className="space-y-3">
            {cadences.length === 0 && !loading && (
              <div className="glass-panel p-8 rounded-2xl border border-slate-800/80 text-center text-slate-500 text-xs">
                No active cadences found. Click "Create New Cadence" above.
              </div>
            )}

            {cadences.map((c) => (
              <div
                key={c.id}
                onClick={() => fetchDetails(c.id)}
                className={`glass-panel p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedCadence?.id === c.id
                    ? "border-indigo-500/60 bg-indigo-950/20 shadow-lg"
                    : "border-slate-800/80 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white tracking-wide truncate max-w-[180px]">{c.title}</span>
                  <span
                    className={`px-2 py-0.5 text-[10px] font-bold rounded-full uppercase border ${
                      c.status === "ACTIVE"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : c.status === "WAITING_APPROVAL"
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse"
                        : c.status === "COMPLETED"
                        ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
                        : "bg-slate-500/10 text-slate-400 border-slate-500/20"
                    }`}
                  >
                    {c.status}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>
                    Progress: <span className="text-white font-mono">{c.current_step_index} / {c.total_steps} Steps</span>
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Selected Cadence Step Visualizer */}
        <div className="lg:col-span-2 space-y-6">
          {selectedCadence ? (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 shadow-2xl space-y-6">
              {/* Header Details */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
                <div>
                  <h2 className="text-lg font-bold text-white">{selectedCadence.title}</h2>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">Workflow ID: {selectedCadence.id}</p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleExecuteStep(selectedCadence.id)}
                    disabled={selectedCadence.status === "COMPLETED"}
                    className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-sky-500 hover:from-indigo-600 hover:to-sky-600 disabled:opacity-50 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 shadow-md transition-all"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    Advance Next Step
                  </button>

                  <button
                    onClick={() => handleTogglePause(selectedCadence.id, selectedCadence.status)}
                    className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-xl border border-slate-700 flex items-center gap-1.5 transition-colors"
                  >
                    {selectedCadence.status === "PAUSED" ? (
                      <>
                        <Play className="w-3.5 h-3.5" />
                        Resume
                      </>
                    ) : (
                      <>
                        <Pause className="w-3.5 h-3.5" />
                        Pause
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* 4-Step Visualizer */}
              <div>
                <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4">
                  Cadence Touchpoints & Stage Sequence
                </h3>

                <div className="space-y-3">
                  {selectedCadence.steps_config.map((step, idx) => {
                    const isCompleted = idx < selectedCadence.current_step_index;
                    const isCurrent = idx === selectedCadence.current_step_index;

                    return (
                      <div
                        key={step.step_index}
                        className={`p-4 rounded-xl border transition-all ${
                          isCompleted
                            ? "border-emerald-500/30 bg-emerald-950/10"
                            : isCurrent
                            ? "border-indigo-500/50 bg-indigo-950/20 shadow-md"
                            : "border-slate-800/80 bg-slate-900/30 opacity-60"
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs mb-1">
                          <div className="flex items-center gap-2">
                            {isCompleted ? (
                              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            ) : isCurrent ? (
                              <Clock className="w-4 h-4 text-indigo-400 animate-spin" />
                            ) : (
                              <div className="w-4 h-4 rounded-full border border-slate-600 flex items-center justify-center text-[10px] text-slate-500">
                                {idx + 1}
                              </div>
                            )}
                            <span className="font-bold text-white">{step.name}</span>
                          </div>

                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-slate-300 border border-slate-700">
                            {step.channel}
                          </span>
                        </div>

                        <p className="text-xs text-slate-400 mt-1 ml-6">{step.description}</p>

                        {step.requires_hitl && (
                          <div className="mt-2 ml-6 inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20">
                            <ShieldAlert className="w-3 h-3 text-amber-400" />
                            Requires Human Approval before send
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Execution History */}
              {selectedCadence.execution_history && selectedCadence.execution_history.length > 0 && (
                <div className="pt-4 border-t border-slate-800/80">
                  <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
                    Execution Audit Log
                  </h3>
                  <div className="space-y-2">
                    {selectedCadence.execution_history.map((hist, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/60 text-xs flex items-center justify-between"
                      >
                        <div>
                          <p className="font-semibold text-slate-200">{hist.step_name}</p>
                          <p className="text-slate-400 text-[11px] mt-0.5">{hist.note}</p>
                        </div>
                        <span className="text-slate-500 font-mono text-[10px]">
                          {new Date(hist.executed_at).toLocaleTimeString()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="glass-panel p-12 rounded-2xl border border-slate-800/80 text-center text-slate-500 text-sm">
              Select a cadence on the left to view stage timeline and execution logs.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

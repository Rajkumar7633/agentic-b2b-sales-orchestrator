"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Bot, Cpu, Sparkles, CheckCircle2, Zap, UserCheck, ShieldCheck } from "lucide-react";

export default function AgentRegistryPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAgents() {
      try {
        const data = await fetchApi("/agents");
        setAgents(data || []);
      } catch (err) {
        console.error("Fetch agents error:", err);
        setAgents([]);
      } finally {
        setLoading(false);
      }
    }
    loadAgents();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Agent Telemetry &amp; Registry...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              AI Agent Registry &amp; Human Boundaries
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-sky-300 bg-sky-500/10 rounded-full border border-sky-500/20 uppercase tracking-wider flex items-center gap-1">
              <Zap className="w-3 h-3 text-sky-400 fill-current" /> {agents.length} Active AI Agents
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Live telemetry for active AI agents alongside explicit Human-in-the-Loop task boundaries.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="px-3.5 py-1.5 text-xs font-bold text-slate-300 bg-slate-800/80 rounded-xl border border-slate-700/80 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" /> Multi-Provider LLM Engine
          </span>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {/* Active AI Agents Column */}
        <div className="space-y-4">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" /> Active AI Reasoning Agents ({agents.length})
          </h2>
          <div className="space-y-4">
            {agents.map((agent) => (
              <div
                key={agent.id || agent.agent_id}
                className="p-5 rounded-3xl glass-panel space-y-3 border-l-4 border-l-indigo-500"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-2xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30 shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div>
                      <h3 className="font-extrabold text-sm text-white">{agent.name}</h3>
                      <span className="text-[10px] text-slate-400 font-mono">ID: {agent.id || agent.agent_id}</span>
                    </div>
                  </div>

                  <span className="px-2.5 py-0.5 text-[10px] font-extrabold rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">
                    {agent.status || "HEALTHY"}
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  {(agent.capabilities || []).map((cap: string, idx: number) => (
                    <span key={idx} className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-slate-900 text-slate-300 rounded border border-slate-800">
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Human Task Boundaries Column */}
        <div className="space-y-4">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-amber-400" /> Human-in-the-Loop Action Boundaries
          </h2>
          <div className="space-y-4">
            <div className="p-5 rounded-3xl glass-panel space-y-3 border-l-4 border-l-amber-500">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-amber-400" />
                <h3 className="font-extrabold text-sm text-white">LinkedIn Prospecting &amp; Messaging</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                LinkedIn outreach, connection requests, and message sends are 100% human tasks. AI provides candidate copy holding for human approval.
              </p>
            </div>

            <div className="p-5 rounded-3xl glass-panel space-y-3 border-l-4 border-l-sky-500">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-sky-400" />
                <h3 className="font-extrabold text-sm text-white">Google Meet Booking &amp; Calls</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Meeting scheduling and live customer calls are conducted by human sales reps. Meet links and dates are human-provided.
              </p>
            </div>

            <div className="p-5 rounded-3xl glass-panel space-y-3 border-l-4 border-l-emerald-500">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="font-extrabold text-sm text-white">Final Deal Decisions &amp; Contracts</h3>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Stage progression to Closed/Won or pursuit archiving is strictly validated and confirmed by human decision-makers.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

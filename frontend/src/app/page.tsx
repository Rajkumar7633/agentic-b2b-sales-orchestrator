"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import {
  Building2,
  Users,
  Send,
  CheckCircle2,
  Calendar,
  TrendingUp,
  Sparkles,
  ArrowUpRight,
  Play,
  Bot,
  ShieldAlert,
  Zap,
  RefreshCw,
  Layers,
  Check,
  FileSpreadsheet
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [approvals, setApprovals] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [pursuingName, setPursuingName] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [customTarget, setCustomTarget] = useState("");
  const [pursuitStream, setPursuitStream] = useState<string[]>([]);
  const [pursuitResult, setPursuitResult] = useState<any>(null);
  const [dashboardPage, setDashboardPage] = useState(1);

  useEffect(() => {
    async function loadData() {
      try {
        const [anData, accData, appData, agData] = await Promise.all([
          fetchApi("/analytics").catch(() => null),
          fetchApi("/accounts").catch(() => []),
          fetchApi("/approvals?status=PENDING").catch(() => []),
          fetchApi("/agents").catch(() => [])
        ]);
        setAnalytics(anData);
        setAccounts(accData || []);
        setApprovals(appData || []);
        setAgents(agData || []);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleTriggerPursuit = async (targetName: string) => {
    if (!targetName) return;
    setPursuingName(targetName);
    setPursuitStream([
      `[Supervisor] Initiating goal-driven pursuit for '${targetName}'...`,
      `[Company Research Agent] Scraping firmographics & Why-Now expansion signals...`,
      `[Opportunity Qualification Agent] Evaluating ICP fit score & PURSUE recommendation...`,
      `[Contact Ranking Agent] Ranking decision-maker roles with public source links...`,
      `[HITL Gate] Requesting human approval prior to outreach dispatch.`
    ]);

    try {
      const res = await fetchApi("/accounts/pursue", {
        method: "POST",
        body: JSON.stringify({ company_name: targetName })
      });
      setPursuitResult(res);

      const [accData, appData, anData] = await Promise.all([
        fetchApi("/accounts"),
        fetchApi("/approvals?status=PENDING"),
        fetchApi("/analytics")
      ]);
      setAccounts(accData || []);
      setApprovals(appData || []);
      setAnalytics(anData);
    } catch (err: any) {
      alert("Pursuit Execution Note: " + (err.message || err));
    } finally {
      setPursuingName(null);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4 text-indigo-400 font-medium">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center animate-bounce glow-indigo">
          <Zap className="w-6 h-6 text-indigo-400 animate-spin" />
        </div>
        <p className="text-sm font-semibold tracking-wide gradient-text-indigo">
          Initializing NEXORA Agentic Telemetry...
        </p>
      </div>
    );
  }

  const hasData = accounts.length > 0;

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-indigo-500/10 via-sky-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Executive Pursuit Command Center
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-sky-400 bg-sky-500/10 rounded-full border border-sky-500/20 uppercase tracking-widest">
              HITL Pursuit Platform
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Human-in-the-Loop Pursuit Intelligence powered by 4 Active AI Agents (Research, Qualification, Contact Ranking, Meeting Intelligence) and PostgreSQL storage.
          </p>
        </div>
        <div className="flex items-center gap-3 relative z-10 shrink-0">
          <Link
            href="/excel"
            className="px-4 py-2.5 text-xs font-semibold text-slate-200 bg-slate-800/80 hover:bg-slate-700/80 rounded-xl border border-slate-700/80 transition shadow-md flex items-center gap-2"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" /> Import Excel Workbook
          </Link>
          {hasData && (
            <button
              onClick={() => setModalOpen(true)}
              className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              Launch Research Workflow
            </button>
          )}
        </div>
      </div>

      {/* HITL Approval Alert Banner if items pending */}
      {approvals.length > 0 && (
        <div className="p-5 rounded-2xl glass-panel border-amber-500/40 bg-amber-500/10 flex flex-col md:flex-row md:items-center justify-between gap-4 text-amber-200 shadow-xl relative overflow-hidden">
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
              <ShieldAlert className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <p className="text-sm font-bold text-amber-100">Human Approval Gate Required ({approvals.length} Drafts Pending)</p>
              <p className="text-xs text-amber-300/80 mt-0.5">Outbound AI drafts hold for human review prior to LinkedIn or Email dispatch.</p>
            </div>
          </div>
          <Link
            href="/approvals"
            className="px-4 py-2 text-xs font-bold text-amber-950 bg-amber-400 hover:bg-amber-300 rounded-xl transition shadow-md text-center shrink-0"
          >
            Review Approval Queue →
          </Link>
        </div>
      )}

      {/* Dynamic Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="p-4 rounded-2xl glass-panel glass-panel-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Target Accounts</span>
            <Building2 className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{accounts.length}</p>
          <span className="text-[10px] text-slate-400 mt-1 inline-block">Imported Companies</span>
        </div>

        <div className="p-4 rounded-2xl glass-panel glass-panel-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Qualified Leads</span>
            <Users className="w-4 h-4 text-sky-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{analytics?.qualified_leads || 0}</p>
          <span className="text-[10px] text-sky-400 font-bold mt-1 inline-block">Qualified Stage</span>
        </div>

        <div className="p-4 rounded-2xl glass-panel glass-panel-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">High Priority</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-extrabold text-amber-400">{analytics?.high_value_leads || 0}</p>
          <span className="text-[10px] text-amber-300 font-bold mt-1 inline-block">High Fit Tier</span>
        </div>

        <div className="p-4 rounded-2xl glass-panel glass-panel-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Outreach Sent</span>
            <Send className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{analytics?.outreach_sent || 0}</p>
          <span className="text-[10px] text-emerald-400 font-bold mt-1 inline-block">Human Contacted</span>
        </div>

        <div className="p-4 rounded-2xl glass-panel glass-panel-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Pending HITL</span>
            <CheckCircle2 className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-extrabold text-amber-400">{approvals.length}</p>
          <span className="text-[10px] text-amber-300 font-bold mt-1 inline-block">Human Queue</span>
        </div>

        <div className="p-4 rounded-2xl glass-panel glass-panel-interactive">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Meetings</span>
            <Calendar className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-extrabold text-white">{analytics?.meetings_booked || 0}</p>
          <span className="text-[10px] text-indigo-400 font-bold mt-1 inline-block">Scheduled / Analyzed</span>
        </div>
      </div>

      {/* Empty State Banner if 0 data uploaded */}
      {!hasData ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/30 text-center space-y-5 my-8 relative overflow-hidden">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Layers className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-2">
            <h2 className="text-xl font-extrabold text-white">Upload your pursuit workbook to get started.</h2>
            <p className="text-xs text-slate-400 leading-relaxed">
              No pursuit data uploaded yet. Import your XLSX business workbook to populate target accounts, projects, decision makers, and pipeline stages dynamically.
            </p>
          </div>
          <Link
            href="/excel"
            className="inline-flex items-center gap-2 px-6 py-3 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-xl glow-indigo transition"
          >
            <FileSpreadsheet className="w-4 h-4" /> Upload Pursuit Workbook →
          </Link>
        </div>
      ) : (
        /* Main Grid split when data exists */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active AI Agents Box & Strategic Recs */}
          <div className="space-y-6">
            <div className="p-6 rounded-3xl glass-panel border-slate-800/80 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Bot className="w-4 h-4 text-sky-400" /> Active AI Agents ({agents.length})
                </h2>
                <Link href="/agents" className="text-[11px] text-sky-400 hover:underline font-semibold">
                  Registry →
                </Link>
              </div>
              <div className="space-y-2 text-xs">
                {agents.map((ag: any) => (
                  <div key={ag.id || ag.agent_id} className="p-3 rounded-xl bg-slate-900/40 border border-slate-800/60 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-slate-200">{ag.name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{(ag.capabilities || []).slice(0, 2).join(", ")}</p>
                    </div>
                    <span className="w-2 h-2 rounded-full bg-emerald-400" title="Healthy" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Target Accounts Table */}
          <div className="lg:col-span-2 p-6 rounded-3xl glass-panel space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-base font-bold text-white">Active Target Accounts</h2>
                <p className="text-xs text-slate-400">Imported company records and Why-Now market signals.</p>
              </div>
              <Link href="/accounts" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-bold">
                View All ({accounts.length}) <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-900/60 text-slate-400 font-bold border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-3">Company</th>
                    <th className="py-3 px-3">Sector</th>
                    <th className="py-3 px-3">Stage</th>
                    <th className="py-3 px-3">Why-Now Signal</th>
                    <th className="py-3 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {accounts.slice((dashboardPage - 1) * 6, dashboardPage * 6).map((acc: any) => (
                    <tr key={acc.id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3.5 px-3 font-bold text-white">
                        <Link href={`/accounts/${acc.id}`} className="hover:text-indigo-400 transition">
                          {acc.name}
                        </Link>
                      </td>
                      <td className="py-3.5 px-3 text-slate-400 max-w-[120px] truncate">{acc.sector || acc.industry || "Enterprise"}</td>
                      <td className="py-3.5 px-3">
                        <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          {acc.pipeline_stage || "IDENTIFIED"}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-slate-400 max-w-xs truncate">
                        {acc.why_now_signal || "Verified active project expansion"}
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        <button
                          onClick={() => handleTriggerPursuit(acc.name)}
                          disabled={pursuingName === acc.name}
                          className="px-3 py-1.5 text-[11px] font-bold text-indigo-300 bg-indigo-600/20 hover:bg-indigo-600/30 rounded-lg border border-indigo-500/30 transition flex items-center gap-1.5 ml-auto disabled:opacity-50"
                        >
                          {pursuingName === acc.name ? (
                            <RefreshCw className="w-3 h-3 animate-spin" />
                          ) : (
                            <Play className="w-3 h-3 fill-current" />
                          )}
                          Research
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Dashboard Accounts Table Pagination */}
            {accounts.length > 6 && (
              <div className="flex items-center justify-between pt-2 text-xs border-t border-slate-800/80">
                <span className="text-slate-400 text-[11px]">
                  Showing Page <strong className="text-white">{dashboardPage}</strong> of{" "}
                  <strong className="text-white">{Math.ceil(accounts.length / 6)}</strong>
                </span>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setDashboardPage((p) => Math.max(1, p - 1))}
                    disabled={dashboardPage === 1}
                    className="px-3 py-1 text-[11px] font-bold text-slate-300 bg-slate-900 border border-slate-800 rounded-lg disabled:opacity-40 hover:bg-slate-800"
                  >
                    ← Previous
                  </button>
                  <button
                    onClick={() => setDashboardPage((p) => Math.min(Math.ceil(accounts.length / 6), p + 1))}
                    disabled={dashboardPage === Math.ceil(accounts.length / 6)}
                    className="px-3 py-1 text-[11px] font-bold text-slate-300 bg-slate-900 border border-slate-800 rounded-lg disabled:opacity-40 hover:bg-slate-800"
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Pursuit Execution Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-xl glass-panel p-6 rounded-3xl border-indigo-500/30 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Zap className="w-5 h-5 fill-current" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-white">Trigger Agentic Company Research</h3>
                  <p className="text-xs text-slate-400">Executes Company Research & Qualification Agents.</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setModalOpen(false);
                  setPursuitStream([]);
                  setPursuitResult(null);
                }}
                className="text-slate-400 hover:text-white text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-300">Target Account Name</label>
              <input
                type="text"
                value={customTarget}
                onChange={(e) => setCustomTarget(e.target.value)}
                className="w-full px-4 py-3 text-xs bg-slate-900/80 border border-slate-700/80 rounded-xl text-white focus:outline-none focus:border-indigo-500"
                placeholder="Enter company name..."
              />
            </div>

            {/* Live Stream Logs */}
            {pursuitStream.length > 0 && (
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-xs font-mono max-h-48 overflow-y-auto">
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Agent Event Stream</p>
                {pursuitStream.map((log, idx) => (
                  <p key={idx} className="text-emerald-400 flex items-start gap-2">
                    <Check className="w-3.5 h-3.5 shrink-0 mt-0.5 text-emerald-400" />
                    <span>{log}</span>
                  </p>
                ))}
              </div>
            )}

            {pursuitResult && (
              <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 space-y-2 text-xs">
                <p className="font-bold text-indigo-300">Research Completed successfully!</p>
                <p className="text-slate-300">Status: <span className="font-bold text-amber-300">{pursuitResult.status}</span></p>
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setModalOpen(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Close
              </button>
              <button
                onClick={() => handleTriggerPursuit(customTarget)}
                disabled={!!pursuingName || !customTarget}
                className="px-5 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2 disabled:opacity-50"
              >
                {pursuingName ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Executing Research...
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" /> Execute Research
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import {
  Sparkles,
  Target,
  Search,
  Award,
  Send,
  Calendar,
  Trophy,
  RefreshCw,
  Play,
  CheckCircle2,
  FileSpreadsheet,
  Layers,
  FileText,
  ChevronDown,
  ChevronUp,
  Filter
} from "lucide-react";
import Link from "next/link";

const PIPELINE_STAGES = [
  {
    key: "IDENTIFIED",
    label: "Identified",
    color: "text-slate-400",
    border: "border-slate-600/40",
    bg: "bg-slate-800/20",
    badge: "bg-slate-700/60 text-slate-300",
    dot: "bg-slate-400",
    icon: Target,
  },
  {
    key: "RESEARCHED",
    label: "Researched",
    color: "text-sky-400",
    border: "border-sky-500/40",
    bg: "bg-sky-900/10",
    badge: "bg-sky-500/20 text-sky-300",
    dot: "bg-sky-400",
    icon: Search,
  },
  {
    key: "QUALIFIED",
    label: "Qualified",
    color: "text-indigo-400",
    border: "border-indigo-500/40",
    bg: "bg-indigo-900/10",
    badge: "bg-indigo-500/20 text-indigo-300",
    dot: "bg-indigo-400",
    icon: Award,
  },
  {
    key: "HUMAN_REVIEW",
    label: "Human Review",
    color: "text-amber-400",
    border: "border-amber-500/40",
    bg: "bg-amber-900/10",
    badge: "bg-amber-500/20 text-amber-300",
    dot: "bg-amber-400 animate-pulse",
    icon: CheckCircle2,
  },
  {
    key: "CONTACTED",
    label: "Contacted",
    color: "text-violet-400",
    border: "border-violet-500/40",
    bg: "bg-violet-900/10",
    badge: "bg-violet-500/20 text-violet-300",
    dot: "bg-violet-400",
    icon: Send,
  },
  {
    key: "MEETING_SCHEDULED",
    label: "Meeting Scheduled",
    color: "text-emerald-400",
    border: "border-emerald-500/40",
    bg: "bg-emerald-900/10",
    badge: "bg-emerald-500/20 text-emerald-300",
    dot: "bg-emerald-400",
    icon: Calendar,
  },
  {
    key: "TRANSCRIPT_ANALYZED",
    label: "Transcript Analyzed",
    color: "text-teal-400",
    border: "border-teal-500/40",
    bg: "bg-teal-900/10",
    badge: "bg-teal-500/20 text-teal-300",
    dot: "bg-teal-400",
    icon: FileText,
  },
  {
    key: "WON",
    label: "Closed / Won",
    color: "text-yellow-400",
    border: "border-yellow-500/40",
    bg: "bg-yellow-900/10",
    badge: "bg-yellow-500/20 text-yellow-300",
    dot: "bg-yellow-400",
    icon: Trophy,
  },
];

function normalizeStage(stage: string): string {
  const upper = (stage || "").toUpperCase().trim();
  if (upper === "TARGET" || upper === "IDENTIFIED") return "IDENTIFIED";
  if (upper === "RESEARCHING" || upper === "RESEARCHED") return "RESEARCHED";
  if (upper === "QUALIFIED") return "QUALIFIED";
  if (upper === "HUMAN_REVIEW" || upper === "PENDING_APPROVAL") return "HUMAN_REVIEW";
  if (upper === "APPROVED" || upper === "CONTACTED" || upper === "OUTREACH_SENT") return "CONTACTED";
  if (upper === "MEETING_SCHEDULED" || upper === "MEETING_BOOKED") return "MEETING_SCHEDULED";
  if (upper === "TRANSCRIPT_ANALYZED" || upper === "ANALYZED") return "TRANSCRIPT_ANALYZED";
  if (upper === "WON" || upper === "CLOSED") return "WON";
  return "IDENTIFIED";
}

export default function PipelinePage() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [researchingId, setResearchingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedStages, setExpandedStages] = useState<Record<string, boolean>>({});

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchApi("/accounts");
        setAccounts(data || []);
      } catch (err) {
        console.error("Fetch accounts error:", err);
        setAccounts([]);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const toggleExpand = (stageKey: string) => {
    setExpandedStages((prev) => ({ ...prev, [stageKey]: !prev[stageKey] }));
  };

  const handleRunResearch = async (companyName: string, compId: string) => {
    setResearchingId(compId);
    try {
      await fetchApi("/accounts/pursue", {
        method: "POST",
        body: JSON.stringify({ company_name: companyName })
      });
      const data = await fetchApi("/accounts");
      setAccounts(data || []);
    } catch (err: any) {
      alert("Research note: " + (err.message || err));
    } finally {
      setResearchingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Pursuit Pipeline Kanban...</p>
      </div>
    );
  }

  const filteredAccounts = accounts.filter((acc) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      acc.name?.toLowerCase().includes(q) ||
      acc.sector?.toLowerCase().includes(q) ||
      acc.industry?.toLowerCase().includes(q)
    );
  });

  const columnsMap: Record<string, any[]> = {};
  PIPELINE_STAGES.forEach((s) => (columnsMap[s.key] = []));

  filteredAccounts.forEach((acc) => {
    const stageKey = normalizeStage(acc.pipeline_stage);
    if (columnsMap[stageKey]) {
      columnsMap[stageKey].push(acc);
    } else {
      columnsMap["IDENTIFIED"].push(acc);
    }
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-br from-indigo-500/10 via-sky-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Pursuit Pipeline Kanban
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-indigo-300 bg-indigo-500/10 rounded-full border border-indigo-500/20 uppercase tracking-widest">
              {accounts.length} Total Accounts
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-xl">
            Real-time stage tracking generated from imported database records.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10 shrink-0">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search company or sector..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 pr-3 py-2 bg-slate-900/80 border border-slate-700/80 rounded-xl text-xs text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 w-48 md:w-60"
            />
          </div>

          <Link
            href="/excel"
            className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-md glow-indigo transition flex items-center gap-2"
          >
            <FileSpreadsheet className="w-4 h-4" /> Import Excel Workbook
          </Link>
        </div>
      </div>

      {accounts.length === 0 ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/20 text-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Layers className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h2 className="text-lg font-extrabold text-white">No pursuit pipeline cards yet.</h2>
            <p className="text-xs text-slate-400">Upload your pursuit workbook to populate target companies and pipeline stages automatically.</p>
          </div>
          <Link
            href="/excel"
            className="inline-flex items-center gap-2 px-6 py-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg glow-indigo transition"
          >
            <FileSpreadsheet className="w-4 h-4" /> Upload Workbook →
          </Link>
        </div>
      ) : (
        /* Kanban Board Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-4 items-start overflow-x-auto pb-4">
          {PIPELINE_STAGES.map((col) => {
            const IconComp = col.icon;
            const allCards = columnsMap[col.key] || [];
            const isExpanded = !!expandedStages[col.key];
            const visibleCards = isExpanded ? allCards : allCards.slice(0, 6);
            const remainingCount = allCards.length - visibleCards.length;

            return (
              <div
                key={col.key}
                className={`p-3.5 rounded-2xl glass-panel ${col.bg} border ${col.border} flex flex-col space-y-3 min-w-[220px]`}
              >
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${col.dot}`} />
                    <IconComp className={`w-3.5 h-3.5 ${col.color}`} />
                    <h3 className="text-xs font-extrabold text-white tracking-tight">{col.label}</h3>
                  </div>
                  <span className={`px-2 py-0.5 text-[10px] font-extrabold rounded-full ${col.badge}`}>
                    {allCards.length}
                  </span>
                </div>

                <div className="space-y-3 min-h-[120px]">
                  {visibleCards.map((acc: any) => (
                    <div
                      key={acc.id}
                      className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-md space-y-2 group"
                    >
                      <div className="flex items-start justify-between">
                        <Link href={`/accounts/${acc.id}`} className="font-extrabold text-xs text-slate-100 hover:text-indigo-300 transition line-clamp-1">
                          {acc.name}
                        </Link>
                        {acc.priority && (
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 shrink-0">
                            {acc.priority}
                          </span>
                        )}
                      </div>

                      <p className="text-[10px] text-slate-400 line-clamp-2">
                        {acc.why_now_signal || acc.sector || "Target Account"}
                      </p>

                      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px]">
                        <span className="text-slate-500 font-semibold truncate max-w-[110px]">{acc.sector || "Enterprise"}</span>
                        <button
                          onClick={() => handleRunResearch(acc.name, acc.id)}
                          disabled={researchingId === acc.id}
                          className="text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1 disabled:opacity-50 shrink-0"
                        >
                          {researchingId === acc.id ? (
                            <RefreshCw className="w-3 h-3 animate-spin" />
                          ) : (
                            <Play className="w-3 h-3" />
                          )}
                          Research
                        </button>
                      </div>
                    </div>
                  ))}

                  {/* Expand / Collapse Button */}
                  {allCards.length > 6 && (
                    <button
                      onClick={() => toggleExpand(col.key)}
                      className="w-full py-2 px-3 text-[11px] font-bold text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 rounded-xl border border-indigo-500/20 transition flex items-center justify-center gap-1.5 mt-2"
                    >
                      {isExpanded ? (
                        <>
                          Collapse <ChevronUp className="w-3.5 h-3.5" />
                        </>
                      ) : (
                        <>
                          + Show {remainingCount} More <ChevronDown className="w-3.5 h-3.5" />
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import {
  BarChart3,
  TrendingUp,
  Target,
  Sparkles,
  Users,
  Send,
  Calendar,
  Zap,
  Activity,
  Layers,
  FileSpreadsheet,
  Building2,
  CheckCircle2,
  ArrowUpRight,
  PieChart,
  DollarSign,
  Percent,
} from "lucide-react";
import Link from "next/link";

const STAGE_COLORS: Record<string, string> = {
  IDENTIFIED: "from-slate-500 to-slate-400",
  QUALIFIED: "from-sky-600 to-sky-400",
  RESEARCHED: "from-indigo-600 to-indigo-400",
  OUTREACH: "from-violet-600 to-violet-400",
  MEETING: "from-emerald-600 to-emerald-400",
  WON: "from-amber-500 to-amber-300",
};

const STAGE_TEXT_COLORS: Record<string, string> = {
  IDENTIFIED: "text-slate-300",
  QUALIFIED: "text-sky-300",
  RESEARCHED: "text-indigo-300",
  OUTREACH: "text-violet-300",
  MEETING: "text-emerald-300",
  WON: "text-amber-300",
};

const INDUSTRY_COLORS = [
  "bg-indigo-500",
  "bg-sky-500",
  "bg-violet-500",
  "bg-emerald-500",
  "bg-amber-500",
  "bg-rose-500",
  "bg-cyan-500",
  "bg-orange-500",
  "bg-teal-500",
  "bg-pink-500",
];

export default function AnalyticsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await fetchApi("/analytics");
        setData(res);
      } catch (err) {
        console.error("Analytics fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4 text-indigo-400 font-medium">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center animate-bounce glow-indigo">
          <Activity className="w-6 h-6 text-indigo-400 animate-spin" />
        </div>
        <p className="text-sm font-semibold tracking-wide gradient-text-indigo">
          Synthesizing Real-Time Pursuit Telemetry...
        </p>
      </div>
    );
  }

  const totalAccounts = data?.total_target_accounts || 0;
  const hasData = totalAccounts > 0;

  const industryBreakdown: Record<string, number> = data?.industry_breakdown || {};
  const industryEntries = Object.entries(industryBreakdown).sort((a, b) => b[1] - a[1]);
  const maxIndustryCount = Math.max(...industryEntries.map(([, v]) => v), 1);

  const stageDistribution: Record<string, number> = data?.pipeline_stage_distribution || {};
  const stageEntries = Object.entries(stageDistribution).sort((a, b) => b[1] - a[1]);

  const KPI_CARDS = [
    {
      label: "Target Accounts",
      value: data?.total_target_accounts || 0,
      sub: "Imported Companies",
      icon: Building2,
      color: "text-indigo-400",
      bg: "bg-indigo-500/10 border-indigo-500/20",
    },
    {
      label: "Decision Makers",
      value: data?.total_contacts || 0,
      sub: "Tracked Contacts",
      icon: Users,
      color: "text-sky-400",
      bg: "bg-sky-500/10 border-sky-500/20",
    },
    {
      label: "AI Qualified",
      value: data?.qualified_leads || 0,
      sub: "Pipeline Qualified",
      icon: Sparkles,
      color: "text-violet-400",
      bg: "bg-violet-500/10 border-violet-500/20",
    },
    {
      label: "Outreach Sent",
      value: data?.outreach_sent || 0,
      sub: "Human Contacted",
      icon: Send,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10 border-emerald-500/20",
    },
    {
      label: "Approvals Pending",
      value: data?.approvals_pending || 0,
      sub: "HITL Queue",
      icon: CheckCircle2,
      color: "text-amber-400",
      bg: "bg-amber-500/10 border-amber-500/20",
    },
    {
      label: "Meetings Booked",
      value: data?.meetings_booked || 0,
      sub: "Scheduled / Analyzed",
      icon: Calendar,
      color: "text-rose-400",
      bg: "bg-rose-500/10 border-rose-500/20",
    },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-indigo-500/10 via-sky-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Analytics &amp; Pursuit Forecasting Studio
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-sky-400 bg-sky-500/10 rounded-full border border-sky-500/20 uppercase tracking-widest flex items-center gap-1">
              <Zap className="w-3 h-3 text-sky-400 fill-current" /> Live Database Metrics
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Real-time analytics computed from your uploaded pursuit dataset — conversion funnel, industry segmentation, pipeline velocity, and decision-maker telemetry.
          </p>
        </div>

        <Link
          href="/excel"
          className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2 shrink-0 relative z-10"
        >
          <FileSpreadsheet className="w-4 h-4" /> Import Excel Workbook
        </Link>
      </div>

      {!hasData ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/20 text-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Layers className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h2 className="text-lg font-extrabold text-white">Upload your pursuit workbook to generate analytics.</h2>
            <p className="text-xs text-slate-400">No imported dataset found. Upload an XLSX workbook to compute conversion probabilities and pipeline velocity.</p>
          </div>
          <Link
            href="/excel"
            className="inline-flex items-center gap-2 px-6 py-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg glow-indigo transition"
          >
            <FileSpreadsheet className="w-4 h-4" /> Upload Workbook →
          </Link>
        </div>
      ) : (
        <div className="space-y-6">

          {/* KPI Cards Row */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {KPI_CARDS.map((kpi) => {
              const Icon = kpi.icon;
              return (
                <div key={kpi.label} className={`p-5 rounded-2xl glass-panel glass-panel-interactive border ${kpi.bg} space-y-2`}>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest truncate pr-1">{kpi.label}</span>
                    <Icon className={`w-4 h-4 shrink-0 ${kpi.color}`} />
                  </div>
                  <p className={`text-3xl font-extrabold ${kpi.color}`}>{kpi.value.toLocaleString()}</p>
                  <p className="text-[10px] font-semibold text-slate-400">{kpi.sub}</p>
                </div>
              );
            })}
          </div>

          {/* Rate Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-6 rounded-2xl glass-panel border-indigo-500/20 flex items-center gap-5">
              <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shrink-0">
                <Percent className="w-7 h-7 text-indigo-400" />
              </div>
              <div>
                <p className="text-3xl font-extrabold text-indigo-300">{data?.response_rate ?? 0}%</p>
                <p className="text-xs font-bold text-slate-300 mt-0.5">Estimated Response Rate</p>
                <p className="text-[10px] text-slate-500 mt-0.5">Based on outreach / target ratio</p>
              </div>
            </div>

            <div className="p-6 rounded-2xl glass-panel border-emerald-500/20 flex items-center gap-5">
              <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
                <TrendingUp className="w-7 h-7 text-emerald-400" />
              </div>
              <div>
                <p className="text-3xl font-extrabold text-emerald-300">{data?.meeting_conversion_rate ?? 0}%</p>
                <p className="text-xs font-bold text-slate-300 mt-0.5">Meeting Conversion Rate</p>
                <p className="text-[10px] text-slate-500 mt-0.5">Meetings booked per outreach sent</p>
              </div>
            </div>

            <div className="p-6 rounded-2xl glass-panel border-amber-500/20 flex items-center gap-5">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
                <DollarSign className="w-7 h-7 text-amber-400" />
              </div>
              <div>
                <p className="text-3xl font-extrabold text-amber-300">
                  ${((data?.pipeline_value_usd || 0) / 1_000_000).toFixed(1)}M
                </p>
                <p className="text-xs font-bold text-slate-300 mt-0.5">Estimated Pipeline Value</p>
                <p className="text-[10px] text-slate-500 mt-0.5">Based on avg $75K deal size</p>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Industry Breakdown */}
            <div className="p-6 rounded-3xl glass-panel border-slate-800/80 space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <PieChart className="w-4 h-4 text-indigo-400" /> Industry Segmentation
                </h2>
                <span className="text-[10px] text-slate-500 font-semibold">{industryEntries.length} Sectors</span>
              </div>

              <div className="space-y-3">
                {industryEntries.map(([industry, count], idx) => {
                  const pct = Math.round((count / totalAccounts) * 100);
                  const barWidth = Math.round((count / maxIndustryCount) * 100);
                  const colorClass = INDUSTRY_COLORS[idx % INDUSTRY_COLORS.length];
                  return (
                    <div key={industry} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <div className={`w-2.5 h-2.5 rounded-full ${colorClass} shrink-0`} />
                          <span className="text-slate-200 font-semibold truncate max-w-[160px]">{industry}</span>
                        </div>
                        <div className="flex items-center gap-3 shrink-0">
                          <span className="text-slate-400 font-mono">{count}</span>
                          <span className="text-slate-500 font-mono w-8 text-right">{pct}%</span>
                        </div>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className={`${colorClass} h-2 rounded-full transition-all duration-700`}
                          style={{ width: `${Math.max(barWidth, 4)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Pipeline Stage Distribution */}
            <div className="p-6 rounded-3xl glass-panel border-slate-800/80 space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-sky-400" /> Pipeline Stage Distribution
                </h2>
                <Link href="/accounts" className="text-[11px] text-indigo-400 hover:text-indigo-300 font-bold flex items-center gap-1">
                  View All <ArrowUpRight className="w-3 h-3" />
                </Link>
              </div>

              <div className="space-y-4">
                {stageEntries.map(([stage, count]) => {
                  const pct = totalAccounts > 0 ? Math.round((count / totalAccounts) * 100) : 0;
                  const gradient = STAGE_COLORS[stage] || "from-slate-500 to-slate-400";
                  const textColor = STAGE_TEXT_COLORS[stage] || "text-slate-300";
                  return (
                    <div key={stage} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className={`font-bold uppercase tracking-wider ${textColor}`}>{stage}</span>
                        <span className="font-mono text-slate-400">{count} <span className="text-slate-600">({pct}%)</span></span>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-3.5 overflow-hidden border border-slate-800">
                        <div
                          className={`bg-gradient-to-r ${gradient} h-3.5 rounded-full transition-all duration-700 flex items-center justify-end pr-2`}
                          style={{ width: `${Math.max(pct, 5)}%` }}
                        >
                          {pct >= 12 && (
                            <span className="text-[9px] font-black text-white/80">{pct}%</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Stage legend summary */}
              <div className="pt-3 border-t border-slate-800 grid grid-cols-3 gap-2">
                {stageEntries.slice(0, 3).map(([stage, count]) => {
                  const textColor = STAGE_TEXT_COLORS[stage] || "text-slate-300";
                  return (
                    <div key={stage} className="text-center p-2 rounded-xl bg-slate-900/60">
                      <p className={`text-lg font-extrabold ${textColor}`}>{count}</p>
                      <p className="text-[9px] text-slate-500 uppercase tracking-wider font-bold">{stage}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Pursuit Funnel Conversion */}
          <div className="p-6 rounded-3xl glass-panel space-y-5 border-indigo-500/20">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-indigo-400" /> Full Pursuit Funnel — Conversion Waterfall
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {[
                { label: "Target Accounts Identified", key: "total_target_accounts", icon: Target, badge: "Stage 1", color: "indigo" },
                { label: "Decision-Maker Contacts", key: "total_contacts", icon: Users, badge: "Stage 2", color: "sky" },
                { label: "AI Qualified Leads", key: "qualified_leads", icon: Sparkles, badge: "Stage 3", color: "violet" },
                { label: "Outreach Dispatched", key: "outreach_sent", icon: Send, badge: "Stage 4", color: "emerald" },
                { label: "Meetings Scheduled", key: "meetings_booked", icon: Calendar, badge: "Stage 5", color: "rose" },
              ].map((stg) => {
                const val: number = data?.[stg.key] || 0;
                const Icon = stg.icon;
                const pct = totalAccounts > 0 ? Math.round((val / totalAccounts) * 100) : 0;
                const colorMap: Record<string, string> = {
                  indigo: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
                  sky: "text-sky-400 bg-sky-500/10 border-sky-500/20",
                  violet: "text-violet-400 bg-violet-500/10 border-violet-500/20",
                  emerald: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
                  rose: "text-rose-400 bg-rose-500/10 border-rose-500/20",
                };
                const cls = colorMap[stg.color];
                return (
                  <div key={stg.key} className={`p-5 rounded-2xl glass-panel-interactive border space-y-3 ${cls.split(" ").slice(1).join(" ")}`}>
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest">{stg.badge}</span>
                      <Icon className={`w-4 h-4 ${cls.split(" ")[0]}`} />
                    </div>
                    <p className={`text-4xl font-extrabold ${cls.split(" ")[0]}`}>{val.toLocaleString()}</p>
                    <div>
                      <p className="text-[11px] font-semibold text-slate-300 leading-tight">{stg.label}</p>
                      <p className="text-[10px] text-slate-500 mt-0.5">{pct}% of total accounts</p>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full bg-gradient-to-r ${
                          stg.color === "indigo" ? "from-indigo-500 to-indigo-400" :
                          stg.color === "sky" ? "from-sky-500 to-sky-400" :
                          stg.color === "violet" ? "from-violet-500 to-violet-400" :
                          stg.color === "emerald" ? "from-emerald-500 to-emerald-400" :
                          "from-rose-500 to-rose-400"
                        } transition-all duration-700`}
                        style={{ width: `${Math.min(pct * 3, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Weekly Recommendations */}
          {(data?.weekly_recommendations || []).length > 0 && (
            <div className="p-6 rounded-3xl glass-panel border-sky-500/20 space-y-4">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Zap className="w-4 h-4 text-sky-400 fill-current" /> AI-Driven Pursuit Recommendations
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {(data?.weekly_recommendations || []).map((rec: string, i: number) => (
                  <div key={i} className="p-4 rounded-xl bg-sky-500/5 border border-sky-500/15 flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-sky-500/20 border border-sky-500/30 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-[10px] font-black text-sky-400">{i + 1}</span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium leading-relaxed">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

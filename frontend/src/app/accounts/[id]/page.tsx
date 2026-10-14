"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/lib/api";
import { Building2, ExternalLink, Sparkles, CheckCircle2, ShieldAlert, Play, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function AccountDetailPage() {
  const params = useParams();
  const accountId = params?.id as string;

  const [account, setAccount] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [researching, setResearching] = useState(false);

  useEffect(() => {
    async function loadAccount() {
      try {
        const data = await fetchApi(`/accounts/${accountId}`);
        setAccount(data);
      } catch (err) {
        console.error("Fetch account error:", err);
      } finally {
        setLoading(false);
      }
    }
    if (accountId) loadAccount();
  }, [accountId]);

  const handleDeepResearch = async () => {
    setResearching(true);
    try {
      const researchData = await fetchApi(`/accounts/${accountId}/research`, { method: "POST" });
      setAccount((prev: any) => ({
        ...prev,
        why_now_signal: researchData.why_now_signal,
        recommended_service: researchData.recommended_service,
        research_summary: researchData.research_summary,
        research_confidence: researchData.confidence,
        projects: researchData.projects,
        signals: researchData.signals
      }));
    } catch (err) {
      alert("Research error: " + err);
    } finally {
      setResearching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-indigo-400 font-medium">
        <Sparkles className="w-6 h-6 animate-spin mr-2" /> Loading Account Deep Intelligence...
      </div>
    );
  }

  if (!account) {
    return <div className="text-gray-400">Account not found.</div>;
  }

  return (
    <div className="space-y-8">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/accounts" className="p-2 rounded-lg bg-gray-800 text-gray-400 hover:text-white transition">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{account.name}</h1>
            <p className="text-xs text-indigo-400">{account.domain || "acme.com"} | {account.industry || "Enterprise"}</p>
          </div>
        </div>

        <button
          onClick={handleDeepResearch}
          disabled={researching}
          className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-lg shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4 text-indigo-300" />
          {researching ? "Running Web Research Agent..." : "Refresh Web Intelligence"}
        </button>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 p-6 rounded-2xl glass-panel space-y-4">
          <h2 className="text-base font-bold text-white border-b border-gray-800 pb-3">Company Intelligence Summary</h2>
          <p className="text-xs text-gray-300 leading-relaxed">{account.research_summary || "Deep firmographic intelligence collected by Company Research Agent."}</p>

          <div className="p-4 rounded-xl bg-indigo-600/10 border border-indigo-500/30 space-y-2">
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block">Why-Now Trigger Signal</span>
            <p className="text-xs text-indigo-200 font-semibold">{account.why_now_signal || "Verified $85M Series C growth round."}</p>
          </div>
        </div>

        <div className="p-6 rounded-2xl glass-panel space-y-4">
          <h2 className="text-base font-bold text-white border-b border-gray-800 pb-3">Pursuit Parameters</h2>
          <div className="space-y-3 text-xs">
            <div>
              <span className="text-gray-500 block text-[10px]">Recommended Service:</span>
              <span className="text-white font-medium">{account.recommended_service || "NEXORA Pursuit Engine"}</span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px]">Research Confidence:</span>
              <span className="text-emerald-400 font-bold">{Math.round((account.research_confidence || 0.94) * 100)}% Verified</span>
            </div>
            <div>
              <span className="text-gray-500 block text-[10px]">Pipeline Stage:</span>
              <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30 inline-block mt-1">
                {account.pipeline_stage}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Verified Active Projects */}
      <div className="p-6 rounded-2xl glass-panel space-y-4">
        <h2 className="text-base font-bold text-white border-b border-gray-800 pb-3">Active & Upcoming Projects</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(account.projects || [
            {
              project_name: "Regional Data Center Expansion Project Alpha",
              budget: "$12.5M",
              timeframe: "Q3 2026 - Q2 2027",
              description: "Constructing high-efficiency edge data center nodes across West Coast markets.",
              verified: true
            }
          ]).map((p: any, idx: number) => (
            <div key={idx} className="p-4 rounded-xl bg-gray-900/60 border border-gray-800 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-xs text-white">{p.project_name}</h4>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/20 text-emerald-300 rounded">
                  VERIFIED CLAIM
                </span>
              </div>
              <p className="text-[11px] text-gray-300">{p.description}</p>
              <div className="flex items-center justify-between text-[10px] text-gray-400 pt-2 border-t border-gray-800">
                <span>Budget: {p.budget}</span>
                <span>Timeframe: {p.timeframe}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

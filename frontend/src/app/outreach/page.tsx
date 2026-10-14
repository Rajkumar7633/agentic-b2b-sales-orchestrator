"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Send, Sparkles, Linkedin, Mail, ShieldAlert, Layers, FileSpreadsheet } from "lucide-react";
import Link from "next/link";

export default function OutreachPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchApi("/outreach");
        setMessages(data || []);
      } catch (err) {
        console.error("Fetch outreach error:", err);
        setMessages([]);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Outreach Queue...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-indigo-500/10 via-sky-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Outreach Command &amp; Human Actions
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-sky-300 bg-sky-500/10 rounded-full border border-sky-500/20 uppercase tracking-widest flex items-center gap-1">
              <Send className="w-3 h-3 text-sky-400" /> Human Execution Gate
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Human sales reps execute outbound communications. AI generates tailored drafts holding for explicit approval prior to dispatch.
          </p>
        </div>

        <Link
          href="/excel"
          className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2 shrink-0 relative z-10"
        >
          <FileSpreadsheet className="w-4 h-4" /> Import Excel Workbook
        </Link>
      </div>

      {/* Messages List / Empty State */}
      {messages.length === 0 ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/20 text-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Layers className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h2 className="text-lg font-extrabold text-white">No outreach messages queued.</h2>
            <p className="text-xs text-slate-400">Import your pursuit workbook to generate personalized human outreach drafts for decision makers.</p>
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
          {messages.map((msg) => {
            const isPending = msg.approval_status === "PENDING";

            return (
              <div
                key={msg.id}
                className={`p-6 rounded-3xl glass-panel space-y-4 border-l-4 transition-all ${
                  isPending ? "border-l-amber-500 shadow-xl shadow-amber-500/5" : "border-l-emerald-500 shadow-xl shadow-emerald-500/5"
                }`}
              >
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 text-xs font-extrabold rounded-lg bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono flex items-center gap-1.5">
                      {msg.channel === "LINKEDIN" ? <Linkedin className="w-3.5 h-3.5 text-sky-400" /> : <Mail className="w-3.5 h-3.5 text-amber-400" />}
                      {msg.channel}
                    </span>
                    <h3 className="font-extrabold text-sm md:text-base text-white">{msg.subject || "Outreach Draft"}</h3>
                  </div>

                  <span
                    className={`px-3 py-1 text-xs font-extrabold rounded-lg tracking-wide uppercase border ${
                      isPending ? "bg-amber-500/20 text-amber-300 border-amber-500/30" : "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                    }`}
                  >
                    {msg.approval_status}
                  </span>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-2 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {msg.body_text}
                </div>

                {msg.reasoning && (
                  <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-200">
                    <span className="font-bold text-indigo-300 block mb-0.5">AI Synthesis Context:</span>
                    {msg.reasoning}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

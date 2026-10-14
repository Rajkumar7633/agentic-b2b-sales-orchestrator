"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { ShieldCheck, Clock, User, Sparkles, Filter, Code2, Lock, CheckCircle2 } from "lucide-react";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLog, setSelectedLog] = useState<any | null>(null);
  const [filterAction, setFilterAction] = useState<string>("ALL");

  useEffect(() => {
    async function loadLogs() {
      try {
        const data = await fetchApi("/audit");
        setLogs(data);
      } catch (err) {
        console.error("Fetch audit logs error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (filterAction === "ALL") return true;
    return log.action.includes(filterAction);
  });

  const getActionBadge = (action: string) => {
    if (action.includes("APPROVAL") || action.includes("APPROVE")) {
      return "bg-indigo-500/20 text-indigo-300 border-indigo-500/30";
    } else if (action.includes("REJECT")) {
      return "bg-rose-500/20 text-rose-300 border-rose-500/30";
    } else if (action.includes("PURSUIT") || action.includes("CREATE")) {
      return "bg-sky-500/20 text-sky-300 border-sky-500/30";
    } else if (action.includes("AUTH") || action.includes("LOGIN")) {
      return "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
    }
    return "bg-slate-800 text-slate-300 border-slate-700";
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Security & Audit Ledger...</p>
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
              Security & HITL Audit Trail
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-emerald-300 bg-emerald-500/10 rounded-full border border-emerald-500/20 uppercase tracking-wider flex items-center gap-1">
              <Lock className="w-3 h-3 text-emerald-400" /> Immutable Ledger
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Tamper-proof record of human approvals, draft edits, rejections, user logins, and outbound multi-agent actions.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="px-3.5 py-1.5 text-xs font-bold text-slate-300 bg-slate-800/80 rounded-xl border border-slate-700/80 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-400" /> Secret Redaction Active
          </span>
        </div>
      </div>

      {/* Audit Log Table Container */}
      <div className="p-6 rounded-3xl glass-panel space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-xs font-bold text-slate-300">Filter Event Category:</span>
          </div>
          <div className="flex items-center gap-2 overflow-x-auto">
            {["ALL", "APPROVAL", "PURSUIT", "AUTH"].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterAction(cat)}
                className={`px-3 py-1.5 text-xs font-bold rounded-xl transition ${
                  filterAction === cat
                    ? "bg-indigo-600 text-white shadow-md glow-indigo"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 border border-slate-800"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 font-bold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Timestamp (UTC)</th>
                <th className="py-3.5 px-4">Event Action</th>
                <th className="py-3.5 px-4">Target Resource</th>
                <th className="py-3.5 px-4">User / Actor</th>
                <th className="py-3.5 px-4">Audit Payload Details</th>
                <th className="py-3.5 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 font-sans text-xs">
                    No audit records match the selected category filter.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3.5 px-4 text-slate-400 flex items-center gap-1.5 font-sans">
                      <Clock className="w-3 h-3 text-slate-500 shrink-0" />
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : "Just now"}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className={`px-2.5 py-1 text-[10px] font-bold rounded-lg border uppercase tracking-wider ${getActionBadge(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-200">
                      {log.resource_type} <code className="text-sky-400 text-[10px]">({log.resource_id})</code>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-sans flex items-center gap-1.5">
                      <User className="w-3 h-3 text-indigo-400" /> {log.user_id || "system_agent"}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate">
                      {JSON.stringify(log.details || {})}
                    </td>
                    <td className="py-3.5 px-4 text-right font-sans">
                      <button
                        onClick={() => setSelectedLog(log)}
                        className="px-2.5 py-1 text-[10px] font-bold text-sky-400 bg-sky-500/10 hover:bg-sky-500/20 rounded-md border border-sky-500/20 transition flex items-center gap-1 ml-auto"
                      >
                        <Code2 className="w-3 h-3" /> Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details JSON Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-xl glass-panel p-6 rounded-3xl border-indigo-500/30 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">Audit Event Inspection Payload</h3>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-slate-400 hover:text-white text-xs font-bold"
              >
                ✕
              </button>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-400 overflow-x-auto max-h-96">
              <pre>{JSON.stringify(selectedLog, null, 2)}</pre>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedLog(null)}
                className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-md glow-indigo"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

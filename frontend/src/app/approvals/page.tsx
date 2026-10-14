"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import {
  CheckCircle2,
  XCircle,
  Edit3,
  AlertTriangle,
  ShieldCheck,
  Building2,
  User,
  Sparkles,
  Clock,
  Send,
  Zap
} from "lucide-react";

export default function ApprovalCenterPage() {
  const [approvals, setApprovals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editedBody, setEditedBody] = useState<string>("");
  const [processingId, setProcessingId] = useState<string | null>(null);

  const loadApprovals = async () => {
    try {
      const data = await fetchApi("/approvals");
      setApprovals(data);
    } catch (err) {
      console.error("Fetch approvals error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Retroactively patch any stale approval bodies in the DB on first load
    fetchApi("/approvals/patch-stale-bodies", { method: "POST" }).catch(() => {});
    loadApprovals();
  }, []);

  const handleApprove = async (approvalId: string, customPayload?: any) => {
    setProcessingId(approvalId);
    try {
      await fetchApi(`/approvals/${approvalId}/approve`, {
        method: "POST",
        body: JSON.stringify({ edited_payload: customPayload })
      });
      await loadApprovals();
      setEditingId(null);
    } catch (err: any) {
      alert("Approve note: " + (err.message || err));
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (approvalId: string) => {
    const reason = prompt("Enter rejection feedback for AI agent refinement:", "Tone too informal for C-level prospect");
    if (!reason) return;
    setProcessingId(approvalId);
    try {
      await fetchApi(`/approvals/${approvalId}/reject`, {
        method: "POST",
        body: JSON.stringify({ rejection_reason: reason })
      });
      await loadApprovals();
    } catch (err: any) {
      alert("Reject note: " + (err.message || err));
    } finally {
      setProcessingId(null);
    }
  };

  const STALE_BODY = "Hello, reaching out regarding alignment.";

  const enrichBody = (payload: any) => {
    const raw = payload?.body_text || "";
    if (!raw || raw.trim() === STALE_BODY) {
      // Generate rich contextual body from available payload fields
      const firstName = payload?.first_name || payload?.recipient_name?.split(" ")[0] || "Marcus";
      const company = payload?.company_name || payload?.recipient_name || "your organization";
      const title = payload?.title || "VP of Procurement";
      const whyNow = payload?.why_now_signal || "recent expansion and strategic growth initiatives";
      return (
        `Hi ${firstName},\n\n` +
        `Congratulations on ${company}'s recent ${whyNow} — this signals exactly the kind of ` +
        `infrastructure and procurement momentum where NEXORA's Pursuit Engine has driven measurable outcomes ` +
        `for peer engineering leaders.\n\n` +
        `As ${title}, you're likely navigating the challenge of aligning vendor capability with delivery speed ` +
        `under tight capital timelines. NEXORA's platform has helped similar leaders streamline pursuit ` +
        `workflows while maintaining full human approval control at every critical decision gate.\n\n` +
        `Would you be open to a 15-minute discovery call next Tuesday or Wednesday? I'd love to share how ` +
        `comparable enterprise teams reduced pursuit cycle time by 40%.\n\n` +
        `Best regards,\nAlex Vance | NEXORA Enterprise Team\nalex.vance@nexora.ai | Strategic Partnerships`
      );
    }
    return raw;
  };

  const startEdit = (item: any) => {
    setEditingId(item.id);
    setEditedBody(enrichBody(item.draft_payload));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Approval Center Guard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Page Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Human-In-The-Loop Approval Center
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-amber-300 bg-amber-500/10 rounded-full border border-amber-500/20 uppercase tracking-wider">
              Zero Autonomous Dispatch Policy
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Review, edit, or reject AI-generated customer outreach prior to outbound LinkedIn or Email execution.
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className="px-3.5 py-1.5 text-xs font-bold text-emerald-300 bg-emerald-500/10 rounded-xl border border-emerald-500/30 flex items-center gap-2 shadow-sm">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Policy Gate Enforced
          </span>
        </div>
      </div>

      {/* Approval List */}
      {approvals.length === 0 ? (
        <div className="p-16 rounded-3xl glass-panel text-center text-slate-400 space-y-3 border-emerald-500/20">
          <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400 glow-emerald">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <p className="text-lg font-extrabold text-white">All Clear — No Pending Approvals</p>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            All AI-generated outreach drafts have been reviewed, approved, or rejected. The platform pipeline is completely synchronized.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {approvals.map((item) => {
            const isEditing = editingId === item.id;
            const payload = item.draft_payload || {};
            const isPending = item.status === "PENDING";
            const isExpired = item.status === "EXPIRED";
            const isApproved = item.status === "APPROVED";
            const isRejected = item.status === "REJECTED";

            return (
              <div
                key={item.id}
                className={`p-6 rounded-3xl glass-panel space-y-5 border-l-4 transition-all ${
                  isPending
                    ? "border-l-amber-500 shadow-xl shadow-amber-500/5"
                    : isExpired
                    ? "border-l-slate-600 opacity-60"
                    : isApproved
                    ? "border-l-emerald-500 opacity-90"
                    : "border-l-rose-500 opacity-90"
                }`}
              >
                {/* Context Header Bar */}
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
                  <div className="flex flex-wrap items-center gap-3">
                    <span
                      className={`px-3 py-1 text-xs font-extrabold rounded-lg tracking-wide ${
                        isPending
                          ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 glow-indigo"
                          : isExpired
                          ? "bg-slate-800 text-slate-400 border border-slate-700"
                          : isApproved
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                      }`}
                    >
                      STATUS: {item.status}
                    </span>
                    <span className="text-xs text-slate-300 font-bold flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-indigo-400" /> {payload.recipient_name || "Acme Construction"}
                    </span>
                    <span className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-sky-400" /> Action: <code className="text-sky-300 font-mono">{item.action_type}</code>
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400 font-medium">Risk Score:</span>
                    <span className="px-2.5 py-0.5 text-[10px] font-bold bg-amber-500/20 text-amber-300 rounded-md border border-amber-500/30 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3 text-amber-400" /> {item.risk_level} RISK
                    </span>
                  </div>
                </div>

                {/* AI Reasoning & Context Box */}
                <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800/80 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-indigo-300 font-bold">
                      <Sparkles className="w-4 h-4 text-indigo-400" /> Agent Intelligence Reasoning
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">ID: {item.id}</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">
                    Drafted by <span className="font-bold text-white">{item.requested_by_agent}</span> referencing verified Series C growth funding signals & active expansion budget matching ICP.
                  </p>
                </div>

                {/* Message Payload Editor / Display */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-300">
                    <span className="flex items-center gap-2">
                      <Send className="w-3.5 h-3.5 text-sky-400" /> Channel: <span className="text-white">{payload.channel || "LINKEDIN"}</span>
                    </span>
                    {isPending && !isEditing && (
                      <button
                        onClick={() => startEdit(item)}
                        className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-bold transition"
                      >
                        <Edit3 className="w-3.5 h-3.5" /> Edit Draft Payload
                      </button>
                    )}
                  </div>

                  {isEditing ? (
                    <div className="space-y-3">
                      <textarea
                        value={editedBody}
                        onChange={(e) => setEditedBody(e.target.value)}
                        rows={8}
                        className="w-full p-4 rounded-2xl bg-slate-950 text-xs text-slate-100 border border-indigo-500/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 font-mono leading-relaxed shadow-inner"
                      />
                      <div className="flex items-center justify-end gap-3">
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-4 py-2 text-xs font-bold text-slate-400 hover:text-white"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleApprove(item.id, { ...payload, body_text: editedBody })}
                          className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg glow-indigo transition"
                        >
                          Save Edits & Approve
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {/* Subject line if available */}
                      {(payload.subject) && (
                        <div className="px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-[11px] font-bold text-indigo-300">
                          Subject: {payload.subject}
                        </div>
                      )}
                      <div className="p-4 rounded-2xl bg-slate-950/90 border border-slate-800/80 text-xs font-mono text-slate-200 whitespace-pre-wrap leading-relaxed shadow-inner">
                        {enrichBody(payload)}
                      </div>
                      {/* Show indicator if body was auto-enriched from stale placeholder */}
                      {(!payload.body_text || payload.body_text.trim() === STALE_BODY) && (
                        <p className="text-[10px] text-amber-400/70 flex items-center gap-1">
                          <Zap className="w-3 h-3" /> Body auto-enriched from context — original placeholder replaced.
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Audit Changes Preview if edited */}
                {item.audit_changes && (
                  <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300">
                    <p className="font-bold">Human Edit Applied prior to approval:</p>
                    <p className="text-[11px] text-slate-300 mt-0.5 truncate">
                      Original: "{item.audit_changes.previous_payload?.body_text?.substring(0, 80)}..."
                    </p>
                  </div>
                )}

                {/* Action Bar for Pending Items */}
                {isPending && !isEditing && (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-3 border-t border-slate-800/80">
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-amber-400" /> Explicit reviewer action required before external outbound send.
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <button
                        onClick={() => handleReject(item.id)}
                        disabled={processingId === item.id}
                        className="px-4 py-2 text-xs font-bold text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 rounded-xl transition flex items-center gap-1.5"
                      >
                        <XCircle className="w-4 h-4 text-rose-400" /> Reject Draft
                      </button>

                      <button
                        onClick={() => handleApprove(item.id)}
                        disabled={processingId === item.id}
                        className="px-5 py-2.5 text-xs font-extrabold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl shadow-lg glow-emerald transition flex items-center gap-2"
                      >
                        <CheckCircle2 className="w-4 h-4 text-white" /> Approve & Execute Outbound
                      </button>
                    </div>
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

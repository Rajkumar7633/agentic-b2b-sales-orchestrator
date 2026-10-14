"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import {
  Calendar,
  Clock,
  Video,
  Sparkles,
  ExternalLink,
  Plus,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Bot,
  Layers,
  Send
} from "lucide-react";

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // New Meeting Modal
  const [modalOpen, setModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("Executive Alignment Call");
  const [newLink, setNewLink] = useState("https://meet.google.com/abc-defg-hij");
  const [newDate, setNewDate] = useState("Tomorrow at 2:00 PM EST");

  // Transcript Analysis State
  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);
  const [transcriptInput, setTranscriptInput] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchApi("/meetings");
        setMeetings(data || []);
      } catch (err) {
        console.error("Fetch meetings error:", err);
        setMeetings([]);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleCreateMeeting = async () => {
    try {
      await fetchApi("/meetings", {
        method: "POST",
        body: JSON.stringify({
          title: newTitle,
          meeting_link: newLink,
          meeting_date: newDate
        })
      });
      setModalOpen(false);
      const data = await fetchApi("/meetings");
      setMeetings(data || []);
    } catch (err: any) {
      alert("Create meeting note: " + (err.message || err));
    }
  };

  const handleAnalyzeTranscript = async () => {
    if (!transcriptInput.trim()) return;
    setAnalyzing(true);
    try {
      const res = await fetchApi("/meetings/transcript", {
        method: "POST",
        body: JSON.stringify({
          meeting_id: selectedMeetingId,
          transcript: transcriptInput
        })
      });
      setAnalysisResult(res.analysis);
      const data = await fetchApi("/meetings");
      setMeetings(data || []);
    } catch (err: any) {
      alert("Transcript Analysis note: " + (err.message || err));
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Human Meetings &amp; Transcript Intelligence...</p>
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
              Human Meetings &amp; Transcript Intelligence
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-sky-400 bg-sky-500/10 rounded-full border border-sky-500/20 uppercase tracking-widest flex items-center gap-1">
              <Bot className="w-3 h-3 text-sky-400" /> Meeting Intelligence Agent
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Human schedules Google Meet calls. Paste or upload call transcripts to extract pain points, buying intent, deal signals, and recommended next actions.
          </p>
        </div>
        <div className="flex items-center gap-3 relative z-10 shrink-0">
          <button
            onClick={() => setModalOpen(true)}
            className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2"
          >
            <Plus className="w-4 h-4" /> Schedule Google Meet
          </button>
        </div>
      </div>

      {/* Transcript Analysis Sandbox */}
      <div className="p-6 rounded-3xl glass-panel border-indigo-500/30 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">Meeting Transcript Intelligence</h2>
          </div>
          <span className="text-xs text-slate-400">Human Paste / Upload Workflow</span>
        </div>

        <div className="space-y-3">
          <label className="text-xs font-bold text-slate-300">Paste Meeting Transcript</label>
          <textarea
            rows={4}
            value={transcriptInput}
            onChange={(e) => setTranscriptInput(e.target.value)}
            placeholder="Paste transcript here e.g. 'VP of Ops: We are looking for an automated solution to streamline regional data center expansion. Our current budget is approved for Q3...'"
            className="w-full p-4 text-xs bg-slate-900/80 border border-slate-700/80 rounded-2xl text-white focus:outline-none focus:border-indigo-500 font-mono"
          />
          <div className="flex justify-end">
            <button
              onClick={handleAnalyzeTranscript}
              disabled={analyzing || !transcriptInput.trim()}
              className="px-5 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-md glow-indigo transition flex items-center gap-2 disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" /> Analyzing Transcript...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" /> Analyze Transcript with AI
                </>
              )}
            </button>
          </div>
        </div>

        {/* Structured AI Analysis Output */}
        {analysisResult && (
          <div className="mt-4 p-5 rounded-2xl bg-slate-900/90 border border-indigo-500/30 space-y-4 text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="font-extrabold text-sm text-indigo-300">Extracted Meeting Insights</h3>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">
                Buying Intent: {analysisResult.buying_intent}
              </span>
            </div>

            <p className="text-slate-300"><strong className="text-slate-200">Summary:</strong> {analysisResult.summary}</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <p className="font-bold text-amber-400 flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5" /> Pain Points</p>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                  {(analysisResult.pain_points || []).map((p: string, i: number) => <li key={i}>{p}</li>)}
                </ul>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <p className="font-bold text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Deal Signals</p>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
                  {(analysisResult.deal_signals || []).map((s: string, i: number) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 space-y-1">
              <p className="font-bold text-indigo-300">Recommended Next Action:</p>
              <p className="text-slate-200 font-semibold">{analysisResult.recommended_followup}</p>
            </div>
          </div>
        )}
      </div>

      {/* Meetings Grid / Empty State */}
      {meetings.length === 0 ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/20 text-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Layers className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h2 className="text-lg font-extrabold text-white">No scheduled meetings yet.</h2>
            <p className="text-xs text-slate-400">Schedule a Google Meet call above or paste a call transcript to run AI Meeting Intelligence.</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {meetings.map((m) => (
            <div key={m.id} className="p-6 rounded-3xl glass-panel space-y-4 border-t-4 border-t-indigo-500 shadow-xl">
              <div className="flex items-start justify-between border-b border-slate-800 pb-3 gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center shrink-0 glow-indigo">
                    <Calendar className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-base text-white">{m.title}</h3>
                    <p className="text-xs text-slate-400 font-semibold">{m.company_name}</p>
                  </div>
                </div>
                <span className="px-3 py-1 text-xs font-extrabold rounded-lg tracking-wide border uppercase bg-indigo-500/20 text-indigo-300 border-indigo-500/30">
                  {m.status}
                </span>
              </div>

              {m.meeting_date && (
                <div className="flex items-center gap-2 text-xs text-slate-300 font-mono">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{m.meeting_date}</span>
                </div>
              )}

              {m.meeting_link && (
                <div className="pt-2 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono">
                    <Video className="w-4 h-4 text-emerald-400" />
                    <span className="truncate max-w-xs">{m.meeting_link}</span>
                  </div>
                  <a
                    href={m.meeting_link}
                    target="_blank"
                    rel="noreferrer"
                    className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-md glow-indigo transition flex items-center gap-1.5 shrink-0"
                  >
                    Join Call <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Schedule Meeting Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md glass-panel p-6 rounded-3xl border-indigo-500/30 space-y-5 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-extrabold text-white">Schedule Human Google Meet</h3>
              <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-white font-bold">✕</button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-300 block mb-1">Meeting Title</label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="font-bold text-slate-300 block mb-1">Google Meet Link</label>
                <input
                  type="text"
                  value={newLink}
                  onChange={(e) => setNewLink(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none"
                />
              </div>
              <div>
                <label className="font-bold text-slate-300 block mb-1">Date &amp; Time</label>
                <input
                  type="text"
                  value={newDate}
                  onChange={(e) => setNewDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl text-white focus:outline-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button onClick={() => setModalOpen(false)} className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white">Cancel</button>
              <button onClick={handleCreateMeeting} className="px-5 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg glow-indigo">Save Meeting</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

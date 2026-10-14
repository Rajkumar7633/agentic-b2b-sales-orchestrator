"use client";

import { useState, useRef } from "react";
import {
  Activity,
  Play,
  RotateCcw,
  Sparkles,
  Bot,
  ShieldCheck,
  CheckCircle2,
  Radio,
  Sliders,
  Send,
  Zap,
} from "lucide-react";

interface StreamStep {
  event_id: string;
  step: number;
  total_steps: number;
  phase: string;
  agent_id: string;
  agent_name: string;
  thought: string;
  data: Record<string, any>;
  progress: number;
  timestamp: string;
}

export default function StreamPage() {
  const [companyName, setCompanyName] = useState("Titan Aerospace");
  const [speed, setSpeed] = useState(0.08);
  const [isStreaming, setIsStreaming] = useState(false);
  const [steps, setSteps] = useState<StreamStep[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [broadcastMsg, setBroadcastMsg] = useState("");
  const [broadcastStatus, setBroadcastStatus] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = async () => {
    setIsStreaming(true);
    setSteps([]);
    setCurrentProgress(0);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/stream/pursuit?company_name=${encodeURIComponent(companyName)}&speed=${speed}`,
        {
          headers: {
            Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
          },
          signal: controller.signal,
        }
      );

      if (!response.ok || !response.body) {
        throw new Error("Failed to connect to SSE stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const parsed: StreamStep = JSON.parse(line.replace("data: ", ""));
              setSteps((prev) => [...prev, parsed]);
              setCurrentProgress(parsed.progress);
            } catch (err) {
              console.error("Failed to parse SSE line", err);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        console.error("Stream error", err);
      }
    } finally {
      setIsStreaming(false);
    }
  };

  const stopStream = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsStreaming(false);
  };

  const handleBroadcast = async () => {
    if (!broadcastMsg.trim()) return;
    try {
      const res = await fetch("http://localhost:8000/api/v1/stream/broadcast", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("nexora_token") || "" : ""}`,
        },
        body: JSON.stringify({
          event_type: "CUSTOM_BROADCAST",
          data: { message: broadcastMsg, source: "Dashboard UI" },
        }),
      });
      if (res.ok) {
        setBroadcastStatus("Broadcast published to live stream!");
        setBroadcastMsg("");
        setTimeout(() => setBroadcastStatus(null), 3000);
      }
    } catch (err) {
      console.error("Broadcast failed", err);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Real-Time Telemetry (SSE)
            </span>
            <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Phase 1 Live
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight mt-2 flex items-center gap-3">
            <Activity className="w-8 h-8 text-indigo-400" />
            Live Agent Thought Streaming
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Observe autonomous multi-agent reasoning, step-by-step tool invocations, deterministic fit scoring, and HITL gate creation in real time.
          </p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 shadow-xl space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Target Company Name
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Titan Aerospace, Stripe, Acme"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900/80 border border-slate-700/80 text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>Streaming Delay (Seconds)</span>
              <span className="text-indigo-400 font-mono text-xs">{speed}s</span>
            </label>
            <input
              type="range"
              min="0.02"
              max="0.5"
              step="0.02"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
          </div>

          <div className="flex gap-3">
            {!isStreaming ? (
              <button
                onClick={startStream}
                className="flex-1 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-sky-500 hover:from-indigo-600 hover:to-sky-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2 transition-all"
              >
                <Play className="w-4 h-4 fill-current" />
                Launch Agent Stream
              </button>
            ) : (
              <button
                onClick={stopStream}
                className="flex-1 px-5 py-2.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 text-sm font-semibold rounded-xl flex items-center justify-center gap-2 transition-all"
              >
                <RotateCcw className="w-4 h-4" />
                Halt Stream
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="pt-2">
          <div className="flex justify-between text-xs text-slate-400 mb-1.5 font-medium">
            <span>Autonomous Execution Progress</span>
            <span className="text-indigo-400 font-mono">{currentProgress}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800/80 overflow-hidden border border-slate-700/40">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-sky-400 to-emerald-400 transition-all duration-300"
              style={{ width: `${currentProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Stream Terminal / Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Bot className="w-4 h-4 text-indigo-400" />
            Live Execution Feed
            {isStreaming && (
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 animate-pulse">
                STREAMING
              </span>
            )}
          </h2>

          <div className="space-y-3 min-h-[400px]">
            {steps.length === 0 ? (
              <div className="glass-panel p-12 rounded-2xl border border-slate-800/80 text-center flex flex-col items-center justify-center text-slate-500">
                <Sparkles className="w-10 h-10 text-slate-600 mb-3" />
                <p className="text-sm font-medium">Stream is idle.</p>
                <p className="text-xs text-slate-500 mt-1">
                  Click "Launch Agent Stream" above to watch multi-agent reasoning token-by-token.
                </p>
              </div>
            ) : (
              steps.map((st) => (
                <div
                  key={st.event_id}
                  className="glass-panel p-5 rounded-2xl border border-slate-800/80 shadow-md space-y-3 animate-fade-in"
                >
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                        Step {st.step} / {st.total_steps}
                      </span>
                      <span className="font-semibold text-white">{st.agent_name}</span>
                    </div>
                    <span className="text-slate-500 font-mono text-[11px]">{new Date(st.timestamp).toLocaleTimeString()}</span>
                  </div>

                  <p className="text-sm text-slate-300 font-medium leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-slate-800/60">
                    💭 <span className="italic text-slate-200">"{st.thought}"</span>
                  </p>

                  {st.data && (
                    <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-800/60 text-xs font-mono text-slate-300 overflow-x-auto">
                      <pre>{JSON.stringify(st.data, null, 2)}</pre>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Live Broadcast & Telemetry Sidebar */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 shadow-xl space-y-4">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Radio className="w-4 h-4 text-emerald-400" />
              Live Broadcast Telemetry
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Broadcast custom pipeline stage updates or agent directives to all active connected browser sessions via SSE.
            </p>

            <div className="space-y-2">
              <input
                type="text"
                value={broadcastMsg}
                onChange={(e) => setBroadcastMsg(e.target.value)}
                placeholder="e.g. Account Titan Aerospace moved to WON"
                className="w-full px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 text-white text-xs focus:outline-none focus:border-indigo-500"
              />
              <button
                onClick={handleBroadcast}
                className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 flex items-center justify-center gap-1.5 transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                Send Broadcast Event
              </button>
              {broadcastStatus && (
                <p className="text-xs text-emerald-400 text-center font-medium mt-1">{broadcastStatus}</p>
              )}
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 shadow-xl space-y-3">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-sky-400" />
              HITL Safety Architecture
            </h3>
            <ul className="text-xs text-slate-400 space-y-2 list-disc list-inside">
              <li>SSE transport works across enterprise firewalls (HTTP/2).</li>
              <li>Outreach drafts pause automatically at Step 6.</li>
              <li>No external email or LinkedIn message is sent without explicit sign-off.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

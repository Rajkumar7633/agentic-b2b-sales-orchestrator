"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Kanban,
  CheckCircle2,
  Building2,
  Users,
  Send,
  Calendar,
  FileSpreadsheet,
  BarChart3,
  Bot,
  ShieldCheck,
  Award,
  Sparkles,
  Zap,
  Activity,
  Layers,
} from "lucide-react";

const navItems = [
  { name: "Executive Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Pursuit Pipeline", href: "/pipeline", icon: Kanban },
  { name: "Real-Time Stream", href: "/stream", icon: Activity, badge: "SSE Live" },
  { name: "Cadence Workflows", href: "/workflows", icon: Layers, badge: "Durable" },
  { name: "Approval Center", href: "/approvals", icon: CheckCircle2, badge: "HITL Gate" },
  { name: "Accounts & Intelligence", href: "/accounts", icon: Building2 },
  { name: "Executive Contacts", href: "/contacts", icon: Users },
  { name: "Outreach Command", href: "/outreach", icon: Send },
  { name: "Meeting Scheduler", href: "/meetings", icon: Calendar },
  { name: "Excel Studio", href: "/excel", icon: FileSpreadsheet },
  { name: "Analytics Studio", href: "/analytics", icon: BarChart3 },
  { name: "Agent Registry", href: "/agents", icon: Bot, highlight: true },
  { name: "AI Evaluation", href: "/evaluation", icon: Award },
  { name: "Audit Trail", href: "/audit", icon: ShieldCheck },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen glass-panel flex flex-col fixed left-0 top-0 z-40 border-r border-slate-800/80 shadow-2xl">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-sky-500 flex items-center justify-center glow-indigo shadow-lg">
            <Zap className="w-5 h-5 text-white fill-current" />
          </div>
          <div>
            <h1 className="font-extrabold tracking-tight text-white text-base leading-tight">NEXORA</h1>
            <p className="text-[11px] text-indigo-400 font-semibold tracking-wider uppercase">Pursuit Engine</p>
          </div>
        </div>
        <span className="px-2 py-0.5 text-[9px] font-bold tracking-widest text-emerald-400 bg-emerald-500/10 rounded-full border border-emerald-500/20 uppercase">
          v2.0
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                isActive
                  ? "bg-gradient-to-r from-indigo-600/30 to-slate-800/50 text-white border border-indigo-500/40 shadow-lg shadow-indigo-500/10"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`p-1.5 rounded-lg transition-colors ${
                  isActive ? "bg-indigo-500 text-white" : "bg-slate-800/80 text-slate-400 group-hover:text-indigo-400"
                }`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span>{item.name}</span>
              </div>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-[9px] font-bold text-amber-300 bg-amber-500/10 rounded-md border border-amber-500/30 tracking-wider">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* LLM Engine Telemetry Banner */}
      <div className="mx-3 mb-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-sky-400 animate-pulse" />
          <div>
            <p className="text-[11px] font-bold text-slate-200 leading-none">Groq Llama-70B</p>
            <p className="text-[9px] text-slate-400 leading-tight mt-0.5">Latency: ~280ms</p>
          </div>
        </div>
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
      </div>

      {/* User Context Footer */}
      <div className="p-4 border-t border-slate-800/80 flex items-center justify-between bg-slate-900/80">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-sky-400 flex items-center justify-center text-xs font-bold text-white shadow-md">
            RK
          </div>
          <div className="text-xs">
            <p className="text-slate-100 font-bold leading-none">Raj Kumar</p>
            <p className="text-slate-400 text-[10px] leading-tight mt-0.5">Staff Enterprise Architect</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

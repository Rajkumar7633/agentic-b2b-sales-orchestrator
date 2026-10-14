"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Users, Mail, Linkedin, Sparkles, Search, ExternalLink, FileSpreadsheet, ShieldCheck, ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

const ITEMS_PER_PAGE = 12;

export default function ContactsPage() {
  const [contacts, setContacts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    async function loadData() {
      try {
        const cData = await fetchApi("/contacts");
        setContacts(cData || []);
      } catch (err) {
        console.error("Fetch contacts error:", err);
        setContacts([]);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const filteredContacts = contacts.filter((c) => {
    const q = searchQuery.toLowerCase();
    return (
      (c.first_name || "").toLowerCase().includes(q) ||
      (c.last_name || "").toLowerCase().includes(q) ||
      (c.title || "").toLowerCase().includes(q) ||
      (c.email || "").toLowerCase().includes(q)
    );
  });

  const totalPages = Math.max(1, Math.ceil(filteredContacts.length / ITEMS_PER_PAGE));
  const pageIndex = Math.min(currentPage, totalPages);
  const startIdx = (pageIndex - 1) * ITEMS_PER_PAGE;
  const paginatedContacts = filteredContacts.slice(startIdx, startIdx + ITEMS_PER_PAGE);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-80 space-y-4 text-indigo-400 font-medium">
        <Sparkles className="w-8 h-8 animate-spin text-indigo-400" />
        <p className="text-sm font-semibold tracking-wide">Loading Executive Contacts &amp; Decision Makers...</p>
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
              Executive Contacts &amp; Role Coverage
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-sky-400 bg-sky-500/10 rounded-full border border-sky-500/20 uppercase tracking-widest flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-sky-400" /> Human Outreach Matrix
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Imported decision-makers, executive role coverage targets, why-this-person intelligence, and human LinkedIn action status.
          </p>
        </div>

        <Link
          href="/excel"
          className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2 shrink-0 relative z-10"
        >
          <FileSpreadsheet className="w-4 h-4" /> Import Excel Workbook
        </Link>
      </div>

      {/* Search Input & Pagination Info Bar */}
      {contacts.length > 0 && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative max-w-md w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search decision makers by name, title, or email..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 text-xs text-white border border-slate-800 focus:outline-none focus:border-indigo-500 font-sans"
            />
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400 font-semibold shrink-0">
            <span>
              Showing <strong className="text-white">{filteredContacts.length > 0 ? startIdx + 1 : 0}</strong>-
              <strong className="text-white">{Math.min(startIdx + ITEMS_PER_PAGE, filteredContacts.length)}</strong> of{" "}
              <strong className="text-white">{filteredContacts.length}</strong> Contacts
            </span>
          </div>
        </div>
      )}

      {/* Empty State vs Contacts Grid */}
      {contacts.length === 0 ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/20 text-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Users className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h2 className="text-lg font-extrabold text-white">Upload your pursuit workbook to get started.</h2>
            <p className="text-xs text-slate-400">No contact records loaded. Import your Named Contacts or Role Coverage sheets to display decision makers.</p>
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {paginatedContacts.map((c) => (
              <div key={c.id} className="p-6 rounded-3xl glass-panel glass-panel-interactive space-y-4 flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-extrabold text-base text-white">
                        {c.first_name} {c.last_name}
                      </h3>
                      <p className="text-xs text-indigo-400 font-semibold">{c.title}</p>
                    </div>
                    {c.priority && (
                      <span className="px-2.5 py-0.5 text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 rounded-md border border-indigo-500/30">
                        {c.priority}
                      </span>
                    )}
                  </div>

                  {c.why_this_person && (
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                      <span className="text-[10px] font-bold text-sky-400 uppercase tracking-widest block">Why This Person</span>
                      <p className="text-xs text-slate-300 line-clamp-2">{c.why_this_person}</p>
                    </div>
                  )}

                  {c.next_best_action && (
                    <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 space-y-1">
                      <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">Next Action</span>
                      <p className="text-xs text-slate-200 font-medium line-clamp-2">{c.next_best_action}</p>
                    </div>
                  )}

                  <div className="space-y-1 text-xs text-slate-400 pt-2 border-t border-slate-800">
                    {c.email && (
                      <div className="flex items-center gap-2 truncate">
                        <Mail className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        <a href={`mailto:${c.email}`} className="hover:text-slate-200 transition truncate">{c.email}</a>
                      </div>
                    )}
                    {c.public_profile && (
                      <div className="flex items-center gap-2 truncate">
                        <Linkedin className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                        <a href={c.public_profile} target="_blank" rel="noreferrer" className="hover:text-sky-300 transition truncate">
                          LinkedIn Profile <ExternalLink className="w-3 h-3 inline ml-0.5" />
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                    LinkedIn: <span className="text-amber-400 font-semibold">{c.linkedin_status || "NOT_STARTED"}</span>
                  </span>
                  <span className="text-[10px] text-slate-400">Human Action Task</span>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between p-4 glass-panel rounded-2xl border-slate-800">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 text-xs font-bold text-slate-300 bg-slate-800/80 hover:bg-slate-800 rounded-xl border border-slate-700 transition flex items-center gap-1 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>

              <span className="text-xs font-mono text-slate-400">
                Page <strong className="text-white">{currentPage}</strong> of <strong className="text-white">{totalPages}</strong>
              </span>

              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 text-xs font-bold text-slate-300 bg-slate-800/80 hover:bg-slate-800 rounded-xl border border-slate-700 transition flex items-center gap-1 disabled:opacity-40"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { fetchApi } from "@/lib/api";
import { Building2, Search, Sparkles, ExternalLink, Play, FileSpreadsheet, RefreshCw, ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

const ITEMS_PER_PAGE = 9;

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [pursuingId, setPursuingId] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    async function loadAccounts() {
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
    loadAccounts();
  }, []);

  const handlePursue = async (companyName: string, accountId: string) => {
    setPursuingId(accountId);
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
      setPursuingId(null);
    }
  };

  const filtered = accounts.filter((a) =>
    (a.name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    (a.sector || a.industry || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.max(1, Math.ceil(filtered.length / ITEMS_PER_PAGE));
  const pageIndex = Math.min(currentPage, totalPages);
  const startIdx = (pageIndex - 1) * ITEMS_PER_PAGE;
  const paginatedAccounts = filtered.slice(startIdx, startIdx + ITEMS_PER_PAGE);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-indigo-400 font-medium">
        <Sparkles className="w-6 h-6 animate-spin mr-2" /> Loading Target Accounts &amp; Deep Research...
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Title Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20">
        <div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">Target Accounts &amp; Intelligence</h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">Company firmographics, active projects, why-now expansion signals, and deep AI research.</p>
        </div>
        <Link
          href="/excel"
          className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-lg glow-indigo transition flex items-center gap-2 shrink-0"
        >
          <FileSpreadsheet className="w-4 h-4" /> Import Excel Workbook
        </Link>
      </div>

      {/* Search & Pagination Info Bar */}
      {accounts.length > 0 && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative max-w-md w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Filter target accounts by name or sector..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 text-xs text-white border border-slate-800 focus:outline-none focus:border-indigo-500 font-sans"
            />
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400 font-semibold shrink-0">
            <span>
              Showing <strong className="text-white">{filtered.length > 0 ? startIdx + 1 : 0}</strong>-
              <strong className="text-white">{Math.min(startIdx + ITEMS_PER_PAGE, filtered.length)}</strong> of{" "}
              <strong className="text-white">{filtered.length}</strong> Accounts
            </span>
          </div>
        </div>
      )}

      {/* Empty State vs Grid */}
      {accounts.length === 0 ? (
        <div className="p-12 rounded-3xl glass-panel border-indigo-500/20 text-center space-y-4">
          <div className="w-16 h-16 rounded-3xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 glow-indigo">
            <Building2 className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h2 className="text-lg font-extrabold text-white">Upload your pursuit workbook to get started.</h2>
            <p className="text-xs text-slate-400">No account data loaded. Import your XLSX business workbook to populate target companies and projects.</p>
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
            {paginatedAccounts.map((acc) => (
              <div key={acc.id} className="p-6 rounded-3xl glass-panel glass-panel-interactive flex flex-col justify-between space-y-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-extrabold text-base text-white">{acc.name}</h3>
                      <p className="text-xs text-indigo-400">{acc.domain || `${acc.name.toLowerCase().replace(/ /g, '')}.com`}</p>
                    </div>
                    <span className="px-2.5 py-1 text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 rounded-lg border border-indigo-500/30">
                      {acc.pipeline_stage || "IDENTIFIED"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                    <div>
                      <span className="text-slate-500 block">Sector / Industry:</span>
                      <span className="text-slate-200 font-semibold">{acc.sector || acc.industry || "Enterprise"}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Location / HQ:</span>
                      <span className="text-slate-200 font-semibold">{acc.location || acc.hq_focus || "USA"}</span>
                    </div>
                  </div>

                  {acc.why_now_signal && (
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                      <span className="text-[10px] font-bold text-sky-400 uppercase tracking-widest block">Why-Now Signal</span>
                      <p className="text-xs text-slate-300 line-clamp-2">{acc.why_now_signal}</p>
                    </div>
                  )}

                  {acc.recommended_next_action && (
                    <div className="p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 space-y-1">
                      <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest block">Recommended Next Action</span>
                      <p className="text-xs text-slate-200 font-medium line-clamp-2">{acc.recommended_next_action}</p>
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                  <Link href={`/accounts/${acc.id}`} className="text-xs text-slate-400 hover:text-white font-semibold flex items-center gap-1">
                    Details <ExternalLink className="w-3 h-3" />
                  </Link>

                  <button
                    onClick={() => handlePursue(acc.name, acc.id)}
                    disabled={pursuingId === acc.id}
                    className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-md glow-indigo transition flex items-center gap-1.5 disabled:opacity-50"
                  >
                    {pursuingId === acc.id ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Play className="w-3.5 h-3.5 fill-current" />
                    )}
                    Deep Research
                  </button>
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

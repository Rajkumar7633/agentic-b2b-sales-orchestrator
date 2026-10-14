"use client";

import { useState } from "react";
import { fetchApi } from "@/lib/api";
import { FileSpreadsheet, Upload, Download, CheckCircle2, AlertCircle, Sparkles, RefreshCw, Layers, Database, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function ExcelStudioPage() {
  const [file, setFile] = useState<File | null>(null);
  const [inspection, setInspection] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);

  const handleInspect = async (selectedFile: File) => {
    setLoading(true);
    setFile(selectedFile);
    setImportResult(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("http://localhost:8000/api/v1/excel/inspect", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setInspection(data);
    } catch (err: any) {
      alert("Inspection note: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/api/v1/excel/import", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setImportResult(data);
    } catch (err: any) {
      alert("Import note: " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    window.open("http://localhost:8000/api/v1/excel/export", "_blank");
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 glass-panel p-6 rounded-3xl border-indigo-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-indigo-500/10 via-sky-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Dynamic XLSX Ingestion Studio
            </h1>
            <span className="px-2.5 py-1 text-[10px] font-bold text-emerald-300 bg-emerald-500/10 rounded-full border border-emerald-500/20 uppercase tracking-widest flex items-center gap-1">
              <Database className="w-3 h-3 text-emerald-400" /> PostgreSQL Persistence
            </span>
          </div>
          <p className="text-xs md:text-sm text-slate-400 mt-1 max-w-2xl">
            Upload custom pursuit workbooks (Master Pipeline, Named Contacts, Active Projects, Outreach Tracker, Role Coverage, Pursuit Profiles). Normalizes columns and updates all application pages live.
          </p>
        </div>

        <button
          onClick={handleExport}
          className="px-5 py-2.5 text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl shadow-lg glow-emerald transition flex items-center gap-2 shrink-0 relative z-10"
        >
          <Download className="w-4 h-4" /> Export Pipeline to Excel
        </button>
      </div>

      {/* Upload Dropzone Container */}
      <div className="p-10 rounded-3xl glass-panel text-center border-2 border-dashed border-slate-700/80 hover:border-indigo-500/60 transition-all duration-300 space-y-5 relative overflow-hidden group">
        <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 group-hover:scale-110 group-hover:bg-indigo-600 group-hover:text-white transition duration-300 shadow-lg glow-indigo">
          <FileSpreadsheet className="w-8 h-8" />
        </div>
        
        <div>
          <h3 className="font-extrabold text-lg text-white">Upload User Pursuit Workbook</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
            Supports Master Pipeline, Named Contacts, Active Projects, Outreach Tracker, Role Coverage, and Pursuit Profiles sheets (<code className="text-sky-300">.xlsx</code>, <code className="text-sky-300">.csv</code>)
          </p>
        </div>

        <label className="inline-block px-6 py-3 text-xs font-extrabold text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 rounded-xl shadow-xl glow-indigo cursor-pointer transition">
          <Upload className="w-4 h-4 inline mr-2" /> Select Workbook File
          <input
            type="file"
            accept=".xlsx, .xls, .csv"
            className="hidden"
            onChange={(e) => {
              if (e.target.files?.[0]) handleInspect(e.target.files[0]);
            }}
          />
        </label>

        {file && (
          <div className="p-3 rounded-xl bg-slate-900/80 border border-indigo-500/30 inline-block text-xs font-mono text-indigo-300">
            Selected File: <span className="font-bold text-white">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
          </div>
        )}
      </div>

      {/* Inspection Summary Card */}
      {inspection && (
        <div className="p-6 rounded-3xl glass-panel space-y-5 border-indigo-500/30 shadow-2xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base text-white">Workbook Inspection &amp; Column Detection</h3>
                <p className="text-xs text-slate-400">Dynamic sheet identification &amp; fuzzy header mapping layer.</p>
              </div>
            </div>

            <button
              onClick={handleImport}
              disabled={loading}
              className="px-6 py-2.5 text-xs font-extrabold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg glow-indigo transition disabled:opacity-50 shrink-0"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Ingesting to PostgreSQL...
                </span>
              ) : (
                "Confirm & Ingest Workbook"
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(inspection.parsed_summary || {}).map(([sheetName, sheetInfo]: [string, any]) => (
              <div key={sheetName} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5 text-indigo-400" /> {sheetName}
                  </span>
                  <span className="px-2.5 py-0.5 text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 rounded-md border border-indigo-500/30 font-mono">
                    {sheetInfo.row_count} Rows
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-mono bg-slate-950 p-2.5 rounded-xl border border-slate-800/80 truncate">
                  Headers: {(sheetInfo.columns || []).join(", ")}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Import Result Banner */}
      {importResult && (
        <div className="p-6 rounded-3xl glass-panel border-emerald-500/40 bg-emerald-500/10 text-emerald-200 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <h4 className="font-extrabold text-base text-white">Workbook Ingested Successfully!</h4>
                <p className="text-xs text-emerald-300">All business records are now live across Dashboards, Pipeline, Accounts, and Contacts.</p>
              </div>
            </div>

            <Link
              href="/"
              className="px-5 py-2 text-xs font-extrabold text-emerald-950 bg-emerald-400 hover:bg-emerald-300 rounded-xl transition shadow-md flex items-center gap-1.5 shrink-0"
            >
              View Dashboard <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs font-mono text-emerald-300 space-y-1">
            <p>• Import Job ID: <span className="text-sky-300 font-bold">{importResult.import_id}</span></p>
            <p>• Companies Ingested: <span className="font-bold text-white">{importResult.imported_companies}</span></p>
            <p>• Contacts Ingested: <span className="font-bold text-white">{importResult.imported_contacts}</span></p>
            <p>• Projects Ingested: <span className="font-bold text-white">{importResult.imported_projects}</span></p>
            <p>• Tenant Context: <span className="text-indigo-300 font-bold">tenant_nexora_default (Multi-Tenant Isolated)</span></p>
          </div>
        </div>
      )}
    </div>
  );
}

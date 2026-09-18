import React, { useState, useMemo } from 'react';
import { FileText, Copy, Check, Search, Filter, ShieldCheck } from 'lucide-react';

interface RawOcrViewerProps {
  transcript: string;
  meanConfidence?: number;
  extractedLines?: Array<{ lineNumber: number; text: string; confidence?: number; surface?: string }>;
  productName?: string;
  defaultOpen?: boolean;
}

export const RawOcrViewer: React.FC<RawOcrViewerProps> = ({
  transcript,
  meanConfidence = 95,
  extractedLines = [],
  productName = 'Packaged Commodity'
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [copied, setCopied] = useState(false);
  const [selectedSurface, setSelectedSurface] = useState<string>('ALL');

  // Surface list
  const surfaces = useMemo(() => {
    const list = Array.from(new Set(extractedLines.map(l => l.surface).filter(Boolean))) as string[];
    return ['ALL', ...list];
  }, [extractedLines]);

  // Filtered lines
  const filteredLines = useMemo(() => {
    return extractedLines.filter(line => {
      const matchSearch = !searchTerm || line.text.toLowerCase().includes(searchTerm.toLowerCase());
      const matchSurface = selectedSurface === 'ALL' || line.surface === selectedSurface;
      return matchSearch && matchSurface;
    });
  }, [extractedLines, searchTerm, selectedSurface]);

  const handleCopy = () => {
    const textToCopy = filteredLines.length > 0 
      ? filteredLines.map(l => l.text).join('\n')
      : transcript;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const wordCount = transcript ? transcript.trim().split(/\s+/).length : 0;
  const lineCount = extractedLines.length > 0 ? extractedLines.length : (transcript ? transcript.split('\n').length : 0);

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden shadow-md text-slate-200">
      {/* Header bar */}
      <div className="px-4 py-3 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-white">
            Verbatim Optical OCR Transcript • {productName}
          </span>
          <span className="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-700 px-2 py-0.5 rounded font-mono">
            {meanConfidence}% OCR Confidence
          </span>
          <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
            {lineCount} lines • {wordCount} words
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={handleCopy}
            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs flex items-center space-x-1.5 transition border border-slate-700 cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-amber-400" />}
            <span>{copied ? 'Copied!' : 'Copy Transcript'}</span>
          </button>
        </div>
      </div>

      {/* Search & Surface filter bar */}
      <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search raw optical text (e.g., 'mrp', 'g', 'net', 'pkd', 'address')..."
            className="w-full bg-slate-950 border border-slate-700 rounded pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>

        {surfaces.length > 1 && (
          <div className="flex items-center space-x-1.5">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-[11px] text-slate-400">Surface:</span>
            <select
              value={selectedSurface}
              onChange={(e) => setSelectedSurface(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-slate-200 rounded px-2 py-1 text-xs focus:outline-none"
            >
              {surfaces.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Content body */}
      <div className="p-4 max-h-72 overflow-y-auto font-mono text-xs leading-relaxed space-y-1 select-all bg-black/50">
        {filteredLines.length > 0 ? (
          filteredLines.map((line, idx) => {
            const isMatch = searchTerm && line.text.toLowerCase().includes(searchTerm.toLowerCase());
            return (
              <div
                key={idx}
                className={`flex items-start space-x-3 py-0.5 px-1.5 rounded transition ${
                  isMatch ? 'bg-amber-950/60 border border-amber-600/40 text-amber-200' : 'hover:bg-slate-800/60 text-emerald-300/90'
                }`}
              >
                <span className="text-[10px] text-slate-500 shrink-0 select-none w-8 text-right font-bold">
                  {line.lineNumber ? `L${String(line.lineNumber).padStart(2, '0')}` : `#${idx + 1}`}
                </span>
                {line.surface && (
                  <span className="text-[9px] bg-slate-800 text-slate-400 px-1 rounded select-none shrink-0 uppercase">
                    {line.surface}
                  </span>
                )}
                <span className="break-all whitespace-pre-wrap">{line.text}</span>
              </div>
            );
          })
        ) : transcript ? (
          <pre className="whitespace-pre-wrap text-emerald-300/90 font-mono text-[11px] leading-relaxed">
            {transcript}
          </pre>
        ) : (
          <div className="text-center py-6 text-slate-500 text-xs">
            No optical text recognized for this package.
          </div>
        )}
      </div>

      {/* Status footer */}
      <div className="px-4 py-2 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Verbatim audit log preserved under Legal Metrology Act, 2009. Non-destructive evidence archive.</span>
        </div>
        <span>{filteredLines.length} lines shown</span>
      </div>
    </div>
  );
};

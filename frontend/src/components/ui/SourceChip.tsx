import React from 'react';
import { BookOpen, ExternalLink, ShieldCheck } from 'lucide-react';

interface SourceChipProps {
  title: string;
  section?: string;
  page?: string;
  url?: string;
  isSample?: boolean;
}

export const SourceChip: React.FC<SourceChipProps> = ({
  title,
  section,
  page,
  url,
  isSample = false,
}) => {
  return (
    <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-50/80 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800/60 max-w-full">
      <BookOpen className="w-3.5 h-3.5 shrink-0 text-emerald-600 dark:text-emerald-400" />
      <span className="truncate">{title}</span>
      {section && <span className="text-slate-500 dark:text-slate-400 shrink-0">· {section}</span>}
      {page && <span className="text-slate-500 dark:text-slate-400 shrink-0">(p. {page})</span>}
      {isSample && (
        <span className="px-1 py-0.2 rounded text-[10px] bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-400 font-semibold shrink-0">
          Sample
        </span>
      )}
      {url && (
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-emerald-700 hover:text-emerald-900 shrink-0 ml-1"
        >
          <ExternalLink className="w-3 h-3" />
        </a>
      )}
    </div>
  );
};

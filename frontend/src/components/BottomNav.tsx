import React from 'react';
import { useTranslation } from 'react-i18next';
import { NavLink } from 'react-router-dom';
import { Home, MessageSquare, Camera, TrendingUp, Calendar, AlertTriangle } from 'lucide-react';

export const BottomNav: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-slate-200 dark:border-slate-800 pb-safe">
      <div className="flex items-center justify-around h-16 px-2 max-w-md mx-auto relative">
        {/* Home */}
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 text-xs font-medium transition-colors ${
              isActive
                ? 'text-emerald-700 dark:text-emerald-400 font-semibold'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900'
            }`
          }
        >
          <Home className="w-5 h-5 mb-0.5" />
          <span>{t('nav.home')}</span>
        </NavLink>

        {/* Chat */}
        <NavLink
          to="/chat"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 text-xs font-medium transition-colors ${
              isActive
                ? 'text-emerald-700 dark:text-emerald-400 font-semibold'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900'
            }`
          }
        >
          <MessageSquare className="w-5 h-5 mb-0.5" />
          <span>{t('nav.chat')}</span>
        </NavLink>

        {/* Prominent Center Scan Button */}
        <div className="flex-1 flex justify-center -mt-6">
          <NavLink
            to="/scan"
            aria-label="Scan Leaf for Disease"
            className={({ isActive }) =>
              `w-14 h-14 rounded-full bg-gradient-to-tr from-emerald-700 to-emerald-500 flex flex-col items-center justify-center text-white shadow-lg shadow-emerald-600/30 border-4 border-white dark:border-slate-900 transition-transform hover:scale-105 active:scale-95 animate-pulse-subtle ${
                isActive ? 'ring-2 ring-emerald-500 ring-offset-2' : ''
              }`
            }
          >
            <Camera className="w-6 h-6" />
            <span className="text-[9px] font-bold mt-0.5">Scan</span>
          </NavLink>
        </div>

        {/* Market */}
        <NavLink
          to="/market"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 text-xs font-medium transition-colors ${
              isActive
                ? 'text-emerald-700 dark:text-emerald-400 font-semibold'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900'
            }`
          }
        >
          <TrendingUp className="w-5 h-5 mb-0.5" />
          <span>{t('nav.market')}</span>
        </NavLink>

        {/* Calendar / Alerts */}
        <NavLink
          to="/calendar"
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 py-1 text-xs font-medium transition-colors ${
              isActive
                ? 'text-emerald-700 dark:text-emerald-400 font-semibold'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-900'
            }`
          }
        >
          <Calendar className="w-5 h-5 mb-0.5" />
          <span>{t('nav.calendar')}</span>
        </NavLink>
      </div>
    </div>
  );
};

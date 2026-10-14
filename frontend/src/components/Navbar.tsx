import React from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { Moon, Sun, Globe, WifiOff, ShieldCheck, Sparkles, UserCheck } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export const Navbar: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user, switchRole, setLanguage } = useAuthStore();
  const { theme, toggleTheme, isOffline } = useUIStore();
  const location = useLocation();

  const handleLanguageChange = (lang: 'en' | 'hi' | 'gu') => {
    i18n.changeLanguage(lang);
    setLanguage(lang);
  };

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <Link to="/dashboard" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-700 to-emerald-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            <span className="text-2xl" role="img" aria-label="sprout">🌾</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold bg-gradient-to-r from-emerald-800 to-emerald-600 dark:from-emerald-400 dark:to-emerald-200 bg-clip-text text-transparent">
                {t('appName')}
              </span>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                <Sparkles className="w-2.5 h-2.5 mr-1 text-emerald-600 dark:text-emerald-400" />
                IBM Granite
              </span>
            </div>
            <p className="text-[10px] text-slate-500 dark:text-slate-400 hidden sm:block">
              {t('tagline')}
            </p>
          </div>
        </Link>

        {/* Center / Navigation Links (Desktop) */}
        <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
          <Link
            to="/dashboard"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/dashboard'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.home')}
          </Link>
          <Link
            to="/chat"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/chat'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.chat')}
          </Link>
          <Link
            to="/scan"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/scan'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.scan')}
          </Link>
          <Link
            to="/market"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/market'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.market')}
          </Link>
          <Link
            to="/calendar"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/calendar'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.calendar')}
          </Link>
          <Link
            to="/officer"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/officer'
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.officer')}
          </Link>
          <Link
            to="/trace"
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              location.pathname === '/trace'
                ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {t('nav.trace')}
          </Link>
        </nav>

        {/* Right Tools: Language, Role Switcher, Dark Mode */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Offline indicator */}
          {isOffline && (
            <div className="flex items-center px-2 py-1 bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 rounded-md text-xs font-medium">
              <WifiOff className="w-3.5 h-3.5 mr-1" />
              Offline
            </div>
          )}

          {/* Language Switcher */}
          <div className="relative flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5 border border-slate-200 dark:border-slate-700">
            <Globe className="w-3.5 h-3.5 ml-2 text-slate-500" />
            <select
              aria-label="Select Language"
              value={i18n.language}
              onChange={(e) => handleLanguageChange(e.target.value as any)}
              className="bg-transparent text-xs font-semibold py-1 px-2 text-slate-700 dark:text-slate-200 outline-none cursor-pointer"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="gu">ગુજરાતી</option>
            </select>
          </div>

          {/* Quick Persona / Role Switcher for Demo */}
          <button
            onClick={() => switchRole(user?.role === 'officer' ? 'farmer' : 'officer')}
            title="Click to toggle between Farmer and Extension Officer roles"
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white transition-all shadow-sm"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">
              {user?.role === 'officer' ? 'Officer Mode' : 'Farmer Mode'}
            </span>
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
};

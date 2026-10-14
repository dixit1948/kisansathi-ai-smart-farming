import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { BottomNav } from './components/BottomNav';
import { useUIStore } from './store/uiStore';
import { LandingPage } from './features/LandingPage';
import { LoginPage } from './features/LoginPage';
import { OnboardingWizard } from './features/OnboardingWizard';
import { FarmOverview } from './features/FarmOverview';
import { ChatPage } from './features/ChatPage';
import { ScanPage } from './features/ScanPage';
import { CalendarPage } from './features/CalendarPage';
import { MarketPage } from './features/MarketPage';
import { AlertsPage } from './features/AlertsPage';
import { OfficerPage } from './features/OfficerPage';
import { TracePage } from './features/TracePage';
import { SettingsPage } from './features/SettingsPage';
import { NotFoundPage } from './features/NotFoundPage';
import { WifiOff, X } from 'lucide-react';

export const App: React.FC = () => {
  const { isOffline, toasts, removeToast } = useUIStore();

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-200">
        {/* Offline Shell Banner */}
        {isOffline && (
          <div className="bg-amber-500 text-slate-950 px-4 py-2 text-xs font-bold text-center flex items-center justify-center space-x-2 sticky top-0 z-50">
            <WifiOff className="w-4 h-4" />
            <span>
              Offline Shell Mode Active — Showing cached farm data and offline mock heuristics.
            </span>
          </div>
        )}

        {/* Global Toast Container */}
        {toasts.length > 0 && (
          <div className="fixed top-20 right-4 z-50 space-y-2 max-w-sm w-full">
            {toasts.map((t) => (
              <div
                key={t.id}
                className={`p-3 rounded-xl shadow-lg border text-xs font-semibold flex items-center justify-between backdrop-blur-md transition-all ${
                  t.type === 'success'
                    ? 'bg-emerald-500/90 text-white border-emerald-600'
                    : t.type === 'error'
                    ? 'bg-rose-500/90 text-white border-rose-600'
                    : t.type === 'warning'
                    ? 'bg-amber-500/90 text-slate-900 border-amber-600'
                    : 'bg-slate-800/90 text-white border-slate-700'
                }`}
              >
                <span>{t.message}</span>
                <button
                  onClick={() => removeToast(t.id)}
                  className="p-1 hover:opacity-75 transition-opacity"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Top Navbar */}
        <Navbar />

        {/* Main Content Area */}
        <main className="flex-1 pb-20 md:pb-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/onboarding" element={<OnboardingWizard />} />
            <Route path="/dashboard" element={<FarmOverview />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/market" element={<MarketPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/officer" element={<OfficerPage />} />
            <Route path="/trace" element={<TracePage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>

        {/* Mobile Bottom Navigation */}
        <BottomNav />
      </div>
    </BrowserRouter>
  );
};

export default App;

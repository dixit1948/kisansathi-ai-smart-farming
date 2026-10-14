import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import {
  Sparkles,
  Camera,
  CloudSun,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  UserCheck,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { switchRole } = useAuthStore();

  const handleDemoLogin = (role: 'farmer' | 'officer' | 'admin') => {
    switchRole(role);
    if (role === 'officer') {
      navigate('/officer');
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50/50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-20 text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-100 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-300 text-xs font-semibold mb-8 border border-emerald-300/80 dark:border-emerald-800">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>IBM Granite Foundation Models on watsonx.ai</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 dark:text-white tracking-tight max-w-4xl mx-auto leading-tight">
          Smart Farming Advice,{' '}
          <span className="bg-gradient-to-r from-emerald-600 to-emerald-500 bg-clip-text text-transparent">
            In Every Farmer's Language.
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-slate-600 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed">
          KisanSathi pairs multi-agent AI with IBM Granite to diagnose leaf diseases in under 10 seconds, forecast weather-aware irrigation, and optimize mandi sell-timing.
        </p>

        {/* Quick Demo Access Bar */}
        <div className="mt-10 max-w-lg mx-auto bg-white dark:bg-slate-900 p-4 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
            Quick 1-Click Demo Personas
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Button
              size="lg"
              variant="primary"
              onClick={() => handleDemoLogin('farmer')}
              leftIcon={<span className="text-xl">👨‍🌾</span>}
            >
              Enter as Farmer
            </Button>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => handleDemoLogin('officer')}
              leftIcon={<span className="text-xl">🏛️</span>}
            >
              Agri Extension Officer
            </Button>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Pre-seeded with Surat, Navsari & Bharuch farms (cotton, groundnut, wheat).
          </p>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-t-4 border-t-emerald-500">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 dark:bg-emerald-950/60 flex items-center justify-center text-emerald-700 dark:text-emerald-300 mb-4">
              <Camera className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Leaf Pathology Scan
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Snap a phone photo of a sick leaf. Granite vision diagnoses disease with severity and organic-first remedies in &lt;10s.
            </p>
          </Card>

          <Card className="border-t-4 border-t-amber-500">
            <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-950/60 flex items-center justify-center text-amber-700 dark:text-amber-300 mb-4">
              <CloudSun className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              ET0 Weather & Irrigation
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Open-Meteo 7-day forecast combined with Penman-Monteith evapotranspiration for soil-specific watering advice.
            </p>
          </Card>

          <Card className="border-t-4 border-t-blue-500">
            <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-950/60 flex items-center justify-center text-blue-700 dark:text-blue-300 mb-4">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Mandi Price Timing
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              30-day modal price trend line and AI-powered "Hold vs Sell" indicators to maximize smallholder crop profits.
            </p>
          </Card>

          <Card className="border-t-4 border-t-purple-500">
            <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-950/60 flex items-center justify-center text-purple-700 dark:text-purple-300 mb-4">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Vernacular & WhatsApp
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Full Gujarati, Hindi, and English support. Accessible via Progressive Web App and Meta WhatsApp Cloud API webhooks.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

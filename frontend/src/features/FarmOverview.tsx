import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { api } from '../api/client';
import type { FarmOverviewData } from '../api/client';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  CloudSun,
  Droplets,
  Wind,
  CheckCircle2,
  Camera,
  MessageSquare,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Calendar,
  ShieldAlert,
} from 'lucide-react';

export const FarmOverview: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { addToast } = useUIStore();

  const [data, setData] = useState<FarmOverviewData | null>(null);
  const [taskDone, setTaskDone] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOverview().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  const handleMarkTask = () => {
    setTaskDone(!taskDone);
    addToast('success', !taskDone ? 'Task marked as completed!' : 'Task reset.');
  };

  if (loading || !data) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 animate-pulse space-y-6">
        <div className="h-8 bg-slate-200 dark:bg-slate-800 rounded-lg w-1/3" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-48 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          <div className="h-48 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
          <div className="h-48 bg-slate-200 dark:bg-slate-800 rounded-2xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 sm:py-8 space-y-6 sm:space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-emerald-800 to-emerald-700 text-white p-6 rounded-3xl shadow-lg shadow-emerald-900/20 relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-48 h-48 bg-white/10 rounded-full blur-2xl pointer-events-none" />
        <div>
          <div className="flex items-center space-x-2 text-emerald-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <span>📍 {data.district}</span>
            <span>•</span>
            <span>{data.crop_name}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            {t('welcome', { name: user?.name || data.farmer_name })}
          </h1>
          <p className="text-xs sm:text-sm text-emerald-100 mt-1">
            Season Stage: <span className="font-semibold">{data.crop_stage}</span> (Sown: {data.sowing_date})
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Badge variant="warning" size="md" className="bg-amber-400 text-slate-900 font-bold border-none">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" />
            2 Active Farm Alerts
          </Badge>
        </div>
      </div>

      {/* Quick Action Tiles (Top Priority) */}
      <div>
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3">
          Instant Farming Actions
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
          <Card
            hoverable
            onClick={() => navigate('/scan')}
            className="border-emerald-200 dark:border-emerald-800/80 bg-gradient-to-b from-emerald-50/50 to-white dark:from-emerald-950/20 dark:to-slate-900 flex flex-col items-center text-center p-4"
          >
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-md shadow-emerald-600/30 mb-2">
              <Camera className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {t('actions.scanLeaf')}
            </span>
            <span className="text-[11px] text-slate-500 mt-0.5">Diagnose in &lt;10s</span>
          </Card>

          <Card
            hoverable
            onClick={() => navigate('/chat')}
            className="flex flex-col items-center text-center p-4"
          >
            <div className="w-12 h-12 rounded-2xl bg-sky-600 text-white flex items-center justify-center shadow-md shadow-sky-600/30 mb-2">
              <MessageSquare className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {t('actions.askAI')}
            </span>
            <span className="text-[11px] text-slate-500 mt-0.5">Voice or Text Chat</span>
          </Card>

          <Card
            hoverable
            onClick={() => navigate('/market')}
            className="flex flex-col items-center text-center p-4"
          >
            <div className="w-12 h-12 rounded-2xl bg-amber-500 text-white flex items-center justify-center shadow-md shadow-amber-500/30 mb-2">
              <TrendingUp className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {t('actions.checkPrices')}
            </span>
            <span className="text-[11px] text-slate-500 mt-0.5">Mandi Rates & Timing</span>
          </Card>

          <Card
            hoverable
            onClick={() => navigate('/calendar')}
            className="flex flex-col items-center text-center p-4"
          >
            <div className="w-12 h-12 rounded-2xl bg-purple-600 text-white flex items-center justify-center shadow-md shadow-purple-600/30 mb-2">
              <Calendar className="w-6 h-6" />
            </div>
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {t('actions.cropSchedule')}
            </span>
            <span className="text-[11px] text-slate-500 mt-0.5">Stage Milestones</span>
          </Card>
        </div>
      </div>

      {/* Two-Column Grid: Weather & Irrigation vs Task of the Day */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weather & Irrigation Card (2 Columns) */}
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div className="flex items-center space-x-2">
              <CloudSun className="w-5 h-5 text-amber-500" />
              <h3 className="font-bold text-slate-900 dark:text-white text-base">
                {t('weather.title')}
              </h3>
            </div>
            <span className="text-xs text-slate-500">Live Open-Meteo & ET0</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
              <span className="text-[11px] text-slate-500 block">{t('weather.temp')}</span>
              <span className="text-2xl font-black text-slate-900 dark:text-white">
                {data.weather.max_temp}°C
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">Min: {data.weather.min_temp}°C</span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
              <span className="text-[11px] text-slate-500 block">{t('weather.irrigationNeed')}</span>
              <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                {data.weather.irrigation_needed_mm} mm
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">Drip: 2 hrs tomorrow</span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
              <span className="text-[11px] text-slate-500 block">{t('weather.wind')}</span>
              <span className="text-2xl font-black text-slate-900 dark:text-white">
                {data.weather.wind_kmh} km/h
              </span>
              <span className="text-[10px] text-emerald-600 block mt-0.5">Low Drift Risk</span>
            </div>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
              <span className="text-[11px] text-slate-500 block">{t('weather.rain')}</span>
              <span className="text-2xl font-black text-slate-900 dark:text-white">
                {data.weather.rainfall_mm} mm
              </span>
              <span className="text-[10px] text-slate-400 block mt-0.5">0% probability</span>
            </div>
          </div>

          {/* Spray Window Banner */}
          <div className="p-3.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/80 rounded-xl flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-xl">✅</span>
              <div>
                <p className="text-xs font-bold text-emerald-900 dark:text-emerald-200">
                  {data.weather.spray_window}
                </p>
                <p className="text-[11px] text-emerald-700 dark:text-emerald-400">
                  Ideal conditions for bio-pesticide and foliar spray application.
                </p>
              </div>
            </div>
          </div>

          {/* 7-Day Mini Forecast */}
          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800">
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 block mb-3">
              7-Day Weather Outlook
            </span>
            <div className="grid grid-cols-7 gap-1 sm:gap-2 text-center">
              {data.weather.forecast_7d.map((f, i) => (
                <div
                  key={i}
                  className={`p-2 rounded-xl text-xs ${
                    i === 0
                      ? 'bg-emerald-100/70 dark:bg-emerald-950/60 font-bold'
                      : 'bg-slate-50 dark:bg-slate-800/50'
                  }`}
                >
                  <p className="text-[11px] text-slate-500">{f.day}</p>
                  <p className="text-sm font-bold text-slate-900 dark:text-white my-1">{f.max_temp}°</p>
                  <p className="text-[10px] text-slate-400">{f.rain_mm}mm</p>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Task of the Day & Live Alerts */}
        <div className="space-y-6">
          <Card className="border-l-4 border-l-emerald-600">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                {t('taskOfDay.title')}
              </span>
              {taskDone && (
                <Badge variant="success" size="sm">
                  {t('taskOfDay.completed')}
                </Badge>
              )}
            </div>

            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-2">
              {data.task_of_day.title}
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
              {data.task_of_day.description}
            </p>

            <Button
              variant={taskDone ? 'outline' : 'primary'}
              size="sm"
              onClick={handleMarkTask}
              className="w-full"
              leftIcon={<CheckCircle2 className="w-4 h-4" />}
            >
              {taskDone ? 'Reset Task' : t('taskOfDay.markDone')}
            </Button>
          </Card>

          {/* Active Alerts Teaser */}
          <Card className="border-l-4 border-l-rose-500">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400">
                Farm Risk Warnings
              </span>
              <button
                onClick={() => navigate('/alerts')}
                className="text-xs text-emerald-600 dark:text-emerald-400 font-semibold"
              >
                View all (2) →
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-2.5 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/40 rounded-xl">
                <p className="text-xs font-bold text-rose-900 dark:text-rose-200">
                  Pink Bollworm Outbreak Cluster
                </p>
                <p className="text-[11px] text-rose-700 dark:text-rose-300 mt-0.5">
                  Reported in nearby farms within 5km in Bardoli. Inspect floral buds.
                </p>
              </div>

              <div className="p-2.5 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/40 rounded-xl">
                <p className="text-xs font-bold text-amber-900 dark:text-amber-200">
                  Mandi Price Opportunity
                </p>
                <p className="text-[11px] text-amber-700 dark:text-amber-300 mt-0.5">
                  Cotton price up 4% in Navsari Mandi. Good time to hold stock.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

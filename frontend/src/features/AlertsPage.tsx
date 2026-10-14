import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  Bell,
  AlertTriangle,
  CloudRain,
  TrendingUp,
  Droplets,
  CheckCircle,
  Eye,
  Filter,
} from 'lucide-react';

interface AlertItem {
  id: string;
  type: 'weather' | 'pest' | 'price' | 'irrigation';
  severity: 'critical' | 'warning' | 'info';
  title: string;
  body: string;
  action: string;
  date: string;
  read: boolean;
}

export const AlertsPage: React.FC = () => {
  const { t } = useTranslation();

  const [alerts, setAlerts] = useState<AlertItem[]>([
    {
      id: 'alt-1',
      type: 'pest',
      severity: 'critical',
      title: 'Pink Bollworm Outbreak Cluster in Bardoli',
      body: '14 confirmed cases of Pectinophora gossypiella detected by farmers within 5km radius. Adult moths active at night.',
      action: 'Install 5 pheromone traps/acre immediately. Inspect rosette flowers and square bolls.',
      date: 'Today, 8:30 AM',
      read: false,
    },
    {
      id: 'alt-2',
      type: 'weather',
      severity: 'warning',
      title: 'Heat Stress Advisory (Forecast > 38°C)',
      body: 'Temperatures expected to exceed 38°C for the next 3 consecutive days with 0mm precipitation in Surat.',
      action: 'Ensure sufficient moisture in black cotton soil to prevent premature square shedding.',
      date: 'Today, 6:00 AM',
      read: false,
    },
    {
      id: 'alt-3',
      type: 'irrigation',
      severity: 'warning',
      title: 'ET0 Moisture Deficit Warning',
      body: 'Evapotranspiration deficit has reached 40mm. Drip line top-up required.',
      action: 'Run drip irrigation for 2.5 hours tomorrow morning between 6:00 AM and 8:30 AM.',
      date: 'Yesterday, 5:00 PM',
      read: true,
    },
    {
      id: 'alt-4',
      type: 'price',
      severity: 'info',
      title: 'Navsari Mandi Price Spike (+4.2%)',
      body: 'Modal rate for Shankar-6 cotton increased from ₹6,580 to ₹6,850/quintal due to high mill arrivals.',
      action: 'Hold stock for 7-10 days if dry storage available to capture peak ₹7,100 price.',
      date: '2 days ago',
      read: true,
    },
  ]);

  const [filterType, setFilterType] = useState<string>('all');

  const toggleRead = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: !a.read } : a))
    );
  };

  const markAllRead = () => {
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
  };

  const filtered = alerts.filter(
    (a) => filterType === 'all' || a.type === filterType
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 sm:py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white flex items-center space-x-2">
            <Bell className="w-7 h-7 text-emerald-600" />
            <span>Farm Alerts Centre (ચેતવણી કેન્દ્ર)</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
            Real-time agro-meteorological, pest epidemic, and mandi price alerts.
          </p>
        </div>

        <Button variant="outline" size="sm" onClick={markAllRead}>
          Mark All as Read
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex bg-slate-100 dark:bg-slate-800 rounded-xl p-1 gap-1 overflow-x-auto">
        {['all', 'pest', 'weather', 'irrigation', 'price'].map((type) => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${
              filterType === type
                ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 shadow-sm'
                : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filtered.map((alert) => (
          <Card
            key={alert.id}
            className={`border-l-4 transition-all ${
              alert.severity === 'critical'
                ? 'border-l-rose-600'
                : alert.severity === 'warning'
                ? 'border-l-amber-500'
                : 'border-l-sky-500'
            } ${!alert.read ? 'bg-emerald-50/20 dark:bg-emerald-950/10' : 'opacity-85'}`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center space-x-2">
                <Badge
                  variant={
                    alert.severity === 'critical'
                      ? 'danger'
                      : alert.severity === 'warning'
                      ? 'warning'
                      : 'info'
                  }
                  size="sm"
                >
                  {alert.severity.toUpperCase()}
                </Badge>
                <span className="text-xs font-semibold text-slate-400">{alert.date}</span>
                {!alert.read && (
                  <span className="w-2 h-2 rounded-full bg-emerald-600 animate-ping" />
                )}
              </div>

              <button
                onClick={() => toggleRead(alert.id)}
                className="text-xs text-slate-500 hover:text-emerald-600 font-medium transition-colors"
              >
                {alert.read ? 'Mark as Unread' : 'Mark as Read'}
              </button>
            </div>

            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">
              {alert.title}
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed mb-3">
              {alert.body}
            </p>

            <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl text-xs flex items-start space-x-2">
              <span className="font-bold text-emerald-600 shrink-0">Action:</span>
              <span className="text-slate-700 dark:text-slate-300 font-medium">
                {alert.action}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

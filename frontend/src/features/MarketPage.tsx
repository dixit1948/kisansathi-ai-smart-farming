import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import type { MarketPriceRecord } from '../api/client';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  TrendingUp,
  MapPin,
  Calendar,
  Sparkles,
  ArrowUpRight,
  Clock,
  ShieldCheck,
  Building,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const MarketPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedCrop, setSelectedCrop] = useState<'cotton' | 'groundnut' | 'wheat'>('cotton');
  const [priceData, setPriceData] = useState<MarketPriceRecord[]>([]);
  const [trendText, setTrendText] = useState('');
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await api.getMarketPrices(selectedCrop);
        if (!cancelled) {
          setPriceData(res.records);
          setTrendText(res.trend);
          setRecommendation(res.recommendation);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    fetchData();
    return () => { cancelled = true; };
  }, [selectedCrop]);

  const nearbyMandis = [
    { name: 'Navsari APMC', dist: '14 km', rate: '₹6,850/qtl', trend: '+4.2%' },
    { name: 'Surat Central Market', dist: '28 km', rate: '₹6,780/qtl', trend: '+2.8%' },
    { name: 'Bardoli Yard', dist: '6 km', rate: '₹6,720/qtl', trend: '+1.5%' },
    { name: 'Bharuch APMC', dist: '54 km', rate: '₹6,650/qtl', trend: '+0.8%' },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 sm:py-8 space-y-6">
      {/* Header & Crop Toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white flex items-center space-x-2">
            <TrendingUp className="w-7 h-7 text-emerald-600" />
            <span>{t('market.title')}</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
            {t('market.subtitle')}
          </p>
        </div>

        {/* Commodity Toggle */}
        <div className="flex bg-slate-100 dark:bg-slate-800 rounded-xl p-1 shrink-0">
          {[
            { id: 'cotton', label: 'Cotton (કપાસ)' },
            { id: 'groundnut', label: 'Groundnut (મગફળી)' },
            { id: 'wheat', label: 'Wheat (ઘઉં)' },
          ].map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedCrop(c.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                selectedCrop === c.id
                  ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {/* Intelligence Recommendation Card (Sell vs Hold) */}
      <Card className="border-l-4 border-l-emerald-600 bg-gradient-to-r from-emerald-50/50 to-white dark:from-emerald-950/20 dark:to-slate-900">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Badge variant="success" size="md">
                <Sparkles className="w-3.5 h-3.5 mr-1" />
                AI Timing: HOLD RECOMMENDATION
              </Badge>
              <span className="text-xs text-slate-500 font-semibold">{trendText}</span>
            </div>
            <p className="text-sm sm:text-base font-bold text-slate-900 dark:text-white">
              {recommendation}
            </p>
            <p className="text-xs text-slate-500">
              Source: Agmarknet APMC Navsari Time-Series Forecast (Sample Model)
            </p>
          </div>

          <div className="text-right shrink-0">
            <span className="text-xs text-slate-500 block">Today's Modal Rate</span>
            <span className="text-3xl font-black text-emerald-700 dark:text-emerald-400">
              ₹{priceData[priceData.length - 1]?.modal_price || 6850}
            </span>
            <span className="text-[11px] text-slate-400 block">per Quintal (100 kg)</span>
          </div>
        </div>
      </Card>

      {/* 30-Day Trend Chart */}
      <Card>
        <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-100 dark:border-slate-800">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            {t('market.last30Days')}
          </h3>
          <span className="text-xs text-emerald-600 font-semibold flex items-center">
            <ArrowUpRight className="w-3.5 h-3.5 mr-1" />
            +₹450 / qtl in last 30 days
          </span>
        </div>

        <div className="h-64 sm:h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={priceData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  borderRadius: '12px',
                  border: 'none',
                  color: '#fff',
                  fontSize: '12px',
                }}
              />
              <Line
                type="monotone"
                dataKey="modal_price"
                name="Modal Price (₹)"
                stroke="#16a34a"
                strokeWidth={3}
                dot={{ r: 3, fill: '#16a34a' }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="max_price"
                name="Max Price (₹)"
                stroke="#94a3b8"
                strokeDasharray="4 4"
                strokeWidth={1.5}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Nearby Mandi Rate Table */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center space-x-2">
            <Building className="w-4 h-4 text-emerald-600" />
            <span>Nearby APMC Mandi Rates</span>
          </h3>
          <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
            {nearbyMandis.map((m, i) => (
              <div key={i} className="py-2.5 flex items-center justify-between">
                <div>
                  <p className="font-bold text-slate-900 dark:text-white">{m.name}</p>
                  <span className="text-slate-400 text-[11px]">{m.dist} away</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-emerald-700 dark:text-emerald-400 block text-sm">
                    {m.rate}
                  </span>
                  <span className="text-[10px] text-emerald-600 font-semibold">{m.trend}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Cost Saving Tips */}
        <Card className="bg-slate-50/50 dark:bg-slate-900">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Market Selling Tips & Cost Savings</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-600 dark:text-slate-400">
            <li className="flex items-start space-x-2">
              <span className="font-bold text-emerald-600">•</span>
              <span>
                <strong>Moisture Deduction Guard:</strong> Ensure cotton moisture is under 8% before bringing to APMC yard to avoid trader moisture penalty cuts (₹150-200/qtl).
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="font-bold text-emerald-600">•</span>
              <span>
                <strong>Direct Ginning Mill Sale:</strong> Navsari Ginners offer a ₹50 premium on clean staple lengths without trash contamination.
              </span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="font-bold text-emerald-600">•</span>
              <span>
                <strong>e-NAM Integration:</strong> You can place a limit order on e-NAM to lock in ₹7,000 threshold without paying broker commissions.
              </span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

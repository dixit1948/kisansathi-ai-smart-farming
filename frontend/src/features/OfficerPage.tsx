import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  ShieldAlert,
  MapPin,
  Download,
  Send,
  Users,
  AlertTriangle,
  Building,
  Filter,
  CheckCircle,
  ExternalLink,
} from 'lucide-react';

export const OfficerPage: React.FC = () => {
  const { t } = useTranslation();

  const [selectedCrop, setSelectedCrop] = useState('all');
  const [selectedDistrict, setSelectedDistrict] = useState('Surat');
  const [advisorySent, setAdvisorySent] = useState(false);

  const stats = [
    { label: 'Registered Farms', value: '124', icon: Users, color: 'text-emerald-600' },
    { label: 'Total Area Under Watch', value: '412 ha', icon: Building, color: 'text-sky-600' },
    { label: 'Active Outbreak Clusters', value: '2', icon: AlertTriangle, color: 'text-rose-600' },
    { label: 'Diagnosis Precision', value: '91.4%', icon: CheckCircle, color: 'text-purple-600' },
  ];

  const clusters = [
    {
      id: 'cl-1',
      name: 'Bardoli Cotton Outbreak Cluster',
      taluka: 'Bardoli',
      district: 'Surat',
      crop: 'Cotton',
      lat: 21.12,
      lon: 73.11,
      pathogen: 'Pink Bollworm & Leaf Curl Virus',
      cases: 14,
      affectedFarmers: 8,
      severity: 'critical' as const,
      riskLevel: 'High Epidemiological Spread',
    },
    {
      id: 'cl-2',
      name: 'Navsari Groundnut Cluster',
      taluka: 'Navsari',
      district: 'Navsari',
      crop: 'Groundnut',
      lat: 20.95,
      lon: 72.95,
      pathogen: 'Tikka Early Leaf Spot (Cercospora)',
      cases: 8,
      affectedFarmers: 5,
      severity: 'warning' as const,
      riskLevel: 'Moderate Humidity Spread',
    },
  ];

  const handleDispatch = () => {
    setAdvisorySent(true);
    setTimeout(() => setAdvisorySent(false), 4000);
  };

  const handleExportCSV = () => {
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      'Cluster ID,Name,District,Taluka,Crop,Pathogen,Detected Cases,Farmers Affected,Severity\n' +
      'cl-1,Bardoli Cotton Cluster,Surat,Bardoli,Cotton,Pink Bollworm & Leaf Curl,14,8,CRITICAL\n' +
      'cl-2,Navsari Groundnut Cluster,Navsari,Navsari,Groundnut,Tikka Leaf Spot,8,5,WARNING\n';
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'KisanSathi_Epidemiological_Report.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 sm:py-8 space-y-6">
      {/* Officer Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-purple-700 dark:text-purple-400 mb-1">
            <span>🏛️ Krishi Vigyan Kendra (KVK) Extension Command</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
            {t('officer.title')}
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
            {t('officer.subtitle')} • South Gujarat Agro-Climatic Zone
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            size="md"
            onClick={handleExportCSV}
            leftIcon={<Download className="w-4 h-4" />}
          >
            {t('officer.exportCSV')}
          </Button>
          <Button
            variant="primary"
            size="md"
            onClick={handleDispatch}
            leftIcon={<Send className="w-4 h-4" />}
          >
            {advisorySent ? 'Advisory Dispatched!' : t('officer.dispatchAdvisory')}
          </Button>
        </div>
      </div>

      {/* Metric Tiles */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {stats.map((st, i) => (
          <Card key={i} className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-500">{st.label}</span>
              <st.icon className={`w-4 h-4 ${st.color}`} />
            </div>
            <span className="text-2xl font-black text-slate-900 dark:text-white">
              {st.value}
            </span>
          </Card>
        ))}
      </div>

      {/* Map & Cluster Surveillance Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Map Visualizer */}
        <Card className="lg:col-span-2 p-0 overflow-hidden flex flex-col">
          <div className="p-4 bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-bold text-slate-900 dark:text-white">
                Geospatial Outbreak Heatmap (Surat • Navsari • Bharuch)
              </span>
            </div>
            <span className="text-[11px] text-slate-500 font-semibold">Live Leaf Scans</span>
          </div>

          {/* Map canvas container */}
          <div className="h-80 sm:h-96 bg-slate-900 relative flex items-center justify-center p-6 text-center overflow-hidden">
            {/* Simulated Satellite Grid Canvas */}
            <div
              className="absolute inset-0 opacity-20"
              style={{
                backgroundImage:
                  'radial-gradient(#22c55e 1px, transparent 1px), radial-gradient(#22c55e 1px, #0f172a 1px)',
                backgroundSize: '24px 24px',
              }}
            />

            {/* Simulated Outbreak Pin 1 (Bardoli Cluster - Red) */}
            <div className="absolute left-[52%] top-[48%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center group cursor-pointer">
              <div className="w-12 h-12 rounded-full bg-rose-500/20 border-2 border-rose-500 animate-ping absolute" />
              <div className="w-6 h-6 rounded-full bg-rose-600 text-white font-bold text-[10px] flex items-center justify-center shadow-lg shadow-rose-600/50 z-10">
                14
              </div>
              <div className="mt-1 px-2 py-0.5 bg-slate-900/90 text-white text-[10px] font-bold rounded shadow-md border border-rose-500/50 whitespace-nowrap z-10">
                🔴 Bardoli: Pink Bollworm (14 cases)
              </div>
            </div>

            {/* Simulated Outbreak Pin 2 (Navsari Cluster - Amber) */}
            <div className="absolute left-[38%] top-[65%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center group cursor-pointer">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-500 animate-ping absolute" />
              <div className="w-5 h-5 rounded-full bg-amber-500 text-white font-bold text-[10px] flex items-center justify-center shadow-lg shadow-amber-500/50 z-10">
                8
              </div>
              <div className="mt-1 px-2 py-0.5 bg-slate-900/90 text-white text-[10px] font-bold rounded shadow-md border border-amber-500/50 whitespace-nowrap z-10">
                🟡 Navsari: Groundnut Tikka (8 cases)
              </div>
            </div>

            {/* Simulated Healthy Cluster (Ankleshwar) */}
            <div className="absolute left-[70%] top-[30%] -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
              <div className="w-4 h-4 rounded-full bg-emerald-500 text-white font-bold text-[9px] flex items-center justify-center shadow z-10">
                ✓
              </div>
              <div className="mt-1 px-1.5 py-0.5 bg-slate-900/90 text-emerald-300 text-[9px] rounded z-10">
                Bharuch: Normal
              </div>
            </div>

            <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-700 px-3 py-1.5 rounded-lg text-left z-20 text-[10px] text-slate-300">
              <span className="font-bold text-white block">Epidemiological Map Legend:</span>
              <span className="text-rose-400">🔴 High Risk (&gt;10 detections)</span> •{' '}
              <span className="text-amber-400">🟡 Moderate (&gt;5 detections)</span> •{' '}
              <span className="text-emerald-400">🟢 Normal</span>
            </div>
          </div>
        </Card>

        {/* Live Cluster Triage Column */}
        <div className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Detected Outbreak Clusters
          </h3>

          {clusters.map((cl) => (
            <Card
              key={cl.id}
              className={`border-l-4 ${
                cl.severity === 'critical' ? 'border-l-rose-600' : 'border-l-amber-500'
              } p-4`}
            >
              <div className="flex justify-between items-start mb-2">
                <Badge variant={cl.severity === 'critical' ? 'danger' : 'warning'} size="sm">
                  {cl.severity.toUpperCase()}
                </Badge>
                <span className="text-[11px] font-bold text-slate-400">{cl.crop}</span>
              </div>

              <h4 className="text-sm font-bold text-slate-900 dark:text-white mb-1">
                {cl.name}
              </h4>
              <p className="text-xs text-rose-600 dark:text-rose-400 font-semibold mb-2">
                Pathogen: {cl.pathogen}
              </p>

              <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-400 mb-3 pt-2 border-t border-slate-100 dark:border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[10px]">Diagnosed Cases:</span>
                  <span className="font-bold text-slate-900 dark:text-white">{cl.cases}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Farmers Affected:</span>
                  <span className="font-bold text-slate-900 dark:text-white">
                    {cl.affectedFarmers}
                  </span>
                </div>
              </div>

              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs"
                onClick={handleDispatch}
                leftIcon={<Send className="w-3.5 h-3.5" />}
              >
                Dispatch Advisory to {cl.taluka}
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

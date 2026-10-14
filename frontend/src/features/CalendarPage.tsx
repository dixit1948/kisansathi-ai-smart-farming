import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  Calendar as CalendarIcon,
  CheckCircle2,
  Clock,
  CloudRain,
  Sprout,
  AlertCircle,
  SunMedium,
} from 'lucide-react';

export const CalendarPage: React.FC = () => {
  const { t } = useTranslation();

  const stages = [
    {
      stage: 'Sowing & Germination (બિજ વાવણી)',
      days: 'Days 1 - 15',
      date: '15 June - 30 June',
      status: 'completed' as const,
      tasks: [
        'Seed treatment with Imidacloprid (5g/kg seed) to prevent early sucking pests',
        'Basal dose fertilizer: 20kg DAP + 15kg MOP per acre',
      ],
      weatherNote: '22mm Monsoon shower received (Optimum moisture)',
    },
    {
      stage: 'Vegetative Growth (વનસ્પતિક વૃદ્ધિ - Current)',
      days: 'Days 16 - 55',
      date: '1 July - 10 August',
      status: 'current' as const,
      tasks: [
        'Weeding and interculturing at 25 and 45 DAS',
        'Apply 1st split Urea top dressing (30kg/acre)',
        'Erect yellow sticky cards for whitefly monitoring',
      ],
      weatherNote: 'Dry spell expected next 4 days; run drip line 2 hrs',
    },
    {
      stage: 'Square & Flowering (ચાંપવા અને ફૂલ અવસ્થા)',
      days: 'Days 56 - 90',
      date: '11 August - 15 September',
      status: 'upcoming' as const,
      tasks: [
        'Apply 2nd split Nitrogen + Micronutrient spray (19:19:19 @ 1%)',
        'Install 5 Pheromone traps per acre for Pink Bollworm monitoring',
      ],
      weatherNote: 'High heat forecast; avoid moisture stress to prevent square shedding',
    },
    {
      stage: 'Boll Formation & Maturity (જીંડવા વિકાસ)',
      days: 'Days 91 - 130',
      date: '16 September - 25 October',
      status: 'upcoming' as const,
      tasks: [
        'Foliar spray of 2% DAP or Potassium Nitrate for boll weight',
        'Maintain optimum soil moisture; do not water-log',
      ],
      weatherNote: 'Retreating monsoon showers monitored',
    },
    {
      stage: 'Picking & Harvest (વીણી અને કાપણી)',
      days: 'Days 131 - 160',
      date: '26 October - 25 November',
      status: 'upcoming' as const,
      tasks: [
        'First picking when 50% bolls are fully opened in bright sunlight',
        'Store seed cotton at <8% moisture to prevent yellowing',
      ],
      weatherNote: 'Clear skies required for clean lint quality',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 sm:py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white flex items-center space-x-2">
          <CalendarIcon className="w-7 h-7 text-emerald-600" />
          <span>Crop Calendar (પાક સમયપત્રક)</span>
        </h1>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
          Kharif Season • Cotton (Gossypium hirsutum) • Sown 15 June 2024 (Bardoli, Surat)
        </p>
      </div>

      {/* Progress Summary Card */}
      <Card className="bg-gradient-to-r from-emerald-800 to-emerald-700 text-white p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-200 block mb-1">
              Active Stage Progress
            </span>
            <h2 className="text-xl font-black">Vegetative Stage (Day 45 of 160)</h2>
            <p className="text-xs text-emerald-100 mt-1">
              Estimated Harvest Window: 25 Oct - 15 Nov 2024
            </p>
          </div>
          <div className="text-right shrink-0">
            <span className="text-3xl font-black">28%</span>
            <span className="text-xs text-emerald-200 block">Season Complete</span>
          </div>
        </div>
        <div className="w-full bg-emerald-950/60 h-2 rounded-full overflow-hidden mt-4">
          <div className="bg-emerald-400 h-full rounded-full" style={{ width: '28%' }} />
        </div>
      </Card>

      {/* Timeline Stages */}
      <div className="relative border-l-2 border-slate-200 dark:border-slate-800 ml-4 pl-6 space-y-8">
        {stages.map((stg, i) => (
          <div key={i} className="relative group">
            {/* Timeline bullet icon */}
            <div
              className={`absolute -left-[35px] top-1.5 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 ${
                stg.status === 'completed'
                  ? 'bg-emerald-600 border-emerald-600 text-white'
                  : stg.status === 'current'
                  ? 'bg-amber-500 border-amber-500 text-white animate-pulse'
                  : 'bg-white dark:bg-slate-900 border-slate-300 dark:border-slate-700 text-slate-400'
              }`}
            >
              {stg.status === 'completed' ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : stg.status === 'current' ? (
                <Clock className="w-4 h-4" />
              ) : (
                i + 1
              )}
            </div>

            <Card
              className={`${
                stg.status === 'current'
                  ? 'ring-2 ring-emerald-500 border-transparent shadow-md'
                  : ''
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3 pb-2 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <span className="text-[11px] font-semibold text-slate-400 block">{stg.days} • {stg.date}</span>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    {stg.stage}
                  </h3>
                </div>

                <Badge
                  variant={
                    stg.status === 'completed'
                      ? 'success'
                      : stg.status === 'current'
                      ? 'warning'
                      : 'neutral'
                  }
                  size="sm"
                >
                  {stg.status === 'completed'
                    ? 'Completed'
                    : stg.status === 'current'
                    ? 'In Progress'
                    : 'Upcoming'}
                </Badge>
              </div>

              {/* Tasks */}
              <div className="space-y-1.5 mb-3">
                <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400 block">
                  Prescribed Field Practices (ICAR-CICR)
                </span>
                {stg.tasks.map((task, tIdx) => (
                  <div key={tIdx} className="flex items-start space-x-2 text-xs text-slate-700 dark:text-slate-300">
                    <span className="text-emerald-600 font-bold">•</span>
                    <span>{task}</span>
                  </div>
                ))}
              </div>

              {/* Weather Overlay */}
              <div className="p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl flex items-center space-x-2 text-xs text-slate-600 dark:text-slate-300">
                <SunMedium className="w-4 h-4 text-amber-500 shrink-0" />
                <span>
                  <strong>Weather Heuristic:</strong> {stg.weatherNote}
                </span>
              </div>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
};

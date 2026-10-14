import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MapPin, Globe, Sprout, Droplets, Check, ArrowRight, ArrowLeft } from 'lucide-react';

export const OnboardingWizard: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { setLanguage } = useAuthStore();
  const { addToast } = useUIStore();

  const [step, setStep] = useState(1);
  const [selectedLang, setSelectedLang] = useState<'gu' | 'hi' | 'en'>('gu');
  const [district, setDistrict] = useState('Surat');
  const [taluka, setTaluka] = useState('Bardoli');
  const [selectedCrop, setSelectedCrop] = useState('cotton');
  const [landArea, setLandArea] = useState('3.5');
  const [soilType, setSoilType] = useState('black');
  const [irrigationType, setIrrigationType] = useState('drip');

  const handleLangSelect = (l: 'gu' | 'hi' | 'en') => {
    setSelectedLang(l);
    i18n.changeLanguage(l);
    setLanguage(l);
  };

  const handleFinish = () => {
    addToast('success', 'Farm profile successfully established!');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] max-w-2xl mx-auto px-4 py-8">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400">
            Step {step} of 4
          </span>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-xs text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 underline"
          >
            {t('onboarding.skip')}
          </button>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
          <div
            className="bg-emerald-600 h-full transition-all duration-300 ease-out"
            style={{ width: `${(step / 4) * 100}%` }}
          />
        </div>
      </div>

      <Card className="shadow-lg">
        {/* Step 1: Language Selection */}
        {step === 1 && (
          <div>
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 rounded-2xl flex items-center justify-center mx-auto mb-2">
                <Globe className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {t('onboarding.step1')} / ભાષા પસંદ કરો
              </h2>
              <p className="text-xs text-slate-500">KisanSathi will provide all advisories in this language.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { code: 'gu', label: 'ગુજરાતી', sub: 'Gujarati' },
                { code: 'hi', label: 'हिंदी', sub: 'Hindi' },
                { code: 'en', label: 'English', sub: 'Global' },
              ].map((item) => (
                <button
                  key={item.code}
                  type="button"
                  onClick={() => handleLangSelect(item.code as any)}
                  className={`p-4 rounded-xl border-2 text-center transition-all ${
                    selectedLang === item.code
                      ? 'border-emerald-600 bg-emerald-50/50 dark:bg-emerald-950/40 text-emerald-900 dark:text-white shadow-sm'
                      : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
                  }`}
                >
                  <p className="text-lg font-bold">{item.label}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{item.sub}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Location */}
        {step === 2 && (
          <div>
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 rounded-2xl flex items-center justify-center mx-auto mb-2">
                <MapPin className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {t('onboarding.step2')} / ખેતરનું સ્થળ
              </h2>
              <p className="text-xs text-slate-500">Used for hyper-local Open-Meteo weather and mandi prices.</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  District (જિલ્લો)
                </label>
                <select
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
                >
                  <option value="Surat">Surat (સુરત)</option>
                  <option value="Navsari">Navsari (નવસારી)</option>
                  <option value="Bharuch">Bharuch (ભરૂચ)</option>
                  <option value="Junagadh">Junagadh (જૂનાગઢ)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Taluka / Village (તાલુકો / ગામ)
                </label>
                <input
                  type="text"
                  value={taluka}
                  onChange={(e) => setTaluka(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
                  placeholder="e.g. Bardoli"
                />
              </div>

              <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center space-x-3 text-xs text-slate-600 dark:text-slate-300">
                <MapPin className="w-5 h-5 text-emerald-600 shrink-0" />
                <span>Pinned Location: 21.12° N, 73.11° E (Bardoli Agro-Climatic Zone)</span>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Crops & Land Size */}
        {step === 3 && (
          <div>
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 rounded-2xl flex items-center justify-center mx-auto mb-2">
                <Sprout className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {t('onboarding.step3')} / મુખ્ય પાક
              </h2>
              <p className="text-xs text-slate-500">Select what you cultivate this season.</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                  Primary Crop (મુખ્ય પાક)
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[
                    { id: 'cotton', name: 'Cotton (કપાસ)', icon: '☁️' },
                    { id: 'groundnut', name: 'Groundnut (મગફળી)', icon: '🥜' },
                    { id: 'wheat', name: 'Wheat (ઘઉં)', icon: '🌾' },
                    { id: 'sugarcane', name: 'Sugarcane (શેરડી)', icon: '🎋' },
                    { id: 'rice', name: 'Rice (ડાંગર)', icon: '🍚' },
                  ].map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setSelectedCrop(c.id)}
                      className={`p-3 rounded-xl border-2 text-left transition-all ${
                        selectedCrop === c.id
                          ? 'border-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-white'
                          : 'border-slate-200 dark:border-slate-800'
                      }`}
                    >
                      <span className="text-xl block mb-1">{c.icon}</span>
                      <span className="text-xs font-bold block">{c.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Farm Size in Hectares (જમીન ક્ષેત્રફળ)
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={landArea}
                  onChange={(e) => setLandArea(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
                  placeholder="3.5"
                />
              </div>
            </div>
          </div>
        )}

        {/* Step 4: Soil & Irrigation */}
        {step === 4 && (
          <div>
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 rounded-2xl flex items-center justify-center mx-auto mb-2">
                <Droplets className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                {t('onboarding.step4')} / માટી અને પિયત પદ્ધતિ
              </h2>
              <p className="text-xs text-slate-500">Fine-tunes Penman-Monteith ET0 irrigation schedules.</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Soil Type (જમીનનો પ્રકાર)
                </label>
                <select
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
                >
                  <option value="black">Black Cotton Soil (કાળી માટી - High retention)</option>
                  <option value="loam">Loam / Goradu Soil (ગોરાડુ માટી)</option>
                  <option value="clay">Clay Soil (ચીકણી માટી)</option>
                  <option value="sandy">Sandy Loam (રેતાળ માટી)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Irrigation Source (પિયત વ્યવસ્થા)
                </label>
                <select
                  value={irrigationType}
                  onChange={(e) => setIrrigationType(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm"
                >
                  <option value="drip">Drip Irrigation (ટપક પદ્ધતિ - Highly Efficient)</option>
                  <option value="sprinkler">Sprinkler (ફુવારા પદ્ધતિ)</option>
                  <option value="canal">Canal / Flood (નહેર / ધોરિયા પદ્ધતિ)</option>
                  <option value="rainfed">Rainfed (વરસાદ આધારિત)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Wizard Controls */}
        <div className="mt-8 flex justify-between items-center pt-4 border-t border-slate-100 dark:border-slate-800">
          {step > 1 ? (
            <Button
              variant="outline"
              size="md"
              onClick={() => setStep(step - 1)}
              leftIcon={<ArrowLeft className="w-4 h-4" />}
            >
              Previous
            </Button>
          ) : <div />}

          {step < 4 ? (
            <Button
              variant="primary"
              size="md"
              onClick={() => setStep(step + 1)}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Continue
            </Button>
          ) : (
            <Button
              variant="primary"
              size="md"
              onClick={handleFinish}
              rightIcon={<Check className="w-4 h-4" />}
            >
              {t('onboarding.complete')}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
};

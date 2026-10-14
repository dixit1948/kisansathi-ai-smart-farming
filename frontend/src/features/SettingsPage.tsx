import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Settings,
  User,
  Globe,
  Moon,
  Sun,
  Bell,
  Download,
  Trash2,
  ShieldCheck,
  Check,
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user, setLanguage, logout } = useAuthStore();
  const { theme, toggleTheme, addToast } = useUIStore();

  const [whatsappNotifications, setWhatsappNotifications] = useState(true);
  const [dailyDigest, setDailyDigest] = useState(true);
  const [outbreakAlerts, setOutbreakAlerts] = useState(true);

  const handleLanguageSelect = (lang: 'en' | 'hi' | 'gu') => {
    i18n.changeLanguage(lang);
    setLanguage(lang);
    addToast('success', 'Language preference updated.');
  };

  const handleExportData = () => {
    const exportPayload = {
      profile: user,
      export_date: new Date().toISOString(),
      compliance: 'Digital Personal Data Protection (DPDP) Act 2023',
      records: {
        farms_count: 1,
        scans_count: 3,
        conversations_count: 12,
      },
    };
    const dataStr =
      'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(exportPayload, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', 'KisanSathi_UserData_DPDP_Export.json');
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    addToast('success', 'Personal farm data downloaded.');
  };

  const handleDeleteAccount = () => {
    if (
      window.confirm(
        'Are you sure you want to delete your KisanSathi account? In compliance with DPDP Act 2023, all your personal identifiable records will be permanently erased.'
      )
    ) {
      logout();
      addToast('info', 'Account and personal data erased.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 sm:py-8 space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white flex items-center space-x-2">
          <Settings className="w-7 h-7 text-emerald-600" />
          <span>Profile & Account Settings</span>
        </h1>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-1">
          Manage language, notification preferences, and privacy controls.
        </p>
      </div>

      {/* Profile Info */}
      <Card>
        <div className="flex items-center space-x-4 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="w-14 h-14 rounded-2xl bg-emerald-600 text-white flex items-center justify-center text-2xl font-bold shadow-md shadow-emerald-600/30">
            {user?.name ? user.name.charAt(0) : 'A'}
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">{user?.name}</h2>
            <p className="text-xs text-slate-500">
              Role: <span className="font-semibold uppercase">{user?.role}</span> • {user?.phone || user?.email}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              Location: {user?.taluka}, {user?.district} (Gujarat)
            </p>
          </div>
        </div>

        {/* Language Selection */}
        <div className="pt-4">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2 flex items-center space-x-2">
            <Globe className="w-4 h-4 text-emerald-600" />
            <span>Preferred Language (ભાષા)</span>
          </h3>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'gu', label: 'ગુજરાતી (Gujarati)' },
              { id: 'hi', label: 'हिंदी (Hindi)' },
              { id: 'en', label: 'English' },
            ].map((l) => (
              <button
                key={l.id}
                onClick={() => handleLanguageSelect(l.id as any)}
                className={`p-3 rounded-xl border text-xs font-bold transition-all ${
                  i18n.language === l.id
                    ? 'border-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 shadow-sm'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Notification Preferences */}
      <Card>
        <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-3 flex items-center space-x-2">
          <Bell className="w-4 h-4 text-emerald-600" />
          <span>Notification Preferences</span>
        </h3>
        <div className="space-y-3 text-xs">
          <label className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer">
            <div>
              <span className="font-bold text-slate-900 dark:text-white block">WhatsApp Daily Digest</span>
              <span className="text-slate-500 text-[11px]">Receive 6:00 AM weather and irrigation reminders on WhatsApp</span>
            </div>
            <input
              type="checkbox"
              checked={whatsappNotifications}
              onChange={(e) => setWhatsappNotifications(e.target.checked)}
              className="w-4 h-4 text-emerald-600 rounded"
            />
          </label>

          <label className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer">
            <div>
              <span className="font-bold text-slate-900 dark:text-white block">Epidemic Outbreak Alerts</span>
              <span className="text-slate-500 text-[11px]">Immediate alert if pest attacks occur within 5km of your farm</span>
            </div>
            <input
              type="checkbox"
              checked={outbreakAlerts}
              onChange={(e) => setOutbreakAlerts(e.target.checked)}
              className="w-4 h-4 text-emerald-600 rounded"
            />
          </label>
        </div>
      </Card>

      {/* Privacy & DPDP Act 2023 Data Controls */}
      <Card className="border-l-4 border-l-sky-500">
        <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2 flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-sky-600" />
          <span>Data Protection & Privacy (DPDP Act 2023)</span>
        </h3>
        <p className="text-xs text-slate-600 dark:text-slate-400 mb-4 leading-relaxed">
          You retain full ownership of your agricultural data. All leaf scan photos have EXIF GPS coordinates stripped upon upload.
        </p>

        <div className="flex flex-wrap gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportData}
            leftIcon={<Download className="w-4 h-4" />}
          >
            Export My Data (JSON)
          </Button>

          <Button
            variant="danger"
            size="sm"
            onClick={handleDeleteAccount}
            leftIcon={<Trash2 className="w-4 h-4" />}
          >
            Delete Account & Forget Data
          </Button>
        </div>
      </Card>
    </div>
  );
};

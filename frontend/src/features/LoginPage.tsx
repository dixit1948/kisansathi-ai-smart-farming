import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Phone, Mail, ArrowRight, ShieldCheck, KeyRound } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const { addToast } = useUIStore();

  const [mode, setMode] = useState<'phone' | 'email'>('phone');
  const [phone, setPhone] = useState('+919876543210');
  const [email, setEmail] = useState('officer@kvk.gov.in');
  const [password, setPassword] = useState('Demo@1234');
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('123456');

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    setOtpSent(true);
    addToast('success', 'Demo OTP sent: 123456');
  };

  const handleVerifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    login('mock-jwt-farmer-token', {
      id: 'f1a9b2c3-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
      phone,
      name: 'Arjun Bhai Patel',
      role: 'farmer',
      language: 'gu',
      district: 'Surat',
      taluka: 'Bardoli',
    });
    addToast('success', 'Welcome back, Arjun Bhai!');
    navigate('/dashboard');
  };

  const handleEmailLogin = (e: React.FormEvent) => {
    e.preventDefault();
    login('mock-jwt-officer-token', {
      id: '0f1e2d3c-4b5a-6f7e-8d9c-1a2b3c4d5e6f',
      email,
      name: 'Ramesh Patel (KVK Scientist)',
      role: 'officer',
      language: 'en',
      district: 'Surat',
      taluka: 'Olpad',
    });
    addToast('success', 'Extension Officer access granted.');
    navigate('/officer');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl border-slate-200 dark:border-slate-800">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 rounded-2xl flex items-center justify-center mx-auto mb-3 text-2xl">
            🌾
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Sign In to KisanSathi</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Access your personalized smart advisory portal
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex bg-slate-100 dark:bg-slate-800 rounded-xl p-1 mb-6">
          <button
            onClick={() => setMode('phone')}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === 'phone'
                ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 shadow-sm'
                : 'text-slate-500'
            }`}
          >
            Farmer (Phone OTP)
          </button>
          <button
            onClick={() => setMode('email')}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              mode === 'email'
                ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 shadow-sm'
                : 'text-slate-500'
            }`}
          >
            Officer / Admin (Email)
          </button>
        </div>

        {mode === 'phone' ? (
          !otpSent ? (
            <form onSubmit={handleSendOtp} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Mobile Number (મોબાઇલ નંબર)
                </label>
                <div className="relative">
                  <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                    placeholder="+91 98765 43210"
                  />
                </div>
              </div>
              <Button type="submit" size="md" className="w-full" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Send Login OTP
              </Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Enter 6-Digit OTP (ઓટીપી દાખલ કરો)
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                  <input
                    type="text"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    required
                    maxLength={6}
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl text-sm tracking-widest text-center font-bold focus:ring-2 focus:ring-emerald-500 outline-none"
                    placeholder="123456"
                  />
                </div>
                <p className="text-[11px] text-emerald-600 dark:text-emerald-400 mt-1">
                  Demo hint: Use default OTP 123456
                </p>
              </div>
              <Button type="submit" size="md" className="w-full">
                Verify & Enter Farm
              </Button>
            </form>
          )
        ) : (
          <form onSubmit={handleEmailLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Gov / KVK Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
              />
            </div>
            <Button type="submit" size="md" className="w-full">
              Sign In as Officer
            </Button>
          </form>
        )}

        <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 text-center">
          <button
            onClick={() => navigate('/onboarding')}
            className="text-xs font-medium text-emerald-600 hover:text-emerald-700 dark:text-emerald-400"
          >
            First time farmer? Start 4-step onboarding wizard →
          </button>
        </div>
      </Card>
    </div>
  );
};

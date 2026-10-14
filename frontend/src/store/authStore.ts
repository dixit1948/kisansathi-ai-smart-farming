import { create } from 'zustand';

export interface User {
  id: string;
  phone?: string;
  email?: string;
  name: string;
  role: 'farmer' | 'officer' | 'admin';
  language: 'en' | 'hi' | 'gu';
  district?: string;
  taluka?: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setLanguage: (lang: 'en' | 'hi' | 'gu') => void;
  switchRole: (role: 'farmer' | 'officer' | 'admin') => void;
}

const DEMO_FARMER: User = {
  id: 'f1a9b2c3-4d5e-6f7a-8b9c-0d1e2f3a4b5c',
  phone: '+919876543210',
  name: 'Arjun Bhai Patel',
  role: 'farmer',
  language: 'gu',
  district: 'Surat',
  taluka: 'Bardoli',
};

const DEMO_OFFICER: User = {
  id: '0f1e2d3c-4b5a-6f7e-8d9c-1a2b3c4d5e6f',
  email: 'officer@kvk.gov.in',
  name: 'Ramesh Patel (KVK Scientist)',
  role: 'officer',
  language: 'en',
  district: 'Surat',
  taluka: 'Olpad',
};

export const useAuthStore = create<AuthState>((set) => ({
  token: 'mock-jwt-token-kisansathi',
  user: DEMO_FARMER,
  isAuthenticated: true,
  login: (token, user) => set({ token, user, isAuthenticated: true }),
  logout: () => set({ token: null, user: null, isAuthenticated: false }),
  setLanguage: (lang) =>
    set((state) => ({
      user: state.user ? { ...state.user, language: lang } : null,
    })),
  switchRole: (role) =>
    set(() => ({
      user: role === 'officer' ? DEMO_OFFICER : DEMO_FARMER,
    })),
}));

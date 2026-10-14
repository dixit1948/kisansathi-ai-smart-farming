/**
 * Typed KisanSathi API Client with automated mock fallbacks
 */

export interface WeatherData {
  location: string;
  max_temp: number;
  min_temp: number;
  humidity: number;
  wind_kmh: number;
  rainfall_mm: number;
  irrigation_needed_mm: number;
  et0_deficit_mm: number;
  spray_window: string;
  is_spray_safe: boolean;
  forecast_7d: Array<{
    date: string;
    day: string;
    max_temp: number;
    min_temp: number;
    rain_mm: number;
    wind_kmh: number;
  }>;
}

export interface DiseaseScanResult {
  id: string;
  predicted_label: string;
  confidence: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  treatment_organic: string[];
  treatment_chemical: string[];
  prevention_tips: string[];
  sources: Array<{ title: string; section?: string; page?: string }>;
  image_url: string;
  created_at: string;
  is_mock?: boolean;
}

export interface MarketPriceRecord {
  date: string;
  mandi: string;
  crop: string;
  min_price: number;
  modal_price: number;
  max_price: number;
}

export interface ChatResponse {
  answer: string;
  intent: string;
  language: string;
  agents_used: string[];
  all_sources: Array<{ title: string; section?: string; page?: string }>;
  total_latency_ms: number;
  is_mock: boolean;
  trace_id: string;
}

export interface FarmOverviewData {
  farmer_name: string;
  district: string;
  crop_name: string;
  crop_stage: string;
  sowing_date: string;
  task_of_day: {
    title: string;
    description: string;
    completed: boolean;
  };
  weather: WeatherData;
  active_alerts_count: number;
}

const API_BASE = '/api/v1';

export const api = {
  // Farm Overview
  async getOverview(): Promise<FarmOverviewData> {
    try {
      const res = await fetch(`${API_BASE}/farms/overview`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback to deterministic mock
    }
    return {
      farmer_name: 'Arjun Bhai Patel',
      district: 'Bardoli, Surat',
      crop_name: 'Cotton (કપાસ)',
      crop_stage: 'Vegetative (Day 45)',
      sowing_date: '15 June 2024',
      task_of_day: {
        title: 'Apply 1st Split Urea (30 kg/acre)',
        description: 'Vegetative peak stage requires nitrogen top-dressing. Water within 24 hours of application.',
        completed: false,
      },
      weather: {
        location: 'Bardoli, Surat (Gujarat)',
        max_temp: 36,
        min_temp: 25,
        humidity: 68,
        wind_kmh: 11,
        rainfall_mm: 0,
        irrigation_needed_mm: 40,
        et0_deficit_mm: 38,
        spray_window: 'Safe spray window: Today 4:00 PM – 7:00 PM (Wind < 12 km/h)',
        is_spray_safe: true,
        forecast_7d: [
          { date: 'Today', day: 'Mon', max_temp: 36, min_temp: 25, rain_mm: 0, wind_kmh: 11 },
          { date: 'Tue', day: 'Tue', max_temp: 37, min_temp: 26, rain_mm: 0, wind_kmh: 14 },
          { date: 'Wed', day: 'Wed', max_temp: 35, min_temp: 24, rain_mm: 8, wind_kmh: 18 },
          { date: 'Thu', day: 'Thu', max_temp: 34, min_temp: 24, rain_mm: 12, wind_kmh: 10 },
          { date: 'Fri', day: 'Fri', max_temp: 35, min_temp: 25, rain_mm: 2, wind_kmh: 9 },
          { date: 'Sat', day: 'Sat', max_temp: 38, min_temp: 26, rain_mm: 0, wind_kmh: 12 },
          { date: 'Sun', day: 'Sun', max_temp: 38, min_temp: 27, rain_mm: 0, wind_kmh: 13 },
        ],
      },
      active_alerts_count: 2,
    };
  },

  // Multi-Agent Chat
  async sendChatMessage(message: string, language: string = 'en'): Promise<ChatResponse> {
    try {
      const res = await fetch(`${API_BASE}/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, language, crop: 'cotton' }),
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return {
      answer: `🌱 **KisanSathi AI (IBM Granite):**\n\nFor cotton in Gujarat at vegetative stage:\n• Nitrogen split: Apply 30kg urea/acre now before evening irrigation.\n• Pest alert: Pheromone traps show mild whitefly activity. Spray 5% neem oil if nymph count > 5 per leaf.\n• Water guidance: Next 48 hours show 0mm rain. Run drip lines for 2.5 hours tomorrow morning.`,
      intent: 'advisory',
      language,
      agents_used: ['crop_advisory', 'weather_irrigation'],
      all_sources: [
        { title: 'ICAR-CICR Cotton Cultivation Guidelines', section: 'Fertilizer Management', page: '14' },
        { title: 'Open-Meteo Surat Agro-Meteorological Station', section: '7-Day ET0' }
      ],
      total_latency_ms: 138,
      is_mock: true,
      trace_id: 'trc-' + Math.random().toString(36).substring(2, 9),
    };
  },

  // Disease Scan Upload
  async uploadScan(file: File | Blob): Promise<DiseaseScanResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('crop', 'cotton');
      const res = await fetch(`${API_BASE}/scan/upload`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    return {
      id: 'scn-' + Math.random().toString(36).substring(2, 9),
      predicted_label: 'Cotton Leaf Curl Virus (CLCuV)',
      confidence: 0.88,
      severity: 'medium',
      treatment_organic: [
        'Roguing: Immediately uproot and bury plants showing severe upward curling.',
        'Apply 5% Neem Seed Kernel Extract (NSKE) or Neem Oil @ 5ml/litre water to repel whiteflies.',
        'Install bright yellow sticky cards (10-12 per acre) to trap whitefly vectors.'
      ],
      treatment_chemical: [
        'Imidacloprid 17.8% SL @ 0.5 ml per litre of water (Use only if threshold > 10 whiteflies/leaf).',
        'Observe a mandatory 21-day Pre-Harvest Interval (PHI) before boll opening.'
      ],
      prevention_tips: [
        'Sow CLCuV-tolerant hybrids such as RCH-2 BG-II or Bunny.',
        'Keep field borders free from weed hosts like Abutilon indicum (Kangi).',
        'Avoid excessive early nitrogen application which produces succulent growth attractive to whiteflies.'
      ],
      sources: [
        { title: 'ICAR-CICR Tech Bulletin No. 42: Viral Diseases of Cotton', page: '28' },
        { title: 'Navsari Agricultural University Extension Bulletin 2024', page: '9' }
      ],
      image_url: URL.createObjectURL(file),
      created_at: new Date().toLocaleTimeString(),
      is_mock: true,
    };
  },

  // Market Prices
  async getMarketPrices(crop: string = 'cotton'): Promise<{ records: MarketPriceRecord[]; trend: string; recommendation: string }> {
    try {
      const res = await fetch(`${API_BASE}/market/prices?crop=${crop}`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }
    const today = new Date();
    const records: MarketPriceRecord[] = [];
    const base = crop === 'cotton' ? 6800 : crop === 'groundnut' ? 5100 : 2250;
    for (let i = 29; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      const variation = Math.sin(i / 3) * 150 + (30 - i) * 6;
      const modal = Math.round(base + variation);
      records.push({
        date: d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }),
        mandi: 'Navsari APMC',
        crop: crop.toUpperCase(),
        min_price: modal - 250,
        modal_price: modal,
        max_price: modal + 320,
      });
    }
    return {
      records,
      trend: 'Rising (+4.2% over 7 days)',
      recommendation: 'HOLD: Anticipate peak prices at ₹7,100 next week due to ginning mill demand.',
    };
  },

  // Extension Officer Data
  async getOfficerOverview() {
    return {
      total_farms: 124,
      total_hectares: 412,
      active_outbreaks: 2,
      critical_alerts: 4,
      clusters: [
        {
          id: 'cl-1',
          name: 'Bardoli Cotton Cluster',
          taluka: 'Bardoli',
          lat: 21.12,
          lon: 73.11,
          disease: 'Pink Bollworm & Leaf Curl',
          affected_farmers: 14,
          severity: 'high',
          radius_km: 4.5,
        },
        {
          id: 'cl-2',
          name: 'Navsari Groundnut Cluster',
          taluka: 'Navsari',
          lat: 20.95,
          lon: 72.95,
          disease: 'Tikka Early Leaf Spot',
          affected_farmers: 8,
          severity: 'medium',
          radius_km: 3.2,
        },
      ],
    };
  },
};

export interface Launch {
  launch_id: string;
  status: 'pending' | 'running' | 'hitl_pending' | 'completed' | 'failed';
  product_name: string;
  description: string;
  target_market: string;
  competitors: string[];
  launch_date?: string;
  created_at: string;
  updated_at: string;
}

export interface MarketData {
  market_size: string;
  growth_rate: string;
  competitors: Array<{
    name: string;
    positioning: string;
    strengths: string[];
    weaknesses: string[];
    pricing?: string;
  }>;
  trends: Array<{ trend: string; relevance: string; source?: string }>;
  white_space: string;
  recommended_positioning: string;
}

export interface Persona {
  name: string;
  role: string;
  age_range: string;
  pain_points: string[];
  goals: string[];
  channels: string[];
  message_hook: string;
  willingness_to_pay: string;
}

export interface LaunchStrategy {
  positioning_statement: string;
  launch_date_recommendation: string;
  phases: Array<{
    phase: string;
    duration: string;
    goals: string[];
    tactics: string[];
    kpis: string[];
  }>;
  channels: string[];
  budget_allocation: Record<string, string>;
  success_metrics: string[];
  risks: string[];
}

export interface ContentItem {
  format: 'email' | 'linkedin' | 'twitter' | 'ad_copy' | 'landing_page';
  variant: 'a' | 'b';
  headline: string;
  body: string;
  cta: string;
  target_persona: string;
}

export interface ContentBundle {
  email_sequence: ContentItem[];
  social_posts: ContentItem[];
  ad_copy: ContentItem[];
  brand_voice_notes: string;
}

export interface LaunchBrief {
  launch_id: string;
  market_data?: MarketData;
  personas?: Persona[];
  strategy?: LaunchStrategy;
  content?: ContentBundle;
}

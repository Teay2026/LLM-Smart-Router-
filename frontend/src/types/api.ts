export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  messages: Message[];
  latency_hint?: 'fast' | 'normal';
  priority?: 'low' | 'normal' | 'high';
}

export interface ChatMeta {
  reason: string;
  latency_ms: number;
  queue_depth: number;
}

export interface ChatResponse {
  model_selected: string;
  completion: string;
  meta: ChatMeta;
}

export interface HealthResponse {
  status: string;
}

export type LatencyHint = 'fast' | 'normal';
export type Priority = 'low' | 'normal' | 'high';
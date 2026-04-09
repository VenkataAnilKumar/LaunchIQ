export const MAX_CONTEXT_TOKENS = 180_000;
export const MAX_OUTPUT_TOKENS = 8_192;
export const HITL_TIMEOUT_SECONDS = 86_400;
export const CELERY_TASK_TIMEOUT = 300;
export const RATE_LIMIT_REQUESTS = 60;
export const RATE_LIMIT_WINDOW = 60; // seconds

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
export const SSE_RECONNECT_DELAY_MS = 3_000;

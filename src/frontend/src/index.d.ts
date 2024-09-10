export {};

declare global {
  interface Window {
    SENTRY_DSN: string;
    SENTRY_ENVIRONMENT: string;
  }
}

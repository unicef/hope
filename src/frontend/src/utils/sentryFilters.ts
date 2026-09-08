import type { ErrorEvent, EventHint } from '@sentry/react';

const isUnhandledRejection = (event: ErrorEvent): boolean =>
  event.exception?.values?.some(
    (value) => value.mechanism?.type === 'onunhandledrejection',
  ) ?? false;

const isClientApiError = (exception: unknown): boolean => {
  if (!exception || typeof exception !== 'object') return false;
  const { name, status } = exception as { name?: unknown; status?: unknown };
  return (
    name === 'ApiError' &&
    typeof status === 'number' &&
    status >= 400 &&
    status < 500
  );
};

export function dropHandledApiErrors(
  event: ErrorEvent,
  hint: EventHint,
): ErrorEvent | null {
  if (isUnhandledRejection(event) && isClientApiError(hint?.originalException)) {
    return null;
  }
  return event;
}

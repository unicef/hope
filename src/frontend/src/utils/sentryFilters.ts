import type { ErrorEvent, EventHint } from '@sentry/react';

// The browser SDK tags rejections caught by its global handler as
// "auto.browser.global_handlers.onunhandledrejection" (older versions used the bare
// "onunhandledrejection"), so match on the suffix rather than the full string.
const isUnhandledRejection = (event: ErrorEvent): boolean =>
  event.exception?.values?.some(
    (value) =>
      value.mechanism?.handled === false &&
      value.mechanism?.type?.endsWith('onunhandledrejection'),
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

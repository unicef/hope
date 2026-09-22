import type { ErrorEvent, EventHint } from '@sentry/react';
import { describe, expect, it } from 'vitest';
import { dropHandledApiErrors } from './sentryFilters';

const REJECTION = 'auto.browser.global_handlers.onunhandledrejection';

const eventWith = (mechanismType: string, handled = false): ErrorEvent =>
  ({
    exception: {
      values: [
        { type: 'ApiError', mechanism: { type: mechanismType, handled } },
      ],
    },
  }) as ErrorEvent;

const apiError = (status: number): Error => {
  const error = new Error('Bad Request');
  error.name = 'ApiError';
  (error as Error & { status: number }).status = status;
  return error;
};

const hintFor = (originalException: unknown): EventHint =>
  ({ originalException }) as EventHint;

describe('dropHandledApiErrors', () => {
  it('drops a 4xx ApiError reported as an unhandled rejection, because the mutation onError already told the user', () => {
    expect(
      dropHandledApiErrors(eventWith(REJECTION), hintFor(apiError(400))),
    ).toBeNull();
  });

  it('drops the same event under the bare mechanism type older SDKs emit', () => {
    expect(
      dropHandledApiErrors(
        eventWith('onunhandledrejection'),
        hintFor(apiError(400)),
      ),
    ).toBeNull();
  });

  it('keeps a 5xx ApiError, which is a real backend failure the user cannot act on', () => {
    const event = eventWith(REJECTION);
    expect(dropHandledApiErrors(event, hintFor(apiError(500)))).toBe(event);
  });

  it('keeps a 4xx ApiError that was captured explicitly rather than floated', () => {
    const event = eventWith('generic');
    expect(dropHandledApiErrors(event, hintFor(apiError(400)))).toBe(event);
  });

  it('keeps a rejection the SDK marked as handled', () => {
    const event = eventWith(REJECTION, true);
    expect(dropHandledApiErrors(event, hintFor(apiError(400)))).toBe(event);
  });

  it('keeps a non-ApiError unhandled rejection', () => {
    const event = eventWith(REJECTION);
    expect(dropHandledApiErrors(event, hintFor(new Error('boom')))).toBe(event);
  });

  it('keeps an event with no original exception', () => {
    const event = eventWith(REJECTION);
    expect(dropHandledApiErrors(event, hintFor(undefined))).toBe(event);
  });
});

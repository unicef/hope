import type { ApiErrorShape } from './utils';

export class NotFoundError extends Error {
  constructor(message = 'Not found') {
    super(message);
    this.name = 'NotFoundError';
  }
}

/**
 * Read a displayable message off a value caught in `catch`. Under
 * `useUnknownInCatchVariables` the binding is `unknown`, and the REST layer
 * throws a mix of `Error`, bare strings, and generated API error objects.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  if (error && typeof error === 'object' && 'message' in error) {
    const { message } = error as { message?: unknown };
    return typeof message === 'string' ? message : '';
  }
  return '';
}

/**
 * True when a request succeeded but the client choked parsing an empty body.
 * DELETE endpoints answer 204 with no content, which the generated client
 * still runs through `JSON.parse`. Callers must treat this as success —
 * reporting it as a failure tells the user a completed delete did not happen.
 */
export function isEmptyJsonResponseError(error: unknown): boolean {
  return getErrorMessage(error).includes('Unexpected end of JSON input');
}

/**
 * Narrow a caught value for `showApiErrorMessages`, which reads `body` and
 * `message` and already guards every access it makes.
 */
export function toApiError(error: unknown): ApiErrorShape {
  return error ?? {};
}

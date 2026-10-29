import { fireEvent, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { LoginPage } from './LoginPage';

const jsonResponse = (body: unknown, ok = true) =>
  ({ ok, json: () => Promise.resolve(body) }) as Response;

describe('LoginPage', () => {
  let submitSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // jsdom does not implement form navigation.
    submitSpy = vi
      .spyOn(HTMLFormElement.prototype, 'submit')
      .mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('shows an error and re-enables the button when fetching the CSRF token fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')));
    renderWithProviders(<LoginPage />);

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    expect((await screen.findByRole('alert')).textContent).toBe(
      'Could not start signing in. Please try again.',
    );
    expect(
      screen.getByRole<HTMLButtonElement>('button', { name: 'Sign in' })
        .disabled,
    ).toBe(false);
    expect(submitSpy).not.toHaveBeenCalled();
  });

  it.each([
    ['an error status', jsonResponse({ csrf_token: 'token' }, false)],
    ['no token', jsonResponse({})],
  ])('shows an error when the CSRF response has %s', async (_, response) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response));
    renderWithProviders(<LoginPage />);

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await screen.findByRole('alert');
    expect(submitSpy).not.toHaveBeenCalled();
  });

  it('submits the login form with the CSRF token after a failed attempt is retried', async () => {
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockRejectedValueOnce(new TypeError('offline'))
        .mockResolvedValueOnce(jsonResponse({ csrf_token: 'token-123' })),
    );
    const { container } = renderWithProviders(<LoginPage />);
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));
    await screen.findByRole('alert');

    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }));

    await waitFor(() => expect(submitSpy).toHaveBeenCalledTimes(1));
    expect(
      container.querySelector<HTMLInputElement>(
        'input[name="csrfmiddlewaretoken"]',
      ).value,
    ).toBe('token-123');
    expect(screen.queryByRole('alert')).toBeNull();
  });
});

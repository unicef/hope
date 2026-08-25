import React from 'react';
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { setupCommonMocks, utilsMock } from 'src/testUtils/commonMocks';
import { UserProfileMenu } from './UserProfileMenu';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import type { Profile } from '@restgenerated/models/Profile';

setupCommonMocks();

const buildProfile = (overrides: Partial<Profile> = {}): Profile =>
  ({
    id: 'user-1',
    username: 'user1',
    email: 'user1@example.com',
    firstName: 'User',
    lastName: 'One',
    isSuperuser: false,
    partner: { id: 1, name: 'Partner' } as any,
    userRoles: {},
    partnerRoles: {},
    status: undefined,
    lastLogin: null,
    timezone: null,
    businessAreas: {},
    permissionsInScope: '',
    crossAreaFilterAvailable: false,
    jobTitle: '',
    effectiveTimezone: 'Asia/Kabul',
    ...overrides,
  }) as Profile;

const businessArea = {
  id: 'ba-1',
  name: 'Afghanistan',
  code: 'AFG',
  longName: 'Afghanistan',
  slug: 'afghanistan',
  timezone: 'Asia/Kabul',
  countries: [],
} as any;

const timezoneChoices = {
  results: [
    { name: 'Asia/Kabul', value: 'Asia/Kabul' },
    { name: 'Europe/Warsaw', value: 'Europe/Warsaw' },
  ],
};

const openMenu = () => {
  fireEvent.click(screen.getByText('user1@example.com'));
};

const openPicker = async (): Promise<HTMLInputElement> => {
  const input = await screen.findByTestId('input-timezone-select');
  fireEvent.mouseDown(input);
  await screen.findByRole('listbox');
  return input as HTMLInputElement;
};

const selectOption = async (label: string): Promise<void> => {
  const option = await screen.findByRole('option', { name: label });
  fireEvent.click(option);
};

describe('UserProfileMenu timezone picker', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.mocked(RestService.restBusinessAreasRetrieve).mockResolvedValue(
      businessArea,
    );
    vi.mocked(
      RestService.restBusinessAreasUsersTimezoneChoicesList,
    ).mockResolvedValue(timezoneChoices as any);
  });

  const renderMenu = (meData: Profile) => {
    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <UserProfileMenu meData={meData} />
      </QueryClientProvider>,
    );
  };

  it('does not request timezone choices before the menu is opened', () => {
    renderMenu(buildProfile());
    expect(
      RestService.restBusinessAreasUsersTimezoneChoicesList,
    ).not.toHaveBeenCalled();
  });

  it('requests choices once when opened and shows a loading state', async () => {
    let resolveChoices: (value: unknown) => void;
    vi.mocked(
      RestService.restBusinessAreasUsersTimezoneChoicesList,
    ).mockReturnValue(
      new Promise((resolve) => {
        resolveChoices = resolve;
      }) as any,
    );

    renderMenu(buildProfile());
    openMenu();

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasUsersTimezoneChoicesList,
      ).toHaveBeenCalledTimes(1),
    );
    expect(screen.getByRole('progressbar')).toBeTruthy();

    resolveChoices!(timezoneChoices);
    await waitFor(() => expect(screen.queryByRole('progressbar')).toBeNull());

    openMenu();
    openMenu();
    expect(
      RestService.restBusinessAreasUsersTimezoneChoicesList,
    ).toHaveBeenCalledTimes(1);
  });

  it('preselects the existing explicit preference', async () => {
    renderMenu(buildProfile({ timezone: 'Europe/Warsaw' }));
    openMenu();

    const input = await screen.findByTestId('input-timezone-select');
    await waitFor(() =>
      expect((input as HTMLInputElement).value).toBe('Europe/Warsaw'),
    );
  });

  it('preselects the inheritance option when the preference is null', async () => {
    renderMenu(buildProfile({ timezone: null }));
    openMenu();

    const input = await screen.findByTestId('input-timezone-select');
    await waitFor(() =>
      expect((input as HTMLInputElement).value).toBe(
        'Use Afghanistan timezone (Asia/Kabul)',
      ),
    );
  });

  it('PATCHes the selected explicit zone', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
    ).mockResolvedValue({
      timezone: 'Europe/Warsaw',
      effectiveTimezone: 'Europe/Warsaw',
    });

    renderMenu(buildProfile({ timezone: null }));
    openMenu();
    await openPicker();
    await selectOption('Europe/Warsaw');

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        requestBody: { timezone: 'Europe/Warsaw' },
      }),
    );
  });

  it('PATCHes {timezone: null} when the inheritance option is selected', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
    ).mockResolvedValue({ timezone: null, effectiveTimezone: 'Asia/Kabul' });

    renderMenu(buildProfile({ timezone: 'Europe/Warsaw' }));
    openMenu();
    await openPicker();
    await selectOption('Use Afghanistan timezone (Asia/Kabul)');

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        requestBody: { timezone: null },
      }),
    );
  });

  it('updates the cached profile timezone and effectiveTimezone on success', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
    ).mockResolvedValue({
      timezone: 'Europe/Warsaw',
      effectiveTimezone: 'Europe/Warsaw',
    });

    const profileParams = { businessAreaSlug: 'afghanistan' };
    const fullKey = restQueryKey(
      RestService.restBusinessAreasUsersProfileRetrieve,
      profileParams,
    );
    const seeded = buildProfile({ timezone: null });
    queryClient.setQueryData(fullKey, seeded);

    renderMenu(seeded);
    openMenu();
    await openPicker();
    await selectOption('Europe/Warsaw');

    await waitFor(() => {
      const cached = queryClient.getQueryData<Profile>(fullKey);
      expect(cached?.timezone).toBe('Europe/Warsaw');
      expect(cached?.effectiveTimezone).toBe('Europe/Warsaw');
    });
  });

  it('restores the previous option and shows an error snackbar on failure', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
    ).mockRejectedValue({ body: { timezone: ['Invalid timezone.'] } });

    renderMenu(buildProfile({ timezone: null }));
    openMenu();
    await openPicker();
    await selectOption('Europe/Warsaw');

    const input = await screen.findByTestId('input-timezone-select');
    await waitFor(() =>
      expect((input as HTMLInputElement).value).toBe(
        'Use Afghanistan timezone (Asia/Kabul)',
      ),
    );
    expect(utilsMock.showApiErrorMessages).toHaveBeenCalled();
  });

  it('ticks the current-local-time preview every minute while open, with no extra API calls', async () => {
    vi.useFakeTimers();
    renderMenu(buildProfile());
    openMenu();

    const before = screen.getByTestId('current-local-time').textContent;

    await vi.advanceTimersByTimeAsync(60 * 1000);
    await vi.advanceTimersByTimeAsync(60 * 1000);

    const after = screen.getByTestId('current-local-time').textContent;
    expect(after).not.toBe(before);
    expect(
      RestService.restBusinessAreasUsersProfileTimezonePartialUpdate,
    ).not.toHaveBeenCalled();

    vi.useRealTimers();
  });

  it('clears the clock interval when the menu closes', async () => {
    vi.useFakeTimers();
    const clearSpy = vi.spyOn(global, 'clearInterval');
    renderMenu(buildProfile());
    openMenu();

    // Tab closes the menu (handleListKeyDown), same as clicking away.
    fireEvent.keyDown(screen.getByRole('menu'), { key: 'Tab' });

    expect(clearSpy).toHaveBeenCalled();

    vi.useRealTimers();
  });

  it('keyboard interaction inside the picker does not trigger logout', async () => {
    const assignSpy = vi.fn();
    Object.defineProperty(window, 'location', {
      value: { ...window.location, assign: assignSpy },
      writable: true,
    });

    renderMenu(buildProfile());
    openMenu();
    const input = await openPicker();

    fireEvent.keyDown(input, { key: 'ArrowDown' });
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(assignSpy).not.toHaveBeenCalled();
    expect(screen.getByText('Logout')).toBeTruthy();
  });
});

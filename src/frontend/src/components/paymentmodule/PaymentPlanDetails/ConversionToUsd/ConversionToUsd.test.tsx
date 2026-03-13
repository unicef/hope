import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, renderWithProviders, screen, waitFor } from 'src/testUtils/testUtils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from 'src/config/permissions';
import ConversionToUsd from './ConversionToUsd';

vi.mock('@components/core/withErrorBoundary', () => ({
  default: (Component) => Component,
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
  }),
}));

vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({
    showMessage: vi.fn(),
  }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsPaymentPlansCustomExchangeRateCreate: vi.fn(() =>
      Promise.resolve({}),
    ),
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, params?: Record<string, string>) => {
      if (key === '1 USD = {{rate}} {{currency}}') {
        return `1 USD = ${params?.rate} ${params?.currency}`;
      }
      return key;
    },
  }),
}));

const basePaymentPlan = {
  id: 'payment-plan-1',
  status: PaymentPlanStatusEnum.OPEN,
  currency: 'PLN',
  exchangeRate: '1.25000000',
  customExchangeRate: true,
  unoreExchangeRate: '2.00000000',
  version: 3,
  backgroundActionStatus: null,
  backgroundActionStatusDisplay: '',
} as const;

function renderComponent(overrides = {}, permissions = [PERMISSIONS.PM_CUSTOM_EXCHANGE_RATE]) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return renderWithProviders(
    <QueryClientProvider client={queryClient}>
      <ConversionToUsd
        paymentPlan={{ ...basePaymentPlan, ...overrides }}
        permissions={permissions}
      />
    </QueryClientProvider>,
  );
}

describe('ConversionToUsd', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('prefills the custom exchange rate input and shows helper text', () => {
    renderComponent();

    const input = screen.getByRole('spinbutton') as HTMLInputElement;

    expect(screen.getByText('Enter the amount of local currency against 1 USD')).toBeTruthy();
    expect(input.value).toBe('1.25000000');
  });

  it('disables conversion controls for unsupported statuses', () => {
    renderComponent({ status: PaymentPlanStatusEnum.LOCKED });

    const input = screen.getByRole('spinbutton') as HTMLInputElement;
    const applyButton = screen.getByRole('button', { name: 'Apply' }) as HTMLButtonElement;
    const unoreRadio = screen.getByRole('radio', { name: 'Use UNORE exchange rate' }) as HTMLInputElement;
    const customRadio = screen.getByRole('radio', { name: 'Custom exchange rate' }) as HTMLInputElement;

    expect(input.disabled).toBe(true);
    expect(applyButton.disabled).toBe(true);
    expect(unoreRadio.disabled).toBe(true);
    expect(customRadio.disabled).toBe(true);
  });

  it('sets the custom exchange rate input to read-only without permission', () => {
    renderComponent({}, []);

    const input = screen.getByRole('spinbutton') as HTMLInputElement;

    expect(input.readOnly).toBe(true);
  });

  it('sends only the custom exchange rate when custom option is selected', async () => {
    renderComponent();

    fireEvent.click(screen.getByRole('button', { name: 'Apply' }));

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsPaymentPlansCustomExchangeRateCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        id: 'payment-plan-1',
        programSlug: 'test-program',
        requestBody: {
          customExchangeRate: '1.25000000',
          version: 3,
        },
      });
    });
  });

  it('sends only the UNORE exchange rate when unore option is selected', async () => {
    renderComponent();

    fireEvent.click(screen.getByRole('radio', { name: 'Use UNORE exchange rate' }));
    fireEvent.click(screen.getByRole('button', { name: 'Apply' }));

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsPaymentPlansCustomExchangeRateCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        id: 'payment-plan-1',
        programSlug: 'test-program',
        requestBody: {
          unoreExchangeRate: '2.00000000',
          version: 3,
        },
      });
    });
  });
});

import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { PaymentDetail } from '@restgenerated/models/PaymentDetail';
import { RestService } from '@restgenerated/services/RestService';
import { TestProviders } from 'src/testUtils/testProviders';
import { PERMISSIONS } from '../../../config/permissions';
import PaymentDetailsPage from './PaymentDetailsPage';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'sudan',
    programId: '8zg_',
    baseUrl: 'sudan/8zg_',
  }),
}));

const mockUsePermissions = vi.hoisted(() => vi.fn((): string[] => []));

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: mockUsePermissions,
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    selectedProgram: { beneficiaryGroup: { groupLabel: 'Household' } },
    isSocialDctType: false,
  }),
}));

// A payment with no verification at all - the shape that used to blow up when the
// page handed `undefined` down to PaymentDetails.
const paymentWithoutVerification = {
  id: 'e41cc395-75ca-4265-94cf-8a5813fd6e20',
  unicefId: 'RCPT-0060-25-0.000.001',
  status: 'Distribution Successful',
  currency: 'SDG',
  entitlementQuantity: '100.00',
  deliveredQuantity: '100.00',
  parent: {
    id: 'a9f1a3f4-0d3a-4c54-9c0c-1c0f4a5b6c7d',
    unicefId: 'PP-0060-25-00000001',
    name: 'Sudan Cash Payment Plan',
    status: 'ACCEPTED',
    planType: 'STANDARD',
    isPaymentGateway: false,
  },
} as unknown as PaymentDetail;

const renderPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <PaymentDetailsPage />
      </QueryClientProvider>
    </MemoryRouter>,
    { wrapper: TestProviders },
  );
};

describe('PaymentDetailsPage', () => {
  let retrieve;

  beforeEach(() => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_VIEW_DETAILS]);
    retrieve = vi.spyOn(
      RestService,
      'restBusinessAreasProgramsPaymentPlansPaymentsRetrieve',
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows the error page instead of a blank screen when the payment is not found', async () => {
    retrieve.mockRejectedValue(new Error('Not Found'));

    renderPage();

    expect(
      await screen.findByText('Payment has been removed or does not exist', {
        exact: false,
      }),
    ).toBeTruthy();
    expect(screen.getByText('Oops! Something went wrong')).toBeTruthy();
  });

  it('shows the error page when the request fails for any other reason', async () => {
    retrieve.mockRejectedValue(new Error('Internal Server Error'));

    renderPage();

    expect(
      await screen.findByText('Oops! Something went wrong'),
    ).toBeTruthy();
    expect(
      screen.queryByText('Payment has been removed or does not exist', {
        exact: false,
      }),
    ).toBeNull();
  });

  it('shows Permission Denied when the API rejects the user', async () => {
    retrieve.mockRejectedValue(new Error('Permission Denied'));

    renderPage();

    expect(await screen.findByText('Permission Denied')).toBeTruthy();
  });

  it('renders the details for a payment that has no verification', async () => {
    retrieve.mockResolvedValue(paymentWithoutVerification);

    renderPage();

    expect(
      await screen.findByText(`Payment ${paymentWithoutVerification.unicefId}`),
    ).toBeTruthy();
    await waitFor(() => {
      expect(screen.queryByText('Oops! Something went wrong')).toBeNull();
    });
    expect(screen.queryByText('Verification Details')).toBeNull();
  });
});

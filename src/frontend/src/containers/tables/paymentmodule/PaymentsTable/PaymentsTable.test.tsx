import type { ReactNode } from 'react';
import { renderWithProviders, screen, waitFor } from 'src/testUtils/testUtils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RestService } from '@restgenerated/services/RestService';
import PaymentsTable from './PaymentsTable';

vi.mock('@components/core/withErrorBoundary', () => ({
  default: (Component) => Component,
}));

vi.mock('@components/core/TableWrapper', () => ({
  TableWrapper: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

vi.mock('@components/rest/UniversalRestTable/UniversalRestTable', () => ({
  UniversalRestTable: () => <div data-testid="payments-rest-table" />,
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    baseUrl: 'afghanistan/test-program',
    programId: 'test-program',
  }),
}));

vi.mock('@hooks/useScrollToRefOnChange', () => ({
  useScrollToRefOnChange: vi.fn(),
}));

vi.mock('./PaymentsFilters', () => ({
  PaymentsFilters: () => <div data-testid="payments-filters" />,
}));

vi.mock('./WarningTooltipTable', () => ({
  WarningTooltipTable: () => null,
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    isSocialDctType: false,
    selectedProgram: {
      beneficiaryGroup: {
        groupLabel: 'Household',
        memberLabel: 'Individual',
      },
    },
  }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@utils/queryKeys', () => ({
  restQueryKey: (method, params) => [method.getMockName(), params],
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasUsersProfileRetrieve: vi.fn().mockName('profile'),
    restBusinessAreasProgramsPaymentPlansPaymentsList: vi
      .fn()
      .mockName('eligible-list'),
    restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve: vi
      .fn()
      .mockName('eligible-count'),
    restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleList: vi
      .fn()
      .mockName('not-eligible-list'),
    restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve: vi
      .fn()
      .mockName('not-eligible-count'),
  },
}));

const paymentPlan = { id: 'payment-plan-id' };

function renderPaymentsTable(): void {
  renderWithProviders(
    <PaymentsTable
      businessArea="afghanistan"
      paymentPlan={paymentPlan as any}
      permissions={[]}
    />,
  );
}

describe('PaymentsTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsList,
    ).mockResolvedValue({ results: [] });
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsCountRetrieve,
    ).mockResolvedValue({ count: 0 });
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleList,
    ).mockResolvedValue({ results: [] });
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve,
    ).mockResolvedValue({ count: 0 });
  });

  it('renders the Not Eligible section for a superuser when its base count is positive', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileRetrieve,
    ).mockResolvedValue({ isSuperuser: true } as any);
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve,
    ).mockResolvedValue({ count: 1 });

    renderPaymentsTable();

    expect(await screen.findByText('Not Eligible Payee List')).toBeTruthy();
    expect(screen.getAllByTestId('payments-filters')).toHaveLength(2);
  });

  it('does not render the Not Eligible section when its base count is zero', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileRetrieve,
    ).mockResolvedValue({ isSuperuser: true } as any);

    renderPaymentsTable();

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve,
      ).toHaveBeenCalled();
    });
    expect(screen.queryByText('Not Eligible Payee List')).toBeNull();
  });

  it('does not request or render Not Eligible payments for a non-superuser', async () => {
    vi.mocked(
      RestService.restBusinessAreasUsersProfileRetrieve,
    ).mockResolvedValue({ isSuperuser: false } as any);

    renderPaymentsTable();

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasUsersProfileRetrieve,
      ).toHaveBeenCalled();
    });
    expect(
      RestService.restBusinessAreasProgramsPaymentPlansPaymentsNotEligibleCountRetrieve,
    ).not.toHaveBeenCalled();
    expect(screen.queryByText('Not Eligible Payee List')).toBeNull();
  });
});

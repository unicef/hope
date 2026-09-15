import {
  fireEvent,
  renderWithProviders,
  screen,
} from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentsFilters } from './PaymentsFilters';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    isSocialDctType: false,
    selectedProgram: {
      beneficiaryGroup: {
        groupLabel: 'Household',
      },
    },
  }),
}));

const sharedProps = {
  setFilter: vi.fn(),
  setAppliedFilter: vi.fn(),
  appliedFilter: {},
};

describe('PaymentsFilters', () => {
  it('offers raw eligible payment statuses without Not Eligible', () => {
    const initialFilter = {
      paymentUnicefId: '',
      individualUnicefId: '',
      householdUnicefId: '',
      collectorFullName: '',
      status: '',
    };
    renderWithProviders(
      <PaymentsFilters
        {...sharedProps}
        filter={initialFilter}
        initialFilter={initialFilter}
        filterKeys={{
          paymentUnicefId: 'paymentUnicefId',
          individualUnicefId: 'individualUnicefId',
          householdUnicefId: 'householdUnicefId',
          collectorFullName: 'collectorFullName',
          status: 'status',
        }}
        showStatus
      />,
    );

    fireEvent.mouseDown(screen.getByLabelText('Status'));

    expect(screen.getByRole('option', { name: 'Pending' })).toBeTruthy();
    expect(screen.queryByRole('option', { name: 'Not Eligible' })).toBeNull();
  });

  it('offers all ineligibility causes in a multi-select filter', () => {
    const initialFilter = {
      notEligiblePaymentUnicefId: '',
      notEligibleIndividualUnicefId: '',
      notEligibleHouseholdUnicefId: '',
      notEligibleCollectorFullName: '',
      notEligibleIneligibilityCause: [],
    };
    renderWithProviders(
      <PaymentsFilters
        {...sharedProps}
        filter={initialFilter}
        initialFilter={initialFilter}
        filterKeys={{
          paymentUnicefId: 'notEligiblePaymentUnicefId',
          individualUnicefId: 'notEligibleIndividualUnicefId',
          householdUnicefId: 'notEligibleHouseholdUnicefId',
          collectorFullName: 'notEligibleCollectorFullName',
          ineligibilityCause: 'notEligibleIneligibilityCause',
        }}
        showIneligibilityCause
      />,
    );

    fireEvent.mouseDown(screen.getByLabelText('Ineligibility Cause'));

    expect(screen.getByRole('option', { name: 'Hard Conflict' })).toBeTruthy();
    expect(
      screen.getByRole('option', { name: 'Manual Exclusion' }),
    ).toBeTruthy();
    expect(screen.getByRole('option', { name: 'Invalid Wallet' })).toBeTruthy();
  });
});

import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentStatusEnum } from '@restgenerated/models/PaymentStatusEnum';
import { PaymentsTableRow } from './PaymentsTableRow';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ baseUrl: 'afghanistan/test-program' }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({ isSocialDctType: false }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const payment = {
  id: 'payment-id',
  parentId: 'payment-plan-id',
  unicefId: 'RCPT-001',
  householdId: 'household-id',
  householdUnicefId: 'HH-001',
  householdSize: 1,
  householdAdmin2: 'Admin 2',
  snapshotCollectorFullName: null,
  collectorId: 'collector-id',
  fspName: null,
  entitlementQuantity: null,
  deliveredQuantity: null,
  status: PaymentStatusEnum.NOT_ELIGIBLE,
  paymentPlanHardConflicted: false,
  paymentPlanSoftConflicted: false,
  conflicted: true,
  excluded: true,
  hasValidWallet: false,
};

describe('PaymentsTableRow', () => {
  it('shows the Not Eligible status and every active ineligibility cause', () => {
    renderWithProviders(
      <table>
        <tbody>
          <PaymentsTableRow
            payment={payment as any}
            canViewDetails={false}
            permissions={[]}
            showIneligibilityCauses
          />
        </tbody>
      </table>,
    );

    expect(screen.getByText('NOT ELIGIBLE')).toBeTruthy();
    expect(screen.getByText('Hard Conflict')).toBeTruthy();
    expect(screen.getByText('Manual Exclusion')).toBeTruthy();
    expect(screen.getByText('Invalid Wallet')).toBeTruthy();
  });
});

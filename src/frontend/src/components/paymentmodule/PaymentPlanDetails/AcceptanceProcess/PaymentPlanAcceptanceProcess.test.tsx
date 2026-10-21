import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PaymentPlanAcceptanceProcess } from './PaymentPlanAcceptanceProcess';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/usePaymentPlanGroup', () => ({
  usePaymentPlanGroup: (groupId: string | undefined) => ({
    data: groupId
      ? { approvalProcess: [{ sentForApprovalDate: 'group-approval' }] }
      : undefined,
  }),
}));

vi.mock('./AcceptanceProcessRow', () => ({
  AcceptanceProcessRow: ({ acceptanceProcess }: any) => (
    <div data-cy={acceptanceProcess.sentForApprovalDate} />
  ),
}));

describe('PaymentPlanAcceptanceProcess', () => {
  it('shows the own approvals of an instruction-managed plan', () => {
    renderWithProviders(
      <PaymentPlanAcceptanceProcess
        paymentPlan={
          {
            status: PaymentPlanStatusEnum.IN_AUTHORIZATION,
            isInstructionManaged: true,
            paymentPlanGroup: null,
            approvalProcess: [{ sentForApprovalDate: 'plan-approval' }],
          } as any
        }
      />,
    );

    expect(screen.getByTestId('plan-approval')).toBeTruthy();
  });

  it('shows the group approvals of a grouped plan', () => {
    renderWithProviders(
      <PaymentPlanAcceptanceProcess
        paymentPlan={
          {
            status: PaymentPlanStatusEnum.IN_AUTHORIZATION,
            isInstructionManaged: false,
            paymentPlanGroup: { id: 'group-1' },
            approvalProcess: [],
          } as any
        }
      />,
    );

    expect(screen.getByTestId('group-approval')).toBeTruthy();
  });
});

import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { PaymentListAcceptanceProcess } from './PaymentListAcceptanceProcess';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('./AcceptanceProcessRow', () => ({
  AcceptanceProcessRow: ({ acceptanceProcess }: any) => (
    <div data-cy={acceptanceProcess.sentForApprovalDate} />
  ),
}));

describe('PaymentListAcceptanceProcess', () => {
  it('shows the instruction approvals of an instruction-managed plan', () => {
    renderWithProviders(
      <PaymentListAcceptanceProcess
        paymentList={
          {
            status: PaymentListStatusEnum.IN_AUTHORIZATION,
            isInstructionManaged: true,
            paymentPlan: null,
            approvalProcess: [{ sentForApprovalDate: 'instruction-approval' }],
          } as any
        }
      />,
    );

    expect(screen.getByTestId('instruction-approval')).toBeTruthy();
  });

  it('shows the payment plan approvals of a grouped plan', () => {
    renderWithProviders(
      <PaymentListAcceptanceProcess
        paymentList={
          {
            status: PaymentListStatusEnum.IN_AUTHORIZATION,
            isInstructionManaged: false,
            paymentPlan: { id: 'group-1' },
            approvalProcess: [{ sentForApprovalDate: 'group-approval' }],
          } as any
        }
      />,
    );

    expect(screen.getByTestId('group-approval')).toBeTruthy();
  });
});

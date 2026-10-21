import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { FollowUpPaymentPlanDetailsHeader } from './FollowUpPaymentPlanDetailsHeader';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@components/core/AdminButton', () => ({
  AdminButton: () => null,
}));

const { mockButtons } = vi.hoisted(() => ({
  mockButtons: (name: string) => () => <div data-cy={name} />,
}));

vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons',
  () => ({ OpenPaymentPlanHeaderButtons: mockButtons('open-buttons') }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons',
  () => ({ LockedPaymentPlanHeaderButtons: mockButtons('locked-buttons') }),
);

function renderHeader(
  status: PaymentPlanStatusEnum,
  isInstructionManaged: boolean,
) {
  renderWithProviders(
    <FollowUpPaymentPlanDetailsHeader
      baseUrl="afghanistan/test-program"
      permissions={[]}
      paymentPlan={
        {
          id: 'payment-plan-1',
          unicefId: 'PP-1',
          status,
          isInstructionManaged,
          visionManaged: false,
        } as any
      }
    />,
  );
}

const workflowStatuses: [PaymentPlanStatusEnum, string][] = [
  [PaymentPlanStatusEnum.OPEN, 'open-buttons'],
  [PaymentPlanStatusEnum.LOCKED, 'locked-buttons'],
];

describe('FollowUpPaymentPlanDetailsHeader', () => {
  it.each(workflowStatuses)(
    'hides %s buttons for an instruction-managed plan',
    (status, testId) => {
      renderHeader(status, true);
      expect(screen.queryByTestId(testId)).toBeNull();
    },
  );

  it.each(workflowStatuses)(
    'shows %s buttons for a regular plan',
    (status, testId) => {
      renderHeader(status, false);
      expect(screen.getByTestId(testId)).toBeTruthy();
    },
  );
});

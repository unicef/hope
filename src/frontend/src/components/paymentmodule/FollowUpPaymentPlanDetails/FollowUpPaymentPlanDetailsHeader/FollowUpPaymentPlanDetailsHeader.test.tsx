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
  mockButtons:
    (name: string) => (props: { isInstructionManaged?: boolean }) => (
      <div
        data-cy={name}
        data-instruction-managed={String(!!props.isInstructionManaged)}
      />
    ),
}));

vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/OpenPaymentPlanHeaderButtons',
  () => ({ OpenPaymentPlanHeaderButtons: mockButtons('open-buttons') }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedPaymentPlanHeaderButtons',
  () => ({ LockedPaymentPlanHeaderButtons: mockButtons('locked-buttons') }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/LockedFspPaymentPlanHeaderButtons',
  () => ({
    LockedFspPaymentPlanHeaderButtons: mockButtons('locked-fsp-buttons'),
  }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InApprovalPaymentPlanHeaderButtons',
  () => ({
    InApprovalPaymentPlanHeaderButtons: mockButtons('in-approval-buttons'),
  }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InAuthorizationPaymentPlanHeaderButtons',
  () => ({
    InAuthorizationPaymentPlanHeaderButtons: mockButtons(
      'in-authorization-buttons',
    ),
  }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/InReviewPaymentPlanHeaderButtons',
  () => ({
    InReviewPaymentPlanHeaderButtons: mockButtons('in-review-buttons'),
  }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/AcceptedPaymentPlanHeaderButtons',
  () => ({ AcceptedPaymentPlanHeaderButtons: mockButtons('accepted-buttons') }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/FinishedPaymentPlanHeaderButtons',
  () => ({ FinishedPaymentPlanHeaderButtons: mockButtons('finished-buttons') }),
);
vi.mock(
  '../../PaymentPlanDetails/PaymentPlanDetailsHeader/HeaderButtons/ReadyForClosurePaymentPlanHeaderButtons',
  () => ({
    ReadyForClosurePaymentPlanHeaderButtons: mockButtons(
      'ready-for-closure-buttons',
    ),
  }),
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
  [PaymentPlanStatusEnum.LOCKED_FSP, 'locked-fsp-buttons'],
  [PaymentPlanStatusEnum.IN_APPROVAL, 'in-approval-buttons'],
  [PaymentPlanStatusEnum.IN_AUTHORIZATION, 'in-authorization-buttons'],
  [PaymentPlanStatusEnum.IN_REVIEW, 'in-review-buttons'],
];

const postAcceptanceStatuses: [PaymentPlanStatusEnum, string][] = [
  [PaymentPlanStatusEnum.ACCEPTED, 'accepted-buttons'],
  [PaymentPlanStatusEnum.FINISHED, 'finished-buttons'],
  [PaymentPlanStatusEnum.READY_FOR_CLOSURE, 'ready-for-closure-buttons'],
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

  it.each(postAcceptanceStatuses)(
    'passes isInstructionManaged to %s buttons',
    (status, testId) => {
      renderHeader(status, true);
      expect(
        screen.getByTestId(testId).getAttribute('data-instruction-managed'),
      ).toBe('true');
    },
  );
});

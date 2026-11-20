import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { FollowUpPaymentListDetailsHeader } from './FollowUpPaymentListDetailsHeader';

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
  '../../PaymentListDetails/PaymentListDetailsHeader/HeaderButtons/OpenPaymentListHeaderButtons',
  () => ({ OpenPaymentListHeaderButtons: mockButtons('open-buttons') }),
);
vi.mock(
  '../../PaymentListDetails/PaymentListDetailsHeader/HeaderButtons/LockedPaymentListHeaderButtons',
  () => ({ LockedPaymentListHeaderButtons: mockButtons('locked-buttons') }),
);

function renderHeader(
  status: PaymentListStatusEnum,
  isInstructionManaged: boolean,
) {
  renderWithProviders(
    <FollowUpPaymentListDetailsHeader
      baseUrl="afghanistan/test-program"
      permissions={[]}
      paymentList={
        {
          id: 'payment-list-1',
          unicefId: 'PP-1',
          status,
          isInstructionManaged,
          visionManaged: false,
        } as any
      }
    />,
  );
}

const workflowStatuses: [PaymentListStatusEnum, string][] = [
  [PaymentListStatusEnum.OPEN, 'open-buttons'],
  [PaymentListStatusEnum.LOCKED, 'locked-buttons'],
];

describe('FollowUpPaymentListDetailsHeader', () => {
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

  it.each([
    [PlanTypeEnum.FOLLOW_UP, 'Follow-up Payment List ID:'],
    [PlanTypeEnum.TOP_UP, 'Top Up Payment List ID:'],
    [PlanTypeEnum.TOP_UP_AMENDMENT, 'Top Up Amendment Payment List ID:'],
  ])('titles a %s list with its type', (planType, title) => {
    renderWithProviders(
      <FollowUpPaymentListDetailsHeader
        baseUrl="afghanistan/test-program"
        permissions={[]}
        paymentList={
          {
            id: 'payment-list-1',
            unicefId: 'PP-1',
            status: PaymentListStatusEnum.OPEN,
            planType,
            isInstructionManaged: false,
            visionManaged: false,
          } as any
        }
      />,
    );
    expect(screen.getByTestId('page-header-title').textContent).toContain(
      title,
    );
  });
});

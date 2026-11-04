import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { LinkedPaymentPlansTable } from './LinkedPaymentPlansTable';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ baseUrl: 'afghanistan/test-program' }),
}));

describe('LinkedGroupsTable', () => {
  it('renders nothing without linked payment plans', () => {
    const { container } = render(
      <MemoryRouter>
        <LinkedPaymentPlansTable linkedPaymentPlans={[]} />
      </MemoryRouter>,
      { wrapper: TestProviders },
    );
    expect(container.innerHTML).toBe('');
  });

  it('lists each linked payment plan with a link to its page', () => {
    render(
      <MemoryRouter>
        <LinkedPaymentPlansTable
          linkedPaymentPlans={[
            {
              id: 'group-2',
              unicefId: 'PPG-0002',
              name: 'North follow-up',
              planType: PlanTypeEnum.FOLLOW_UP,
              status: PaymentPlanStatusEnum.OPEN,
            },
            {
              id: 'group-3',
              unicefId: 'PPG-0003',
              name: 'North top-up',
              planType: PlanTypeEnum.TOP_UP,
              status: PaymentPlanStatusEnum.ACCEPTED,
            },
          ]}
        />
      </MemoryRouter>,
      { wrapper: TestProviders },
    );

    expect(screen.getAllByTestId('linked-group-row')).toHaveLength(2);
    expect(
      screen.getByText('PPG-0002').closest('a')?.getAttribute('href'),
    ).toBe(
      '/afghanistan/test-program/payment-module/payment-plans/group-2',
    );
    expect(screen.getByText('Follow Up')).not.toBeNull();
    expect(screen.getByText('Top Up')).not.toBeNull();
  });
});

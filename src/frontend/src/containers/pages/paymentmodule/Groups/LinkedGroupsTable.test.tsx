import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { LinkedGroupsTable } from './LinkedGroupsTable';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ baseUrl: 'afghanistan/test-program' }),
}));

describe('LinkedGroupsTable', () => {
  it('renders nothing without linked groups', () => {
    const { container } = render(
      <MemoryRouter>
        <LinkedGroupsTable linkedGroups={[]} />
      </MemoryRouter>,
      { wrapper: TestProviders },
    );
    expect(container.innerHTML).toBe('');
  });

  it('lists each linked group with a link to its page', () => {
    render(
      <MemoryRouter>
        <LinkedGroupsTable
          linkedGroups={[
            {
              id: 'group-2',
              unicefId: 'PPG-0002',
              name: 'North follow-up',
              planType: PlanTypeEnum.FOLLOW_UP,
              status: PaymentPlanGroupStatusEnum.OPEN,
            },
            {
              id: 'group-3',
              unicefId: 'PPG-0003',
              name: 'North top-up',
              planType: PlanTypeEnum.TOP_UP,
              status: PaymentPlanGroupStatusEnum.ACCEPTED,
            },
          ]}
        />
      </MemoryRouter>,
      { wrapper: TestProviders },
    );

    expect(screen.getAllByTestId('linked-group-row')).toHaveLength(2);
    expect(
      screen.getByText('PPG-0002').closest('a')?.getAttribute('href'),
    ).toBe('/afghanistan/test-program/payment-module/groups/group-2');
    expect(screen.getByText('Follow Up')).not.toBeNull();
    expect(screen.getByText('Top Up')).not.toBeNull();
  });
});

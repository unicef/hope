import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import type { PaginatedPaymentPlanManagerialList } from '@restgenerated/models/PaginatedPaymentPlanManagerialList';
import type { PaymentPlanManagerial } from '@restgenerated/models/PaymentPlanManagerial';
import type { BulkActionMutation } from './types';
import { ApprovalSection } from './ApprovalSection';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ businessArea: 'afghanistan' }),
}));

const paymentPlan = (overrides: Partial<PaymentPlanManagerial>) =>
  ({
    id: 'group-1',
    unicefId: 'PPG-0001',
    name: 'North',
    program: 'Cash Programme',
    programCode: 'prog1',
    lastApprovalProcessDate: '2026-10-01T10:00:00Z',
    lastApprovalProcessBy: 'Approver',
    ...overrides,
  }) as PaymentPlanManagerial;

describe('ApprovalSection', () => {
  it('lists payment plans and links each row to its payment plan page', () => {
    const handleSelect = vi.fn();
    const data = {
      count: 2,
      results: [
        paymentPlan({}),
        paymentPlan({ id: 'group-2', unicefId: 'PPG-0002', name: 'South' }),
      ],
    } as PaginatedPaymentPlanManagerialList;

    render(
      <MemoryRouter>
        <ApprovalSection
          selectedApproved={[]}
          setSelectedApproved={vi.fn()}
          handleSelect={handleSelect}
          handleSelectAll={vi.fn()}
          inApprovalData={data}
          bulkAction={{ mutateAsync: vi.fn() } as unknown as BulkActionMutation}
        />
      </MemoryRouter>,
      { wrapper: TestProviders },
    );

    expect(
      screen.getByText('PPG-0002').closest('a')?.getAttribute('href'),
    ).toBe('/afghanistan/programs/prog1/payment-module/payment-plans/group-2');
    expect(screen.getByText('South')).not.toBeNull();

    const checkbox = within(
      screen.getAllByTestId('select-approval')[1],
    ).getByRole('checkbox');
    fireEvent.click(checkbox);
    expect(handleSelect).toHaveBeenCalledWith(
      [],
      expect.any(Function),
      'group-2',
    );
  });
});

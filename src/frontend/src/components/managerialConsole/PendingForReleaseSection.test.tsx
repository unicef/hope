import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import type { PaginatedPaymentPlanManagerialList } from '@restgenerated/models/PaginatedPaymentPlanManagerialList';
import type { PaymentPlanManagerial } from '@restgenerated/models/PaymentPlanManagerial';
import type { BulkActionMutation, SelectAllHandler } from './types';
import { PendingForReleaseSection } from './PendingForReleaseSection';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ businessArea: 'afghanistan' }),
}));

const paymentPlan = (overrides: Partial<PaymentPlanManagerial>) =>
  ({
    id: 'plan-1',
    unicefId: 'PPG-0001',
    name: 'North',
    program: 'Cash Programme',
    programCode: 'prog1',
    lastApprovalProcessDate: '2026-10-01T10:00:00Z',
    lastApprovalProcessBy: 'Authorizer',
    visionManaged: false,
    ...overrides,
  }) as PaymentPlanManagerial;

const renderSection = (
  data: PaginatedPaymentPlanManagerialList,
  handleSelectAll: SelectAllHandler,
) =>
  render(
    <MemoryRouter>
      <PendingForReleaseSection
        selectedInReview={[]}
        setSelectedInReview={vi.fn()}
        handleSelect={vi.fn()}
        handleSelectAll={handleSelectAll}
        inReviewData={data}
        bulkAction={{ mutateAsync: vi.fn() } as unknown as BulkActionMutation}
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('PendingForReleaseSection', () => {
  it('does not let a Vision-managed payment plan be selected for release', () => {
    const data = {
      count: 2,
      results: [
        paymentPlan({}),
        paymentPlan({
          id: 'plan-2',
          unicefId: 'PPG-0002',
          name: 'South',
          visionManaged: true,
        }),
      ],
    } as PaginatedPaymentPlanManagerialList;

    renderSection(data, vi.fn());

    const checkboxes = screen
      .getAllByTestId('select-release')
      .map((cell) => within(cell).getByRole('checkbox') as HTMLInputElement);
    expect(checkboxes[0].disabled).toBe(false);
    expect(checkboxes[1].disabled).toBe(true);
  });

  it('selects only the payment plans Vision does not manage with select all', () => {
    const handleSelectAll = vi.fn();
    const data = {
      count: 2,
      results: [
        paymentPlan({}),
        paymentPlan({
          id: 'plan-2',
          unicefId: 'PPG-0002',
          visionManaged: true,
        }),
      ],
    } as PaginatedPaymentPlanManagerialList;

    renderSection(data, handleSelectAll);

    fireEvent.click(
      within(screen.getByTestId('select-all-release')).getByRole('checkbox'),
    );
    expect(handleSelectAll).toHaveBeenCalledWith(
      ['plan-1'],
      [],
      expect.any(Function),
    );
  });
});

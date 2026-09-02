import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, renderWithProviders, screen } from 'src/testUtils/testUtils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PERMISSIONS } from 'src/config/permissions';
import ExcludeSection from './ExcludeSection';

vi.mock('@components/core/withErrorBoundary', () => ({
  default: (Component) => Component,
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
  }),
}));

vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({ showMessage: vi.fn() }),
}));

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => [PERMISSIONS.PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP],
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsPaymentPlansExcludeBeneficiariesCreate: vi.fn(() =>
      Promise.resolve({}),
    ),
    restBusinessAreasProgramsPaymentPlansRetrieve: vi.fn(),
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const basePaymentPlan = {
  id: 'payment-plan-1',
  status: PaymentPlanStatusEnum.OPEN,
  backgroundActionStatus: null,
  backgroundActionStatusDisplay: '',
  exclusionReason: 'Awaiting confirmation',
  excludeHouseholdError: '',
  excludedHouseholds: [{ unicefId: 'HH-26-0000.0001' }],
} as const;

function renderComponent(overrides = {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return renderWithProviders(
    <QueryClientProvider client={queryClient}>
      <ExcludeSection
        paymentPlan={{ ...basePaymentPlan, ...overrides } as any}
        initialOpen
      />
    </QueryClientProvider>,
  );
}

describe('ExcludeSection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('enables Save after a failed exclusion so the user can retry', () => {
    renderComponent({ backgroundActionStatus: 'EXCLUDE_BENEFICIARIES_ERROR' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));

    const save = screen.getByRole('button', {
      name: 'Save',
    }) as HTMLButtonElement;
    expect(save.disabled).toBe(false);
  });

  it('disables Save while an exclusion is still running', () => {
    renderComponent({ backgroundActionStatus: 'EXCLUDE_BENEFICIARIES' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));

    const save = screen.getByRole('button', {
      name: 'Save',
    }) as HTMLButtonElement;
    expect(save.disabled).toBe(true);
  });

  it('disables Save while an unrelated background action is running', () => {
    renderComponent({ backgroundActionStatus: 'RULE_ENGINE_RUN' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));

    const save = screen.getByRole('button', {
      name: 'Save',
    }) as HTMLButtonElement;
    expect(save.disabled).toBe(true);
  });

  it('disables Save when another action failed, which the exclude FSM rejects', () => {
    renderComponent({ backgroundActionStatus: 'XLSX_EXPORT_ERROR' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));

    const save = screen.getByRole('button', {
      name: 'Save',
    }) as HTMLButtonElement;
    expect(save.disabled).toBe(true);
  });

  it('enables Apply after a failed exclusion so the user can retry', () => {
    renderComponent({ backgroundActionStatus: 'EXCLUDE_BENEFICIARIES_ERROR' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Households Ids' }), {
      target: { value: 'HH-26-0000.0002' },
    });

    const apply = screen.getByRole('button', {
      name: 'Apply',
    }) as HTMLButtonElement;
    expect(apply.disabled).toBe(false);
  });

  it('disables Apply while an exclusion is still running', () => {
    renderComponent({ backgroundActionStatus: 'EXCLUDE_BENEFICIARIES' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
    fireEvent.change(screen.getByRole('textbox', { name: 'Households Ids' }), {
      target: { value: 'HH-26-0000.0002' },
    });

    const apply = screen.getByRole('button', {
      name: 'Apply',
    }) as HTMLButtonElement;
    expect(apply.disabled).toBe(true);
  });

  it('says the action is running when one is still in progress', async () => {
    renderComponent({ backgroundActionStatus: 'EXCLUDE_BENEFICIARIES' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const save = screen.getByRole('button', { name: 'Save' });
    fireEvent.mouseOver(save.parentElement as HTMLElement);

    expect(
      await screen.findByText(
        'Another background action is currently running on this Payment Plan',
      ),
    ).toBeTruthy();
  });

  it('says the action failed when it is at a terminal error status', async () => {
    renderComponent({ backgroundActionStatus: 'XLSX_EXPORT_ERROR' });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
    const save = screen.getByRole('button', { name: 'Save' });
    fireEvent.mouseOver(save.parentElement as HTMLElement);

    expect(
      await screen.findByText(
        'Another background action on this Payment Plan failed and must be resolved first',
      ),
    ).toBeTruthy();
  });

  it('shows the stored exclusion error when no exclusion reason is set', () => {
    renderComponent({
      exclusionReason: '',
      excludeHouseholdError: "['Something went wrong.']",
    });

    expect(screen.getByText('Something went wrong.')).toBeTruthy();
  });

  it('shows the stored exclusion error while editing the list', () => {
    renderComponent({
      excludeHouseholdError: "['Something went wrong.']",
    });

    fireEvent.click(screen.getByRole('button', { name: 'Edit' }));

    expect(screen.getByText('Something went wrong.')).toBeTruthy();
  });
});

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders, screen } from 'src/testUtils/testUtils';
import { describe, expect, it, vi } from 'vitest';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { PERMISSIONS } from 'src/config/permissions';
import { LockFspPaymentPlan } from './LockFspPaymentPlan';

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

vi.mock('../../../../programContext', () => ({
  useProgramContext: () => ({ isActiveProgram: true }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsPaymentPlansLockFspRetrieve: vi.fn(),
    restBusinessAreasProgramsPaymentPlansRetrieve: vi.fn(),
    restBusinessAreasProgramsPaymentPlansList: vi.fn(),
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

function renderComponent(backgroundActionStatus: string | null) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  renderWithProviders(
    <QueryClientProvider client={queryClient}>
      <LockFspPaymentPlan
        paymentPlan={
          {
            id: 'payment-plan-1',
            status: PaymentPlanStatusEnum.LOCKED,
            backgroundActionStatus,
          } as any
        }
        permissions={[PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP]}
      />
    </QueryClientProvider>,
  );

  return screen.getByRole('button', { name: 'Lock FSP' }) as HTMLButtonElement;
}

describe('LockFspPaymentPlan', () => {
  it('enables Lock FSP when no background action is running', () => {
    expect(renderComponent(null).disabled).toBe(false);
  });

  it('disables Lock FSP while the entitlement formula is running', () => {
    expect(renderComponent('RULE_ENGINE_RUN').disabled).toBe(true);
  });

  it('enables Lock FSP after a failed background action, which the backend allows', () => {
    expect(renderComponent('RULE_ENGINE_ERROR').disabled).toBe(false);
  });
});

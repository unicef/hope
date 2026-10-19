import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../../../config/permissions';
import { PaymentPlansTable } from './PaymentPlansTable';

const permissions = vi.hoisted(() => ({ current: [] as string[] }));
vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => permissions.current,
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    baseUrl: 'afghanistan/programs/prog-1',
    businessArea: 'afghanistan',
    businessAreaSlug: 'afghanistan',
    programId: 'prog-1',
  }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    selectedProgram: { beneficiaryGroup: null },
    isSocialDctType: false,
  }),
}));

vi.mock('@restgenerated/services/RestService', () => {
  const methods = {
    restBusinessAreasProgramsPaymentPlansList: vi.fn(),
    restBusinessAreasProgramsPaymentPlansCountRetrieve: vi.fn(),
  };
  // restQueryKey derives the cache key root from `fn.name`.
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

vi.mock('@components/rest/UniversalRestTable/UniversalRestTable', () => ({
  UniversalRestTable: () => <div data-cy="table" />,
}));

const renderTable = () =>
  render(
    <MemoryRouter>
      <PaymentPlansTable
        programCycle={{ id: 'cycle-1' } as any}
        filter={{ search: '', status: [] }}
        canViewDetails
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('PaymentPlansTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansList,
    ).mockResolvedValue({ results: [], count: 0 } as any);
    vi.mocked(
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve,
    ).mockResolvedValue({ count: 0 });
  });

  it('fetches payment plans when the user can list them', async () => {
    permissions.current = [PERMISSIONS.PM_VIEW_LIST];
    renderTable();

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsPaymentPlansList,
      ).toHaveBeenCalled();
      expect(
        RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve,
      ).toHaveBeenCalled();
    });
  });

  it('does not fetch payment plans without the list permission', async () => {
    // A 403 from the list endpoint redirects the whole page to Access Denied.
    permissions.current = [PERMISSIONS.PM_VIEW_DETAILS];
    renderTable();

    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(
      RestService.restBusinessAreasProgramsPaymentPlansList,
    ).not.toHaveBeenCalled();
    expect(
      RestService.restBusinessAreasProgramsPaymentPlansCountRetrieve,
    ).not.toHaveBeenCalled();
  });
});

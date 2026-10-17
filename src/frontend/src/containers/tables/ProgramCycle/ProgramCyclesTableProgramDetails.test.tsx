import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../config/permissions';
import ProgramCyclesTableProgramDetails from './ProgramCyclesTableProgramDetails';

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

vi.mock('@restgenerated/services/RestService', () => {
  const methods = {
    restBusinessAreasProgramsCyclesList: vi.fn(),
    restBusinessAreasProgramsCyclesCountRetrieve: vi.fn(),
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

vi.mock(
  '@containers/tables/ProgramCycle/NewProgramCycle/AddNewProgramCycle',
  () => ({ default: () => null }),
);

const renderTable = () =>
  render(
    <MemoryRouter>
      <ProgramCyclesTableProgramDetails
        program={{ code: 'prog-1', status: 'ACTIVE' } as any}
      />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('ProgramCyclesTableProgramDetails', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(
      RestService.restBusinessAreasProgramsCyclesList,
    ).mockResolvedValue({ results: [], count: 0 } as any);
    vi.mocked(
      RestService.restBusinessAreasProgramsCyclesCountRetrieve,
    ).mockResolvedValue({ count: 0 });
  });

  it('fetches cycles when the user can list them', async () => {
    permissions.current = [PERMISSIONS.PM_PROGRAMME_CYCLE_VIEW_LIST];
    renderTable();

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasProgramsCyclesList,
      ).toHaveBeenCalled();
      expect(
        RestService.restBusinessAreasProgramsCyclesCountRetrieve,
      ).toHaveBeenCalled();
    });
  });

  it('does not fetch cycles without the list permission', async () => {
    // A 403 from the list endpoint redirects the whole page to Access Denied.
    permissions.current = [PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS];
    renderTable();

    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(
      RestService.restBusinessAreasProgramsCyclesList,
    ).not.toHaveBeenCalled();
    expect(
      RestService.restBusinessAreasProgramsCyclesCountRetrieve,
    ).not.toHaveBeenCalled();
  });
});

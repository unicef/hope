import { beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders, waitFor } from 'src/testUtils/testUtils';
import { RestService } from '@restgenerated/services/RestService';
import { GrievancesTable } from './GrievancesTable';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'ukraine',
    businessAreaSlug: 'ukraine',
    programCode: 'all',
    programId: 'all',
    isAllPrograms: true,
    baseUrl: 'ukraine/programs/all',
  }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({
    isSocialDctType: false,
    selectedProgram: null,
  }),
}));

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => [],
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@restgenerated/services/RestService', () => {
  const methods = {
    restBusinessAreasGrievanceTicketsList: vi.fn(),
    restBusinessAreasGrievanceTicketsCountRetrieve: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsList: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsCountRetrieve: vi.fn(),
    restBusinessAreasUsersList: vi.fn(),
    restBusinessAreasUsersProfileRetrieve: vi.fn(),
    restChoicesGrievanceTicketsRetrieve: vi.fn(),
  };
  // restQueryKey derives the cache key root from `fn.name`.
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

const filter = {
  search: '',
  documentType: '',
  documentNumber: '',
  status: '',
  fsp: '',
  createdAtBefore: '',
  createdAtAfter: '',
  category: '',
  issueType: '',
  assignedTo: '',
  createdBy: '',
  admin1: '',
  admin2: '',
  registrationDataImport: '',
  cashPlan: '',
  scoreMin: '',
  scoreMax: '',
  grievanceType: 'system',
  grievanceStatus: 'active',
  priority: '',
  urgency: '',
  submissionChannel: '',
  preferredLanguage: '',
  program: '',
  areaScope: '',
};

describe('GrievancesTable', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    vi.mocked(
      RestService.restBusinessAreasGrievanceTicketsList,
    ).mockResolvedValue({ next: null, previous: null, results: [] });
    vi.mocked(
      RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
    ).mockResolvedValue({ count: 0 });
    vi.mocked(RestService.restBusinessAreasUsersList).mockResolvedValue({
      next: null,
      previous: null,
      results: [],
    });
    vi.mocked(
      RestService.restBusinessAreasUsersProfileRetrieve,
    ).mockResolvedValue({ id: 'user-1' } as any);
    vi.mocked(
      RestService.restChoicesGrievanceTicketsRetrieve,
    ).mockResolvedValue({
      grievanceTicketStatusChoices: [],
      grievanceTicketCategoryChoices: [],
      grievanceTicketIssueTypeChoices: [],
      grievanceTicketPriorityChoices: [],
      grievanceTicketUrgencyChoices: [],
    } as any);
  });

  it('requests the list and the count exactly once on mount', async () => {
    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <GrievancesTable filter={filter} selectedTab={0} />
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasGrievanceTicketsList,
      ).toHaveBeenCalled();
      expect(
        RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
      ).toHaveBeenCalled();
    });
    // Give any stray re-render a chance to fire a second request.
    await new Promise((resolve) => setTimeout(resolve, 50));

    const listMock = vi.mocked(
      RestService.restBusinessAreasGrievanceTicketsList,
    );
    expect(listMock).toHaveBeenCalledTimes(1);
    expect(listMock).toHaveBeenCalledWith(
      expect.objectContaining({
        businessAreaSlug: 'ukraine',
        grievanceType: 'system',
        grievanceStatus: 'active',
        isActiveProgram: true,
        ordering: '-created_at',
        limit: 10,
        offset: 0,
      }),
    );

    const countMock = vi.mocked(
      RestService.restBusinessAreasGrievanceTicketsCountRetrieve,
    );
    expect(countMock).toHaveBeenCalledTimes(1);
    const countParams = countMock.mock.calls[0][0];
    expect(countParams).toEqual(
      expect.objectContaining({
        businessAreaSlug: 'ukraine',
        grievanceType: 'system',
        grievanceStatus: 'active',
        isActiveProgram: true,
      }),
    );
    expect(countParams).not.toHaveProperty('ordering');
    expect(countParams).not.toHaveProperty('limit');
    expect(countParams).not.toHaveProperty('offset');
  });
});

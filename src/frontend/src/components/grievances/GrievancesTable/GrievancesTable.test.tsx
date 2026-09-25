import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../config/permissions';
import { GrievancesTable } from './GrievancesTable';

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => [PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE],
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    baseUrl: 'afghanistan/programs/all',
    businessArea: 'afghanistan',
    businessAreaSlug: 'afghanistan',
    programCode: 'all',
    programId: 'all',
    isAllPrograms: true,
    isGlobal: false,
  }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@restgenerated/services/RestService', () => {
  const methods = {
    restChoicesGrievanceTicketsRetrieve: vi.fn(),
    restBusinessAreasUsersProfileRetrieve: vi.fn(),
    restBusinessAreasUsersList: vi.fn(),
    restBusinessAreasGrievanceTicketsList: vi.fn(),
    restBusinessAreasGrievanceTicketsCountRetrieve: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsList: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsCountRetrieve: vi.fn(),
  };
  // restQueryKey derives the cache key root from `fn.name`.
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

const TICKETS = [
  { id: 'ticket-1', status: 1, category: 3 },
  { id: 'ticket-2', status: 1, category: 3 },
];

// The real table is exercised elsewhere; here it is a probe for the params the query is built
// with and for how many rows are still ticked.
const universalTableProps = vi.fn();
vi.mock('@components/rest/UniversalRestTable/UniversalRestTable', () => ({
  UniversalRestTable: (props: any) => {
    universalTableProps(props);
    return (
      <button
        data-cy="select-all"
        onClick={() => props.onSelectAllClick(null, TICKETS)}
      >
        {props.numSelected}
      </button>
    );
  },
}));

const BASE_FILTER = {
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
  grievanceType: '',
  grievanceStatus: 'active',
  priority: '',
  urgency: '',
  submissionChannel: '',
  preferredLanguage: '',
  program: '',
  areaScope: 'all',
  overdue: '',
  sensitive: '',
};

const renderTable = (props: Record<string, unknown> = {}) =>
  render(
    <MemoryRouter>
      <GrievancesTable filter={BASE_FILTER} {...props} />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

const listParams = () =>
  (RestService.restBusinessAreasGrievanceTicketsList as any).mock.calls.at(
    -1,
  )?.[0];

describe('GrievancesTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (RestService.restChoicesGrievanceTicketsRetrieve as any).mockResolvedValue({
      grievanceTicketCategoryChoices: [],
      grievanceTicketIssueTypeChoices: [],
      grievanceTicketPriorityChoices: [],
      grievanceTicketUrgencyChoices: [],
      grievanceTicketStatusChoices: [],
    });
    (
      RestService.restBusinessAreasUsersProfileRetrieve as any
    ).mockResolvedValue({ id: 'user-1' });
    (RestService.restBusinessAreasUsersList as any).mockResolvedValue({
      results: [],
    });
    (
      RestService.restBusinessAreasGrievanceTicketsList as any
    ).mockResolvedValue({ results: TICKETS, count: TICKETS.length });
    (
      RestService.restBusinessAreasGrievanceTicketsCountRetrieve as any
    ).mockResolvedValue({ count: TICKETS.length });
  });

  it('requests the list and the count exactly once on mount', async () => {
    renderTable();

    // Wait until both responses have landed and been rendered. A duplicate request would come
    // from state being rewritten after mount, which happens before this point.
    await waitFor(() => {
      const props = universalTableProps.mock.lastCall?.[0];
      expect(props?.isFetching).toBe(false);
      expect(props?.data?.results).toEqual(TICKETS);
      expect(props?.itemsCount).toBe(TICKETS.length);
    });

    const listMock = vi.mocked(
      RestService.restBusinessAreasGrievanceTicketsList,
    );
    expect(listMock).toHaveBeenCalledTimes(1);
    expect(listMock).toHaveBeenCalledWith(
      expect.objectContaining({
        businessAreaSlug: 'afghanistan',
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
        businessAreaSlug: 'afghanistan',
        grievanceStatus: 'active',
        isActiveProgram: true,
      }),
    );
    expect(countParams).not.toHaveProperty('ordering');
    expect(countParams).not.toHaveProperty('limit');
    expect(countParams).not.toHaveProperty('offset');
  });

  it('sends the sensitivity filter to the list endpoint', async () => {
    renderTable({ filter: { ...BASE_FILTER, sensitive: 'false' } });

    await screen.findByTestId('select-all');
    // 'false' means "every category but sensitive" on the backend, so it has to survive the
    // empty-param stripping rather than being treated as unset.
    await waitFor(() => expect(listParams().sensitive).toBe('false'));
  });

  it('omits the sensitivity filter when the page does not use it', async () => {
    renderTable({ filter: { ...BASE_FILTER, sensitive: '' } });

    await screen.findByTestId('select-all');
    await waitFor(() => expect(listParams()).not.toHaveProperty('sensitive'));
  });

  it('clears the selection when the query changes', async () => {
    const { rerender } = renderTable({
      extraQueryParams: { unassigned: true },
    });

    const selectAll = await screen.findByTestId('select-all');
    selectAll.click();
    await waitFor(() => expect(selectAll.textContent).toBe('2'));

    // Switching tab swaps the pinned params. The previously ticked rows are not in the new list,
    // but they would still have been picked up by a bulk action.
    rerender(
      <MemoryRouter>
        <GrievancesTable
          filter={BASE_FILTER}
          extraQueryParams={{ assignedTo: 'user-1' }}
        />
      </MemoryRouter>,
    );

    await waitFor(() =>
      expect(screen.getByTestId('select-all').textContent).toBe('0'),
    );
  });
});

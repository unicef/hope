import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import type { ReactElement } from 'react';
import { TestProviders } from 'src/testUtils/testProviders';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { restQueryKey } from '@utils/queryKeys';
import { PERMISSIONS } from '../../../config/permissions';
import { MyTasksPage } from './MyTasksPage';

let mockPermissions: string[] = [];
vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => mockPermissions,
}));

let mockProgramCode = 'all';
vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    baseUrl: `afghanistan/programs/${mockProgramCode}`,
    businessArea: 'afghanistan',
    businessAreaSlug: 'afghanistan',
    programCode: mockProgramCode,
    programId: mockProgramCode,
    isAllPrograms: mockProgramCode === 'all',
    isGlobal: false,
  }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@restgenerated/services/RestService', () => {
  // restQueryKey derives the cache key root from fn.name, so name the spies.
  const methods = {
    restChoicesGrievanceTicketsRetrieve: vi.fn(),
    restBusinessAreasGrievanceTicketsMyTasksVisitCreate: vi.fn(),
    restBusinessAreasGrievanceTicketsMyTasksMarkReadCreate: vi.fn(),
    // Not called here (the table is stubbed), but mark-read builds query keys from their names.
    restBusinessAreasGrievanceTicketsList: vi.fn(),
    restBusinessAreasGrievanceTicketsCountRetrieve: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsList: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsCountRetrieve: vi.fn(),
  };
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

// The table and the filter bar are exercised elsewhere; here we only care that the page hands
// the table the right preset params, so both are stubbed out.
const tableProps = vi.fn();
vi.mock('@components/grievances/GrievancesTable/GrievancesTable', () => ({
  GrievancesTable: (props: any) => {
    tableProps(props);
    return <div data-cy="grievances-table" />;
  },
}));

const filtersProps = vi.fn();
vi.mock('@components/grievances/MyTasks/MyTasksFilters', () => ({
  MyTasksFilters: (props: any) => {
    filtersProps(props);
    return <div data-cy="my-tasks-filters" />;
  },
}));

const ALL_PERMISSIONS = [
  PERMISSIONS.GRIEVANCE_ASSIGN,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
];

const APPROVE_PERMISSION = PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE;

const LocationProbe = (): ReactElement => {
  const location = useLocation();
  return <div data-cy="location-search">{location.search}</div>;
};

// Stands in for the stubbed table's list query, so a test can see it being invalidated.
const ListProbe = (): ReactElement => {
  useQuery({
    queryKey: restQueryKey(RestService.restBusinessAreasGrievanceTicketsList, {
      businessAreaSlug: 'afghanistan',
    }),
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsList({
        businessAreaSlug: 'afghanistan',
      }),
  });
  return null;
};

const renderPage = (search: string) =>
  render(
    <MemoryRouter
      initialEntries={[`/afghanistan/programs/all/grievance/my-tasks${search}`]}
    >
      <MyTasksPage />
      <LocationProbe />
      <ListProbe />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

const lastTableProps = () => tableProps.mock.calls.at(-1)?.[0];
const lastFiltersProps = () => filtersProps.mock.calls.at(-1)?.[0];

describe('MyTasksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPermissions = [...ALL_PERMISSIONS];
    mockProgramCode = 'all';
    (RestService.restChoicesGrievanceTicketsRetrieve as any).mockResolvedValue({
      grievanceTicketCategoryChoices: [],
      grievanceTicketIssueTypeChoices: [],
      grievanceTicketPriorityChoices: [],
      grievanceTicketUrgencyChoices: [],
      grievanceTicketStatusChoices: [],
    });
    (
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate as any
    ).mockResolvedValue({ unreadTabs: [] });
    (
      RestService.restBusinessAreasGrievanceTicketsList as any
    ).mockResolvedValue({ count: 0, results: [] });
  });

  it('sends the needs-assignment tab and pins it to active tickets', async () => {
    renderPage('?tab=needs-assignment&sensitive=true');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      // Active is pinned rather than merely defaulted: a closed unassigned ticket can never be
      // acted on from this tab, and the email's count leaves it out too.
      expect(lastTableProps().extraQueryParams).toEqual({
        myTasksTab: 'needs-assignment',
        grievanceStatus: 'active',
      }),
    );
    expect(lastTableProps().filter.sensitive).toBe(true);
    // No approve grant, so no Pending Approval tab.
    expect(screen.getAllByRole('tab')).toHaveLength(2);
    expect(screen.getByRole('tab', { selected: true }).textContent).toBe(
      'NEEDS ASSIGNMENT',
    );
  });

  it('reads ?sensitive=false from the URL into the filter', async () => {
    renderPage('?tab=mine&sensitive=false');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({
        myTasksTab: 'mine',
      }),
    );
    // Asserted explicitly: were this dropped, the list would silently widen to every ticket
    // assigned to the user, sensitive ones included.
    expect(lastTableProps().filter.sensitive).toBe(false);
  });

  it('leaves sensitivity unset when the email did not narrow it', async () => {
    renderPage('?tab=mine');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({
        myTasksTab: 'mine',
      }),
    );
    expect(lastTableProps().filter.sensitive).toBe('');
  });

  it('composes ?sensitive= with ?overdue=', async () => {
    renderPage('?tab=mine&sensitive=true&overdue=true');

    await screen.findByTestId('grievances-table');
    await waitFor(() => expect(lastTableProps().filter.overdue).toBe(true));
    expect(lastTableProps().filter.sensitive).toBe(true);
  });

  it('falls back to the first permitted tab and states it in the URL', async () => {
    renderPage('');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(screen.getByTestId('location-search').textContent).toContain(
        'tab=needs-assignment',
      ),
    );
  });

  it('only offers the tabs the user holds permissions for', async () => {
    mockPermissions = [PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE];
    renderPage('');

    await screen.findByTestId('grievances-table');
    expect(screen.getAllByRole('tab')).toHaveLength(1);
  });

  it('pins sensitivity and hides its filter when only one half is granted', async () => {
    mockPermissions = [PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE];
    renderPage('?tab=mine&sensitive=false');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      // The pinned param is spread last by the table, so it beats the ?sensitive=false the URL
      // asked for rather than showing tickets the user may not see.
      expect(lastTableProps().extraQueryParams).toEqual({
        myTasksTab: 'mine',
        sensitive: 'true',
      }),
    );
    expect(lastFiltersProps().showSensitiveFilter).toBe(false);
    // Folded into the filter as well, so the category list narrows the same way it would for a
    // value the user picked themselves.
    expect(lastFiltersProps().filter.sensitive).toBe('true');
    expect(lastTableProps().filter.sensitive).toBe('true');
  });

  it('hides the ticket-status filter on the active-only tabs', async () => {
    mockPermissions = [...ALL_PERMISSIONS, APPROVE_PERMISSION];
    renderPage('?tab=needs-assignment');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastFiltersProps().showStatusFilter).toBe(false),
    );

    fireEvent.click(screen.getByRole('tab', { name: 'ASSIGNED TO ME' }));
    await waitFor(() => expect(lastFiltersProps().showStatusFilter).toBe(true));

    fireEvent.click(screen.getByRole('tab', { name: 'PENDING APPROVAL' }));
    await waitFor(() =>
      expect(lastFiltersProps().showStatusFilter).toBe(false),
    );
  });

  it('offers Pending Approval to a list viewer who can approve or close', async () => {
    mockPermissions = [
      PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
      APPROVE_PERMISSION,
    ];
    renderPage('?tab=pending-approval');

    await screen.findByTestId('grievances-table');
    expect(screen.getByRole('tab', { selected: true }).textContent).toBe(
      'PENDING APPROVAL',
    );
    await waitFor(() =>
      // Only the non-sensitive half is granted, so sensitivity is pinned too.
      expect(lastTableProps().extraQueryParams).toEqual({
        myTasksTab: 'pending-approval',
        sensitive: 'false',
      }),
    );
  });

  it('withholds Pending Approval from an approver with no list-view grant', async () => {
    mockPermissions = [APPROVE_PERMISSION];
    renderPage('?tab=pending-approval');

    expect(await screen.findByText('Permission Denied')).toBeTruthy();
  });

  it('sends unread=true only while Only unread is applied', async () => {
    // Applying a filter scrolls to the table, which jsdom does not implement.
    Element.prototype.scrollIntoView = vi.fn();
    renderPage('?tab=mine&unread=true');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({
        myTasksTab: 'mine',
        unread: true,
      }),
    );

    lastFiltersProps().setAppliedFilter({
      ...lastFiltersProps().appliedFilter,
      unread: '',
    });
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({ myTasksTab: 'mine' }),
    );
  });

  it('refetches the table on every mount so opened tickets lose their highlight', async () => {
    renderPage('?tab=mine');

    await screen.findByTestId('grievances-table');
    expect(lastTableProps().refetchOnMount).toBe('always');
  });

  it('puts a dot on each tab the visit call reports unread', async () => {
    (
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate as any
    ).mockResolvedValue({ unreadTabs: ['mine'] });
    renderPage('?tab=needs-assignment');

    await screen.findByTestId('grievances-table');
    expect(
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate,
    ).toHaveBeenCalledWith({ businessAreaSlug: 'afghanistan' });
    expect(await screen.findByTestId('tab-unread-dot-mine')).toBeTruthy();
    expect(screen.queryByTestId('tab-unread-dot-needs-assignment')).toBeNull();
  });

  it('marks the active tab read and takes the dots from the answer', async () => {
    (
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate as any
    ).mockResolvedValue({ unreadTabs: ['mine', 'needs-assignment'] });
    (
      RestService.restBusinessAreasGrievanceTicketsMyTasksMarkReadCreate as any
    ).mockResolvedValue({ unreadTabs: ['needs-assignment'] });
    renderPage('?tab=mine');

    await screen.findByTestId('tab-unread-dot-mine');
    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsList,
      ).toHaveBeenCalledTimes(1),
    );
    const { toolbarActions } = lastTableProps();
    render(toolbarActions, { wrapper: TestProviders });
    const button = screen.getByTestId('button-mark-all-read');
    expect(button.hasAttribute('disabled')).toBe(false);
    fireEvent.click(button);

    await waitFor(() =>
      expect(screen.queryByTestId('tab-unread-dot-mine')).toBeNull(),
    );
    expect(
      RestService.restBusinessAreasGrievanceTicketsMyTasksMarkReadCreate,
    ).toHaveBeenCalledWith({
      businessAreaSlug: 'afghanistan',
      formData: { tab: 'mine' },
    });
    expect(screen.getByTestId('tab-unread-dot-needs-assignment')).toBeTruthy();
    // The rows just marked read must lose their highlight, so the list is refetched.
    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsList,
      ).toHaveBeenCalledTimes(2),
    );
  });

  it('scopes the dots and Mark all as read to the selected programme', async () => {
    mockProgramCode = 'PRG1';
    (
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate as any
    ).mockResolvedValue({ unreadTabs: ['mine'] });
    (
      RestService.restBusinessAreasGrievanceTicketsMyTasksMarkReadCreate as any
    ).mockResolvedValue({ unreadTabs: [] });
    renderPage('?tab=mine');

    await screen.findByTestId('tab-unread-dot-mine');
    expect(
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate,
    ).toHaveBeenCalledWith({
      businessAreaSlug: 'afghanistan',
      formData: { program: 'PRG1' },
    });
    const { toolbarActions } = lastTableProps();
    render(toolbarActions, { wrapper: TestProviders });
    fireEvent.click(screen.getByTestId('button-mark-all-read'));

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsMyTasksMarkReadCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        formData: { tab: 'mine', program: 'PRG1' },
      }),
    );
  });

  it('asks for the dots again on a tab switch', async () => {
    renderPage('?tab=mine');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate,
      ).toHaveBeenCalledTimes(1),
    );
    fireEvent.click(screen.getByRole('tab', { name: 'NEEDS ASSIGNMENT' }));

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate,
      ).toHaveBeenCalledTimes(2),
    );
  });

  it('denies access to a user with none of the preset permissions', async () => {
    mockPermissions = [PERMISSIONS.GRIEVANCES_CREATE];
    renderPage('');

    expect(await screen.findByText('Permission Denied')).toBeTruthy();
    expect(screen.queryByTestId('grievances-table')).toBeNull();
    // The visit would 403 and the global handler would replace the page with Access Denied.
    expect(
      RestService.restBusinessAreasGrievanceTicketsMyTasksVisitCreate,
    ).not.toHaveBeenCalled();
  });

  it('denies access to a user who can assign but holds no list-view grant', async () => {
    mockPermissions = [PERMISSIONS.GRIEVANCE_ASSIGN];
    renderPage('');

    expect(await screen.findByText('Permission Denied')).toBeTruthy();
    expect(screen.queryByTestId('grievances-table')).toBeNull();
  });

  it('clears the category from state and URL on a tab switch, keeping overdue', async () => {
    renderPage('?tab=mine&overdue=true&category=3');

    await screen.findByTestId('grievances-table');
    fireEvent.click(screen.getByRole('tab', { name: 'NEEDS ASSIGNMENT' }));

    await waitFor(() =>
      expect(screen.getByTestId('location-search').textContent).toContain(
        'tab=needs-assignment',
      ),
    );
    const search = screen.getByTestId('location-search').textContent;
    expect(search).toContain('overdue=true');
    // Left in the URL it would come back on the next reload, contradicting the cleared state.
    expect(search).not.toContain('category=3');
    await waitFor(() => expect(lastTableProps().filter.category).toBe(''));
    expect(lastTableProps().filter.grievanceStatus).toBe('active');
  });

  it('orders by total days and uses the narrow My Tasks column set', async () => {
    renderPage('?tab=mine');

    await screen.findByTestId('grievances-table');
    expect(lastTableProps().defaultOrderBy).toBe('total_days');
    expect(lastTableProps().columns).toEqual([
      'unicef_id',
      'category',
      'issueType',
      'priority',
      'urgency',
      'total_days',
    ]);
  });
});

import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import type { ReactElement } from 'react';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../config/permissions';
import { MyTasksPage } from './MyTasksPage';

let mockPermissions: string[] = [];
vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => mockPermissions,
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

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restChoicesGrievanceTicketsRetrieve: vi.fn(),
    restBusinessAreasUsersProfileRetrieve: vi.fn(),
  },
}));

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

const CURRENT_USER_ID = 'user-1';

const ALL_PERMISSIONS = [
  PERMISSIONS.GRIEVANCE_ASSIGN,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_SENSITIVE,
  PERMISSIONS.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
];

const LocationProbe = (): ReactElement => {
  const location = useLocation();
  return <div data-cy="location-search">{location.search}</div>;
};

const renderPage = (search: string) =>
  render(
    <MemoryRouter
      initialEntries={[`/afghanistan/programs/all/grievance/my-tasks${search}`]}
    >
      <MyTasksPage />
      <LocationProbe />
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

const lastTableProps = () => tableProps.mock.calls.at(-1)?.[0];
const lastFiltersProps = () => filtersProps.mock.calls.at(-1)?.[0];

describe('MyTasksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPermissions = [...ALL_PERMISSIONS];
    (RestService.restChoicesGrievanceTicketsRetrieve as any).mockResolvedValue({
      grievanceTicketCategoryChoices: [],
      grievanceTicketIssueTypeChoices: [],
      grievanceTicketPriorityChoices: [],
      grievanceTicketUrgencyChoices: [],
      grievanceTicketStatusChoices: [],
    });
    (
      RestService.restBusinessAreasUsersProfileRetrieve as any
    ).mockResolvedValue({ id: CURRENT_USER_ID });
  });

  it('pins the needs-assignment tab to unassigned active tickets', async () => {
    renderPage('?tab=needs-assignment&sensitive=true');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      // Active is pinned rather than merely defaulted: a closed unassigned ticket can never be
      // acted on from this tab, and the email's count leaves it out too.
      expect(lastTableProps().extraQueryParams).toEqual({
        unassigned: true,
        grievanceStatus: 'active',
      }),
    );
    expect(lastTableProps().filter.sensitive).toBe(true);
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
        assignedTo: CURRENT_USER_ID,
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
        assignedTo: CURRENT_USER_ID,
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
        assignedTo: CURRENT_USER_ID,
        sensitive: 'true',
      }),
    );
    expect(lastFiltersProps().showSensitiveFilter).toBe(false);
    // Folded into the filter as well, so the category list narrows the same way it would for a
    // value the user picked themselves.
    expect(lastFiltersProps().filter.sensitive).toBe('true');
    expect(lastTableProps().filter.sensitive).toBe('true');
  });

  it('hides the ticket-status filter on the needs-assignment tab only', async () => {
    renderPage('?tab=needs-assignment');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastFiltersProps().showStatusFilter).toBe(false),
    );

    fireEvent.click(screen.getByRole('tab', { name: 'ASSIGNED TO ME' }));
    await waitFor(() => expect(lastFiltersProps().showStatusFilter).toBe(true));
  });

  it('denies access to a user with none of the preset permissions', async () => {
    mockPermissions = [PERMISSIONS.GRIEVANCES_CREATE];
    renderPage('');

    expect(await screen.findByText('Permission Denied')).toBeTruthy();
    expect(screen.queryByTestId('grievances-table')).toBeNull();
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

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

  it('turns ?tab=mine-sensitive into an assigned-to-me sensitive query', async () => {
    renderPage('?tab=mine-sensitive');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({
        assignedTo: CURRENT_USER_ID,
        sensitive: 'true',
      }),
    );
    expect(screen.getByRole('tab', { selected: true }).textContent).toBe(
      'ASSIGNED TO ME - SENSITIVE',
    );
  });

  it('sends sensitive=false on the "other" preset', async () => {
    renderPage('?tab=mine');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      // Asserted explicitly: were this dropped, the tab would silently widen to every ticket
      // assigned to the user, sensitive ones included.
      expect(lastTableProps().extraQueryParams).toEqual({
        assignedTo: CURRENT_USER_ID,
        sensitive: 'false',
      }),
    );
  });

  it('composes ?overdue=true with the needs-assignment preset', async () => {
    renderPage('?tab=needs-assignment&overdue=true');

    await screen.findByTestId('grievances-table');
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({ unassigned: true }),
    );
    expect(lastTableProps().filter.overdue).toBe(true);
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
    await waitFor(() =>
      expect(lastTableProps().extraQueryParams).toEqual({
        assignedTo: CURRENT_USER_ID,
        sensitive: 'false',
      }),
    );
  });

  it('denies access to a user with none of the preset permissions', async () => {
    mockPermissions = [PERMISSIONS.GRIEVANCES_CREATE];
    renderPage('');

    expect(await screen.findByText('Permission Denied')).toBeTruthy();
    expect(screen.queryByTestId('grievances-table')).toBeNull();
  });

  it('keeps overdue in the URL and clears the category when switching tab', async () => {
    renderPage('?tab=needs-assignment&overdue=true&category=3');

    await screen.findByTestId('grievances-table');
    fireEvent.click(
      screen.getByRole('tab', { name: 'ASSIGNED TO ME - OTHER' }),
    );

    await waitFor(() =>
      expect(screen.getByTestId('location-search').textContent).toContain(
        'overdue=true',
      ),
    );
    expect(screen.getByTestId('location-search').textContent).toContain(
      'tab=mine',
    );
    await waitFor(() => expect(lastTableProps().filter.category).toBe(''));
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

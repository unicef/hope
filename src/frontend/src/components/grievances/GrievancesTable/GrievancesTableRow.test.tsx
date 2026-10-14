import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import type { GrievanceTicketList } from '@restgenerated/models/GrievanceTicketList';
import { TestProviders } from 'src/testUtils/testProviders';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { GrievancesTableRow } from './GrievancesTableRow';
import type { GrievanceColumnId } from './GrievancesTableColumns';
import {
  DEFAULT_GRIEVANCE_COLUMNS,
  MY_TASKS_COLUMNS,
} from './GrievancesTableColumns';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    baseUrl: 'afghanistan/programs/all',
    businessArea: 'afghanistan',
    isAllPrograms: true,
  }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({ isSocialDctType: false }),
}));

vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({ showMessage: vi.fn() }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@restgenerated/services/RestService', () => {
  // restQueryKey derives the cache key root from fn.name, so name the spies.
  const methods = {
    restBusinessAreasGrievanceTicketsRelatedTicketsList: vi.fn(() =>
      Promise.resolve([]),
    ),
    restBusinessAreasGrievanceTicketsBulkUpdateAssigneeCreate: vi.fn(),
    restBusinessAreasProgramsGrievanceTicketsList: vi.fn(),
  };
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

const ticket = {
  id: 'ticket-1',
  unicefId: 'GRV-0001',
  status: GRIEVANCE_TICKET_STATES.ASSIGNED,
  assignedTo: { id: 'user-1', firstName: 'Ada', lastName: 'Lovelace' },
  category: 4,
  issueType: null,
  targetId: 'HH-0001',
  householdUnicefId: 'HH-0001',
  priority: 1,
  urgency: 2,
  createdAt: '2026-01-02T00:00:00Z',
  userModified: '2026-01-03T00:00:00Z',
  totalDays: 42,
  programs: [{ id: 'prog-1', code: 'PRG', name: 'Test Programme' }],
} as unknown as GrievanceTicketList;

const statusChoices = { 2: 'Assigned' };
const categoryChoices = { 4: 'Grievance Complaint' };
const priorityChoicesData = [
  { value: 1, name: 'High' },
  { value: 2, name: 'Medium' },
];
const urgencyChoicesData = [
  { value: 1, name: 'Very urgent' },
  { value: 2, name: 'Urgent' },
];

const renderRow = (columns: GrievanceColumnId[]) =>
  render(
    <MemoryRouter>
      <table>
        <tbody>
          <GrievancesTableRow
            ticket={ticket}
            statusChoices={statusChoices}
            categoryChoices={categoryChoices}
            issueTypeChoicesData={[]}
            priorityChoicesData={priorityChoicesData}
            urgencyChoicesData={urgencyChoicesData}
            canViewDetails
            checkboxClickHandler={vi.fn()}
            isSelected={false}
            optionsData={[]}
            setInputValue={vi.fn()}
            columns={columns}
          />
        </tbody>
      </table>
    </MemoryRouter>,
    { wrapper: TestProviders },
  );

describe('GrievancesTableRow', () => {
  it('renders one cell per column, plus the checkbox', () => {
    const { container } = renderRow(DEFAULT_GRIEVANCE_COLUMNS);

    expect(container.querySelectorAll('tbody tr td')).toHaveLength(
      DEFAULT_GRIEVANCE_COLUMNS.length + 1,
    );
    expect(screen.getByText('GRV-0001')).toBeTruthy();
    expect(screen.getByText('Grievance Complaint')).toBeTruthy();
    expect(screen.getByText('High')).toBeTruthy();
    expect(screen.getByText('Urgent')).toBeTruthy();
    expect(screen.getByText('42')).toBeTruthy();
  });

  it('renders only the My Tasks columns when given that list', () => {
    const { container } = renderRow(MY_TASKS_COLUMNS);

    expect(container.querySelectorAll('tbody tr td')).toHaveLength(
      MY_TASKS_COLUMNS.length + 1,
    );
    // The preset pins both, so neither column is built for this list.
    expect(screen.queryByText('Assigned')).toBeNull();
    expect(screen.queryByRole('combobox')).toBeNull();
  });
});

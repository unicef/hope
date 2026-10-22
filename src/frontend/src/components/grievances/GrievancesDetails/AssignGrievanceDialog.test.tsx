import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { AssignGrievanceDialog } from './AssignGrievanceDialog';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessAreaSlug: 'afghanistan',
  }),
}));

vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({ showMessage: vi.fn() }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('../GrievancesTable/AssignedToDropdown', () => ({
  AssignedToDropdown: ({ onFilterChange }) => (
    <button
      type="button"
      data-cy="pick-officer"
      onClick={() => onFilterChange({ id: 'officer-1', email: 'o@x.org' })}
    >
      pick
    </button>
  ),
}));

vi.mock('@restgenerated/services/RestService', () => {
  // restQueryKey derives the cache key root from fn.name, so name the spies.
  const methods = {
    restBusinessAreasGrievanceTicketsBulkUpdateAssigneeCreate: vi.fn(() =>
      Promise.resolve([]),
    ),
    restBusinessAreasGrievanceTicketsRetrieve: vi.fn(),
    restBusinessAreasUsersList: vi.fn(() => Promise.resolve({ results: [] })),
  };
  for (const [name, fn] of Object.entries(methods)) {
    Object.defineProperty(fn, 'name', { value: name, configurable: true });
  }
  return { RestService: methods };
});

const assignMock = vi.mocked(
  RestService.restBusinessAreasGrievanceTicketsBulkUpdateAssigneeCreate,
);

const byCy = (cy: string): HTMLElement =>
  document.querySelector(`[data-cy="${cy}"]`) as HTMLElement;

const renderDialog = () => {
  render(
    <AssignGrievanceDialog
      ticketId="ticket-1"
      currentUserId="me-1"
      programCode="PRG"
    />,
    {
      wrapper: TestProviders,
    },
  );
  fireEvent.click(screen.getByText('ASSIGN'));
};

describe('AssignGrievanceDialog', () => {
  beforeEach(() => {
    assignMock.mockClear();
  });

  it('assigns the ticket to the current user by default', async () => {
    renderDialog();

    expect(byCy('pick-officer')).toBeNull();
    fireEvent.click(byCy('button-confirm-assign'));

    await waitFor(() =>
      expect(assignMock).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        formData: { assignedTo: 'me-1', grievanceTicketIds: ['ticket-1'] },
      }),
    );
  });

  it('assigns the ticket to the picked officer', async () => {
    renderDialog();

    fireEvent.click(byCy('radio-assign-to-other').querySelector('input'));
    expect((byCy('button-confirm-assign') as HTMLButtonElement).disabled).toBe(
      true,
    );
    expect(RestService.restBusinessAreasUsersList).toHaveBeenCalledWith(
      expect.objectContaining({ program: 'PRG' }),
    );

    fireEvent.click(byCy('pick-officer'));
    fireEvent.click(byCy('button-confirm-assign'));

    await waitFor(() =>
      expect(assignMock).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        formData: {
          assignedTo: 'officer-1',
          grievanceTicketIds: ['ticket-1'],
        },
      }),
    );
  });
});

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { RestService } from '@restgenerated/services/RestService';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { TestProviders } from 'src/testUtils/testProviders';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RequestedPhotoErrorDataChange } from './RequestedPhotoErrorDataChange';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    businessAreaSlug: 'afghanistan',
  }),
}));

const showMessage = vi.fn();
vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({ showMessage }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasGrievanceTicketsApproveIndividualDataChangeCreate: vi.fn(),
  },
}));

const makeTicket = (
  overrides: Partial<{
    status: string;
    photo: Record<string, unknown>;
  }> = {},
): GrievanceTicketDetail =>
  ({
    id: 'ticket-1',
    status: overrides.status ?? GRIEVANCE_TICKET_STATES.FOR_APPROVAL,
    ticketDetails: {
      individualData: {
        photo: overrides.photo ?? {
          value: '/api/uploads/new.png',
          previousValue: '/api/uploads/old.png',
          approveStatus: false,
        },
      },
    },
  }) as unknown as GrievanceTicketDetail;

const renderComponent = (ticket: GrievanceTicketDetail, canApprove = true) =>
  render(
    <RequestedPhotoErrorDataChange
      ticket={ticket}
      canApproveDataChange={canApprove}
    />,
    { wrapper: TestProviders },
  );

describe('RequestedPhotoErrorDataChange', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the current and new photo previews', () => {
    renderComponent(makeTicket());
    const previews = screen.getAllByTestId(
      'photo-error-preview',
    ) as HTMLImageElement[];
    expect(previews).toHaveLength(2);
    expect(previews[0].src).toContain('/api/uploads/old.png'); // current
    expect(previews[1].src).toContain('/api/uploads/new.png'); // new
  });

  it('shows a placeholder when the new photo has not been uploaded yet', () => {
    renderComponent(
      makeTicket({
        photo: {
          value: null,
          previousValue: '/api/uploads/old.png',
          approveStatus: false,
        },
      }),
    );
    expect(screen.getByTestId('photo-error-no-photo')).toBeTruthy();
  });

  it('disables the approve button unless the ticket is for approval', () => {
    renderComponent(makeTicket({ status: GRIEVANCE_TICKET_STATES.IN_PROGRESS }));
    expect(
      (screen.getByTestId('button-approve') as HTMLButtonElement).disabled,
    ).toBe(true);
  });

  it('approves the photo change with photo: true', async () => {
    (
      RestService.restBusinessAreasGrievanceTicketsApproveIndividualDataChangeCreate as ReturnType<
        typeof vi.fn
      >
    ).mockResolvedValue({});
    renderComponent(makeTicket());

    fireEvent.click(
      document.querySelector('input[type="checkbox"]') as HTMLInputElement,
    );
    fireEvent.click(screen.getByTestId('button-approve'));

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsApproveIndividualDataChangeCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        id: 'ticket-1',
        formData: { individualApproveData: { photo: true } },
      }),
    );
  });
});

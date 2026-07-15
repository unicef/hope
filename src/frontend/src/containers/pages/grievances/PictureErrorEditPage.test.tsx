import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { TestProviders } from 'src/testUtils/testProviders';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../config/permissions';
import PictureErrorEditPage from './PictureErrorEditPage';

// Router hooks/components the page depends on.
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  useParams: () => ({ id: 'ticket-1' }),
  Link: ({ children, to, ...props }: any) =>
    <a href={to} {...props}>{children}</a>,
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    baseUrl: 'afghanistan/test-program',
    businessAreaSlug: 'afghanistan',
    programCode: 'test-program',
  }),
}));

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: () => [PERMISSIONS.GRIEVANCES_UPDATE],
}));

const showMessage = vi.fn();
vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({ showMessage }),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasGrievanceTicketsRetrieve: vi.fn(),
    restBusinessAreasUsersProfileRetrieve: vi.fn(),
    restBusinessAreasGrievanceTicketsPartialUpdate: vi.fn(),
  },
}));

const mockTicket = {
  id: 'ticket-1',
  unicefId: 'GRV-0001',
  category: 2, // Data Change
  priority: 2,
  urgency: 1,
  language: 'English',
  createdBy: { id: 'user-1' },
  assignedTo: { id: 'user-1' },
  programs: [{ id: 'program-1' }],
  // No pending/previous photo, so the editable widget renders the file input.
  ticketDetails: { individualData: { photo: {} } },
};

describe('PictureErrorEditPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (
      RestService.restBusinessAreasGrievanceTicketsRetrieve as any
    ).mockResolvedValue(mockTicket);
    (
      RestService.restBusinessAreasUsersProfileRetrieve as any
    ).mockResolvedValue({ id: 'user-1' });
    (
      RestService.restBusinessAreasGrievanceTicketsPartialUpdate as any
    ).mockResolvedValue(mockTicket);
  });

  it('uploads the photo through the individual-data-update extras contract', async () => {
    render(<PictureErrorEditPage />, { wrapper: TestProviders });

    // Wait for the ticket + profile queries to resolve and the form to render.
    const fileInput = (await screen.findByDisplayValue(
      '',
    )) as HTMLInputElement;
    expect(fileInput.type).toBe('file');

    const file = new File(['photo-bytes'], 'photo.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });

    fireEvent.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => {
      expect(
        RestService.restBusinessAreasGrievanceTicketsPartialUpdate,
      ).toHaveBeenCalledWith(
        expect.objectContaining({
          businessAreaSlug: 'afghanistan',
          id: 'ticket-1',
          formData: expect.objectContaining({
            priority: 2,
            urgency: 1,
            program: 'program-1',
            extras: {
              individualDataUpdateIssueTypeExtras: {
                individualData: { photo: file },
              },
            },
          }),
        }),
      );
    });
  });
});

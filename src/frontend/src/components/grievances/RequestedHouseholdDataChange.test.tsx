import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { RestService } from '@restgenerated/services/RestService';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { TestProviders } from 'src/testUtils/testProviders';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RequestedHouseholdDataChange } from './RequestedHouseholdDataChange';

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

const confirmation = vi.fn();
vi.mock('@core/ConfirmationDialog', () => ({
  useConfirmation: () => confirmation,
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate: vi.fn(),
    restBusinessAreasProgramsHouseholdsRetrieve: vi.fn(),
    restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList:
      vi.fn(),
    restChoicesCountriesList: vi.fn(),
    restBusinessAreasGeoAreasList: vi.fn(),
  },
}));

const FLEX_FIELD = 'hh_total_eligible_ind_h_f';

// householdData is delivered by the API in snake_case and is deliberately not
// camelized by the REST client (see deepCamelize in utils), so the fixture has
// to use snake_case keys exactly as the component receives them.
const makeTicket = (
  householdData: Record<string, unknown>,
  status = GRIEVANCE_TICKET_STATES.FOR_APPROVAL,
): GrievanceTicketDetail =>
  ({
    id: 'ticket-1',
    status,
    household: { id: 'hh-1', programCode: 'PRG1' },
    ticketDetails: { householdData },
  }) as unknown as GrievanceTicketDetail;

const sizeChange = {
  value: 5,
  previous_value: 4,
  approve_status: false,
};
const flexFieldChange = {
  value: 2,
  previous_value: 1,
  approve_status: false,
};

const renderComponent = (ticket: GrievanceTicketDetail) =>
  render(
    <RequestedHouseholdDataChange ticket={ticket} canApproveDataChange />,
    { wrapper: TestProviders },
  );

const mocked = (fn: unknown) => fn as ReturnType<typeof vi.fn>;

const getCheckboxes = (): HTMLInputElement[] =>
  Array.from(
    document.querySelectorAll<HTMLInputElement>('input[type="checkbox"]'),
  );

describe('RequestedHouseholdDataChange', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    confirmation.mockResolvedValue(undefined);
    mocked(
      RestService.restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate,
    ).mockResolvedValue({});
    mocked(
      RestService.restBusinessAreasProgramsHouseholdsRetrieve,
    ).mockResolvedValue({
      id: 'hh-1',
      size: 4,
      flexFields: { [FLEX_FIELD]: 1 },
    });
    mocked(
      RestService.restBusinessAreasGrievanceTicketsAllEditHouseholdFieldsAttributesList,
    ).mockResolvedValue([
      { name: 'size', type: 'INTEGER', isFlexField: false },
      { name: FLEX_FIELD, type: 'INTEGER', isFlexField: true },
    ]);
    mocked(RestService.restChoicesCountriesList).mockResolvedValue([]);
    mocked(RestService.restBusinessAreasGeoAreasList).mockResolvedValue({
      results: [],
    });
  });

  const waitForRows = async (count: number) => {
    await waitFor(() => expect(getCheckboxes()).toHaveLength(count));
  };

  it('sends approved flex fields in flexFieldsApproveData', async () => {
    renderComponent(
      makeTicket({ flex_fields: { [FLEX_FIELD]: flexFieldChange } }),
    );
    await waitForRows(1);

    fireEvent.click(getCheckboxes()[0]);
    fireEvent.click(screen.getByTestId('button-approve'));

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        id: 'ticket-1',
        formData: {
          householdApproveData: { roles: [] },
          flexFieldsApproveData: { [FLEX_FIELD]: true },
        },
      }),
    );
    // all changes were approved, so no partial-approval confirmation is shown
    expect(confirmation).not.toHaveBeenCalled();
  });

  it('counts flex fields when only some changes are approved', async () => {
    renderComponent(
      makeTicket({
        size: sizeChange,
        flex_fields: { [FLEX_FIELD]: flexFieldChange },
      }),
    );
    await waitForRows(2);

    // rows: size first, then flex fields
    fireEvent.click(getCheckboxes()[1]);
    fireEvent.click(screen.getByTestId('button-approve'));

    await waitFor(() => expect(confirmation).toHaveBeenCalledTimes(1));
    expect(confirmation.mock.calls[0][0].content).toContain(
      'You approved 1 change,',
    );
    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        id: 'ticket-1',
        formData: {
          householdApproveData: { roles: [] },
          flexFieldsApproveData: { [FLEX_FIELD]: true },
        },
      }),
    );
  });

  it('treats core fields plus flex fields as fully approved without confirmation', async () => {
    renderComponent(
      makeTicket({
        size: sizeChange,
        flex_fields: { [FLEX_FIELD]: flexFieldChange },
      }),
    );
    await waitForRows(2);

    getCheckboxes().forEach((checkbox) => fireEvent.click(checkbox));
    fireEvent.click(screen.getByTestId('button-approve'));

    await waitFor(() =>
      expect(
        RestService.restBusinessAreasGrievanceTicketsApproveHouseholdDataChangeCreate,
      ).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        id: 'ticket-1',
        formData: {
          householdApproveData: { size: true, roles: [] },
          flexFieldsApproveData: { [FLEX_FIELD]: true },
        },
      }),
    );
    expect(confirmation).not.toHaveBeenCalled();
  });

  it('starts in read-only mode when only a flex field is already approved', async () => {
    renderComponent(
      makeTicket({
        size: sizeChange,
        flex_fields: {
          [FLEX_FIELD]: { ...flexFieldChange, approve_status: true },
        },
      }),
    );

    // approved changes exist, so the section shows EDIT instead of checkboxes
    await waitFor(() => expect(screen.getByTestId('button-edit')).toBeTruthy());
    expect(screen.queryByTestId('button-approve')).toBeNull();
    await waitFor(() => expect(screen.getByTestId('green-tick')).toBeTruthy());
    expect(getCheckboxes()).toHaveLength(0);
  });
});

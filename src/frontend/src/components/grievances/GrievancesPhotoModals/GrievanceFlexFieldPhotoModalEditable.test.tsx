import { fireEvent, render, screen } from '@testing-library/react';
import { RestService } from '@restgenerated/services/RestService';
import { TestProviders } from 'src/testUtils/testProviders';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { GrievanceFlexFieldPhotoModalEditable } from './GrievanceFlexFieldPhotoModalEditable';

vi.mock('react-router-dom', async (importOriginal) => ({
  ...(await importOriginal<typeof import('react-router-dom')>()),
  useParams: () => ({ id: 'ticket-1' }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    businessAreaSlug: 'afghanistan',
  }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasGrievanceTicketsRetrieve: vi.fn(),
  },
}));

const mocked = (fn: unknown) => fn as ReturnType<typeof vi.fn>;

// householdData keeps its snake_case keys, individualData is camelized.
// See utils/ticketData.
const ticket = {
  id: 'ticket-1',
  ticketDetails: {
    householdData: {
      flex_fields: {
        photo_h_f: {
          value: '/api/uploads/flex/new.jpg',
          previous_value: '/api/uploads/flex/old.jpg',
          approve_status: false,
        },
      },
    },
    individualData: {
      consentSign: {
        value: '/api/uploads/people/new.jpg',
        previousValue: '/api/uploads/people/old.jpg',
        approveStatus: false,
      },
    },
  },
};

const renderEditable = (props: {
  flexField: { name: string };
  isCurrent?: boolean;
  isIndividual?: boolean;
}) =>
  render(
    <GrievanceFlexFieldPhotoModalEditable
      field={{ name: 'fieldValue' }}
      form={{ setFieldValue: vi.fn() }}
      {...props}
    />,
    { wrapper: TestProviders },
  );

describe('GrievanceFlexFieldPhotoModalEditable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocked(
      RestService.restBusinessAreasGrievanceTicketsRetrieve,
    ).mockResolvedValue(ticket);
  });

  it.each([
    [
      'household flex field new value',
      { flexField: { name: 'photo_h_f' } },
      '/api/uploads/flex/new.jpg',
    ],
    [
      'household flex field current value',
      { flexField: { name: 'photo_h_f' }, isCurrent: true },
      '/api/uploads/flex/old.jpg',
    ],
    [
      'individual core field new value',
      { flexField: { name: 'consent_sign' }, isIndividual: true },
      '/api/uploads/people/new.jpg',
    ],
  ])('shows the %s', async (_label, props, expectedSrc) => {
    renderEditable(props);

    fireEvent.click(await screen.findByTestId('mini-image-close'));
    const enlarged = screen.getByAltText('photo') as HTMLImageElement;
    expect(enlarged.src).toContain(expectedSrc);
  });

  it('offers the file input when the ticket holds no picture for the field', async () => {
    renderEditable({ flexField: { name: 'missing_h_f' } });

    expect(await screen.findByTestId('input-fieldValue')).toBeTruthy();
    expect(screen.queryByTestId('mini-image-close')).toBeNull();
  });
});

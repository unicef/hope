import { fireEvent, render, screen } from '@testing-library/react';
import { RestService } from '@restgenerated/index';
import { TestProviders } from 'src/testUtils/testProviders';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { GrievanceFlexFieldPhotoModal } from './GrievanceFlexFieldPhotoModal';

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

vi.mock('@restgenerated/index', () => ({
  RestService: {
    restBusinessAreasGrievanceTicketsRetrieve: vi.fn(),
  },
}));

const mocked = (fn: unknown) => fn as ReturnType<typeof vi.fn>;

// householdData is delivered in snake_case (the REST client does not camelize
// household_data), individualData is camelized.
const ticket = {
  id: 'ticket-1',
  ticketDetails: {
    householdData: {
      consent_sign: {
        value: '/api/uploads/consent/new.jpg',
        previous_value: '/api/uploads/consent/old.jpg',
        approve_status: false,
      },
      flex_fields: {
        photo_h_f: {
          value: '/api/uploads/flex/new.jpg',
          previous_value: '/api/uploads/flex/old.jpg',
          approve_status: false,
        },
      },
    },
    individualData: {
      flexFields: {
        photo_i_f: {
          value: '/api/uploads/ind/new.jpg',
          previousValue: '/api/uploads/ind/old.jpg',
          approveStatus: false,
        },
      },
    },
  },
};

const renderModal = (props: {
  field: { name: string };
  isCurrent?: boolean;
  isIndividual?: boolean;
}) =>
  render(<GrievanceFlexFieldPhotoModal {...props} />, {
    wrapper: TestProviders,
  });

const openEnlargedPhoto = async (): Promise<string> => {
  fireEvent.click(await screen.findByTestId('mini-image'));
  return (screen.getByAltText('photo') as HTMLImageElement).src;
};

describe('GrievanceFlexFieldPhotoModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mocked(
      RestService.restBusinessAreasGrievanceTicketsRetrieve,
    ).mockResolvedValue(ticket);
  });

  it.each([
    [
      'household core field new value',
      { field: { name: 'consent_sign' } },
      '/api/uploads/consent/new.jpg',
    ],
    [
      'household core field current value',
      { field: { name: 'consent_sign' }, isCurrent: true },
      '/api/uploads/consent/old.jpg',
    ],
    [
      'household flex field new value',
      { field: { name: 'photo_h_f' } },
      '/api/uploads/flex/new.jpg',
    ],
    [
      'individual flex field current value',
      { field: { name: 'photo_i_f' }, isCurrent: true, isIndividual: true },
      '/api/uploads/ind/old.jpg',
    ],
  ])('shows the %s', async (_label, props, expectedSrc) => {
    renderModal(props);

    expect(await openEnlargedPhoto()).toContain(expectedSrc);
  });

  it('shows a dash when the ticket holds no picture for the field', async () => {
    renderModal({ field: { name: 'missing_h_f' } });

    expect(await screen.findByText('-')).toBeTruthy();
    expect(screen.queryByTestId('mini-image')).toBeNull();
  });
});

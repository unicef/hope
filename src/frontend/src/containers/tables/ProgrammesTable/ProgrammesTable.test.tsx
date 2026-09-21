import { beforeEach, describe, expect, it, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { TestProviders } from 'src/testUtils/testProviders';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import ProgrammesTable from './ProgrammesTable';
import { RestService } from '@restgenerated/services/RestService';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { FrequencyOfPaymentsEnum } from '@restgenerated/models/FrequencyOfPaymentsEnum';
import { SectorEnum } from '@restgenerated/models/SectorEnum';
import { DataCollectingTypeTypeEnum } from '@restgenerated/models/DataCollectingTypeTypeEnum';
// Explicitly mock all relevant RestService methods as a named export
vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsList: vi.fn(),
    restBusinessAreasProgramsCountRetrieve: vi.fn(),
    restBusinessAreasUsersProfileRetrieve: vi.fn(),
  },
}));

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('ProgrammesTable', () => {
  let queryClient: QueryClient;

  // Mock data
  const mockProgramData = {
    next: null,
    previous: null,
    results: [
      {
        id: 'program-1',
        code: 'pr01',
        beneficiaryGroupMatch: 'test-program',
        compatibleDct: 'test-program',
        numberOfHouseholdsWithTpInProgram: 1000,
        name: 'Emergency Cash Transfer Program',
        startDate: '2023-01-01',
        endDate: '2023-12-31',
        budget: '500000.00',
        frequencyOfPayments: FrequencyOfPaymentsEnum.ONE_OFF,
        sector: SectorEnum.MULTI_PURPOSE,
        status: ProgramStatusEnum.ACTIVE,
        cashPlus: true,
        populationGoal: 1000,
        dataCollectingType: {
          id: 1,
          label: 'Full Individual',
          code: 'full',
          type: DataCollectingTypeTypeEnum.STANDARD,
          typeDisplay: 'Full Individual',
          householdFiltersAvailable: true,
          individualFiltersAvailable: true,
        },
        beneficiaryGroup: {
          id: 'group-1',
          name: 'Household',
          groupLabel: 'Household',
          groupLabelPlural: 'Households',
          memberLabel: 'Member',
          memberLabelPlural: 'Members',
          masterDetail: true,
        },
        pduFields: ['field1', 'field2'],
        householdCount: 1250,
        beneficiaryGroups: [],
      },
      {
        id: 'program-2',
        code: 'pr02',
        numberOfHouseholdsWithTpInProgram: 1000,
        name: 'Education Support Initiative',
        startDate: '2023-06-01',
        endDate: '2024-05-31',
        budget: '750000.00',
        frequencyOfPayments: FrequencyOfPaymentsEnum.REGULAR,
        sector: SectorEnum.EDUCATION,
        status: ProgramStatusEnum.DRAFT,
        cashPlus: false,
        populationGoal: 500,
        dataCollectingType: {
          id: 2,
          label: 'Partial Individual',
          code: 'partial',
          type: DataCollectingTypeTypeEnum.SOCIAL,
          typeDisplay: 'Full Individual',
          householdFiltersAvailable: false,
          individualFiltersAvailable: true,
        },
        beneficiaryGroup: {
          id: 'group-2',
          name: 'Individual',
          groupLabel: 'Individual',
          groupLabelPlural: 'Individuals',
          memberLabel: 'Person',
          memberLabelPlural: 'People',
          masterDetail: false,
        },
        pduFields: ['field3'],
        householdCount: 800,
        beneficiaryGroups: [],
      },
    ],
    count: 2,
  };

  const mockCountData = {
    count: 2,
  };

  const mockChoicesData = {
    programSectorChoices: [
      { name: 'Multi Purpose', value: 'MULTI_PURPOSE' },
      { name: 'Education', value: 'EDUCATION' },
      { name: 'Health', value: 'HEALTH' },
      { name: 'Nutrition', value: 'NUTRITION' },
    ],
    programStatusChoices: [
      { name: 'Active', value: 'ACTIVE' },
      { name: 'Draft', value: 'DRAFT' },
      { name: 'Finished', value: 'FINISHED' },
    ],
    programFrequencyOfPaymentsChoices: [
      { name: 'One-off', value: 'ONE_OFF' },
      { name: 'Regular', value: 'REGULAR' },
    ],
  };

  const mockFilter = {
    search: '',
    startDate: null,
    endDate: null,
    status: '',
    sector: '',
    numberOfHouseholdsMin: null,
    numberOfHouseholdsMax: null,
    budgetMin: null,
    budgetMax: null,
    dataCollectingType: '',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock RestService methods
    vi.mocked(RestService.restBusinessAreasProgramsList).mockResolvedValue(
      mockProgramData,
    );
    vi.mocked(
      RestService.restBusinessAreasProgramsCountRetrieve,
    ).mockResolvedValue(mockCountData);
    vi.mocked(
      RestService.restBusinessAreasUsersProfileRetrieve,
    ).mockResolvedValue({
      id: 'test-user-id',
      username: 'mock-user',
      email: 'mock-user@example.com',
      firstName: 'Mock',
      lastName: 'User',
      isSuperuser: false,
      partner: {
        id: 1,
        name: 'Test Partner',
      },
      businessAreas: {},
      permissionsInScope: '',
      userRoles: {},
      partnerRoles: {},
      crossAreaFilterAvailable: false,
      status: undefined,
      lastLogin: null,
      timezone: null,
      effectiveTimezone: 'UTC',
    });
  });

  it('renders programs table with data', async () => {
    const { findByText, getByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgrammesTable
          businessArea="test-business-area"
          filter={mockFilter}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    // Wait for table to load and check for program names
    await findByText('Emergency Cash Transfer Program');
    expect(getByText('Education Support Initiative')).toBeTruthy();

    // Check table headers
    expect(getByText('Name')).toBeTruthy();
    expect(getByText('Status')).toBeTruthy();
    expect(getByText('Timeframe')).toBeTruthy();
    expect(getByText('Sector')).toBeTruthy();
    expect(getByText('Programme Size')).toBeTruthy();
    expect(getByText('Budget (USD)')).toBeTruthy();

    // Verify REST service was called with correct parameters
    expect(RestService.restBusinessAreasProgramsList).toHaveBeenCalledWith(
      expect.objectContaining({
        businessAreaSlug: 'test-business-area',
        beneficiaryGroupMatch: 'test-program',
        compatibleDct: 'test-program',
      }),
    );

    expect(
      RestService.restBusinessAreasProgramsCountRetrieve,
    ).toHaveBeenCalledWith(
      expect.objectContaining({
        businessAreaSlug: 'test-business-area',
      }),
    );
  });

  it('renders empty table when no programs are available', async () => {
    const emptyData = {
      next: null,
      previous: null,
      results: [],
      count: 0,
    };

    vi.mocked(RestService.restBusinessAreasProgramsList).mockResolvedValue(
      emptyData,
    );
    vi.mocked(
      RestService.restBusinessAreasProgramsCountRetrieve,
    ).mockResolvedValue({ count: 0 });

    const { findByText } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgrammesTable
          businessArea="test-business-area"
          filter={mockFilter}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    // Wait for the table headers to appear
    await findByText('Name');

    // Verify REST service was called
    expect(RestService.restBusinessAreasProgramsList).toHaveBeenCalled();
    expect(
      RestService.restBusinessAreasProgramsCountRetrieve,
    ).toHaveBeenCalled();
  });

  it('requests the list once with the table pagination and the count without it', async () => {
    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgrammesTable
          businessArea="test-business-area"
          filter={mockFilter}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    await vi.waitFor(() => {
      expect(RestService.restBusinessAreasProgramsList).toHaveBeenCalled();
      expect(
        RestService.restBusinessAreasProgramsCountRetrieve,
      ).toHaveBeenCalled();
    });
    await new Promise((resolve) => setTimeout(resolve, 50));

    const listMock = vi.mocked(RestService.restBusinessAreasProgramsList);
    expect(listMock).toHaveBeenCalledTimes(1);
    expect(listMock).toHaveBeenCalledWith(
      expect.objectContaining({ limit: 5, offset: 0 }),
    );

    const countMock = vi.mocked(
      RestService.restBusinessAreasProgramsCountRetrieve,
    );
    expect(countMock).toHaveBeenCalledTimes(1);
    expect(countMock.mock.calls[0][0]).not.toHaveProperty('limit');
    expect(countMock.mock.calls[0][0]).not.toHaveProperty('offset');
  });

  it('applies filters correctly to API calls', async () => {
    const filterWithData = {
      search: 'education',
      startDate: '2023-01-01',
      endDate: '2023-12-31',
      status: 'ACTIVE',
      sector: 'EDUCATION',
      numberOfHouseholdsMin: 100,
      numberOfHouseholdsMax: 1000,
      budgetMin: 50000,
      budgetMax: 500000,
      dataCollectingType: 'full',
    };

    renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <ProgrammesTable
          businessArea="test-business-area"
          filter={filterWithData}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    // Wait for API call
    await vi.waitFor(() => {
      expect(RestService.restBusinessAreasProgramsList).toHaveBeenCalledWith(
        expect.objectContaining({
          businessAreaSlug: 'test-business-area',
          beneficiaryGroupMatch: 'test-program',
          compatibleDct: 'test-program',
          search: 'education',
          startDate: '2023-01-01',
          endDate: '2023-12-31',
          status: 'ACTIVE',
          sector: 'EDUCATION',
          numberOfHouseholdsMin: 100,
          numberOfHouseholdsMax: 1000,
          budgetMin: 50000,
          budgetMax: 500000,
          dataCollectingType: 'full',
        }),
      );
    });
  });

  it('goes back to the first page when the filter changes', async () => {
    vi.mocked(
      RestService.restBusinessAreasProgramsCountRetrieve,
    ).mockResolvedValue({ count: 42 });

    // The wrapper has to keep the same shape across rerenders, otherwise
    // ProgrammesTable remounts and the page resets for the wrong reason.
    const Harness = ({ currentFilter }: { currentFilter: any }) => (
      <TestProviders>
        <BrowserRouter>
          <QueryClientProvider client={queryClient}>
            <ProgrammesTable
              businessArea="test-business-area"
              filter={currentFilter}
              choicesData={mockChoicesData}
            />
          </QueryClientProvider>
        </BrowserRouter>
      </TestProviders>
    );

    const { rerender } = render(<Harness currentFilter={mockFilter} />);

    const nextPage = await waitFor(
      () => {
        const button = screen
          .getAllByRole('button')
          .find((candidate) =>
            /next page/i.test(
              candidate.getAttribute('aria-label') ||
                candidate.getAttribute('title') ||
                '',
            ),
          );
        if (!button) throw new Error('pagination not rendered yet');
        return button;
      },
      { timeout: 3000 },
    );

    const listMock = vi.mocked(RestService.restBusinessAreasProgramsList);

    fireEvent.click(nextPage);
    await waitFor(() => expect(listMock.mock.calls.at(-1)[0].offset).toBe(5));

    rerender(
      <Harness currentFilter={{ ...mockFilter, search: 'education' }} />,
    );

    await waitFor(() => {
      const lastCall = listMock.mock.calls.at(-1)[0];
      expect(lastCall.search).toBe('education');
      // The new filter never goes out together with the old page's offset.
      expect(lastCall.offset).toBe(0);
    });
  });
});

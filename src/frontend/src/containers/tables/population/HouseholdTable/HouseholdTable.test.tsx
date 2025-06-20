import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import { HouseholdTable } from './HouseholdTable';
import { RestService } from '@restgenerated/services/RestService';
import { Status791Enum } from '@restgenerated/models/Status791Enum';
import { ResidenceStatusEnum } from '@restgenerated/models/ResidenceStatusEnum';
import { CurrencyEnum } from '@restgenerated/models/CurrencyEnum';

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('HouseholdTable', () => {
  let queryClient: QueryClient;

  // Mock data
  const mockHouseholdData = {
    next: null,
    previous: null,
    results: [
      {
        id: 'household-1',
        unicefId: 'HH-001',
        headOfHousehold: 'John Doe',
        admin1: {
          id: 'admin2-1',
          name: 'District 1',
        },
        admin2: {
          id: 'admin2-1',
          name: 'District 1',
        },
        residenceStatus: ResidenceStatusEnum.HOST,
        totalCashReceived: '1000.00',
        totalCashReceivedUsd: '1000.00',
        currency: CurrencyEnum.USD,
        size: 5,
        status: 'ACTIVE',
        lastRegistrationDate: '2023-01-15T10:30:00Z',
        firstRegistrationDate: '2023-01-15T10:30:00Z',
        hasDuplicates: false,
        sanctionListPossibleMatch: false,
        sanctionListConfirmedMatch: false,
        program: {
          id: 'test-program',
          name: 'Test Program',
          slug: 'test-program',
          status: Status791Enum.ACTIVE,
        },
      },
    ],
    count: 1,
  };

  const mockCountData = {
    count: 1,
  };

  const defaultFilter = {
    search: '',
    documentType: '',
    documentNumber: '',
    residenceStatus: '',
    admin1: '',
    admin2: '',
    householdSizeMin: '',
    householdSizeMax: '',
    orderBy: 'unicef_id',
    withdrawn: '',
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Setup default mocks
    vi.mocked(
      RestService.restBusinessAreasProgramsHouseholdsList,
    ).mockResolvedValue(mockHouseholdData);
    vi.mocked(
      RestService.restBusinessAreasProgramsHouseholdsCountRetrieve,
    ).mockResolvedValue(mockCountData);
  });

  it('should render HouseholdTable correctly', () => {
    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <HouseholdTable filter={defaultFilter} canViewDetails={true} />
      </QueryClientProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});

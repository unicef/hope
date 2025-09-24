import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import { IndividualsListTable } from './IndividualsListTable';
import { RestService } from '@restgenerated/services/RestService';
import { SexEnum } from '@restgenerated/models/SexEnum';
import { RelationshipEnum } from '@restgenerated/models/RelationshipEnum';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { ResidenceStatusEnum } from '@restgenerated/models/ResidenceStatusEnum';
import type { PaginatedIndividualListList } from '@restgenerated/models/PaginatedIndividualListList';

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('IndividualsListTable', () => {
  let queryClient: QueryClient;

  // Mock data
  const mockIndividualsData :PaginatedIndividualListList = {
    next: null,
    previous: null,
    results: [
      {
        id: 'individual-1',
        unicefId: 'IND-001',
        fullName: 'John Doe',
        sex: SexEnum.MALE,
        age: 25,
        birthDate: '1998-01-15',
        relationship: RelationshipEnum.HEAD,
        status: 'ACTIVE',
        role: 'PRIMARY',
        relationshipDisplay: 'Head of household (self)',
        deduplicationBatchStatusDisplay: 'Unique in batch',
        biometricDeduplicationBatchStatusDisplay: 'Not processed',
        deduplicationGoldenRecordStatusDisplay: 'Unique',
        biometricDeduplicationGoldenRecordStatusDisplay: 'Not processed',
        deduplicationBatchResults: [],
        biometricDeduplicationBatchResults: [],
        deduplicationGoldenRecordResults: [],
        biometricDeduplicationGoldenRecordResults: [],
        household: {
          id: 'household-1',
          unicefId: 'HH-001',
          admin2: { id: 'admin2-1', name: 'District 1' },
        },
        program: {
          id: 'test-program',
          slug: 'test-program',
          name: 'Test Program',
        },
        lastRegistrationDate: '2023-01-15T10:30:00Z',
      },
    ],
  };

  const mockChoicesData = {
    documentTypeChoices: [
      { value: 'NATIONAL_ID', label: 'National ID' },
      { value: 'PASSPORT', label: 'Passport' },
    ],
    sexChoices: [],
    flagChoices: [],
    statusChoices: [],
    relationshipChoices: [],
    roleChoices: [],
    maritalStatusChoices: [],
    identityTypeChoices: [],
    observedDisabilityChoices: [],
    severityOfDisabilityChoices: [],
    workStatusChoices: [],
    deduplicationBatchStatusChoices: [
      { value: 'SomeValue', label: 'SomeLabel' },
    ],
    deduplicationGoldenRecordStatusChoices: [
      { value: 'SomeValue', label: 'SomeLabel' },
    ],
    accountTypeChoices: [],
    accountFinancialInstitutionChoices: [],
  };

  const defaultFilter = {
    search: '',
    documentType: '',
    documentNumber: '',
    admin2: '',
    sex: '',
    ageMin: '',
    ageMax: '',
    flags: [],
    status: [],
    lastRegistrationDateMin: '',
    lastRegistrationDateMax: '',
    orderBy: 'unicef_id',
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
      RestService.restBusinessAreasProgramsIndividualsList,
    ).mockResolvedValue(mockIndividualsData);
  });

  it('should render IndividualsListTable correctly', () => {
    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <IndividualsListTable
          filter={defaultFilter}
          businessArea="test-area"
          canViewDetails={true}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    expect(container).toMatchSnapshot();
  });

  it('should handle empty data', () => {
    const emptyMockData = {
      next: null,
      previous: null,
      results: [],
      count: 0,
    };

    vi.mocked(
      RestService.restBusinessAreasProgramsIndividualsList,
    ).mockResolvedValue(emptyMockData);

    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <IndividualsListTable
          filter={defaultFilter}
          businessArea="test-area"
          canViewDetails={true}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    expect(container).toMatchSnapshot();
  });

  it('should handle no view details permission', () => {
    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <IndividualsListTable
          filter={defaultFilter}
          businessArea="test-area"
          canViewDetails={false}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});

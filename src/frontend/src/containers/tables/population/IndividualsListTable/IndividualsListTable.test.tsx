import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import { IndividualsListTable } from './IndividualsListTable';
import { RestService } from '@restgenerated/services/RestService';
import { SexEnum } from '@restgenerated/models/SexEnum';
import { RelationshipEnum } from '@restgenerated/models/RelationshipEnum';

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('IndividualsListTable', () => {
  let queryClient: QueryClient;

  // Mock data
  const mockIndividualsData = {
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
        household: {
          id: 'household-1',
          unicefId: 'HH-001',
          admin2: {
            id: 'admin2-1',
            name: 'District 1',
          },
        },
        sanctionListPossibleMatch: false,
        sanctionListConfirmedMatch: false,
        lastRegistrationDate: '2023-01-15T10:30:00Z',
        firstRegistrationDate: '2023-01-15T10:30:00Z',
        documents: [],
        identities: [],
        phoneNo: '',
        phoneNoValid: false,
        email: '',
        maritalStatus: '',
        workStatus: '',
        observedDisability: [],
        disability: '',
        pregnant: false,
        deduplicationBatchStatus: '',
        deduplicationGoldenRecordStatus: '',
        deduplicationBatchResults: null,
        deduplicationGoldenRecordResults: null,
        importId: null,
        program: {
          id: 'test-program',
          name: 'Test Program',
          slug: 'test-program',
        },
      },
    ],
    count: 1,
  };

  const mockChoicesData = {
    sexChoices: [
      { value: SexEnum.MALE, label: 'Male' },
      { value: SexEnum.FEMALE, label: 'Female' },
    ],
    relationshipChoices: [
      { value: RelationshipEnum.HEAD, label: 'Head of Household' },
      { value: RelationshipEnum.WIFE_HUSBAND, label: 'Wife/Husband' },
      { value: RelationshipEnum.SON_DAUGHTER, label: 'Son/Daughter' },
    ],
    statusChoices: [
      { value: 'ACTIVE', label: 'Active' },
      { value: 'INACTIVE', label: 'Inactive' },
    ],
    maritalStatusChoices: [],
    workStatusChoices: [],
    observedDisabilityChoices: [],
    severityOfDisabilityChoices: [],
    residenceStatusChoices: [],
    commsDisabilityChoices: [],
    hearingDisabilityChoices: [],
    memoryDisabilityChoices: [],
    physicalDisabilityChoices: [],
    seeingDisabilityChoices: [],
    selfcareDisabilityChoices: [],
    pregnancyChoices: [],
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
});

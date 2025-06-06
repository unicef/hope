import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import { HouseholdMembersTable } from './HouseholdMembersTable';
import { RestService } from '@restgenerated/services/RestService';
import { SexEnum } from '@restgenerated/models/SexEnum';
import { RelationshipEnum } from '@restgenerated/models/RelationshipEnum';
import { Status791Enum } from '@restgenerated/models/Status791Enum';

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('HouseholdMembersTable', () => {
  let queryClient: QueryClient;

  // Mock household data
  const mockHousehold = {
    id: 'household-1',
    unicefId: 'HH-001',
    headOfHousehold: 'John Doe',
    admin1: 'Province 1',
    admin2: {
      id: 'admin2-1',
      name: 'District 1',
    },
    size: 3,
    status: 'ACTIVE',
    program: {
      id: 'test-program',
      name: 'Test Program',
      slug: 'test-program',
      status: Status791Enum.ACTIVE,
    },
  };

  // Mock household members data
  const mockHouseholdMembersData = {
    next: null,
    previous: null,
    results: [
      {
        id: 'individual-1',
        unicefId: 'IND-001',
        fullName: 'John Doe',
        sex: SexEnum.MALE,
        age: 35,
        birthDate: '1988-01-15',
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
      },
      {
        id: 'individual-2',
        unicefId: 'IND-002',
        fullName: 'Jane Doe',
        sex: SexEnum.FEMALE,
        age: 32,
        birthDate: '1991-05-20',
        relationship: RelationshipEnum.WIFE_HUSBAND,
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
      },
      {
        id: 'individual-3',
        unicefId: 'IND-003',
        fullName: 'Alice Doe',
        sex: SexEnum.FEMALE,
        age: 8,
        birthDate: '2015-03-10',
        relationship: RelationshipEnum.SON_DAUGHTER,
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
      },
    ],
    count: 3,
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
      { value: RelationshipEnum.MOTHER_FATHER, label: 'Mother/Father' },
      { value: RelationshipEnum.BROTHER_SISTER, label: 'Brother/Sister' },
      { value: RelationshipEnum.NON_BENEFICIARY, label: 'Not a Family Member' },
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
      RestService.restBusinessAreasProgramsHouseholdsMembersList,
    ).mockResolvedValue(mockHouseholdMembersData);
  });

  it('should render HouseholdMembersTable correctly', () => {
    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <HouseholdMembersTable
          household={mockHousehold}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    expect(container).toMatchSnapshot();
  });

  it('should render multiple household members with different relationships', () => {
    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <HouseholdMembersTable
          household={mockHousehold}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    // The component should render all 3 household members
    expect(container).toMatchSnapshot();
  });

  it('should handle empty household members list', () => {
    const emptyMembersData = {
      ...mockHouseholdMembersData,
      results: [],
      count: 0,
    };

    vi.mocked(
      RestService.restBusinessAreasProgramsHouseholdsMembersList,
    ).mockResolvedValue(emptyMembersData);

    const { container } = renderWithProviders(
      <QueryClientProvider client={queryClient}>
        <HouseholdMembersTable
          household={mockHousehold}
          choicesData={mockChoicesData}
        />
      </QueryClientProvider>,
    );

    expect(container).toMatchSnapshot();
  });
});

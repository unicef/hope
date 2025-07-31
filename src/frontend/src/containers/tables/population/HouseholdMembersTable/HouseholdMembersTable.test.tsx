import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderWithProviders } from 'src/testUtils/testUtils';
import { setupCommonMocks } from 'src/testUtils/commonMocks';
import { HouseholdMembersTable } from './HouseholdMembersTable';
import { RestService } from '@restgenerated/services/RestService';
import { SexEnum } from '@restgenerated/models/SexEnum';
import { RelationshipEnum } from '@restgenerated/models/RelationshipEnum';
import { DataSourceEnum } from '@restgenerated/models/DataSourceEnum';
import { ResidenceStatusEnum } from '@restgenerated/models/ResidenceStatusEnum';

// Setup common mocks (useBaseUrl, useProgramContext, react-router-dom, utils, RestService)
setupCommonMocks();

describe('HouseholdMembersTable', () => {
  let queryClient: QueryClient;

  // Mock household data
  const mockHousehold = {
    id: 'household-1',
    deliveredQuantities: [1, 2],
    unicefId: 'HH-001',
    headOfHousehold: {
      id: 'head-1',
      fullName: 'John Doe',
      phoneNo: '+1234567890',
      phoneNoValid: true,
    },
    admin1: { id: 'admin1-1', name: 'Province 1' },
    admin2: { id: 'admin2-1', name: 'District 1' },
    admin3: { id: 'admin3-1', name: '' },
    admin4: { id: 'admin4-1', name: '' },
    program: 'test-program',
    country: 'Country 1',
    countryOrigin: 'Country 1',
    status: 'ACTIVE',
    totalCashReceived: '1000.00',
    totalCashReceivedUsd: '1000.00',
    sanctionListPossibleMatch: false,
    sanctionListConfirmedMatch: false,
    hasDuplicates: false,
    registrationDataImport: {
      id: 'rdi-1',
      name: 'Test RDI',
      importDate: '2023-01-15T10:30:00Z',
      numberOfIndividuals: 3,
      numberOfHouseholds: 1,
      importedBy: {
        id: 'user-1',
        firstName: 'John',
        lastName: 'Admin',
        username: 'admin',
        email: 'admin@example.com',
      },
      dataSource: DataSourceEnum.API,
    },
    flexFields: {},
    linkedGrievances: {},
    adminAreaTitle: 'District 1',
    activeIndividualsCount: 3,
    geopoint: null,
    importId: 'import-1',
    adminUrl: '/admin/household/1',
    size: 3,
    residenceStatus: null,
    currency: null,
    maleChildrenCount: 0,
    femaleChildrenCount: 1,
    childrenDisabledCount: 0,
    maleAgeGroup05Count: 0,
    femaleAgeGroup05Count: 1,
    maleAgeGroup611Count: 0,
    femaleAgeGroup611Count: 0,
    maleAgeGroup1217Count: 0,
    femaleAgeGroup1217Count: 0,
    maleAgeGroup1859Count: 1,
    femaleAgeGroup1859Count: 1,
    maleAgeGroup60Count: 0,
    femaleAgeGroup60Count: 0,
    pregnantCount: 0,
    femaleAgeGroup05DisabledCount: 0,
    femaleAgeGroup611DisabledCount: 0,
    femaleAgeGroup1217DisabledCount: 0,
    femaleAgeGroup1859DisabledCount: 0,
    femaleAgeGroup60DisabledCount: 0,
    maleAgeGroup05DisabledCount: 0,
    maleAgeGroup611DisabledCount: 0,
    maleAgeGroup1217DisabledCount: 0,
    maleAgeGroup1859DisabledCount: 0,
    maleAgeGroup60DisabledCount: 0,
    start: null,
    deviceid: '',
    fchildHoh: false,
    childHoh: false,
    returnee: false,
    programRegistrationId: null,
    firstRegistrationDate: '2023-01-15T10:30:00Z',
    lastRegistrationDate: '2023-01-15T10:30:00Z',
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
        role: 'PRIMARY',
        sex: SexEnum.MALE,
        birthDate: '1988-01-15',
        relationship: RelationshipEnum.HEAD,
        status: 'ACTIVE',
        household: {
          id: 'household-1',
          unicefId: 'HH-001',
          admin1: { id: 'admin1-1', name: 'Province 1' },
          admin2: { id: 'admin2-1', name: 'District 1' },
          admin3: { id: 'admin3-1', name: '' },
          admin4: { id: 'admin4-1', name: '' },
          firstRegistrationDate: '2023-01-15T10:30:00Z',
          lastRegistrationDate: '2023-01-15T10:30:00Z',
          totalCashReceived: '1000.00',
          totalCashReceivedUsd: '1000.00',
          deliveredQuantities: [],
          residenceStatus: ResidenceStatusEnum.HOST,
          countryOrigin: 'Country 1',
          country: 'Country 1',
          zipCode: null,
          address: '',
          start: null,
          geopoint: null,
          importId: 'import-1',
        },
      },
      {
        id: 'individual-2',
        unicefId: 'IND-002',
        fullName: 'Jane Doe',
        role: 'NO_ROLE',
        sex: SexEnum.FEMALE,
        birthDate: '1991-05-20',
        relationship: RelationshipEnum.WIFE_HUSBAND,
        status: 'ACTIVE',
        household: {
          id: 'household-1',
          unicefId: 'HH-001',
          admin1: { id: 'admin1-1', name: 'Province 1' },
          admin2: { id: 'admin2-1', name: 'District 1' },
          admin3: { id: 'admin3-1', name: '' },
          admin4: { id: 'admin4-1', name: '' },
          firstRegistrationDate: '2023-01-15T10:30:00Z',
          lastRegistrationDate: '2023-01-15T10:30:00Z',
          totalCashReceived: '1000.00',
          totalCashReceivedUsd: '1000.00',
          deliveredQuantities: [],
          residenceStatus: ResidenceStatusEnum.HOST,
          countryOrigin: 'Country 1',
          country: 'Country 1',
          zipCode: null,
          address: '',
          start: null,
          geopoint: null,
          importId: 'import-1',
        },
      },
      {
        id: 'individual-3',
        unicefId: 'IND-003',
        fullName: 'Alice Doe',
        role: 'NO_ROLE',
        sex: SexEnum.FEMALE,
        birthDate: '2015-03-10',
        relationship: RelationshipEnum.SON_DAUGHTER,
        status: 'ACTIVE',
        household: {
          id: 'household-1',
          unicefId: 'HH-001',
          admin1: { id: 'admin1-1', name: 'Province 1' },
          admin2: { id: 'admin2-1', name: 'District 1' },
          admin3: { id: 'admin3-1', name: '' },
          admin4: { id: 'admin4-1', name: '' },
          firstRegistrationDate: '2023-01-15T10:30:00Z',
          lastRegistrationDate: '2023-01-15T10:30:00Z',
          totalCashReceived: '1000.00',
          totalCashReceivedUsd: '1000.00',
          deliveredQuantities: [],
          residenceStatus: ResidenceStatusEnum.HOST,
          countryOrigin: 'Country 1',
          country: 'Country 1',
          zipCode: null,
          address: '',
          start: null,
          geopoint: null,
          importId: 'import-1',
        },
      },
    ],
    count: 3,
  };

  const mockChoicesData = {
    documentTypeChoices: [
      { value: 'PASSPORT', label: 'Passport' },
      { value: 'NATIONAL_ID', label: 'National ID' },
    ],
    sexChoices: [
      { value: SexEnum.MALE, label: 'Male' },
      { value: SexEnum.FEMALE, label: 'Female' },
    ],
    flagChoices: [
      { value: 'HIGH_PRIORITY', label: 'High Priority' },
      { value: 'LOW_PRIORITY', label: 'Low Priority' },
    ],
    relationshipChoices: [
      { value: RelationshipEnum.HEAD, label: 'Head of Household' },
      { value: RelationshipEnum.WIFE_HUSBAND, label: 'Wife/Husband' },
      { value: RelationshipEnum.SON_DAUGHTER, label: 'Son/Daughter' },
      { value: RelationshipEnum.MOTHER_FATHER, label: 'Mother/Father' },
      { value: RelationshipEnum.BROTHER_SISTER, label: 'Brother/Sister' },
      { value: RelationshipEnum.NON_BENEFICIARY, label: 'Not a Family Member' },
    ],
    roleChoices: [
      { value: 'PRIMARY', label: 'Primary' },
      { value: 'ALTERNATE', label: 'Alternate' },
      { value: 'NO_ROLE', label: 'No Role' },
    ],
    statusChoices: [
      { value: 'ACTIVE', label: 'Active' },
      { value: 'INACTIVE', label: 'Inactive' },
    ],
    maritalStatusChoices: [
      { value: 'SINGLE', label: 'Single' },
      { value: 'MARRIED', label: 'Married' },
    ],
    identityTypeChoices: [
      { value: 'PASSPORT', label: 'Passport' },
      { value: 'NATIONAL_ID', label: 'National ID' },
    ],
    observedDisabilityChoices: [
      { value: 'NONE', label: 'None' },
      { value: 'SEEING', label: 'Seeing' },
    ],
    severityOfDisabilityChoices: [
      { value: 'NONE', label: 'None' },
      { value: 'MILD', label: 'Mild' },
    ],
    workStatusChoices: [
      { value: 'EMPLOYED', label: 'Employed' },
      { value: 'UNEMPLOYED', label: 'Unemployed' },
    ],
    deduplicationBatchStatusChoices: [
      { value: 'SomeValue', label: 'SomeLabel' },
    ],
    deduplicationGoldenRecordStatusChoices: [
      { value: 'SomeValue', label: 'SomeLabel' },
    ],
    accountTypeChoices: [],
    accountFinancialInstitutionChoices: [],
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

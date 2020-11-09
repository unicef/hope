import { GraphQLResolveInfo, GraphQLScalarType, GraphQLScalarTypeConfig } from 'graphql';
import gql from 'graphql-tag';
import * as ApolloReactCommon from '@apollo/react-common';
import * as React from 'react';
import * as ApolloReactComponents from '@apollo/react-components';
import * as ApolloReactHoc from '@apollo/react-hoc';
import * as ApolloReactHooks from '@apollo/react-hooks';
export type Maybe<T> = T | null;
export type RequireFields<T, K extends keyof T> = { [X in Exclude<keyof T, K>]?: T[X] } & { [P in K]-?: NonNullable<T[P]> };
export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: string,
  String: string,
  Boolean: boolean,
  Int: number,
  Float: number,
  DateTime: any,
  Date: any,
  UUID: any,
  FlexFieldsScalar: any,
  Decimal: any,
  Arg: any,
  JSONLazyString: any,
  GeoJSON: any,
  JSONString: any,
  Upload: any,
};

export type ActivateCashPlanVerificationMutation = {
   __typename?: 'ActivateCashPlanVerificationMutation',
  cashPlan?: Maybe<CashPlanNode>,
};

export type AddIndividualDataObjectType = {
  fullName: Scalars['String'],
  givenName: Scalars['String'],
  middleName?: Maybe<Scalars['String']>,
  familyName: Scalars['String'],
  sex: Scalars['String'],
  birthDate?: Maybe<Scalars['Date']>,
  estimatedBirthDate?: Maybe<Scalars['Boolean']>,
  maritalStatus?: Maybe<Scalars['String']>,
  phoneNo?: Maybe<Scalars['String']>,
  phoneNoAlternative?: Maybe<Scalars['String']>,
  relationship?: Maybe<Scalars['String']>,
  disability?: Maybe<Scalars['Boolean']>,
  workStatus?: Maybe<Scalars['String']>,
  enrolledInNutritionProgramme?: Maybe<Scalars['Boolean']>,
  administrationOfRutf?: Maybe<Scalars['Boolean']>,
  pregnant?: Maybe<Scalars['Boolean']>,
  observedDisability?: Maybe<Array<Maybe<Scalars['String']>>>,
  seeingDisability?: Maybe<Scalars['String']>,
  hearingDisability?: Maybe<Scalars['String']>,
  physicalDisability?: Maybe<Scalars['String']>,
  memoryDisability?: Maybe<Scalars['String']>,
  selfcareDisability?: Maybe<Scalars['String']>,
  commsDisability?: Maybe<Scalars['String']>,
  whoAnswersPhone?: Maybe<Scalars['String']>,
  whoAnswersAltPhone?: Maybe<Scalars['String']>,
};

export type AddIndividualIssueTypeExtras = {
  household: Scalars['ID'],
  individualData: AddIndividualDataObjectType,
};

export type AdminAreaNode = Node & {
   __typename?: 'AdminAreaNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  title: Scalars['String'],
  parent?: Maybe<AdminAreaNode>,
  adminAreaType: AdminAreaTypeNode,
  lft: Scalars['Int'],
  rght: Scalars['Int'],
  treeId: Scalars['Int'],
  level: Scalars['Int'],
  children: AdminAreaNodeConnection,
  householdSet: HouseholdNodeConnection,
  programs: ProgramNodeConnection,
};


export type AdminAreaNodeChildrenArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
};


export type AdminAreaNodeHouseholdSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type AdminAreaNodeProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
};

export type AdminAreaNodeConnection = {
   __typename?: 'AdminAreaNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<AdminAreaNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type AdminAreaNodeEdge = {
   __typename?: 'AdminAreaNodeEdge',
  node?: Maybe<AdminAreaNode>,
  cursor: Scalars['String'],
};

export type AdminAreaTypeNode = Node & {
   __typename?: 'AdminAreaTypeNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  displayName?: Maybe<Scalars['String']>,
  adminLevel: Scalars['Int'],
  businessArea?: Maybe<UserBusinessAreaNode>,
  locations: AdminAreaNodeConnection,
};


export type AdminAreaTypeNodeLocationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
};

export type AdminAreaTypeNodeConnection = {
   __typename?: 'AdminAreaTypeNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<AdminAreaTypeNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type AdminAreaTypeNodeEdge = {
   __typename?: 'AdminAreaTypeNodeEdge',
  node?: Maybe<AdminAreaTypeNode>,
  cursor: Scalars['String'],
};

export type AgeFilterObject = {
   __typename?: 'AgeFilterObject',
  min?: Maybe<Scalars['Int']>,
  max?: Maybe<Scalars['Int']>,
};

export type AgeInput = {
  min?: Maybe<Scalars['Int']>,
  max?: Maybe<Scalars['Int']>,
};

export type ApproveTargetPopulationMutation = {
   __typename?: 'ApproveTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
};


export type BusinessAreaNode = Node & {
   __typename?: 'BusinessAreaNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  code: Scalars['String'],
  name: Scalars['String'],
  longName: Scalars['String'],
  regionCode: Scalars['String'],
  regionName: Scalars['String'],
  koboToken?: Maybe<Scalars['String']>,
  rapidProHost?: Maybe<Scalars['String']>,
  rapidProApiKey?: Maybe<Scalars['String']>,
  slug: Scalars['String'],
  hasDataSharingAgreement: Scalars['Boolean'],
  adminAreaTypes: AdminAreaTypeNodeConnection,
  userRoles: Array<UserRoleNode>,
  tickets: GrievanceTicketNodeConnection,
  householdSet: HouseholdNodeConnection,
  paymentrecordSet: PaymentRecordNodeConnection,
  serviceproviderSet: ServiceProviderNodeConnection,
  programSet: ProgramNodeConnection,
  cashplanSet: CashPlanNodeConnection,
  targetpopulationSet: TargetPopulationNodeConnection,
  registrationdataimportSet: RegistrationDataImportNodeConnection,
};


export type BusinessAreaNodeAdminAreaTypesArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type BusinessAreaNodeTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type BusinessAreaNodeHouseholdSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type BusinessAreaNodePaymentrecordSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
};


export type BusinessAreaNodeServiceproviderSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type BusinessAreaNodeProgramSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
};


export type BusinessAreaNodeCashplanSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type BusinessAreaNodeTargetpopulationSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type BusinessAreaNodeRegistrationdataimportSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type BusinessAreaNodeConnection = {
   __typename?: 'BusinessAreaNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<BusinessAreaNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type BusinessAreaNodeEdge = {
   __typename?: 'BusinessAreaNodeEdge',
  node?: Maybe<BusinessAreaNode>,
  cursor: Scalars['String'],
};

export enum CashPlanDeliveryType {
  Cash = 'CASH',
  DepositToCard = 'DEPOSIT_TO_CARD',
  Transfer = 'TRANSFER'
}

export type CashPlanNode = Node & {
   __typename?: 'CashPlanNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  businessArea: UserBusinessAreaNode,
  caId?: Maybe<Scalars['String']>,
  caHashId?: Maybe<Scalars['UUID']>,
  status: CashPlanStatus,
  statusDate: Scalars['DateTime'],
  name: Scalars['String'],
  distributionLevel: Scalars['String'],
  startDate: Scalars['DateTime'],
  endDate: Scalars['DateTime'],
  dispersionDate: Scalars['DateTime'],
  coverageDuration: Scalars['Int'],
  coverageUnit: Scalars['String'],
  comments?: Maybe<Scalars['String']>,
  program: ProgramNode,
  deliveryType?: Maybe<CashPlanDeliveryType>,
  assistanceMeasurement: Scalars['String'],
  assistanceThrough: Scalars['String'],
  visionId: Scalars['String'],
  fundsCommitment: Scalars['String'],
  downPayment: Scalars['String'],
  validationAlertsCount: Scalars['Int'],
  totalPersonsCovered: Scalars['Int'],
  totalPersonsCoveredRevised: Scalars['Int'],
  totalEntitledQuantity: Scalars['Float'],
  totalEntitledQuantityRevised: Scalars['Float'],
  totalDeliveredQuantity: Scalars['Float'],
  totalUndeliveredQuantity: Scalars['Float'],
  verificationStatus: CashPlanVerificationStatus,
  paymentRecords: PaymentRecordNodeConnection,
  verifications: CashPlanPaymentVerificationNodeConnection,
  bankReconciliationSuccess?: Maybe<Scalars['Int']>,
  bankReconciliationError?: Maybe<Scalars['Int']>,
};


export type CashPlanNodePaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
};


export type CashPlanNodeVerificationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type CashPlanNodeConnection = {
   __typename?: 'CashPlanNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<CashPlanNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type CashPlanNodeEdge = {
   __typename?: 'CashPlanNodeEdge',
  node?: Maybe<CashPlanNode>,
  cursor: Scalars['String'],
};

export type CashPlanPaymentVerificationNode = Node & {
   __typename?: 'CashPlanPaymentVerificationNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  status: CashPlanPaymentVerificationStatus,
  cashPlan: CashPlanNode,
  sampling: CashPlanPaymentVerificationSampling,
  verificationMethod: CashPlanPaymentVerificationVerificationMethod,
  sampleSize?: Maybe<Scalars['Int']>,
  respondedCount?: Maybe<Scalars['Int']>,
  receivedCount?: Maybe<Scalars['Int']>,
  notReceivedCount?: Maybe<Scalars['Int']>,
  receivedWithProblemsCount?: Maybe<Scalars['Int']>,
  confidenceInterval?: Maybe<Scalars['Float']>,
  marginOfError?: Maybe<Scalars['Float']>,
  rapidProFlowId: Scalars['String'],
  rapidProFlowStartUuid: Scalars['String'],
  ageFilter?: Maybe<AgeFilterObject>,
  excludedAdminAreasFilter?: Maybe<Array<Maybe<Scalars['String']>>>,
  sexFilter?: Maybe<Scalars['String']>,
  activationDate?: Maybe<Scalars['DateTime']>,
  completionDate?: Maybe<Scalars['DateTime']>,
  paymentRecordVerifications: PaymentVerificationNodeConnection,
};


export type CashPlanPaymentVerificationNodePaymentRecordVerificationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type CashPlanPaymentVerificationNodeConnection = {
   __typename?: 'CashPlanPaymentVerificationNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<CashPlanPaymentVerificationNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type CashPlanPaymentVerificationNodeEdge = {
   __typename?: 'CashPlanPaymentVerificationNodeEdge',
  node?: Maybe<CashPlanPaymentVerificationNode>,
  cursor: Scalars['String'],
};

export enum CashPlanPaymentVerificationSampling {
  FullList = 'FULL_LIST',
  Random = 'RANDOM'
}

export enum CashPlanPaymentVerificationStatus {
  Pending = 'PENDING',
  Active = 'ACTIVE',
  Finished = 'FINISHED'
}

export enum CashPlanPaymentVerificationVerificationMethod {
  Rapidpro = 'RAPIDPRO',
  Xlsx = 'XLSX',
  Manual = 'MANUAL'
}

export enum CashPlanStatus {
  DistributionCompleted = 'DISTRIBUTION_COMPLETED',
  DistributionCompletedWithErrors = 'DISTRIBUTION_COMPLETED_WITH_ERRORS',
  TransactionCompleted = 'TRANSACTION_COMPLETED',
  TransactionCompletedWithErrors = 'TRANSACTION_COMPLETED_WITH_ERRORS'
}

export enum CashPlanVerificationStatus {
  Pending = 'PENDING',
  Active = 'ACTIVE',
  Finished = 'FINISHED'
}

export type CategoryExtrasInput = {
  sensitiveGrievanceTicketExtras?: Maybe<SensitiveGrievanceTicketExtras>,
  grievanceComplaintTicketExtras?: Maybe<GrievanceComplaintTicketExtras>,
};

export type CheckAgainstSanctionListMutation = {
   __typename?: 'CheckAgainstSanctionListMutation',
  ok?: Maybe<Scalars['Boolean']>,
  errors?: Maybe<Array<Maybe<XlsxRowErrorNode>>>,
};

export type ChoiceObject = {
   __typename?: 'ChoiceObject',
  name?: Maybe<Scalars['String']>,
  value?: Maybe<Scalars['String']>,
};

export type CopyTargetPopulationInput = {
  id?: Maybe<Scalars['ID']>,
  name?: Maybe<Scalars['String']>,
};

export type CopyTargetPopulationMutationInput = {
  targetPopulationData?: Maybe<CopyTargetPopulationInput>,
  clientMutationId?: Maybe<Scalars['String']>,
};

export type CopyTargetPopulationMutationPayload = {
   __typename?: 'CopyTargetPopulationMutationPayload',
  targetPopulation?: Maybe<TargetPopulationNode>,
  clientMutationId?: Maybe<Scalars['String']>,
};

export type CoreFieldChoiceObject = {
   __typename?: 'CoreFieldChoiceObject',
  labels?: Maybe<Array<Maybe<LabelNode>>>,
  labelEn?: Maybe<Scalars['String']>,
  value?: Maybe<Scalars['String']>,
  admin?: Maybe<Scalars['String']>,
  listName?: Maybe<Scalars['String']>,
};

export type CountAndPercentageNode = {
   __typename?: 'CountAndPercentageNode',
  count?: Maybe<Scalars['Int']>,
  percentage?: Maybe<Scalars['Float']>,
};

export type CreateGrievanceTicketExtrasInput = {
  category?: Maybe<CategoryExtrasInput>,
  issueType?: Maybe<IssueTypeExtrasInput>,
};

export type CreateGrievanceTicketInput = {
  description: Scalars['String'],
  assignedTo: Scalars['ID'],
  category: Scalars['Int'],
  issueType?: Maybe<Scalars['Int']>,
  admin?: Maybe<Scalars['String']>,
  area?: Maybe<Scalars['String']>,
  language: Scalars['String'],
  consent: Scalars['Boolean'],
  businessArea: Scalars['ID'],
  linkedTickets?: Maybe<Array<Maybe<Scalars['ID']>>>,
  extras?: Maybe<CreateGrievanceTicketExtrasInput>,
};

export type CreateGrievanceTicketMutation = {
   __typename?: 'CreateGrievanceTicketMutation',
  grievanceTickets?: Maybe<Array<Maybe<GrievanceTicketNode>>>,
};

export type CreatePaymentVerificationInput = {
  cashPlanId: Scalars['ID'],
  sampling: Scalars['String'],
  verificationChannel: Scalars['String'],
  businessAreaSlug: Scalars['String'],
  fullListArguments?: Maybe<FullListArguments>,
  randomSamplingArguments?: Maybe<RandomSamplingArguments>,
  rapidProArguments?: Maybe<RapidProArguments>,
};

export type CreatePaymentVerificationMutation = {
   __typename?: 'CreatePaymentVerificationMutation',
  cashPlan?: Maybe<CashPlanNode>,
};

export type CreateProgram = {
   __typename?: 'CreateProgram',
  program?: Maybe<ProgramNode>,
};

export type CreateProgramInput = {
  name?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['Date']>,
  endDate?: Maybe<Scalars['Date']>,
  description?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  scope?: Maybe<Scalars['String']>,
  cashPlus?: Maybe<Scalars['Boolean']>,
  populationGoal?: Maybe<Scalars['Int']>,
  administrativeAreasOfImplementation?: Maybe<Scalars['String']>,
  businessAreaSlug?: Maybe<Scalars['String']>,
  individualDataNeeded?: Maybe<Scalars['Boolean']>,
};

export type CreateTargetPopulationInput = {
  name: Scalars['String'],
  targetingCriteria: TargetingCriteriaObjectType,
  businessAreaSlug: Scalars['String'],
  programId: Scalars['ID'],
};

export type CreateTargetPopulationMutation = {
   __typename?: 'CreateTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
};




export type DeduplicationResultNode = {
   __typename?: 'DeduplicationResultNode',
  hitId?: Maybe<Scalars['ID']>,
  fullName?: Maybe<Scalars['String']>,
  score?: Maybe<Scalars['Float']>,
  proximityToScore?: Maybe<Scalars['Float']>,
  location?: Maybe<Scalars['String']>,
  age?: Maybe<Scalars['Int']>,
};

export type DeleteProgram = {
   __typename?: 'DeleteProgram',
  ok?: Maybe<Scalars['Boolean']>,
};

export type DeleteRegistrationDataImport = {
   __typename?: 'DeleteRegistrationDataImport',
  ok?: Maybe<Scalars['Boolean']>,
};

export type DeleteTargetPopulationMutationInput = {
  targetId: Scalars['ID'],
  clientMutationId?: Maybe<Scalars['String']>,
};

export type DeleteTargetPopulationMutationPayload = {
   __typename?: 'DeleteTargetPopulationMutationPayload',
  ok?: Maybe<Scalars['Boolean']>,
  clientMutationId?: Maybe<Scalars['String']>,
};

export type DiscardCashPlanVerificationMutation = {
   __typename?: 'DiscardCashPlanVerificationMutation',
  cashPlan?: Maybe<CashPlanNode>,
};

export type DjangoDebug = {
   __typename?: 'DjangoDebug',
  sql?: Maybe<Array<Maybe<DjangoDebugSql>>>,
};

export type DjangoDebugSql = {
   __typename?: 'DjangoDebugSQL',
  vendor: Scalars['String'],
  alias: Scalars['String'],
  sql?: Maybe<Scalars['String']>,
  duration: Scalars['Float'],
  rawSql: Scalars['String'],
  params: Scalars['String'],
  startTime: Scalars['Float'],
  stopTime: Scalars['Float'],
  isSlow: Scalars['Boolean'],
  isSelect: Scalars['Boolean'],
  transId?: Maybe<Scalars['String']>,
  transStatus?: Maybe<Scalars['String']>,
  isoLevel?: Maybe<Scalars['String']>,
  encoding?: Maybe<Scalars['String']>,
};

export type DocumentNode = Node & {
   __typename?: 'DocumentNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  documentNumber: Scalars['String'],
  photo: Scalars['String'],
  individual: IndividualNode,
  type: DocumentTypeNode,
};

export type DocumentNodeConnection = {
   __typename?: 'DocumentNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<DocumentNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type DocumentNodeEdge = {
   __typename?: 'DocumentNodeEdge',
  node?: Maybe<DocumentNode>,
  cursor: Scalars['String'],
};

export type DocumentTypeNode = {
   __typename?: 'DocumentTypeNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  country?: Maybe<Scalars['String']>,
  label: Scalars['String'],
  type: DocumentTypeType,
  documents: DocumentNodeConnection,
};


export type DocumentTypeNodeDocumentsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export enum DocumentTypeType {
  BirthCertificate = 'BIRTH_CERTIFICATE',
  DriversLicense = 'DRIVERS_LICENSE',
  NationalId = 'NATIONAL_ID',
  NationalPassport = 'NATIONAL_PASSPORT',
  ElectoralCard = 'ELECTORAL_CARD',
  Other = 'OTHER'
}

export type EditCashPlanPaymentVerificationInput = {
  cashPlanPaymentVerificationId: Scalars['ID'],
  sampling: Scalars['String'],
  verificationChannel: Scalars['String'],
  businessAreaSlug: Scalars['String'],
  fullListArguments?: Maybe<FullListArguments>,
  randomSamplingArguments?: Maybe<RandomSamplingArguments>,
  rapidProArguments?: Maybe<RapidProArguments>,
};

export type EditPaymentVerificationMutation = {
   __typename?: 'EditPaymentVerificationMutation',
  cashPlan?: Maybe<CashPlanNode>,
};

export type FieldAttributeNode = {
   __typename?: 'FieldAttributeNode',
  id?: Maybe<Scalars['String']>,
  type?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  labels?: Maybe<Array<Maybe<LabelNode>>>,
  labelEn?: Maybe<Scalars['String']>,
  hint?: Maybe<Scalars['String']>,
  required?: Maybe<Scalars['Boolean']>,
  choices?: Maybe<Array<Maybe<CoreFieldChoiceObject>>>,
  associatedWith?: Maybe<Scalars['String']>,
  isFlexField?: Maybe<Scalars['Boolean']>,
};

export type FinalizeTargetPopulationMutation = {
   __typename?: 'FinalizeTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
};

export type FinishCashPlanVerificationMutation = {
   __typename?: 'FinishCashPlanVerificationMutation',
  cashPlan?: Maybe<CashPlanNode>,
};


export type FullListArguments = {
  excludedAdminAreas?: Maybe<Array<Maybe<Scalars['String']>>>,
};


export type GetCashplanVerificationSampleSizeInput = {
  cashPlanId: Scalars['ID'],
  sampling: Scalars['String'],
  businessAreaSlug: Scalars['String'],
  fullListArguments?: Maybe<FullListArguments>,
  randomSamplingArguments?: Maybe<RandomSamplingArguments>,
};

export type GetCashplanVerificationSampleSizeObject = {
   __typename?: 'GetCashplanVerificationSampleSizeObject',
  paymentRecordCount?: Maybe<Scalars['Int']>,
  sampleSize?: Maybe<Scalars['Int']>,
};

export type GrievanceComplaintTicketExtras = {
  household?: Maybe<Scalars['ID']>,
  individual?: Maybe<Scalars['ID']>,
  paymentRecord?: Maybe<Scalars['ID']>,
};

export type GrievanceTicketNode = Node & {
   __typename?: 'GrievanceTicketNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  userModified?: Maybe<Scalars['DateTime']>,
  createdBy?: Maybe<UserNode>,
  assignedTo?: Maybe<UserNode>,
  status: Scalars['Int'],
  category: Scalars['Int'],
  issueType?: Maybe<Scalars['Int']>,
  description: Scalars['String'],
  admin: Scalars['String'],
  area: Scalars['String'],
  language: Scalars['String'],
  consent: Scalars['Boolean'],
  businessArea: UserBusinessAreaNode,
  linkedTickets: GrievanceTicketNodeConnection,
  grievanceticketSet: GrievanceTicketNodeConnection,
  complaintTicketDetails?: Maybe<TicketComplaintDetailsNode>,
  sensitiveTicketDetails?: Maybe<TicketSensitiveDetailsNode>,
  householdDataUpdateTicketDetails?: Maybe<TicketHouseholdDataUpdateDetailsNode>,
  individualDataUpdateTicketDetails?: Maybe<TicketIndividualDataUpdateDetailsNode>,
  addIndividualTicketDetails?: Maybe<TicketAddIndividualDetailsNode>,
  deleteIndividualTicketDetails?: Maybe<TicketDeleteIndividualDetailsNode>,
};


export type GrievanceTicketNodeLinkedTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type GrievanceTicketNodeGrievanceticketSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type GrievanceTicketNodeConnection = {
   __typename?: 'GrievanceTicketNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<GrievanceTicketNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type GrievanceTicketNodeEdge = {
   __typename?: 'GrievanceTicketNodeEdge',
  node?: Maybe<GrievanceTicketNode>,
  cursor: Scalars['String'],
};

export type GroupAttributeNode = {
   __typename?: 'GroupAttributeNode',
  id: Scalars['UUID'],
  name: Scalars['String'],
  label: Scalars['JSONString'],
  flexAttributes?: Maybe<Array<Maybe<FieldAttributeNode>>>,
  labelEn?: Maybe<Scalars['String']>,
};


export type GroupAttributeNodeFlexAttributesArgs = {
  flexField?: Maybe<Scalars['Boolean']>
};

export enum HouseholdConsentSharing {
  Unicef = 'UNICEF',
  HumanitarianPartner = 'HUMANITARIAN_PARTNER',
  PrivatePartner = 'PRIVATE_PARTNER',
  GovernmentPartner = 'GOVERNMENT_PARTNER'
}

export type HouseholdDataUpdateIssueTypeExtras = {
  household: Scalars['ID'],
  householdData?: Maybe<HouseholdUpdateDataObjectType>,
};

export type HouseholdNode = Node & {
   __typename?: 'HouseholdNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  lastSyncAt?: Maybe<Scalars['DateTime']>,
  status: HouseholdStatus,
  consentSign: Scalars['String'],
  consent: Scalars['Boolean'],
  consentSharing: HouseholdConsentSharing,
  residenceStatus: HouseholdResidenceStatus,
  countryOrigin?: Maybe<Scalars['String']>,
  country?: Maybe<Scalars['String']>,
  size: Scalars['Int'],
  address: Scalars['String'],
  adminArea?: Maybe<AdminAreaNode>,
  representatives: IndividualNodeConnection,
  geopoint?: Maybe<Scalars['GeoJSON']>,
  femaleAgeGroup05Count: Scalars['Int'],
  femaleAgeGroup611Count: Scalars['Int'],
  femaleAgeGroup1217Count: Scalars['Int'],
  femaleAdultsCount: Scalars['Int'],
  pregnantCount: Scalars['Int'],
  maleAgeGroup05Count: Scalars['Int'],
  maleAgeGroup611Count: Scalars['Int'],
  maleAgeGroup1217Count: Scalars['Int'],
  maleAdultsCount: Scalars['Int'],
  femaleAgeGroup05DisabledCount: Scalars['Int'],
  femaleAgeGroup611DisabledCount: Scalars['Int'],
  femaleAgeGroup1217DisabledCount: Scalars['Int'],
  femaleAdultsDisabledCount: Scalars['Int'],
  maleAgeGroup05DisabledCount: Scalars['Int'],
  maleAgeGroup611DisabledCount: Scalars['Int'],
  maleAgeGroup1217DisabledCount: Scalars['Int'],
  maleAdultsDisabledCount: Scalars['Int'],
  registrationDataImport: RegistrationDataImportNode,
  programs: ProgramNodeConnection,
  returnee: Scalars['Boolean'],
  flexFields?: Maybe<Scalars['FlexFieldsScalar']>,
  firstRegistrationDate: Scalars['Date'],
  lastRegistrationDate: Scalars['Date'],
  headOfHousehold: IndividualNode,
  fchildHoh: Scalars['Boolean'],
  childHoh: Scalars['Boolean'],
  unicefId: Scalars['String'],
  businessArea: UserBusinessAreaNode,
  start?: Maybe<Scalars['DateTime']>,
  end?: Maybe<Scalars['DateTime']>,
  deviceid: Scalars['String'],
  nameEnumerator: Scalars['String'],
  orgEnumerator: HouseholdOrgEnumerator,
  orgNameEnumerator: Scalars['String'],
  village: Scalars['String'],
  complaintTicketDetails: TicketComplaintDetailsNodeConnection,
  sensitiveTicketDetails: TicketSensitiveDetailsNodeConnection,
  householdDataUpdateTicketDetails: TicketHouseholdDataUpdateDetailsNodeConnection,
  addIndividualTicketDetails: TicketAddIndividualDetailsNodeConnection,
  individualsAndRoles: Array<IndividualRoleInHouseholdNode>,
  individuals: IndividualNodeConnection,
  paymentRecords: PaymentRecordNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
  selections: Array<HouseholdSelection>,
  totalCashReceived?: Maybe<Scalars['Decimal']>,
  selection?: Maybe<HouseholdSelection>,
  sanctionListPossibleMatch?: Maybe<Scalars['Boolean']>,
  hasDuplicates?: Maybe<Scalars['Boolean']>,
};


export type HouseholdNodeRepresentativesArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type HouseholdNodeProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
};


export type HouseholdNodeComplaintTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type HouseholdNodeSensitiveTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type HouseholdNodeHouseholdDataUpdateTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type HouseholdNodeAddIndividualTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type HouseholdNodeIndividualsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type HouseholdNodePaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
};


export type HouseholdNodeTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};

export type HouseholdNodeConnection = {
   __typename?: 'HouseholdNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<HouseholdNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  individualsCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type HouseholdNodeEdge = {
   __typename?: 'HouseholdNodeEdge',
  node?: Maybe<HouseholdNode>,
  cursor: Scalars['String'],
};

export enum HouseholdOrgEnumerator {
  Unicef = 'UNICEF',
  Partner = 'PARTNER'
}

export enum HouseholdResidenceStatus {
  Idp = 'IDP',
  Refugee = 'REFUGEE',
  OthersOfConcern = 'OTHERS_OF_CONCERN',
  Host = 'HOST',
  NonHost = 'NON_HOST'
}

export type HouseholdSelection = {
   __typename?: 'HouseholdSelection',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  household: HouseholdNode,
  targetPopulation: TargetPopulationNode,
  vulnerabilityScore?: Maybe<Scalars['Float']>,
  final: Scalars['Boolean'],
};

export enum HouseholdStatus {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}

export type HouseholdUpdateDataObjectType = {
  status?: Maybe<Scalars['String']>,
  consent?: Maybe<Scalars['Boolean']>,
  residenceStatus?: Maybe<Scalars['String']>,
  countryOrigin?: Maybe<Scalars['String']>,
  country?: Maybe<Scalars['String']>,
  size?: Maybe<Scalars['Int']>,
  address?: Maybe<Scalars['String']>,
  femaleAgeGroup05Count?: Maybe<Scalars['Int']>,
  femaleAgeGroup611Count?: Maybe<Scalars['Int']>,
  femaleAgeGroup1217Count?: Maybe<Scalars['Int']>,
  femaleAdultsCount?: Maybe<Scalars['Int']>,
  pregnantCount?: Maybe<Scalars['Int']>,
  maleAgeGroup05Count?: Maybe<Scalars['Int']>,
  maleAgeGroup611Count?: Maybe<Scalars['Int']>,
  maleAgeGroup1217Count?: Maybe<Scalars['Int']>,
  maleAdultsCount?: Maybe<Scalars['Int']>,
  femaleAgeGroup05DisabledCount?: Maybe<Scalars['Int']>,
  femaleAgeGroup611DisabledCount?: Maybe<Scalars['Int']>,
  femaleAgeGroup1217DisabledCount?: Maybe<Scalars['Int']>,
  femaleAdultsDisabledCount?: Maybe<Scalars['Int']>,
  maleAgeGroup05DisabledCount?: Maybe<Scalars['Int']>,
  maleAgeGroup611DisabledCount?: Maybe<Scalars['Int']>,
  maleAgeGroup1217DisabledCount?: Maybe<Scalars['Int']>,
  maleAdultsDisabledCount?: Maybe<Scalars['Int']>,
  returnee?: Maybe<Scalars['Boolean']>,
  fchildHoh?: Maybe<Scalars['Boolean']>,
  childHoh?: Maybe<Scalars['Boolean']>,
  start?: Maybe<Scalars['DateTime']>,
  end?: Maybe<Scalars['DateTime']>,
  nameEnumerator?: Maybe<Scalars['String']>,
  orgEnumerator?: Maybe<Scalars['String']>,
  orgNameEnumerator?: Maybe<Scalars['String']>,
  village?: Maybe<Scalars['String']>,
};

export enum ImportDataDataType {
  Xlsx = 'XLSX',
  Json = 'JSON'
}

export type ImportDataNode = Node & {
   __typename?: 'ImportDataNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  file: Scalars['String'],
  dataType: ImportDataDataType,
  numberOfHouseholds: Scalars['Int'],
  numberOfIndividuals: Scalars['Int'],
  registrationDataImport?: Maybe<RegistrationDataImportDatahubNode>,
};

export type ImportedDocumentNode = Node & {
   __typename?: 'ImportedDocumentNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  documentNumber: Scalars['String'],
  photo: Scalars['String'],
  individual: ImportedIndividualNode,
  type: ImportedDocumentTypeNode,
};

export type ImportedDocumentNodeConnection = {
   __typename?: 'ImportedDocumentNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<ImportedDocumentNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type ImportedDocumentNodeEdge = {
   __typename?: 'ImportedDocumentNodeEdge',
  node?: Maybe<ImportedDocumentNode>,
  cursor: Scalars['String'],
};

export enum ImportedDocumentTypeCountry {
  Af = 'AF',
  Ax = 'AX',
  Al = 'AL',
  Dz = 'DZ',
  As = 'AS',
  Ad = 'AD',
  Ao = 'AO',
  Ai = 'AI',
  Aq = 'AQ',
  Ag = 'AG',
  Ar = 'AR',
  Am = 'AM',
  Aw = 'AW',
  Au = 'AU',
  At = 'AT',
  Az = 'AZ',
  Bs = 'BS',
  Bh = 'BH',
  Bd = 'BD',
  Bb = 'BB',
  By = 'BY',
  Be = 'BE',
  Bz = 'BZ',
  Bj = 'BJ',
  Bm = 'BM',
  Bt = 'BT',
  Bo = 'BO',
  Bq = 'BQ',
  Ba = 'BA',
  Bw = 'BW',
  Bv = 'BV',
  Br = 'BR',
  Io = 'IO',
  Bn = 'BN',
  Bg = 'BG',
  Bf = 'BF',
  Bi = 'BI',
  Cv = 'CV',
  Kh = 'KH',
  Cm = 'CM',
  Ca = 'CA',
  Ky = 'KY',
  Cf = 'CF',
  Td = 'TD',
  Cl = 'CL',
  Cn = 'CN',
  Cx = 'CX',
  Cc = 'CC',
  Co = 'CO',
  Km = 'KM',
  Cg = 'CG',
  Cd = 'CD',
  Ck = 'CK',
  Cr = 'CR',
  Ci = 'CI',
  Hr = 'HR',
  Cu = 'CU',
  Cw = 'CW',
  Cy = 'CY',
  Cz = 'CZ',
  Dk = 'DK',
  Dj = 'DJ',
  Dm = 'DM',
  Do = 'DO',
  Ec = 'EC',
  Eg = 'EG',
  Sv = 'SV',
  Gq = 'GQ',
  Er = 'ER',
  Ee = 'EE',
  Sz = 'SZ',
  Et = 'ET',
  Fk = 'FK',
  Fo = 'FO',
  Fj = 'FJ',
  Fi = 'FI',
  Fr = 'FR',
  Gf = 'GF',
  Pf = 'PF',
  Tf = 'TF',
  Ga = 'GA',
  Gm = 'GM',
  Ge = 'GE',
  De = 'DE',
  Gh = 'GH',
  Gi = 'GI',
  Gr = 'GR',
  Gl = 'GL',
  Gd = 'GD',
  Gp = 'GP',
  Gu = 'GU',
  Gt = 'GT',
  Gg = 'GG',
  Gn = 'GN',
  Gw = 'GW',
  Gy = 'GY',
  Ht = 'HT',
  Hm = 'HM',
  Va = 'VA',
  Hn = 'HN',
  Hk = 'HK',
  Hu = 'HU',
  Is = 'IS',
  In = 'IN',
  Id = 'ID',
  Ir = 'IR',
  Iq = 'IQ',
  Ie = 'IE',
  Im = 'IM',
  Il = 'IL',
  It = 'IT',
  Jm = 'JM',
  Jp = 'JP',
  Je = 'JE',
  Jo = 'JO',
  Kz = 'KZ',
  Ke = 'KE',
  Ki = 'KI',
  Kw = 'KW',
  Kg = 'KG',
  La = 'LA',
  Lv = 'LV',
  Lb = 'LB',
  Ls = 'LS',
  Lr = 'LR',
  Ly = 'LY',
  Li = 'LI',
  Lt = 'LT',
  Lu = 'LU',
  Mo = 'MO',
  Mg = 'MG',
  Mw = 'MW',
  My = 'MY',
  Mv = 'MV',
  Ml = 'ML',
  Mt = 'MT',
  Mh = 'MH',
  Mq = 'MQ',
  Mr = 'MR',
  Mu = 'MU',
  Yt = 'YT',
  Mx = 'MX',
  Fm = 'FM',
  Md = 'MD',
  Mc = 'MC',
  Mn = 'MN',
  Me = 'ME',
  Ms = 'MS',
  Ma = 'MA',
  Mz = 'MZ',
  Mm = 'MM',
  Na = 'NA',
  Nr = 'NR',
  Np = 'NP',
  Nl = 'NL',
  Nc = 'NC',
  Nz = 'NZ',
  Ni = 'NI',
  Ne = 'NE',
  Ng = 'NG',
  Nu = 'NU',
  Nf = 'NF',
  Kp = 'KP',
  Mk = 'MK',
  Mp = 'MP',
  No = 'NO',
  Om = 'OM',
  Pk = 'PK',
  Pw = 'PW',
  Ps = 'PS',
  Pa = 'PA',
  Pg = 'PG',
  Py = 'PY',
  Pe = 'PE',
  Ph = 'PH',
  Pn = 'PN',
  Pl = 'PL',
  Pt = 'PT',
  Pr = 'PR',
  Qa = 'QA',
  Re = 'RE',
  Ro = 'RO',
  Ru = 'RU',
  Rw = 'RW',
  Bl = 'BL',
  Sh = 'SH',
  Kn = 'KN',
  Lc = 'LC',
  Mf = 'MF',
  Pm = 'PM',
  Vc = 'VC',
  Ws = 'WS',
  Sm = 'SM',
  St = 'ST',
  Sa = 'SA',
  Sn = 'SN',
  Rs = 'RS',
  Sc = 'SC',
  Sl = 'SL',
  Sg = 'SG',
  Sx = 'SX',
  Sk = 'SK',
  Si = 'SI',
  Sb = 'SB',
  So = 'SO',
  Za = 'ZA',
  Gs = 'GS',
  Kr = 'KR',
  Ss = 'SS',
  Es = 'ES',
  Lk = 'LK',
  Sd = 'SD',
  Sr = 'SR',
  Sj = 'SJ',
  Se = 'SE',
  Ch = 'CH',
  Sy = 'SY',
  Tw = 'TW',
  Tj = 'TJ',
  Tz = 'TZ',
  Th = 'TH',
  Tl = 'TL',
  Tg = 'TG',
  Tk = 'TK',
  To = 'TO',
  Tt = 'TT',
  Tn = 'TN',
  Tr = 'TR',
  Tm = 'TM',
  Tc = 'TC',
  Tv = 'TV',
  Ug = 'UG',
  Ua = 'UA',
  Ae = 'AE',
  Gb = 'GB',
  Um = 'UM',
  Us = 'US',
  Uy = 'UY',
  Uz = 'UZ',
  Vu = 'VU',
  Ve = 'VE',
  Vn = 'VN',
  Vg = 'VG',
  Vi = 'VI',
  Wf = 'WF',
  Eh = 'EH',
  Ye = 'YE',
  Zm = 'ZM',
  Zw = 'ZW'
}

export type ImportedDocumentTypeNode = {
   __typename?: 'ImportedDocumentTypeNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  country?: Maybe<ImportedDocumentTypeCountry>,
  label: Scalars['String'],
  type: ImportedDocumentTypeType,
  documents: ImportedDocumentNodeConnection,
};


export type ImportedDocumentTypeNodeDocumentsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export enum ImportedDocumentTypeType {
  BirthCertificate = 'BIRTH_CERTIFICATE',
  DriversLicense = 'DRIVERS_LICENSE',
  NationalId = 'NATIONAL_ID',
  NationalPassport = 'NATIONAL_PASSPORT',
  ElectoralCard = 'ELECTORAL_CARD',
  Other = 'OTHER'
}

export enum ImportedHouseholdConsentSharing {
  Unicef = 'UNICEF',
  HumanitarianPartner = 'HUMANITARIAN_PARTNER',
  PrivatePartner = 'PRIVATE_PARTNER',
  GovernmentPartner = 'GOVERNMENT_PARTNER'
}

export type ImportedHouseholdNode = Node & {
   __typename?: 'ImportedHouseholdNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  consentSign: Scalars['String'],
  consent: Scalars['Boolean'],
  consentSharing: ImportedHouseholdConsentSharing,
  residenceStatus: ImportedHouseholdResidenceStatus,
  countryOrigin?: Maybe<Scalars['String']>,
  size: Scalars['Int'],
  address: Scalars['String'],
  country?: Maybe<Scalars['String']>,
  admin1: Scalars['String'],
  admin2: Scalars['String'],
  geopoint?: Maybe<Scalars['GeoJSON']>,
  femaleAgeGroup05Count: Scalars['Int'],
  femaleAgeGroup611Count: Scalars['Int'],
  femaleAgeGroup1217Count: Scalars['Int'],
  femaleAdultsCount: Scalars['Int'],
  pregnantCount: Scalars['Int'],
  maleAgeGroup05Count: Scalars['Int'],
  maleAgeGroup611Count: Scalars['Int'],
  maleAgeGroup1217Count: Scalars['Int'],
  maleAdultsCount: Scalars['Int'],
  femaleAgeGroup05DisabledCount: Scalars['Int'],
  femaleAgeGroup611DisabledCount: Scalars['Int'],
  femaleAgeGroup1217DisabledCount: Scalars['Int'],
  femaleAdultsDisabledCount: Scalars['Int'],
  maleAgeGroup05DisabledCount: Scalars['Int'],
  maleAgeGroup611DisabledCount: Scalars['Int'],
  maleAgeGroup1217DisabledCount: Scalars['Int'],
  maleAdultsDisabledCount: Scalars['Int'],
  headOfHousehold?: Maybe<ImportedIndividualNode>,
  fchildHoh: Scalars['Boolean'],
  childHoh: Scalars['Boolean'],
  registrationDataImport: RegistrationDataImportDatahubNode,
  firstRegistrationDate: Scalars['Date'],
  lastRegistrationDate: Scalars['Date'],
  returnee: Scalars['Boolean'],
  flexFields: Scalars['JSONString'],
  start?: Maybe<Scalars['DateTime']>,
  end?: Maybe<Scalars['DateTime']>,
  deviceid: Scalars['String'],
  nameEnumerator: Scalars['String'],
  orgEnumerator: ImportedHouseholdOrgEnumerator,
  orgNameEnumerator: Scalars['String'],
  village: Scalars['String'],
  individuals: ImportedIndividualNodeConnection,
  hasDuplicates?: Maybe<Scalars['Boolean']>,
};


export type ImportedHouseholdNodeIndividualsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type ImportedHouseholdNodeConnection = {
   __typename?: 'ImportedHouseholdNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<ImportedHouseholdNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type ImportedHouseholdNodeEdge = {
   __typename?: 'ImportedHouseholdNodeEdge',
  node?: Maybe<ImportedHouseholdNode>,
  cursor: Scalars['String'],
};

export enum ImportedHouseholdOrgEnumerator {
  Unicef = 'UNICEF',
  Partner = 'PARTNER'
}

export enum ImportedHouseholdResidenceStatus {
  Idp = 'IDP',
  Refugee = 'REFUGEE',
  OthersOfConcern = 'OTHERS_OF_CONCERN',
  Host = 'HOST',
  NonHost = 'NON_HOST'
}

export enum ImportedIndividualCommsDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum ImportedIndividualDeduplicationBatchStatus {
  SimilarInBatch = 'SIMILAR_IN_BATCH',
  DuplicateInBatch = 'DUPLICATE_IN_BATCH',
  UniqueInBatch = 'UNIQUE_IN_BATCH',
  NotProcessed = 'NOT_PROCESSED'
}

export enum ImportedIndividualDeduplicationGoldenRecordStatus {
  Unique = 'UNIQUE',
  Duplicate = 'DUPLICATE',
  NeedsAdjudication = 'NEEDS_ADJUDICATION',
  NotProcessed = 'NOT_PROCESSED'
}

export enum ImportedIndividualHearingDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export type ImportedIndividualIdentityNode = {
   __typename?: 'ImportedIndividualIdentityNode',
  id: Scalars['ID'],
  individual: ImportedIndividualNode,
  documentNumber: Scalars['String'],
  type?: Maybe<Scalars['String']>,
};

export enum ImportedIndividualMaritalStatus {
  Single = 'SINGLE',
  Married = 'MARRIED',
  Widowed = 'WIDOWED',
  Divorced = 'DIVORCED',
  Separated = 'SEPARATED'
}

export enum ImportedIndividualMemoryDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export type ImportedIndividualNode = Node & {
   __typename?: 'ImportedIndividualNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  individualId: Scalars['String'],
  photo: Scalars['String'],
  fullName: Scalars['String'],
  givenName: Scalars['String'],
  middleName: Scalars['String'],
  familyName: Scalars['String'],
  relationship?: Maybe<Scalars['String']>,
  sex: ImportedIndividualSex,
  birthDate: Scalars['Date'],
  estimatedBirthDate?: Maybe<Scalars['Boolean']>,
  maritalStatus: ImportedIndividualMaritalStatus,
  phoneNo: Scalars['String'],
  phoneNoAlternative: Scalars['String'],
  household?: Maybe<ImportedHouseholdNode>,
  registrationDataImport: RegistrationDataImportDatahubNode,
  disability: Scalars['Boolean'],
  workStatus?: Maybe<ImportedIndividualWorkStatus>,
  firstRegistrationDate: Scalars['Date'],
  lastRegistrationDate: Scalars['Date'],
  deduplicationBatchStatus?: Maybe<ImportedIndividualDeduplicationBatchStatus>,
  deduplicationGoldenRecordStatus?: Maybe<ImportedIndividualDeduplicationGoldenRecordStatus>,
  deduplicationBatchResults?: Maybe<Array<Maybe<DeduplicationResultNode>>>,
  deduplicationGoldenRecordResults?: Maybe<Array<Maybe<DeduplicationResultNode>>>,
  flexFields: Scalars['JSONString'],
  pregnant: Scalars['Boolean'],
  observedDisability: ImportedIndividualObservedDisability,
  seeingDisability?: Maybe<ImportedIndividualSeeingDisability>,
  hearingDisability?: Maybe<ImportedIndividualHearingDisability>,
  physicalDisability?: Maybe<ImportedIndividualPhysicalDisability>,
  memoryDisability?: Maybe<ImportedIndividualMemoryDisability>,
  selfcareDisability?: Maybe<ImportedIndividualSelfcareDisability>,
  commsDisability?: Maybe<ImportedIndividualCommsDisability>,
  whoAnswersPhone: Scalars['String'],
  whoAnswersAltPhone: Scalars['String'],
  importedhousehold?: Maybe<ImportedHouseholdNode>,
  documents: ImportedDocumentNodeConnection,
  identities: Array<ImportedIndividualIdentityNode>,
  role?: Maybe<Scalars['String']>,
};


export type ImportedIndividualNodeDocumentsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type ImportedIndividualNodeConnection = {
   __typename?: 'ImportedIndividualNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<ImportedIndividualNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type ImportedIndividualNodeEdge = {
   __typename?: 'ImportedIndividualNodeEdge',
  node?: Maybe<ImportedIndividualNode>,
  cursor: Scalars['String'],
};

export enum ImportedIndividualObservedDisability {
  None = 'NONE',
  Seeing = 'SEEING',
  Hearing = 'HEARING',
  Walking = 'WALKING',
  Memory = 'MEMORY',
  SelfCare = 'SELF_CARE',
  Communicating = 'COMMUNICATING'
}

export enum ImportedIndividualPhysicalDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum ImportedIndividualSeeingDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum ImportedIndividualSelfcareDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum ImportedIndividualSex {
  Male = 'MALE',
  Female = 'FEMALE'
}

export enum ImportedIndividualWorkStatus {
  Yes = 'YES',
  No = 'NO',
  NotProvided = 'NOT_PROVIDED'
}

export type ImportXlsxCashPlanVerification = {
   __typename?: 'ImportXlsxCashPlanVerification',
  cashPlan?: Maybe<CashPlanNode>,
  errors?: Maybe<Array<Maybe<XlsxErrorNode>>>,
};

export enum IndividualCommsDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export type IndividualDataUpdateIssueTypeExtras = {
  individual: Scalars['ID'],
  individualData: IndividualUpdateDataObjectType,
};

export enum IndividualDeduplicationBatchStatus {
  SimilarInBatch = 'SIMILAR_IN_BATCH',
  DuplicateInBatch = 'DUPLICATE_IN_BATCH',
  UniqueInBatch = 'UNIQUE_IN_BATCH',
  NotProcessed = 'NOT_PROCESSED'
}

export enum IndividualDeduplicationGoldenRecordStatus {
  Unique = 'UNIQUE',
  Duplicate = 'DUPLICATE',
  NeedsAdjudication = 'NEEDS_ADJUDICATION',
  NotProcessed = 'NOT_PROCESSED'
}

export type IndividualDeleteIssueTypeExtras = {
  individual: Scalars['ID'],
};

export enum IndividualHearingDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export type IndividualIdentityNode = {
   __typename?: 'IndividualIdentityNode',
  id: Scalars['ID'],
  individual: IndividualNode,
  number: Scalars['String'],
  type?: Maybe<Scalars['String']>,
};

export enum IndividualMaritalStatus {
  Single = 'SINGLE',
  Married = 'MARRIED',
  Widowed = 'WIDOWED',
  Divorced = 'DIVORCED',
  Separated = 'SEPARATED'
}

export enum IndividualMemoryDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export type IndividualNode = Node & {
   __typename?: 'IndividualNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  lastSyncAt?: Maybe<Scalars['DateTime']>,
  status: IndividualStatus,
  individualId: Scalars['String'],
  photo: Scalars['String'],
  fullName: Scalars['String'],
  givenName: Scalars['String'],
  middleName: Scalars['String'],
  familyName: Scalars['String'],
  sex: IndividualSex,
  birthDate: Scalars['Date'],
  estimatedBirthDate?: Maybe<Scalars['Boolean']>,
  maritalStatus: IndividualMaritalStatus,
  phoneNo: Scalars['String'],
  phoneNoAlternative: Scalars['String'],
  relationship?: Maybe<IndividualRelationship>,
  household?: Maybe<HouseholdNode>,
  registrationDataImport: RegistrationDataImportNode,
  disability: Scalars['Boolean'],
  workStatus?: Maybe<IndividualWorkStatus>,
  firstRegistrationDate: Scalars['Date'],
  lastRegistrationDate: Scalars['Date'],
  flexFields?: Maybe<Scalars['FlexFieldsScalar']>,
  enrolledInNutritionProgramme: Scalars['Boolean'],
  administrationOfRutf: Scalars['Boolean'],
  unicefId: Scalars['String'],
  deduplicationGoldenRecordStatus: IndividualDeduplicationGoldenRecordStatus,
  deduplicationBatchStatus: IndividualDeduplicationBatchStatus,
  deduplicationGoldenRecordResults?: Maybe<Array<Maybe<DeduplicationResultNode>>>,
  deduplicationBatchResults?: Maybe<Array<Maybe<DeduplicationResultNode>>>,
  importedIndividualId?: Maybe<Scalars['UUID']>,
  sanctionListPossibleMatch: Scalars['Boolean'],
  sanctionListLastCheck?: Maybe<Scalars['DateTime']>,
  pregnant: Scalars['Boolean'],
  observedDisability: IndividualObservedDisability,
  seeingDisability?: Maybe<IndividualSeeingDisability>,
  hearingDisability?: Maybe<IndividualHearingDisability>,
  physicalDisability?: Maybe<IndividualPhysicalDisability>,
  memoryDisability?: Maybe<IndividualMemoryDisability>,
  selfcareDisability?: Maybe<IndividualSelfcareDisability>,
  commsDisability?: Maybe<IndividualCommsDisability>,
  whoAnswersPhone: Scalars['String'],
  whoAnswersAltPhone: Scalars['String'],
  complaintTicketDetails: TicketComplaintDetailsNodeConnection,
  sensitiveTicketDetails: TicketSensitiveDetailsNodeConnection,
  individualDataUpdateTicketDetails: TicketIndividualDataUpdateDetailsNodeConnection,
  deleteIndividualTicketDetails: TicketDeleteIndividualDetailsNodeConnection,
  representedHouseholds: HouseholdNodeConnection,
  headingHousehold?: Maybe<HouseholdNode>,
  documents: DocumentNodeConnection,
  identities: Array<IndividualIdentityNode>,
  householdsAndRoles: Array<IndividualRoleInHouseholdNode>,
  role?: Maybe<Scalars['String']>,
};


export type IndividualNodeComplaintTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type IndividualNodeSensitiveTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type IndividualNodeIndividualDataUpdateTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type IndividualNodeDeleteIndividualTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type IndividualNodeRepresentedHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type IndividualNodeDocumentsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type IndividualNodeConnection = {
   __typename?: 'IndividualNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<IndividualNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type IndividualNodeEdge = {
   __typename?: 'IndividualNodeEdge',
  node?: Maybe<IndividualNode>,
  cursor: Scalars['String'],
};

export enum IndividualObservedDisability {
  None = 'NONE',
  Seeing = 'SEEING',
  Hearing = 'HEARING',
  Walking = 'WALKING',
  Memory = 'MEMORY',
  SelfCare = 'SELF_CARE',
  Communicating = 'COMMUNICATING'
}

export enum IndividualPhysicalDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum IndividualRelationship {
  NonBeneficiary = 'NON_BENEFICIARY',
  Head = 'HEAD',
  SonDaughter = 'SON_DAUGHTER',
  WifeHusband = 'WIFE_HUSBAND',
  BrotherSister = 'BROTHER_SISTER',
  MotherFather = 'MOTHER_FATHER',
  AuntUncle = 'AUNT_UNCLE',
  GrandmotherGrandfather = 'GRANDMOTHER_GRANDFATHER',
  MotherinlawFatherinlaw = 'MOTHERINLAW_FATHERINLAW',
  DaughterinlawSoninlaw = 'DAUGHTERINLAW_SONINLAW',
  SisterinlawBrotherinlaw = 'SISTERINLAW_BROTHERINLAW',
  GranddaugherGrandson = 'GRANDDAUGHER_GRANDSON',
  NephewNiece = 'NEPHEW_NIECE',
  Cousin = 'COUSIN'
}

export type IndividualRoleInHouseholdNode = {
   __typename?: 'IndividualRoleInHouseholdNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  lastSyncAt?: Maybe<Scalars['DateTime']>,
  individual: IndividualNode,
  household: HouseholdNode,
  role?: Maybe<IndividualRoleInHouseholdRole>,
};

export enum IndividualRoleInHouseholdRole {
  Primary = 'PRIMARY',
  Alternate = 'ALTERNATE',
  NoRole = 'NO_ROLE'
}

export enum IndividualSeeingDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum IndividualSelfcareDisability {
  SomeDifficulty = 'SOME_DIFFICULTY',
  LotDifficulty = 'LOT_DIFFICULTY',
  CannotDo = 'CANNOT_DO'
}

export enum IndividualSex {
  Male = 'MALE',
  Female = 'FEMALE'
}

export enum IndividualStatus {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}

export type IndividualUpdateDataObjectType = {
  status?: Maybe<Scalars['String']>,
  fullName?: Maybe<Scalars['String']>,
  givenName?: Maybe<Scalars['String']>,
  middleName?: Maybe<Scalars['String']>,
  familyName?: Maybe<Scalars['String']>,
  sex?: Maybe<Scalars['String']>,
  birthDate?: Maybe<Scalars['Date']>,
  estimatedBirthDate?: Maybe<Scalars['Boolean']>,
  maritalStatus?: Maybe<Scalars['String']>,
  phoneNo?: Maybe<Scalars['String']>,
  phoneNoAlternative?: Maybe<Scalars['String']>,
  relationship?: Maybe<Scalars['String']>,
  disability?: Maybe<Scalars['Boolean']>,
  workStatus?: Maybe<Scalars['String']>,
  enrolledInNutritionProgramme?: Maybe<Scalars['Boolean']>,
  administrationOfRutf?: Maybe<Scalars['Boolean']>,
  pregnant?: Maybe<Scalars['Boolean']>,
  observedDisability?: Maybe<Array<Maybe<Scalars['String']>>>,
  seeingDisability?: Maybe<Scalars['String']>,
  hearingDisability?: Maybe<Scalars['String']>,
  physicalDisability?: Maybe<Scalars['String']>,
  memoryDisability?: Maybe<Scalars['String']>,
  selfcareDisability?: Maybe<Scalars['String']>,
  commsDisability?: Maybe<Scalars['String']>,
  whoAnswersPhone?: Maybe<Scalars['String']>,
  whoAnswersAltPhone?: Maybe<Scalars['String']>,
};

export enum IndividualWorkStatus {
  Yes = 'YES',
  No = 'NO',
  NotProvided = 'NOT_PROVIDED'
}

export type IssueTypeExtrasInput = {
  householdDataUpdateIssueTypeExtras?: Maybe<HouseholdDataUpdateIssueTypeExtras>,
  individualDataUpdateIssueTypeExtras?: Maybe<IndividualDataUpdateIssueTypeExtras>,
  individualDeleteIssueTypeExtras?: Maybe<IndividualDeleteIssueTypeExtras>,
  addIndividualIssueTypeExtras?: Maybe<AddIndividualIssueTypeExtras>,
};

export type IssueTypesObject = {
   __typename?: 'IssueTypesObject',
  category?: Maybe<Scalars['String']>,
  label?: Maybe<Scalars['String']>,
  subCategories?: Maybe<Array<Maybe<ChoiceObject>>>,
};



export type KoboAssetObject = {
   __typename?: 'KoboAssetObject',
  id?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  country?: Maybe<Scalars['String']>,
  assetType?: Maybe<Scalars['String']>,
  dateModified?: Maybe<Scalars['DateTime']>,
  deploymentActive?: Maybe<Scalars['Boolean']>,
  hasDeployment?: Maybe<Scalars['Boolean']>,
  xlsLink?: Maybe<Scalars['String']>,
};

export type KoboAssetObjectConnection = {
   __typename?: 'KoboAssetObjectConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<KoboAssetObjectEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
};

export type KoboAssetObjectEdge = {
   __typename?: 'KoboAssetObjectEdge',
  node?: Maybe<KoboAssetObject>,
  cursor: Scalars['String'],
};

export type KoboErrorNode = {
   __typename?: 'KoboErrorNode',
  header?: Maybe<Scalars['String']>,
  message?: Maybe<Scalars['String']>,
};

export type LabelNode = {
   __typename?: 'LabelNode',
  language?: Maybe<Scalars['String']>,
  label?: Maybe<Scalars['String']>,
};

export enum LogEntryAction {
  A_0 = 'A_0',
  A_1 = 'A_1',
  A_2 = 'A_2'
}

export type LogEntryObject = {
   __typename?: 'LogEntryObject',
  id: Scalars['ID'],
  objectPk: Scalars['String'],
  objectId?: Maybe<Scalars['Int']>,
  objectRepr: Scalars['String'],
  action: LogEntryAction,
  changes: Scalars['String'],
  actor?: Maybe<UserNode>,
  remoteAddr?: Maybe<Scalars['String']>,
  timestamp?: Maybe<Scalars['DateTime']>,
  changesDisplayDict?: Maybe<Scalars['JSONLazyString']>,
};

export type LogEntryObjectConnection = {
   __typename?: 'LogEntryObjectConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<LogEntryObjectEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
};

export type LogEntryObjectEdge = {
   __typename?: 'LogEntryObjectEdge',
  node?: Maybe<LogEntryObject>,
  cursor: Scalars['String'],
};

export type MergeRegistrationDataImportMutation = {
   __typename?: 'MergeRegistrationDataImportMutation',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type Mutations = {
   __typename?: 'Mutations',
  createGrievanceTicket?: Maybe<CreateGrievanceTicketMutation>,
  createCashPlanPaymentVerification?: Maybe<CreatePaymentVerificationMutation>,
  editCashPlanPaymentVerification?: Maybe<EditPaymentVerificationMutation>,
  importXlsxCashPlanVerification?: Maybe<ImportXlsxCashPlanVerification>,
  activateCashPlanPaymentVerification?: Maybe<ActivateCashPlanVerificationMutation>,
  finishCashPlanPaymentVerification?: Maybe<FinishCashPlanVerificationMutation>,
  discardCashPlanPaymentVerification?: Maybe<DiscardCashPlanVerificationMutation>,
  updatePaymentVerificationStatusAndReceivedAmount?: Maybe<UpdatePaymentVerificationStatusAndReceivedAmount>,
  updatePaymentVerificationReceivedAndReceivedAmount?: Maybe<UpdatePaymentVerificationReceivedAndReceivedAmount>,
  createTargetPopulation?: Maybe<CreateTargetPopulationMutation>,
  updateTargetPopulation?: Maybe<UpdateTargetPopulationMutation>,
  copyTargetPopulation?: Maybe<CopyTargetPopulationMutationPayload>,
  deleteTargetPopulation?: Maybe<DeleteTargetPopulationMutationPayload>,
  approveTargetPopulation?: Maybe<ApproveTargetPopulationMutation>,
  unapproveTargetPopulation?: Maybe<UnapproveTargetPopulationMutation>,
  finalizeTargetPopulation?: Maybe<FinalizeTargetPopulationMutation>,
  setSteficonRuleOnTargetPopulation?: Maybe<SetSteficonRuleOnTargetPopulationMutationPayload>,
  createProgram?: Maybe<CreateProgram>,
  updateProgram?: Maybe<UpdateProgram>,
  deleteProgram?: Maybe<DeleteProgram>,
  uploadImportDataXlsxFile?: Maybe<UploadImportDataXlsxFile>,
  deleteRegistrationDataImport?: Maybe<DeleteRegistrationDataImport>,
  registrationXlsxImport?: Maybe<RegistrationXlsxImportMutation>,
  registrationKoboImport?: Maybe<RegistrationKoboImportMutation>,
  saveKoboImportData?: Maybe<SaveKoboProjectImportDataMutation>,
  mergeRegistrationDataImport?: Maybe<MergeRegistrationDataImportMutation>,
  rerunDedupe?: Maybe<RegistrationDeduplicationMutation>,
  checkAgainstSanctionList?: Maybe<CheckAgainstSanctionListMutation>,
};


export type MutationsCreateGrievanceTicketArgs = {
  input: CreateGrievanceTicketInput
};


export type MutationsCreateCashPlanPaymentVerificationArgs = {
  input: CreatePaymentVerificationInput
};


export type MutationsEditCashPlanPaymentVerificationArgs = {
  input: EditCashPlanPaymentVerificationInput
};


export type MutationsImportXlsxCashPlanVerificationArgs = {
  cashPlanVerificationId: Scalars['ID'],
  file: Scalars['Upload']
};


export type MutationsActivateCashPlanPaymentVerificationArgs = {
  cashPlanVerificationId: Scalars['ID']
};


export type MutationsFinishCashPlanPaymentVerificationArgs = {
  cashPlanVerificationId: Scalars['ID']
};


export type MutationsDiscardCashPlanPaymentVerificationArgs = {
  cashPlanVerificationId: Scalars['ID']
};


export type MutationsUpdatePaymentVerificationStatusAndReceivedAmountArgs = {
  paymentVerificationId: Scalars['ID'],
  receivedAmount: Scalars['Decimal'],
  status?: Maybe<PaymentVerificationStatusForUpdate>
};


export type MutationsUpdatePaymentVerificationReceivedAndReceivedAmountArgs = {
  paymentVerificationId: Scalars['ID'],
  received: Scalars['Boolean'],
  receivedAmount: Scalars['Decimal']
};


export type MutationsCreateTargetPopulationArgs = {
  input: CreateTargetPopulationInput
};


export type MutationsUpdateTargetPopulationArgs = {
  input: UpdateTargetPopulationInput
};


export type MutationsCopyTargetPopulationArgs = {
  input: CopyTargetPopulationMutationInput
};


export type MutationsDeleteTargetPopulationArgs = {
  input: DeleteTargetPopulationMutationInput
};


export type MutationsApproveTargetPopulationArgs = {
  id: Scalars['ID']
};


export type MutationsUnapproveTargetPopulationArgs = {
  id: Scalars['ID']
};


export type MutationsFinalizeTargetPopulationArgs = {
  id: Scalars['ID']
};


export type MutationsSetSteficonRuleOnTargetPopulationArgs = {
  input: SetSteficonRuleOnTargetPopulationMutationInput
};


export type MutationsCreateProgramArgs = {
  programData: CreateProgramInput
};


export type MutationsUpdateProgramArgs = {
  programData?: Maybe<UpdateProgramInput>
};


export type MutationsDeleteProgramArgs = {
  programId: Scalars['String']
};


export type MutationsUploadImportDataXlsxFileArgs = {
  businessAreaSlug: Scalars['String'],
  file: Scalars['Upload']
};


export type MutationsDeleteRegistrationDataImportArgs = {
  registrationDataImportId: Scalars['String']
};


export type MutationsRegistrationXlsxImportArgs = {
  registrationDataImportData: RegistrationXlsxImportMutationInput
};


export type MutationsRegistrationKoboImportArgs = {
  registrationDataImportData: RegistrationKoboImportMutationInput
};


export type MutationsSaveKoboImportDataArgs = {
  businessAreaSlug: Scalars['String'],
  uid: Scalars['Upload']
};


export type MutationsMergeRegistrationDataImportArgs = {
  id: Scalars['ID']
};


export type MutationsRerunDedupeArgs = {
  registrationDataImportDatahubId: Scalars['ID']
};


export type MutationsCheckAgainstSanctionListArgs = {
  file: Scalars['Upload']
};

export type Node = {
  id: Scalars['ID'],
};

export type PageInfo = {
   __typename?: 'PageInfo',
  hasNextPage: Scalars['Boolean'],
  hasPreviousPage: Scalars['Boolean'],
  startCursor?: Maybe<Scalars['String']>,
  endCursor?: Maybe<Scalars['String']>,
};

export enum PaymentRecordDeliveryType {
  Cash = 'CASH',
  DepositToCard = 'DEPOSIT_TO_CARD',
  Transfer = 'TRANSFER'
}

export enum PaymentRecordEntitlementCardStatus {
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}

export type PaymentRecordNode = Node & {
   __typename?: 'PaymentRecordNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  businessArea: UserBusinessAreaNode,
  status: PaymentRecordStatus,
  statusDate: Scalars['DateTime'],
  caId?: Maybe<Scalars['String']>,
  caHashId?: Maybe<Scalars['UUID']>,
  cashPlan?: Maybe<CashPlanNode>,
  household: HouseholdNode,
  fullName: Scalars['String'],
  totalPersonsCovered: Scalars['Int'],
  distributionModality: Scalars['String'],
  targetPopulation: TargetPopulationNode,
  targetPopulationCashAssistId: Scalars['String'],
  entitlementCardNumber: Scalars['String'],
  entitlementCardStatus: PaymentRecordEntitlementCardStatus,
  entitlementCardIssueDate: Scalars['Date'],
  deliveryType: PaymentRecordDeliveryType,
  currency: Scalars['String'],
  entitlementQuantity: Scalars['Float'],
  deliveredQuantity: Scalars['Float'],
  deliveryDate: Scalars['DateTime'],
  serviceProvider: ServiceProviderNode,
  transactionReferenceId?: Maybe<Scalars['String']>,
  visionId?: Maybe<Scalars['String']>,
  complaintTicketDetails: TicketComplaintDetailsNodeConnection,
  sensitiveTicketDetails: TicketSensitiveDetailsNodeConnection,
  verifications: PaymentVerificationNodeConnection,
};


export type PaymentRecordNodeComplaintTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type PaymentRecordNodeSensitiveTicketDetailsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type PaymentRecordNodeVerificationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type PaymentRecordNodeConnection = {
   __typename?: 'PaymentRecordNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<PaymentRecordNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type PaymentRecordNodeEdge = {
   __typename?: 'PaymentRecordNodeEdge',
  node?: Maybe<PaymentRecordNode>,
  cursor: Scalars['String'],
};

export enum PaymentRecordStatus {
  Success = 'SUCCESS',
  Pending = 'PENDING',
  Error = 'ERROR'
}

export type PaymentVerificationNode = Node & {
   __typename?: 'PaymentVerificationNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  cashPlanPaymentVerification: CashPlanPaymentVerificationNode,
  paymentRecord: PaymentRecordNode,
  status: PaymentVerificationStatus,
  statusDate?: Maybe<Scalars['Date']>,
  receivedAmount?: Maybe<Scalars['Float']>,
};

export type PaymentVerificationNodeConnection = {
   __typename?: 'PaymentVerificationNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<PaymentVerificationNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type PaymentVerificationNodeEdge = {
   __typename?: 'PaymentVerificationNodeEdge',
  node?: Maybe<PaymentVerificationNode>,
  cursor: Scalars['String'],
};

export enum PaymentVerificationStatus {
  Pending = 'PENDING',
  Received = 'RECEIVED',
  NotReceived = 'NOT_RECEIVED',
  ReceivedWithIssues = 'RECEIVED_WITH_ISSUES'
}

export enum PaymentVerificationStatusForUpdate {
  Pending = 'PENDING',
  Received = 'RECEIVED',
  NotReceived = 'NOT_RECEIVED',
  ReceivedWithIssues = 'RECEIVED_WITH_ISSUES'
}

export enum ProgramFrequencyOfPayments {
  Regular = 'REGULAR',
  OneOff = 'ONE_OFF'
}

export type ProgramNode = Node & {
   __typename?: 'ProgramNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  lastSyncAt?: Maybe<Scalars['DateTime']>,
  name: Scalars['String'],
  status: ProgramStatus,
  startDate: Scalars['Date'],
  endDate: Scalars['Date'],
  description: Scalars['String'],
  caId?: Maybe<Scalars['String']>,
  caHashId?: Maybe<Scalars['String']>,
  adminAreas: AdminAreaNodeConnection,
  businessArea: UserBusinessAreaNode,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments: ProgramFrequencyOfPayments,
  sector: ProgramSector,
  scope: ProgramScope,
  cashPlus: Scalars['Boolean'],
  populationGoal: Scalars['Int'],
  administrativeAreasOfImplementation: Scalars['String'],
  individualDataNeeded?: Maybe<Scalars['Boolean']>,
  households: HouseholdNodeConnection,
  cashPlans: CashPlanNodeConnection,
  targetpopulationSet: TargetPopulationNodeConnection,
  totalEntitledQuantity?: Maybe<Scalars['Decimal']>,
  totalDeliveredQuantity?: Maybe<Scalars['Decimal']>,
  totalUndeliveredQuantity?: Maybe<Scalars['Decimal']>,
  totalNumberOfHouseholds?: Maybe<Scalars['Int']>,
  history?: Maybe<LogEntryObjectConnection>,
};


export type ProgramNodeAdminAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
};


export type ProgramNodeHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type ProgramNodeCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type ProgramNodeTargetpopulationSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type ProgramNodeHistoryArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type ProgramNodeConnection = {
   __typename?: 'ProgramNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<ProgramNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type ProgramNodeEdge = {
   __typename?: 'ProgramNodeEdge',
  node?: Maybe<ProgramNode>,
  cursor: Scalars['String'],
};

export enum ProgramScope {
  ForPartners = 'FOR_PARTNERS',
  Unicef = 'UNICEF'
}

export enum ProgramSector {
  ChildProtection = 'CHILD_PROTECTION',
  Education = 'EDUCATION',
  Health = 'HEALTH',
  MultiPurpose = 'MULTI_PURPOSE',
  Nutrition = 'NUTRITION',
  SocialPolicy = 'SOCIAL_POLICY',
  Wash = 'WASH'
}

export enum ProgramStatus {
  Draft = 'DRAFT',
  Active = 'ACTIVE',
  Finished = 'FINISHED'
}

export type Query = {
   __typename?: 'Query',
  grievanceTicket?: Maybe<GrievanceTicketNode>,
  allGrievanceTicket?: Maybe<GrievanceTicketNodeConnection>,
  grievanceTicketStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  grievanceTicketCategoryChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  grievanceTicketIssueTypeChoices?: Maybe<Array<Maybe<IssueTypesObject>>>,
  allSteficonRules?: Maybe<SteficonRuleNodeConnection>,
  paymentRecord?: Maybe<PaymentRecordNode>,
  paymentRecordVerification?: Maybe<PaymentVerificationNode>,
  allPaymentRecords?: Maybe<PaymentRecordNodeConnection>,
  allPaymentVerifications?: Maybe<PaymentVerificationNodeConnection>,
  paymentRecordStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  paymentRecordEntitlementCardStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  paymentRecordDeliveryTypeChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  cashPlanVerificationStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  cashPlanVerificationSamplingChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  cashPlanVerificationVerificationMethodChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  paymentVerificationStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  allRapidProFlows?: Maybe<Array<Maybe<RapidProFlow>>>,
  sampleSize?: Maybe<GetCashplanVerificationSampleSizeObject>,
  adminArea?: Maybe<AdminAreaNode>,
  allAdminAreas?: Maybe<AdminAreaNodeConnection>,
  allBusinessAreas?: Maybe<BusinessAreaNodeConnection>,
  allFieldsAttributes?: Maybe<Array<Maybe<FieldAttributeNode>>>,
  allGroupsWithFields?: Maybe<Array<Maybe<GroupAttributeNode>>>,
  koboProject?: Maybe<KoboAssetObject>,
  allKoboProjects?: Maybe<KoboAssetObjectConnection>,
  cashAssistUrlPrefix?: Maybe<Scalars['String']>,
  program?: Maybe<ProgramNode>,
  allPrograms?: Maybe<ProgramNodeConnection>,
  cashPlan?: Maybe<CashPlanNode>,
  allCashPlans?: Maybe<CashPlanNodeConnection>,
  programStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  programFrequencyOfPaymentsChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  programSectorChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  programScopeChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  cashPlanStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  targetPopulation?: Maybe<TargetPopulationNode>,
  allTargetPopulation?: Maybe<TargetPopulationNodeConnection>,
  goldenRecordByTargetingCriteria?: Maybe<HouseholdNodeConnection>,
  candidateHouseholdsListByTargetingCriteria?: Maybe<HouseholdNodeConnection>,
  finalHouseholdsListByTargetingCriteria?: Maybe<HouseholdNodeConnection>,
  targetPopulationStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  household?: Maybe<HouseholdNode>,
  allHouseholds?: Maybe<HouseholdNodeConnection>,
  individual?: Maybe<IndividualNode>,
  allIndividuals?: Maybe<IndividualNodeConnection>,
  residenceStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  sexChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  maritalStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  relationshipChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  roleChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  me?: Maybe<UserObjectType>,
  allUsers?: Maybe<UserNodeConnection>,
  allLogEntries?: Maybe<LogEntryObjectConnection>,
  userRolesChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  userStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  userPartnerChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  hasAvailableUsersToExport?: Maybe<Scalars['Boolean']>,
  importedHousehold?: Maybe<ImportedHouseholdNode>,
  allImportedHouseholds?: Maybe<ImportedHouseholdNodeConnection>,
  registrationDataImportDatahub?: Maybe<RegistrationDataImportDatahubNode>,
  allRegistrationDataImportsDatahub?: Maybe<RegistrationDataImportDatahubNodeConnection>,
  importedIndividual?: Maybe<ImportedIndividualNode>,
  allImportedIndividuals?: Maybe<ImportedIndividualNodeConnection>,
  importData?: Maybe<ImportDataNode>,
  deduplicationBatchStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  deduplicationGoldenRecordStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
  allRegistrationDataImports?: Maybe<RegistrationDataImportNodeConnection>,
  registrationDataStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  _debug?: Maybe<DjangoDebug>,
};


export type QueryGrievanceTicketArgs = {
  id: Scalars['ID']
};


export type QueryAllGrievanceTicketArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>,
  id_Icontains?: Maybe<Scalars['UUID']>,
  category?: Maybe<Scalars['String']>,
  area?: Maybe<Scalars['String']>,
  area_Icontains?: Maybe<Scalars['String']>,
  assignedTo?: Maybe<Scalars['ID']>,
  businessArea: Scalars['String'],
  search?: Maybe<Scalars['String']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  fsp?: Maybe<Array<Maybe<Scalars['ID']>>>,
  admin?: Maybe<Array<Maybe<Scalars['ID']>>>,
  createdAtRange?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryAllSteficonRulesArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  enabled?: Maybe<Scalars['Boolean']>,
  deprecated?: Maybe<Scalars['Boolean']>
};


export type QueryPaymentRecordArgs = {
  id: Scalars['ID']
};


export type QueryPaymentRecordVerificationArgs = {
  id: Scalars['ID']
};


export type QueryAllPaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>,
  individual?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryAllPaymentVerificationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlanPaymentVerification?: Maybe<Scalars['ID']>,
  status?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryAllRapidProFlowsArgs = {
  businessAreaSlug: Scalars['String']
};


export type QuerySampleSizeArgs = {
  input?: Maybe<GetCashplanVerificationSampleSizeInput>
};


export type QueryAdminAreaArgs = {
  id: Scalars['ID']
};


export type QueryAllAdminAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>,
  title_Icontains?: Maybe<Scalars['String']>,
  businessArea?: Maybe<Scalars['String']>
};


export type QueryAllBusinessAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>
};


export type QueryAllFieldsAttributesArgs = {
  flexField?: Maybe<Scalars['Boolean']>
};


export type QueryKoboProjectArgs = {
  uid: Scalars['String'],
  businessAreaSlug: Scalars['String']
};


export type QueryAllKoboProjectsArgs = {
  businessAreaSlug: Scalars['String'],
  onlyDeployed?: Maybe<Scalars['Boolean']>,
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryProgramArgs = {
  id: Scalars['ID']
};


export type QueryAllProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  businessArea: Scalars['String'],
  search?: Maybe<Scalars['String']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  sector?: Maybe<Array<Maybe<Scalars['String']>>>,
  numberOfHouseholds?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['Date']>,
  endDate?: Maybe<Scalars['Date']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryCashPlanArgs = {
  id: Scalars['ID']
};


export type QueryAllCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  program?: Maybe<Scalars['ID']>,
  assistanceThrough?: Maybe<Scalars['String']>,
  assistanceThrough_Icontains?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['DateTime']>,
  startDate_Lte?: Maybe<Scalars['DateTime']>,
  startDate_Gte?: Maybe<Scalars['DateTime']>,
  endDate?: Maybe<Scalars['DateTime']>,
  endDate_Lte?: Maybe<Scalars['DateTime']>,
  endDate_Gte?: Maybe<Scalars['DateTime']>,
  search?: Maybe<Scalars['String']>,
  deliveryType?: Maybe<Array<Maybe<Scalars['String']>>>,
  verificationStatus?: Maybe<Array<Maybe<Scalars['String']>>>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryTargetPopulationArgs = {
  id: Scalars['ID']
};


export type QueryAllTargetPopulationArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryGoldenRecordByTargetingCriteriaArgs = {
  targetingCriteria: TargetingCriteriaObjectType,
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryCandidateHouseholdsListByTargetingCriteriaArgs = {
  targetPopulation: Scalars['ID'],
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryFinalHouseholdsListByTargetingCriteriaArgs = {
  targetPopulation: Scalars['ID'],
  targetingCriteria?: Maybe<TargetingCriteriaObjectType>,
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryHouseholdArgs = {
  id: Scalars['ID']
};


export type QueryAllHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  countryOrigin?: Maybe<Scalars['String']>,
  countryOrigin_Icontains?: Maybe<Scalars['String']>,
  address?: Maybe<Scalars['String']>,
  address_Icontains?: Maybe<Scalars['String']>,
  headOfHousehold_FullName?: Maybe<Scalars['String']>,
  headOfHousehold_FullName_Icontains?: Maybe<Scalars['String']>,
  size_Range?: Maybe<Scalars['Int']>,
  size_Lte?: Maybe<Scalars['Int']>,
  size_Gte?: Maybe<Scalars['Int']>,
  adminArea?: Maybe<Scalars['ID']>,
  targetPopulations?: Maybe<Array<Maybe<Scalars['ID']>>>,
  programs?: Maybe<Array<Maybe<Scalars['ID']>>>,
  residenceStatus?: Maybe<Scalars['String']>,
  size?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>,
  lastRegistrationDate?: Maybe<Scalars['String']>,
  admin2?: Maybe<Array<Maybe<Scalars['ID']>>>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryIndividualArgs = {
  id: Scalars['ID']
};


export type QueryAllIndividualsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  household_Id?: Maybe<Scalars['UUID']>,
  programme?: Maybe<Scalars['String']>,
  businessArea?: Maybe<Scalars['String']>,
  fullName?: Maybe<Scalars['String']>,
  fullName_Icontains?: Maybe<Scalars['String']>,
  sex?: Maybe<Array<Maybe<Scalars['String']>>>,
  age?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>,
  lastRegistrationDate?: Maybe<Scalars['String']>,
  admin2?: Maybe<Array<Maybe<Scalars['ID']>>>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryAllUsersArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  search?: Maybe<Scalars['String']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  partner?: Maybe<Array<Maybe<Scalars['String']>>>,
  roles?: Maybe<Array<Maybe<Scalars['String']>>>,
  businessArea: Scalars['String'],
  orderBy?: Maybe<Scalars['String']>
};


export type QueryAllLogEntriesArgs = {
  objectId: Scalars['String'],
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryHasAvailableUsersToExportArgs = {
  businessAreaSlug: Scalars['String']
};


export type QueryImportedHouseholdArgs = {
  id: Scalars['ID']
};


export type QueryAllImportedHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  rdiId?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryRegistrationDataImportDatahubArgs = {
  id: Scalars['ID']
};


export type QueryAllRegistrationDataImportsDatahubArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryImportedIndividualArgs = {
  id: Scalars['ID']
};


export type QueryAllImportedIndividualsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  household?: Maybe<Scalars['ID']>,
  rdiId?: Maybe<Scalars['String']>,
  duplicatesOnly?: Maybe<Scalars['Boolean']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryImportDataArgs = {
  id: Scalars['ID']
};


export type QueryRegistrationDataImportArgs = {
  id: Scalars['ID']
};


export type QueryAllRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  importedBy_Id?: Maybe<Scalars['UUID']>,
  importDate?: Maybe<Scalars['Date']>,
  status?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  name_Icontains?: Maybe<Scalars['String']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};

export type RandomSamplingArguments = {
  confidenceInterval: Scalars['Float'],
  marginOfError: Scalars['Float'],
  excludedAdminAreas?: Maybe<Array<Maybe<Scalars['String']>>>,
  age?: Maybe<AgeInput>,
  sex?: Maybe<Scalars['String']>,
};

export type RapidProArguments = {
  flowId: Scalars['String'],
};

export type RapidProFlow = {
   __typename?: 'RapidProFlow',
  id?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  type?: Maybe<Scalars['String']>,
  archived?: Maybe<Scalars['Boolean']>,
  labels?: Maybe<Array<Maybe<Scalars['String']>>>,
  expires?: Maybe<Scalars['Int']>,
  runs?: Maybe<Array<Maybe<RapidProFlowRun>>>,
  results?: Maybe<Array<Maybe<RapidProFlowResult>>>,
  createdOn?: Maybe<Scalars['DateTime']>,
  modifiedOn?: Maybe<Scalars['DateTime']>,
};

export type RapidProFlowResult = {
   __typename?: 'RapidProFlowResult',
  key?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  categories?: Maybe<Array<Maybe<Scalars['String']>>>,
  nodeUuids?: Maybe<Array<Maybe<Scalars['String']>>>,
};

export type RapidProFlowRun = {
   __typename?: 'RapidProFlowRun',
  active?: Maybe<Scalars['Int']>,
  completed?: Maybe<Scalars['Int']>,
  interrupted?: Maybe<Scalars['Int']>,
  expired?: Maybe<Scalars['Int']>,
};

export enum RegistrationDataImportDatahubImportDone {
  NotStarted = 'NOT_STARTED',
  Started = 'STARTED',
  Done = 'DONE'
}

export type RegistrationDataImportDatahubNode = Node & {
   __typename?: 'RegistrationDataImportDatahubNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  importDate: Scalars['DateTime'],
  hctId?: Maybe<Scalars['UUID']>,
  importData?: Maybe<ImportDataNode>,
  importDone: RegistrationDataImportDatahubImportDone,
  businessAreaSlug: Scalars['String'],
  households: ImportedHouseholdNodeConnection,
  individuals: ImportedIndividualNodeConnection,
};


export type RegistrationDataImportDatahubNodeHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type RegistrationDataImportDatahubNodeIndividualsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type RegistrationDataImportDatahubNodeConnection = {
   __typename?: 'RegistrationDataImportDatahubNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<RegistrationDataImportDatahubNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type RegistrationDataImportDatahubNodeEdge = {
   __typename?: 'RegistrationDataImportDatahubNodeEdge',
  node?: Maybe<RegistrationDataImportDatahubNode>,
  cursor: Scalars['String'],
};

export enum RegistrationDataImportDataSource {
  Xls = 'XLS',
  Kobo = 'KOBO'
}

export type RegistrationDataImportNode = Node & {
   __typename?: 'RegistrationDataImportNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  status: RegistrationDataImportStatus,
  importDate: Scalars['DateTime'],
  importedBy: UserNode,
  dataSource: RegistrationDataImportDataSource,
  numberOfIndividuals: Scalars['Int'],
  numberOfHouseholds: Scalars['Int'],
  datahubId?: Maybe<Scalars['UUID']>,
  errorMessage: Scalars['String'],
  businessArea?: Maybe<UserBusinessAreaNode>,
  households: HouseholdNodeConnection,
  individuals: IndividualNodeConnection,
  batchDuplicatesCountAndPercentage?: Maybe<CountAndPercentageNode>,
  goldenRecordDuplicatesCountAndPercentage?: Maybe<CountAndPercentageNode>,
  batchPossibleDuplicatesCountAndPercentage?: Maybe<CountAndPercentageNode>,
  goldenRecordPossibleDuplicatesCountAndPercentage?: Maybe<CountAndPercentageNode>,
  batchUniqueCountAndPercentage?: Maybe<CountAndPercentageNode>,
  goldenRecordUniqueCountAndPercentage?: Maybe<CountAndPercentageNode>,
};


export type RegistrationDataImportNodeHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type RegistrationDataImportNodeIndividualsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type RegistrationDataImportNodeConnection = {
   __typename?: 'RegistrationDataImportNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<RegistrationDataImportNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type RegistrationDataImportNodeEdge = {
   __typename?: 'RegistrationDataImportNodeEdge',
  node?: Maybe<RegistrationDataImportNode>,
  cursor: Scalars['String'],
};

export enum RegistrationDataImportStatus {
  InReview = 'IN_REVIEW',
  Merged = 'MERGED',
  Merging = 'MERGING',
  Importing = 'IMPORTING',
  DeduplicationFailed = 'DEDUPLICATION_FAILED',
  Deduplication = 'DEDUPLICATION'
}

export type RegistrationDeduplicationMutation = {
   __typename?: 'RegistrationDeduplicationMutation',
  ok?: Maybe<Scalars['Boolean']>,
};

export type RegistrationKoboImportMutation = {
   __typename?: 'RegistrationKoboImportMutation',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type RegistrationKoboImportMutationInput = {
  importDataId?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  businessAreaSlug?: Maybe<Scalars['String']>,
};

export type RegistrationXlsxImportMutation = {
   __typename?: 'RegistrationXlsxImportMutation',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type RegistrationXlsxImportMutationInput = {
  importDataId?: Maybe<Scalars['ID']>,
  name?: Maybe<Scalars['String']>,
  businessAreaSlug?: Maybe<Scalars['String']>,
};

export type RoleNode = {
   __typename?: 'RoleNode',
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  permissions: Array<Maybe<Scalars['String']>>,
  userRoles: Array<UserRoleNode>,
};

export enum RuleLanguage {
  Jinja2 = 'JINJA2',
  Internal = 'INTERNAL',
  Python = 'PYTHON'
}

export type SaveKoboProjectImportDataMutation = {
   __typename?: 'SaveKoboProjectImportDataMutation',
  importData?: Maybe<ImportDataNode>,
  errors?: Maybe<Array<Maybe<KoboErrorNode>>>,
};

export type SensitiveGrievanceTicketExtras = {
  household?: Maybe<Scalars['ID']>,
  individual?: Maybe<Scalars['ID']>,
  paymentRecord?: Maybe<Scalars['ID']>,
};

export type ServiceProviderNode = Node & {
   __typename?: 'ServiceProviderNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  businessArea: UserBusinessAreaNode,
  caId: Scalars['String'],
  fullName: Scalars['String'],
  shortName: Scalars['String'],
  country: Scalars['String'],
  visionId: Scalars['String'],
  paymentRecords: PaymentRecordNodeConnection,
};


export type ServiceProviderNodePaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
};

export type ServiceProviderNodeConnection = {
   __typename?: 'ServiceProviderNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<ServiceProviderNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type ServiceProviderNodeEdge = {
   __typename?: 'ServiceProviderNodeEdge',
  node?: Maybe<ServiceProviderNode>,
  cursor: Scalars['String'],
};

export type SetSteficonRuleOnTargetPopulationMutationInput = {
  targetId: Scalars['ID'],
  steficonRuleId?: Maybe<Scalars['ID']>,
  clientMutationId?: Maybe<Scalars['String']>,
};

export type SetSteficonRuleOnTargetPopulationMutationPayload = {
   __typename?: 'SetSteficonRuleOnTargetPopulationMutationPayload',
  targetPopulation?: Maybe<TargetPopulationNode>,
  clientMutationId?: Maybe<Scalars['String']>,
};

export type StatsObjectType = {
   __typename?: 'StatsObjectType',
  childMale?: Maybe<Scalars['Int']>,
  childFemale?: Maybe<Scalars['Int']>,
  adultMale?: Maybe<Scalars['Int']>,
  adultFemale?: Maybe<Scalars['Int']>,
};

export type SteficonRuleNode = Node & {
   __typename?: 'SteficonRuleNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  definition: Scalars['String'],
  enabled: Scalars['Boolean'],
  deprecated: Scalars['Boolean'],
  language: RuleLanguage,
  targetPopulations: TargetPopulationNodeConnection,
};


export type SteficonRuleNodeTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};

export type SteficonRuleNodeConnection = {
   __typename?: 'SteficonRuleNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<SteficonRuleNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type SteficonRuleNodeEdge = {
   __typename?: 'SteficonRuleNodeEdge',
  node?: Maybe<SteficonRuleNode>,
  cursor: Scalars['String'],
};

export type TargetingCriteriaNode = {
   __typename?: 'TargetingCriteriaNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  targetPopulationCandidate?: Maybe<TargetPopulationNode>,
  targetPopulationFinal?: Maybe<TargetPopulationNode>,
  rules?: Maybe<Array<Maybe<TargetingCriteriaRuleNode>>>,
};

export type TargetingCriteriaObjectType = {
  rules?: Maybe<Array<Maybe<TargetingCriteriaRuleObjectType>>>,
};

export enum TargetingCriteriaRuleFilterComparisionMethod {
  Equals = 'EQUALS',
  NotEquals = 'NOT_EQUALS',
  Contains = 'CONTAINS',
  NotContains = 'NOT_CONTAINS',
  Range = 'RANGE',
  NotInRange = 'NOT_IN_RANGE',
  GreaterThan = 'GREATER_THAN',
  LessThan = 'LESS_THAN'
}

export type TargetingCriteriaRuleFilterNode = {
   __typename?: 'TargetingCriteriaRuleFilterNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  comparisionMethod: TargetingCriteriaRuleFilterComparisionMethod,
  targetingCriteriaRule: TargetingCriteriaRuleNode,
  isFlexField: Scalars['Boolean'],
  fieldName: Scalars['String'],
  arguments?: Maybe<Array<Maybe<Scalars['Arg']>>>,
  fieldAttribute?: Maybe<FieldAttributeNode>,
};

export type TargetingCriteriaRuleFilterObjectType = {
  comparisionMethod: Scalars['String'],
  isFlexField: Scalars['Boolean'],
  fieldName: Scalars['String'],
  arguments: Array<Maybe<Scalars['Arg']>>,
  headOfHousehold?: Maybe<Scalars['Boolean']>,
};

export type TargetingCriteriaRuleNode = {
   __typename?: 'TargetingCriteriaRuleNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  targetingCriteria: TargetingCriteriaNode,
  individualsFiltersBlocks?: Maybe<Array<Maybe<TargetingIndividualRuleFilterBlockNode>>>,
  filters?: Maybe<Array<Maybe<TargetingCriteriaRuleFilterNode>>>,
};

export type TargetingCriteriaRuleObjectType = {
  filters?: Maybe<Array<Maybe<TargetingCriteriaRuleFilterObjectType>>>,
  individualsFiltersBlocks?: Maybe<Array<Maybe<TargetingIndividualRuleFilterBlockObjectType>>>,
};

export enum TargetingIndividualBlockRuleFilterComparisionMethod {
  Equals = 'EQUALS',
  NotEquals = 'NOT_EQUALS',
  Contains = 'CONTAINS',
  NotContains = 'NOT_CONTAINS',
  Range = 'RANGE',
  NotInRange = 'NOT_IN_RANGE',
  GreaterThan = 'GREATER_THAN',
  LessThan = 'LESS_THAN'
}

export type TargetingIndividualBlockRuleFilterNode = {
   __typename?: 'TargetingIndividualBlockRuleFilterNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  comparisionMethod: TargetingIndividualBlockRuleFilterComparisionMethod,
  individualsFiltersBlock: TargetingIndividualRuleFilterBlockNode,
  isFlexField: Scalars['Boolean'],
  fieldName: Scalars['String'],
  arguments?: Maybe<Array<Maybe<Scalars['Arg']>>>,
  fieldAttribute?: Maybe<FieldAttributeNode>,
};

export type TargetingIndividualRuleFilterBlockNode = {
   __typename?: 'TargetingIndividualRuleFilterBlockNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  targetingCriteriaRule: TargetingCriteriaRuleNode,
  individualBlockFilters?: Maybe<Array<Maybe<TargetingIndividualBlockRuleFilterNode>>>,
};

export type TargetingIndividualRuleFilterBlockObjectType = {
  individualBlockFilters?: Maybe<Array<Maybe<TargetingCriteriaRuleFilterObjectType>>>,
};

export type TargetPopulationNode = Node & {
   __typename?: 'TargetPopulationNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  isRemoved: Scalars['Boolean'],
  name: Scalars['String'],
  caId?: Maybe<Scalars['String']>,
  caHashId?: Maybe<Scalars['String']>,
  createdBy?: Maybe<UserNode>,
  approvedAt?: Maybe<Scalars['DateTime']>,
  approvedBy?: Maybe<UserNode>,
  finalizedAt?: Maybe<Scalars['DateTime']>,
  finalizedBy?: Maybe<UserNode>,
  businessArea?: Maybe<UserBusinessAreaNode>,
  status: TargetPopulationStatus,
  households: HouseholdNodeConnection,
  candidateListTotalHouseholds?: Maybe<Scalars['Int']>,
  candidateListTotalIndividuals?: Maybe<Scalars['Int']>,
  finalListTotalHouseholds?: Maybe<Scalars['Int']>,
  finalListTotalIndividuals?: Maybe<Scalars['Int']>,
  selectionComputationMetadata?: Maybe<Scalars['String']>,
  program?: Maybe<ProgramNode>,
  candidateListTargetingCriteria?: Maybe<TargetingCriteriaNode>,
  finalListTargetingCriteria?: Maybe<TargetingCriteriaNode>,
  sentToDatahub: Scalars['Boolean'],
  steficonRule?: Maybe<SteficonRuleNode>,
  vulnerabilityScoreMin?: Maybe<Scalars['Float']>,
  vulnerabilityScoreMax?: Maybe<Scalars['Float']>,
  paymentRecords: PaymentRecordNodeConnection,
  selections: Array<HouseholdSelection>,
  totalHouseholds?: Maybe<Scalars['Int']>,
  totalFamilySize?: Maybe<Scalars['Int']>,
  finalList?: Maybe<HouseholdNodeConnection>,
  candidateStats?: Maybe<StatsObjectType>,
  finalStats?: Maybe<StatsObjectType>,
};


export type TargetPopulationNodeHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type TargetPopulationNodePaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
};


export type TargetPopulationNodeFinalListArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type TargetPopulationNodeConnection = {
   __typename?: 'TargetPopulationNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TargetPopulationNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TargetPopulationNodeEdge = {
   __typename?: 'TargetPopulationNodeEdge',
  node?: Maybe<TargetPopulationNode>,
  cursor: Scalars['String'],
};

export enum TargetPopulationStatus {
  Draft = 'DRAFT',
  Approved = 'APPROVED',
  Finalized = 'FINALIZED'
}

export type TicketAddIndividualDetailsNode = Node & {
   __typename?: 'TicketAddIndividualDetailsNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  household?: Maybe<HouseholdNode>,
  individualData?: Maybe<Scalars['Arg']>,
};

export type TicketAddIndividualDetailsNodeConnection = {
   __typename?: 'TicketAddIndividualDetailsNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketAddIndividualDetailsNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketAddIndividualDetailsNodeEdge = {
   __typename?: 'TicketAddIndividualDetailsNodeEdge',
  node?: Maybe<TicketAddIndividualDetailsNode>,
  cursor: Scalars['String'],
};

export type TicketComplaintDetailsNode = Node & {
   __typename?: 'TicketComplaintDetailsNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  paymentRecord?: Maybe<PaymentRecordNode>,
  household?: Maybe<HouseholdNode>,
  individual?: Maybe<IndividualNode>,
};

export type TicketComplaintDetailsNodeConnection = {
   __typename?: 'TicketComplaintDetailsNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketComplaintDetailsNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketComplaintDetailsNodeEdge = {
   __typename?: 'TicketComplaintDetailsNodeEdge',
  node?: Maybe<TicketComplaintDetailsNode>,
  cursor: Scalars['String'],
};

export type TicketDeleteIndividualDetailsNode = Node & {
   __typename?: 'TicketDeleteIndividualDetailsNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  individual?: Maybe<IndividualNode>,
  individualData?: Maybe<Scalars['Arg']>,
};

export type TicketDeleteIndividualDetailsNodeConnection = {
   __typename?: 'TicketDeleteIndividualDetailsNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketDeleteIndividualDetailsNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketDeleteIndividualDetailsNodeEdge = {
   __typename?: 'TicketDeleteIndividualDetailsNodeEdge',
  node?: Maybe<TicketDeleteIndividualDetailsNode>,
  cursor: Scalars['String'],
};

export type TicketHouseholdDataUpdateDetailsNode = Node & {
   __typename?: 'TicketHouseholdDataUpdateDetailsNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  household?: Maybe<HouseholdNode>,
  householdData?: Maybe<Scalars['Arg']>,
};

export type TicketHouseholdDataUpdateDetailsNodeConnection = {
   __typename?: 'TicketHouseholdDataUpdateDetailsNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketHouseholdDataUpdateDetailsNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketHouseholdDataUpdateDetailsNodeEdge = {
   __typename?: 'TicketHouseholdDataUpdateDetailsNodeEdge',
  node?: Maybe<TicketHouseholdDataUpdateDetailsNode>,
  cursor: Scalars['String'],
};

export type TicketIndividualDataUpdateDetailsNode = Node & {
   __typename?: 'TicketIndividualDataUpdateDetailsNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  individual?: Maybe<IndividualNode>,
  individualData?: Maybe<Scalars['Arg']>,
};

export type TicketIndividualDataUpdateDetailsNodeConnection = {
   __typename?: 'TicketIndividualDataUpdateDetailsNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketIndividualDataUpdateDetailsNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketIndividualDataUpdateDetailsNodeEdge = {
   __typename?: 'TicketIndividualDataUpdateDetailsNodeEdge',
  node?: Maybe<TicketIndividualDataUpdateDetailsNode>,
  cursor: Scalars['String'],
};

export type TicketNoteNode = Node & {
   __typename?: 'TicketNoteNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  description?: Maybe<Scalars['String']>,
  createdBy?: Maybe<UserNode>,
};

export type TicketNoteNodeConnection = {
   __typename?: 'TicketNoteNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketNoteNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketNoteNodeEdge = {
   __typename?: 'TicketNoteNodeEdge',
  node?: Maybe<TicketNoteNode>,
  cursor: Scalars['String'],
};

export type TicketSensitiveDetailsNode = Node & {
   __typename?: 'TicketSensitiveDetailsNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  paymentRecord?: Maybe<PaymentRecordNode>,
  household?: Maybe<HouseholdNode>,
  individual?: Maybe<IndividualNode>,
};

export type TicketSensitiveDetailsNodeConnection = {
   __typename?: 'TicketSensitiveDetailsNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<TicketSensitiveDetailsNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type TicketSensitiveDetailsNodeEdge = {
   __typename?: 'TicketSensitiveDetailsNodeEdge',
  node?: Maybe<TicketSensitiveDetailsNode>,
  cursor: Scalars['String'],
};

export type UnapproveTargetPopulationMutation = {
   __typename?: 'UnapproveTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
};

export type UpdatePaymentVerificationReceivedAndReceivedAmount = {
   __typename?: 'UpdatePaymentVerificationReceivedAndReceivedAmount',
  paymentVerification?: Maybe<PaymentVerificationNode>,
};

export type UpdatePaymentVerificationStatusAndReceivedAmount = {
   __typename?: 'UpdatePaymentVerificationStatusAndReceivedAmount',
  paymentVerification?: Maybe<PaymentVerificationNode>,
};

export type UpdateProgram = {
   __typename?: 'UpdateProgram',
  program?: Maybe<ProgramNode>,
};

export type UpdateProgramInput = {
  id: Scalars['String'],
  name?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['Date']>,
  endDate?: Maybe<Scalars['Date']>,
  description?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  scope?: Maybe<Scalars['String']>,
  cashPlus?: Maybe<Scalars['Boolean']>,
  populationGoal?: Maybe<Scalars['Int']>,
  administrativeAreasOfImplementation?: Maybe<Scalars['String']>,
  businessAreaSlug?: Maybe<Scalars['String']>,
  individualDataNeeded?: Maybe<Scalars['Boolean']>,
};

export type UpdateTargetPopulationInput = {
  id: Scalars['ID'],
  name?: Maybe<Scalars['String']>,
  targetingCriteria?: Maybe<TargetingCriteriaObjectType>,
  programId?: Maybe<Scalars['ID']>,
  vulnerabilityScoreMin?: Maybe<Scalars['Decimal']>,
  vulnerabilityScoreMax?: Maybe<Scalars['Decimal']>,
};

export type UpdateTargetPopulationMutation = {
   __typename?: 'UpdateTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
};


export type UploadImportDataXlsxFile = {
   __typename?: 'UploadImportDataXLSXFile',
  importData?: Maybe<ImportDataNode>,
  errors?: Maybe<Array<Maybe<XlsxRowErrorNode>>>,
};

export type UserBusinessAreaNode = Node & {
   __typename?: 'UserBusinessAreaNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  code: Scalars['String'],
  name: Scalars['String'],
  longName: Scalars['String'],
  regionCode: Scalars['String'],
  regionName: Scalars['String'],
  koboToken?: Maybe<Scalars['String']>,
  rapidProHost?: Maybe<Scalars['String']>,
  rapidProApiKey?: Maybe<Scalars['String']>,
  slug: Scalars['String'],
  hasDataSharingAgreement: Scalars['Boolean'],
  adminAreaTypes: AdminAreaTypeNodeConnection,
  userRoles: Array<UserRoleNode>,
  tickets: GrievanceTicketNodeConnection,
  householdSet: HouseholdNodeConnection,
  paymentrecordSet: PaymentRecordNodeConnection,
  serviceproviderSet: ServiceProviderNodeConnection,
  programSet: ProgramNodeConnection,
  cashplanSet: CashPlanNodeConnection,
  targetpopulationSet: TargetPopulationNodeConnection,
  registrationdataimportSet: RegistrationDataImportNodeConnection,
  permissions?: Maybe<Array<Maybe<Scalars['String']>>>,
};


export type UserBusinessAreaNodeAdminAreaTypesArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserBusinessAreaNodeTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserBusinessAreaNodeHouseholdSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserBusinessAreaNodePaymentrecordSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
};


export type UserBusinessAreaNodeServiceproviderSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserBusinessAreaNodeProgramSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
};


export type UserBusinessAreaNodeCashplanSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserBusinessAreaNodeTargetpopulationSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserBusinessAreaNodeRegistrationdataimportSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type UserBusinessAreaNodeConnection = {
   __typename?: 'UserBusinessAreaNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<UserBusinessAreaNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type UserBusinessAreaNodeEdge = {
   __typename?: 'UserBusinessAreaNodeEdge',
  node?: Maybe<UserBusinessAreaNode>,
  cursor: Scalars['String'],
};

export type UserNode = Node & {
   __typename?: 'UserNode',
  id: Scalars['ID'],
  lastLogin?: Maybe<Scalars['DateTime']>,
  isSuperuser: Scalars['Boolean'],
  username: Scalars['String'],
  firstName: Scalars['String'],
  lastName: Scalars['String'],
  email: Scalars['String'],
  isStaff: Scalars['Boolean'],
  isActive: Scalars['Boolean'],
  dateJoined: Scalars['DateTime'],
  status: UserStatus,
  partner: UserPartner,
  availableForExport: Scalars['Boolean'],
  userRoles: Array<UserRoleNode>,
  createdTickets: GrievanceTicketNodeConnection,
  assignedTickets: GrievanceTicketNodeConnection,
  ticketNotes: TicketNoteNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
  approvedTargetPopulations: TargetPopulationNodeConnection,
  finalizedTargetPopulations: TargetPopulationNodeConnection,
  registrationDataImports: RegistrationDataImportNodeConnection,
  businessAreas?: Maybe<UserBusinessAreaNodeConnection>,
};


export type UserNodeCreatedTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserNodeAssignedTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserNodeTicketNotesArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserNodeTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserNodeApprovedTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserNodeFinalizedTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserNodeRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserNodeBusinessAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>
};

export type UserNodeConnection = {
   __typename?: 'UserNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<UserNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type UserNodeEdge = {
   __typename?: 'UserNodeEdge',
  node?: Maybe<UserNode>,
  cursor: Scalars['String'],
};

export type UserObjectType = {
   __typename?: 'UserObjectType',
  id: Scalars['UUID'],
  lastLogin?: Maybe<Scalars['DateTime']>,
  isSuperuser: Scalars['Boolean'],
  username: Scalars['String'],
  firstName: Scalars['String'],
  lastName: Scalars['String'],
  email: Scalars['String'],
  isStaff: Scalars['Boolean'],
  isActive: Scalars['Boolean'],
  dateJoined: Scalars['DateTime'],
  status: UserStatus,
  partner: UserPartner,
  availableForExport: Scalars['Boolean'],
  userRoles: Array<UserRoleNode>,
  createdTickets: GrievanceTicketNodeConnection,
  assignedTickets: GrievanceTicketNodeConnection,
  ticketNotes: TicketNoteNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
  approvedTargetPopulations: TargetPopulationNodeConnection,
  finalizedTargetPopulations: TargetPopulationNodeConnection,
  registrationDataImports: RegistrationDataImportNodeConnection,
  businessAreas?: Maybe<UserBusinessAreaNodeConnection>,
};


export type UserObjectTypeCreatedTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserObjectTypeAssignedTicketsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserObjectTypeTicketNotesArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserObjectTypeTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserObjectTypeApprovedTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserObjectTypeFinalizedTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>,
  createdByName?: Maybe<Scalars['String']>,
  createdAt?: Maybe<Scalars['DateTime']>,
  updatedAt?: Maybe<Scalars['DateTime']>,
  status?: Maybe<Scalars['String']>,
  households?: Maybe<Array<Maybe<Scalars['ID']>>>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  candidateListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  finalListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMin?: Maybe<Scalars['Int']>,
  finalListTotalIndividualsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type UserObjectTypeRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserObjectTypeBusinessAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>
};

export enum UserPartner {
  Unhcr = 'UNHCR',
  Wfp = 'WFP',
  Unicef = 'UNICEF'
}

export type UserRoleNode = {
   __typename?: 'UserRoleNode',
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  businessArea: UserBusinessAreaNode,
  role: RoleNode,
};

export enum UserStatus {
  Invited = 'INVITED',
  Active = 'ACTIVE',
  Inactive = 'INACTIVE'
}


export type XlsxErrorNode = {
   __typename?: 'XlsxErrorNode',
  sheet?: Maybe<Scalars['String']>,
  coordinates?: Maybe<Scalars['String']>,
  message?: Maybe<Scalars['String']>,
};

export type XlsxRowErrorNode = {
   __typename?: 'XlsxRowErrorNode',
  rowNumber?: Maybe<Scalars['Int']>,
  header?: Maybe<Scalars['String']>,
  message?: Maybe<Scalars['String']>,
};

export type HouseholdMinimalFragment = (
  { __typename?: 'HouseholdNode' }
  & Pick<HouseholdNode, 'id' | 'createdAt' | 'residenceStatus' | 'size' | 'totalCashReceived' | 'firstRegistrationDate' | 'lastRegistrationDate' | 'status' | 'sanctionListPossibleMatch' | 'hasDuplicates' | 'unicefId' | 'geopoint' | 'village' | 'address'>
  & { adminArea: Maybe<(
    { __typename?: 'AdminAreaNode' }
    & Pick<AdminAreaNode, 'id' | 'title'>
    & { adminAreaType: (
      { __typename?: 'AdminAreaTypeNode' }
      & Pick<AdminAreaTypeNode, 'adminLevel'>
    ) }
  )>, headOfHousehold: (
    { __typename?: 'IndividualNode' }
    & Pick<IndividualNode, 'id' | 'fullName'>
  ), individuals: (
    { __typename?: 'IndividualNodeConnection' }
    & Pick<IndividualNodeConnection, 'totalCount'>
  ), programs: (
    { __typename?: 'ProgramNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'ProgramNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'ProgramNode' }
        & Pick<ProgramNode, 'id' | 'name'>
      )> }
    )>> }
  ) }
);

export type HouseholdDetailedFragment = (
  { __typename?: 'HouseholdNode' }
  & Pick<HouseholdNode, 'countryOrigin' | 'country' | 'flexFields'>
  & { individuals: (
    { __typename?: 'IndividualNodeConnection' }
    & Pick<IndividualNodeConnection, 'totalCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'IndividualNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'IndividualNode' }
        & Pick<IndividualNode, 'birthDate' | 'relationship'>
        & IndividualMinimalFragment
      )> }
    )>> }
  ), programs: (
    { __typename?: 'ProgramNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'ProgramNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'ProgramNode' }
        & Pick<ProgramNode, 'id' | 'name'>
      )> }
    )>> }
  ), registrationDataImport: (
    { __typename?: 'RegistrationDataImportNode' }
    & Pick<RegistrationDataImportNode, 'name' | 'dataSource' | 'importDate'>
    & { importedBy: (
      { __typename?: 'UserNode' }
      & Pick<UserNode, 'firstName' | 'lastName' | 'email' | 'username'>
    ) }
  ), paymentRecords: (
    { __typename?: 'PaymentRecordNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'PaymentRecordNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'PaymentRecordNode' }
        & Pick<PaymentRecordNode, 'id' | 'fullName'>
        & { cashPlan: Maybe<(
          { __typename?: 'CashPlanNode' }
          & Pick<CashPlanNode, 'id' | 'totalPersonsCovered' | 'totalDeliveredQuantity' | 'assistanceMeasurement'>
          & { program: (
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
          ) }
        )> }
      )> }
    )>> }
  ) }
  & HouseholdMinimalFragment
);

export type IndividualMinimalFragment = (
  { __typename?: 'IndividualNode' }
  & Pick<IndividualNode, 'id' | 'lastRegistrationDate' | 'createdAt' | 'updatedAt' | 'fullName' | 'sex' | 'unicefId' | 'birthDate' | 'maritalStatus' | 'phoneNo' | 'sanctionListPossibleMatch' | 'deduplicationGoldenRecordStatus' | 'sanctionListLastCheck' | 'role' | 'relationship' | 'status'>
  & { documents: (
    { __typename?: 'DocumentNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'DocumentNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'DocumentNode' }
        & Pick<DocumentNode, 'id' | 'documentNumber'>
        & { type: (
          { __typename?: 'DocumentTypeNode' }
          & Pick<DocumentTypeNode, 'country' | 'label'>
        ) }
      )> }
    )>> }
  ), household: Maybe<(
    { __typename?: 'HouseholdNode' }
    & Pick<HouseholdNode, 'id' | 'unicefId' | 'status'>
    & { adminArea: Maybe<(
      { __typename?: 'AdminAreaNode' }
      & Pick<AdminAreaNode, 'id' | 'title'>
      & { adminAreaType: (
        { __typename?: 'AdminAreaTypeNode' }
        & Pick<AdminAreaTypeNode, 'adminLevel'>
      ) }
    )>, programs: (
      { __typename?: 'ProgramNodeConnection' }
      & { edges: Array<Maybe<(
        { __typename?: 'ProgramNodeEdge' }
        & { node: Maybe<(
          { __typename?: 'ProgramNode' }
          & Pick<ProgramNode, 'id' | 'name'>
        )> }
      )>> }
    ) }
  )> }
);

export type IndividualDetailedFragment = (
  { __typename?: 'IndividualNode' }
  & Pick<IndividualNode, 'givenName' | 'familyName' | 'estimatedBirthDate' | 'pregnant' | 'status' | 'enrolledInNutritionProgramme' | 'administrationOfRutf' | 'role' | 'relationship' | 'flexFields'>
  & { documents: (
    { __typename?: 'DocumentNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'DocumentNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'DocumentNode' }
        & Pick<DocumentNode, 'documentNumber'>
        & { type: (
          { __typename?: 'DocumentTypeNode' }
          & Pick<DocumentTypeNode, 'label'>
        ) }
      )> }
    )>> }
  ), identities: Array<(
    { __typename?: 'IndividualIdentityNode' }
    & Pick<IndividualIdentityNode, 'number' | 'type'>
  )>, household: Maybe<(
    { __typename?: 'HouseholdNode' }
    & Pick<HouseholdNode, 'status' | 'id' | 'address' | 'countryOrigin'>
    & { adminArea: Maybe<(
      { __typename?: 'AdminAreaNode' }
      & Pick<AdminAreaNode, 'id' | 'title' | 'level'>
    )> }
  )>, headingHousehold: Maybe<(
    { __typename?: 'HouseholdNode' }
    & Pick<HouseholdNode, 'id'>
    & { headOfHousehold: (
      { __typename?: 'IndividualNode' }
      & Pick<IndividualNode, 'id'>
    ) }
  )> }
  & IndividualMinimalFragment
);

export type TargetPopulationMinimalFragment = (
  { __typename?: 'TargetPopulationNode' }
  & Pick<TargetPopulationNode, 'id' | 'name' | 'status' | 'createdAt' | 'updatedAt' | 'candidateListTotalHouseholds' | 'finalListTotalHouseholds'>
  & { createdBy: Maybe<(
    { __typename?: 'UserNode' }
    & Pick<UserNode, 'firstName' | 'lastName'>
  )> }
);

export type TargetPopulationDetailedFragment = (
  { __typename?: 'TargetPopulationNode' }
  & Pick<TargetPopulationNode, 'id' | 'name' | 'status' | 'candidateListTotalHouseholds' | 'candidateListTotalIndividuals' | 'finalListTotalHouseholds' | 'finalListTotalIndividuals' | 'vulnerabilityScoreMin' | 'vulnerabilityScoreMax' | 'approvedAt' | 'finalizedAt'>
  & { steficonRule: Maybe<(
    { __typename?: 'SteficonRuleNode' }
    & Pick<SteficonRuleNode, 'id' | 'name'>
  )>, finalizedBy: Maybe<(
    { __typename?: 'UserNode' }
    & Pick<UserNode, 'firstName' | 'lastName'>
  )>, program: Maybe<(
    { __typename?: 'ProgramNode' }
    & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'caId' | 'description' | 'budget' | 'frequencyOfPayments' | 'populationGoal' | 'sector' | 'totalNumberOfHouseholds' | 'individualDataNeeded'>
  )>, createdBy: Maybe<(
    { __typename?: 'UserNode' }
    & Pick<UserNode, 'firstName' | 'lastName'>
  )>, candidateListTargetingCriteria: Maybe<(
    { __typename?: 'TargetingCriteriaNode' }
    & { targetPopulationCandidate: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & { createdBy: Maybe<(
        { __typename?: 'UserNode' }
        & Pick<UserNode, 'firstName' | 'lastName'>
      )> }
    )>, rules: Maybe<Array<Maybe<(
      { __typename?: 'TargetingCriteriaRuleNode' }
      & Pick<TargetingCriteriaRuleNode, 'id'>
      & { individualsFiltersBlocks: Maybe<Array<Maybe<(
        { __typename?: 'TargetingIndividualRuleFilterBlockNode' }
        & { individualBlockFilters: Maybe<Array<Maybe<(
          { __typename?: 'TargetingIndividualBlockRuleFilterNode' }
          & Pick<TargetingIndividualBlockRuleFilterNode, 'fieldName' | 'isFlexField' | 'arguments' | 'comparisionMethod'>
          & { fieldAttribute: Maybe<(
            { __typename?: 'FieldAttributeNode' }
            & Pick<FieldAttributeNode, 'name' | 'labelEn' | 'type'>
            & { choices: Maybe<Array<Maybe<(
              { __typename?: 'CoreFieldChoiceObject' }
              & Pick<CoreFieldChoiceObject, 'value' | 'labelEn'>
            )>>> }
          )> }
        )>>> }
      )>>>, filters: Maybe<Array<Maybe<(
        { __typename?: 'TargetingCriteriaRuleFilterNode' }
        & Pick<TargetingCriteriaRuleFilterNode, 'fieldName' | 'isFlexField' | 'arguments' | 'comparisionMethod'>
        & { fieldAttribute: Maybe<(
          { __typename?: 'FieldAttributeNode' }
          & Pick<FieldAttributeNode, 'name' | 'labelEn' | 'type'>
          & { choices: Maybe<Array<Maybe<(
            { __typename?: 'CoreFieldChoiceObject' }
            & Pick<CoreFieldChoiceObject, 'value' | 'labelEn'>
          )>>> }
        )> }
      )>>> }
    )>>> }
  )>, finalListTargetingCriteria: Maybe<(
    { __typename?: 'TargetingCriteriaNode' }
    & { targetPopulationFinal: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & { createdBy: Maybe<(
        { __typename?: 'UserNode' }
        & Pick<UserNode, 'firstName' | 'lastName'>
      )> }
    )>, rules: Maybe<Array<Maybe<(
      { __typename?: 'TargetingCriteriaRuleNode' }
      & Pick<TargetingCriteriaRuleNode, 'id'>
      & { filters: Maybe<Array<Maybe<(
        { __typename?: 'TargetingCriteriaRuleFilterNode' }
        & Pick<TargetingCriteriaRuleFilterNode, 'fieldName' | 'isFlexField' | 'arguments' | 'comparisionMethod'>
        & { fieldAttribute: Maybe<(
          { __typename?: 'FieldAttributeNode' }
          & Pick<FieldAttributeNode, 'name' | 'labelEn' | 'type'>
          & { choices: Maybe<Array<Maybe<(
            { __typename?: 'CoreFieldChoiceObject' }
            & Pick<CoreFieldChoiceObject, 'value' | 'labelEn'>
          )>>> }
        )> }
      )>>> }
    )>>> }
  )>, candidateStats: Maybe<(
    { __typename?: 'StatsObjectType' }
    & Pick<StatsObjectType, 'childMale' | 'childFemale' | 'adultMale' | 'adultFemale'>
  )>, finalStats: Maybe<(
    { __typename?: 'StatsObjectType' }
    & Pick<StatsObjectType, 'childMale' | 'childFemale' | 'adultMale' | 'adultFemale'>
  )> }
);

export type ActivateCashPlanPaymentVerificationMutationVariables = {
  cashPlanVerificationId: Scalars['ID']
};


export type ActivateCashPlanPaymentVerificationMutation = (
  { __typename?: 'Mutations' }
  & { activateCashPlanPaymentVerification: Maybe<(
    { __typename?: 'ActivateCashPlanVerificationMutation' }
    & { cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id' | 'status' | 'statusDate'>
    )> }
  )> }
);

export type ApproveTpMutationVariables = {
  id: Scalars['ID']
};


export type ApproveTpMutation = (
  { __typename?: 'Mutations' }
  & { approveTargetPopulation: Maybe<(
    { __typename?: 'ApproveTargetPopulationMutation' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & TargetPopulationDetailedFragment
    )> }
  )> }
);

export type CheckAgainstSanctionListUploadMutationVariables = {
  file: Scalars['Upload']
};


export type CheckAgainstSanctionListUploadMutation = (
  { __typename?: 'Mutations' }
  & { checkAgainstSanctionList: Maybe<(
    { __typename?: 'CheckAgainstSanctionListMutation' }
    & { errors: Maybe<Array<Maybe<(
      { __typename?: 'XlsxRowErrorNode' }
      & Pick<XlsxRowErrorNode, 'header' | 'message' | 'rowNumber'>
    )>>> }
  )> }
);

export type CreateCashPlanPaymentVerificationMutationVariables = {
  input: CreatePaymentVerificationInput
};


export type CreateCashPlanPaymentVerificationMutation = (
  { __typename?: 'Mutations' }
  & { createCashPlanPaymentVerification: Maybe<(
    { __typename?: 'CreatePaymentVerificationMutation' }
    & { cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id'>
    )> }
  )> }
);

export type CreateGrievanceMutationVariables = {
  input: CreateGrievanceTicketInput
};


export type CreateGrievanceMutation = (
  { __typename?: 'Mutations' }
  & { createGrievanceTicket: Maybe<(
    { __typename?: 'CreateGrievanceTicketMutation' }
    & { grievanceTickets: Maybe<Array<Maybe<(
      { __typename?: 'GrievanceTicketNode' }
      & Pick<GrievanceTicketNode, 'id'>
    )>>> }
  )> }
);

export type CreateProgramMutationVariables = {
  programData: CreateProgramInput
};


export type CreateProgramMutation = (
  { __typename?: 'Mutations' }
  & { createProgram: Maybe<(
    { __typename?: 'CreateProgram' }
    & { program: Maybe<(
      { __typename?: 'ProgramNode' }
      & Pick<ProgramNode, 'id' | 'name' | 'status' | 'startDate' | 'endDate' | 'caId' | 'budget' | 'description' | 'frequencyOfPayments' | 'sector' | 'scope' | 'cashPlus' | 'populationGoal' | 'individualDataNeeded'>
    )> }
  )> }
);

export type CreateTpMutationVariables = {
  input: CreateTargetPopulationInput
};


export type CreateTpMutation = (
  { __typename?: 'Mutations' }
  & { createTargetPopulation: Maybe<(
    { __typename?: 'CreateTargetPopulationMutation' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & Pick<TargetPopulationNode, 'id' | 'status' | 'candidateListTotalHouseholds' | 'candidateListTotalIndividuals' | 'finalListTotalHouseholds' | 'finalListTotalIndividuals'>
    )> }
  )> }
);

export type DeleteProgramMutationVariables = {
  programId: Scalars['String']
};


export type DeleteProgramMutation = (
  { __typename?: 'Mutations' }
  & { deleteProgram: Maybe<(
    { __typename?: 'DeleteProgram' }
    & Pick<DeleteProgram, 'ok'>
  )> }
);

export type DeleteTargetPopulationMutationVariables = {
  input: DeleteTargetPopulationMutationInput
};


export type DeleteTargetPopulationMutation = (
  { __typename?: 'Mutations' }
  & { deleteTargetPopulation: Maybe<(
    { __typename?: 'DeleteTargetPopulationMutationPayload' }
    & Pick<DeleteTargetPopulationMutationPayload, 'clientMutationId'>
  )> }
);

export type DiscardCashPlanPaymentVerificationMutationVariables = {
  cashPlanVerificationId: Scalars['ID']
};


export type DiscardCashPlanPaymentVerificationMutation = (
  { __typename?: 'Mutations' }
  & { discardCashPlanPaymentVerification: Maybe<(
    { __typename?: 'DiscardCashPlanVerificationMutation' }
    & { cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id' | 'status' | 'statusDate'>
    )> }
  )> }
);

export type CopyTargetPopulationMutationVariables = {
  input: CopyTargetPopulationMutationInput
};


export type CopyTargetPopulationMutation = (
  { __typename?: 'Mutations' }
  & { copyTargetPopulation: Maybe<(
    { __typename?: 'CopyTargetPopulationMutationPayload' }
    & Pick<CopyTargetPopulationMutationPayload, 'clientMutationId'>
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & Pick<TargetPopulationNode, 'id'>
    )> }
  )> }
);

export type EditCashPlanPaymentVerificationMutationVariables = {
  input: EditCashPlanPaymentVerificationInput
};


export type EditCashPlanPaymentVerificationMutation = (
  { __typename?: 'Mutations' }
  & { editCashPlanPaymentVerification: Maybe<(
    { __typename?: 'EditPaymentVerificationMutation' }
    & { cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id'>
    )> }
  )> }
);

export type FinalizeTpMutationVariables = {
  id: Scalars['ID']
};


export type FinalizeTpMutation = (
  { __typename?: 'Mutations' }
  & { finalizeTargetPopulation: Maybe<(
    { __typename?: 'FinalizeTargetPopulationMutation' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & TargetPopulationDetailedFragment
    )> }
  )> }
);

export type FinishCashPlanPaymentVerificationMutationVariables = {
  cashPlanVerificationId: Scalars['ID']
};


export type FinishCashPlanPaymentVerificationMutation = (
  { __typename?: 'Mutations' }
  & { finishCashPlanPaymentVerification: Maybe<(
    { __typename?: 'FinishCashPlanVerificationMutation' }
    & { cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id' | 'status' | 'statusDate'>
    )> }
  )> }
);

export type ImportXlsxCashPlanVerificationMutationVariables = {
  cashPlanVerificationId: Scalars['ID'],
  file: Scalars['Upload']
};


export type ImportXlsxCashPlanVerificationMutation = (
  { __typename?: 'Mutations' }
  & { importXlsxCashPlanVerification: Maybe<(
    { __typename?: 'ImportXlsxCashPlanVerification' }
    & { cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id'>
    )>, errors: Maybe<Array<Maybe<(
      { __typename?: 'XlsxErrorNode' }
      & Pick<XlsxErrorNode, 'sheet' | 'coordinates' | 'message'>
    )>>> }
  )> }
);

export type RerunDedupeMutationVariables = {
  registrationDataImportDatahubId: Scalars['ID']
};


export type RerunDedupeMutation = (
  { __typename?: 'Mutations' }
  & { rerunDedupe: Maybe<(
    { __typename?: 'RegistrationDeduplicationMutation' }
    & Pick<RegistrationDeduplicationMutation, 'ok'>
  )> }
);

export type SetSteficonRuleOnTargetPopulationMutationVariables = {
  input: SetSteficonRuleOnTargetPopulationMutationInput
};


export type SetSteficonRuleOnTargetPopulationMutation = (
  { __typename?: 'Mutations' }
  & { setSteficonRuleOnTargetPopulation: Maybe<(
    { __typename?: 'SetSteficonRuleOnTargetPopulationMutationPayload' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & TargetPopulationDetailedFragment
    )> }
  )> }
);

export type UnapproveTpMutationVariables = {
  id: Scalars['ID']
};


export type UnapproveTpMutation = (
  { __typename?: 'Mutations' }
  & { unapproveTargetPopulation: Maybe<(
    { __typename?: 'UnapproveTargetPopulationMutation' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & TargetPopulationDetailedFragment
    )> }
  )> }
);

export type UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables = {
  paymentVerificationId: Scalars['ID'],
  receivedAmount: Scalars['Decimal'],
  received: Scalars['Boolean']
};


export type UpdatePaymentVerificationReceivedAndReceivedAmountMutation = (
  { __typename?: 'Mutations' }
  & { updatePaymentVerificationReceivedAndReceivedAmount: Maybe<(
    { __typename?: 'UpdatePaymentVerificationReceivedAndReceivedAmount' }
    & { paymentVerification: Maybe<(
      { __typename?: 'PaymentVerificationNode' }
      & Pick<PaymentVerificationNode, 'id' | 'status' | 'receivedAmount'>
    )> }
  )> }
);

export type UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables = {
  paymentVerificationId: Scalars['ID'],
  receivedAmount: Scalars['Decimal'],
  status?: Maybe<PaymentVerificationStatusForUpdate>
};


export type UpdatePaymentVerificationStatusAndReceivedAmountMutation = (
  { __typename?: 'Mutations' }
  & { updatePaymentVerificationStatusAndReceivedAmount: Maybe<(
    { __typename?: 'UpdatePaymentVerificationStatusAndReceivedAmount' }
    & { paymentVerification: Maybe<(
      { __typename?: 'PaymentVerificationNode' }
      & Pick<PaymentVerificationNode, 'id' | 'status' | 'receivedAmount'>
    )> }
  )> }
);

export type UpdateProgramMutationVariables = {
  programData: UpdateProgramInput
};


export type UpdateProgramMutation = (
  { __typename?: 'Mutations' }
  & { updateProgram: Maybe<(
    { __typename?: 'UpdateProgram' }
    & { program: Maybe<(
      { __typename?: 'ProgramNode' }
      & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'caId' | 'description' | 'budget' | 'frequencyOfPayments' | 'cashPlus' | 'populationGoal' | 'scope' | 'sector' | 'totalNumberOfHouseholds' | 'administrativeAreasOfImplementation' | 'individualDataNeeded'>
    )> }
  )> }
);

export type UpdateTpMutationVariables = {
  input: UpdateTargetPopulationInput
};


export type UpdateTpMutation = (
  { __typename?: 'Mutations' }
  & { updateTargetPopulation: Maybe<(
    { __typename?: 'UpdateTargetPopulationMutation' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & TargetPopulationDetailedFragment
    )> }
  )> }
);

export type CashPlanVerificationStatusChoicesQueryVariables = {};


export type CashPlanVerificationStatusChoicesQuery = (
  { __typename?: 'Query' }
  & { cashPlanVerificationStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, paymentRecordDeliveryTypeChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type PaymentVerificationStatusChoicesQueryVariables = {};


export type PaymentVerificationStatusChoicesQuery = (
  { __typename?: 'Query' }
  & { paymentVerificationStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type CashPlanVerificationSamplingChoicesQueryVariables = {};


export type CashPlanVerificationSamplingChoicesQuery = (
  { __typename?: 'Query' }
  & { cashPlanVerificationSamplingChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type AllAdminAreasQueryVariables = {
  title?: Maybe<Scalars['String']>,
  businessArea?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>
};


export type AllAdminAreasQuery = (
  { __typename?: 'Query' }
  & { allAdminAreas: Maybe<(
    { __typename?: 'AdminAreaNodeConnection' }
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'endCursor' | 'startCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'AdminAreaNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'AdminAreaNode' }
        & Pick<AdminAreaNode, 'id' | 'title'>
      )> }
    )>> }
  )> }
);

export type AllBusinessAreasQueryVariables = {};


export type AllBusinessAreasQuery = (
  { __typename?: 'Query' }
  & { allBusinessAreas: Maybe<(
    { __typename?: 'BusinessAreaNodeConnection' }
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'endCursor' | 'startCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'BusinessAreaNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'BusinessAreaNode' }
        & Pick<BusinessAreaNode, 'id' | 'name' | 'slug'>
      )> }
    )>> }
  )> }
);

export type AllCashPlansQueryVariables = {
  program?: Maybe<Scalars['ID']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>,
  assistanceThrough?: Maybe<Scalars['String']>,
  deliveryType?: Maybe<Array<Maybe<Scalars['String']>>>,
  verificationStatus?: Maybe<Array<Maybe<Scalars['String']>>>,
  startDateGte?: Maybe<Scalars['DateTime']>,
  endDateLte?: Maybe<Scalars['DateTime']>
};


export type AllCashPlansQuery = (
  { __typename?: 'Query' }
  & { allCashPlans: Maybe<(
    { __typename?: 'CashPlanNodeConnection' }
    & Pick<CashPlanNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'CashPlanNodeEdge' }
      & Pick<CashPlanNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'CashPlanNode' }
        & Pick<CashPlanNode, 'id' | 'caId' | 'verificationStatus' | 'assistanceThrough' | 'deliveryType' | 'startDate' | 'endDate' | 'totalPersonsCovered' | 'dispersionDate' | 'assistanceMeasurement' | 'status' | 'totalEntitledQuantity' | 'totalDeliveredQuantity' | 'totalUndeliveredQuantity' | 'updatedAt'>
        & { program: (
          { __typename?: 'ProgramNode' }
          & Pick<ProgramNode, 'id' | 'name'>
        ) }
      )> }
    )>> }
  )> }
);

export type AllGrievanceTicketQueryVariables = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>,
  category?: Maybe<Scalars['String']>,
  businessArea: Scalars['String'],
  search?: Maybe<Scalars['String']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  fsp?: Maybe<Array<Maybe<Scalars['ID']>>>,
  createdAtRange?: Maybe<Scalars['String']>,
  admin?: Maybe<Array<Maybe<Scalars['ID']>>>,
  orderBy?: Maybe<Scalars['String']>
};


export type AllGrievanceTicketQuery = (
  { __typename?: 'Query' }
  & { allGrievanceTicket: Maybe<(
    { __typename?: 'GrievanceTicketNodeConnection' }
    & Pick<GrievanceTicketNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'GrievanceTicketNodeEdge' }
      & Pick<GrievanceTicketNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'GrievanceTicketNode' }
        & Pick<GrievanceTicketNode, 'id' | 'status' | 'category' | 'createdAt' | 'userModified'>
        & { assignedTo: Maybe<(
          { __typename?: 'UserNode' }
          & Pick<UserNode, 'id' | 'firstName' | 'lastName'>
        )> }
      )> }
    )>> }
  )> }
);

export type AllHouseholdsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>,
  familySize?: Maybe<Scalars['String']>,
  programs?: Maybe<Array<Maybe<Scalars['ID']>>>,
  headOfHouseholdFullNameIcontains?: Maybe<Scalars['String']>,
  adminArea?: Maybe<Scalars['ID']>,
  search?: Maybe<Scalars['String']>,
  residenceStatus?: Maybe<Scalars['String']>,
  lastRegistrationDate?: Maybe<Scalars['String']>,
  admin2?: Maybe<Array<Maybe<Scalars['ID']>>>
};


export type AllHouseholdsQuery = (
  { __typename?: 'Query' }
  & { allHouseholds: Maybe<(
    { __typename?: 'HouseholdNodeConnection' }
    & Pick<HouseholdNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'HouseholdNodeEdge' }
      & Pick<HouseholdNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'HouseholdNode' }
        & HouseholdMinimalFragment
      )> }
    )>> }
  )> }
);

export type AllIndividualsQueryVariables = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  fullNameContains?: Maybe<Scalars['String']>,
  sex?: Maybe<Array<Maybe<Scalars['String']>>>,
  age?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>,
  programme?: Maybe<Scalars['String']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  lastRegistrationDate?: Maybe<Scalars['String']>,
  householdId?: Maybe<Scalars['UUID']>
};


export type AllIndividualsQuery = (
  { __typename?: 'Query' }
  & { allIndividuals: Maybe<(
    { __typename?: 'IndividualNodeConnection' }
    & Pick<IndividualNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'IndividualNodeEdge' }
      & Pick<IndividualNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'IndividualNode' }
        & IndividualMinimalFragment
      )> }
    )>> }
  )> }
);

export type AllLogEntriesQueryVariables = {
  objectId: Scalars['String'],
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type AllLogEntriesQuery = (
  { __typename?: 'Query' }
  & { allLogEntries: Maybe<(
    { __typename?: 'LogEntryObjectConnection' }
    & Pick<LogEntryObjectConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'LogEntryObjectEdge' }
      & Pick<LogEntryObjectEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'LogEntryObject' }
        & Pick<LogEntryObject, 'id' | 'action' | 'changesDisplayDict' | 'timestamp'>
        & { actor: Maybe<(
          { __typename?: 'UserNode' }
          & Pick<UserNode, 'id' | 'firstName' | 'lastName'>
        )> }
      )> }
    )>> }
  )> }
);

export type AllPaymentRecordsQueryVariables = {
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type AllPaymentRecordsQuery = (
  { __typename?: 'Query' }
  & { allPaymentRecords: Maybe<(
    { __typename?: 'PaymentRecordNodeConnection' }
    & Pick<PaymentRecordNodeConnection, 'totalCount' | 'edgeCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'PaymentRecordNodeEdge' }
      & Pick<PaymentRecordNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'PaymentRecordNode' }
        & Pick<PaymentRecordNode, 'id' | 'createdAt' | 'updatedAt' | 'fullName' | 'statusDate' | 'status' | 'caId' | 'totalPersonsCovered' | 'entitlementQuantity' | 'deliveredQuantity' | 'deliveryDate'>
        & { household: (
          { __typename?: 'HouseholdNode' }
          & Pick<HouseholdNode, 'id' | 'size'>
        ), cashPlan: Maybe<(
          { __typename?: 'CashPlanNode' }
          & Pick<CashPlanNode, 'id'>
          & { program: (
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
          ) }
        )> }
      )> }
    )>> }
  )> }
);

export type AllPaymentVerificationsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>,
  cashPlanPaymentVerification?: Maybe<Scalars['ID']>,
  search?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>
};


export type AllPaymentVerificationsQuery = (
  { __typename?: 'Query' }
  & { allPaymentVerifications: Maybe<(
    { __typename?: 'PaymentVerificationNodeConnection' }
    & Pick<PaymentVerificationNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'PaymentVerificationNodeEdge' }
      & Pick<PaymentVerificationNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'PaymentVerificationNode' }
        & Pick<PaymentVerificationNode, 'id' | 'status' | 'receivedAmount'>
        & { paymentRecord: (
          { __typename?: 'PaymentRecordNode' }
          & Pick<PaymentRecordNode, 'id' | 'deliveredQuantity'>
          & { household: (
            { __typename?: 'HouseholdNode' }
            & Pick<HouseholdNode, 'unicefId' | 'id'>
            & { headOfHousehold: (
              { __typename?: 'IndividualNode' }
              & Pick<IndividualNode, 'id' | 'fullName' | 'phoneNo' | 'phoneNoAlternative'>
            ) }
          ) }
        ) }
      )> }
    )>> }
  )> }
);

export type AllProgramsQueryVariables = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  sector?: Maybe<Array<Maybe<Scalars['String']>>>,
  businessArea: Scalars['String'],
  search?: Maybe<Scalars['String']>,
  numberOfHouseholds?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['Date']>,
  endDate?: Maybe<Scalars['Date']>,
  orderBy?: Maybe<Scalars['String']>
};


export type AllProgramsQuery = (
  { __typename?: 'Query' }
  & { allPrograms: Maybe<(
    { __typename?: 'ProgramNodeConnection' }
    & Pick<ProgramNodeConnection, 'totalCount' | 'edgeCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'endCursor' | 'startCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'ProgramNodeEdge' }
      & Pick<ProgramNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'ProgramNode' }
        & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'caId' | 'description' | 'budget' | 'frequencyOfPayments' | 'populationGoal' | 'sector' | 'totalNumberOfHouseholds' | 'individualDataNeeded'>
      )> }
    )>> }
  )> }
);

export type AllRapidProFlowsQueryVariables = {
  businessAreaSlug: Scalars['String']
};


export type AllRapidProFlowsQuery = (
  { __typename?: 'Query' }
  & { allRapidProFlows: Maybe<Array<Maybe<(
    { __typename?: 'RapidProFlow' }
    & Pick<RapidProFlow, 'id' | 'name'>
  )>>> }
);

export type AllSteficonRulesQueryVariables = {};


export type AllSteficonRulesQuery = (
  { __typename?: 'Query' }
  & { allSteficonRules: Maybe<(
    { __typename?: 'SteficonRuleNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'SteficonRuleNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'SteficonRuleNode' }
        & Pick<SteficonRuleNode, 'id' | 'name'>
      )> }
    )>> }
  )> }
);

export type AllTargetPopulationsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>,
  candidateListTotalHouseholdsMin?: Maybe<Scalars['Int']>,
  candidateListTotalHouseholdsMax?: Maybe<Scalars['Int']>,
  businessArea?: Maybe<Scalars['String']>
};


export type AllTargetPopulationsQuery = (
  { __typename?: 'Query' }
  & { allTargetPopulation: Maybe<(
    { __typename?: 'TargetPopulationNodeConnection' }
    & Pick<TargetPopulationNodeConnection, 'totalCount' | 'edgeCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'TargetPopulationNodeEdge' }
      & Pick<TargetPopulationNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'TargetPopulationNode' }
        & TargetPopulationMinimalFragment
      )> }
    )>> }
  )> }
);

export type AllUsersQueryVariables = {
  search?: Maybe<Scalars['String']>,
  status?: Maybe<Array<Maybe<Scalars['String']>>>,
  partner?: Maybe<Array<Maybe<Scalars['String']>>>,
  roles?: Maybe<Array<Maybe<Scalars['String']>>>,
  businessArea: Scalars['String'],
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type AllUsersQuery = (
  { __typename?: 'Query' }
  & { allUsers: Maybe<(
    { __typename?: 'UserNodeConnection' }
    & Pick<UserNodeConnection, 'totalCount' | 'edgeCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'endCursor' | 'startCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'UserNodeEdge' }
      & Pick<UserNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'UserNode' }
        & Pick<UserNode, 'id' | 'firstName' | 'lastName' | 'username' | 'email' | 'isActive' | 'lastLogin' | 'status' | 'partner'>
        & { userRoles: Array<(
          { __typename?: 'UserRoleNode' }
          & { businessArea: (
            { __typename?: 'UserBusinessAreaNode' }
            & Pick<UserBusinessAreaNode, 'name'>
          ), role: (
            { __typename?: 'RoleNode' }
            & Pick<RoleNode, 'name' | 'permissions'>
          ) }
        )> }
      )> }
    )>> }
  )> }
);

export type CashPlanQueryVariables = {
  id: Scalars['ID']
};


export type CashPlanQuery = (
  { __typename?: 'Query' }
  & { cashPlan: Maybe<(
    { __typename?: 'CashPlanNode' }
    & Pick<CashPlanNode, 'id' | 'name' | 'startDate' | 'endDate' | 'updatedAt' | 'status' | 'deliveryType' | 'fundsCommitment' | 'downPayment' | 'dispersionDate' | 'assistanceThrough' | 'caId' | 'verificationStatus' | 'bankReconciliationSuccess' | 'bankReconciliationError'>
    & { verifications: (
      { __typename?: 'CashPlanPaymentVerificationNodeConnection' }
      & { edges: Array<Maybe<(
        { __typename?: 'CashPlanPaymentVerificationNodeEdge' }
        & { node: Maybe<(
          { __typename?: 'CashPlanPaymentVerificationNode' }
          & Pick<CashPlanPaymentVerificationNode, 'id' | 'status' | 'sampleSize' | 'receivedCount' | 'notReceivedCount' | 'respondedCount' | 'verificationMethod' | 'sampling' | 'receivedWithProblemsCount' | 'rapidProFlowId' | 'confidenceInterval' | 'marginOfError' | 'activationDate' | 'completionDate' | 'excludedAdminAreasFilter' | 'sexFilter'>
          & { ageFilter: Maybe<(
            { __typename?: 'AgeFilterObject' }
            & Pick<AgeFilterObject, 'min' | 'max'>
          )> }
        )> }
      )>> }
    ), program: (
      { __typename?: 'ProgramNode' }
      & Pick<ProgramNode, 'id' | 'name'>
    ), paymentRecords: (
      { __typename?: 'PaymentRecordNodeConnection' }
      & Pick<PaymentRecordNodeConnection, 'totalCount' | 'edgeCount'>
    ) }
  )> }
);

export type GrievancesChoiceDataQueryVariables = {};


export type GrievancesChoiceDataQuery = (
  { __typename?: 'Query' }
  & { grievanceTicketStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, grievanceTicketCategoryChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, grievanceTicketIssueTypeChoices: Maybe<Array<Maybe<(
    { __typename?: 'IssueTypesObject' }
    & Pick<IssueTypesObject, 'category' | 'label'>
    & { subCategories: Maybe<Array<Maybe<(
      { __typename?: 'ChoiceObject' }
      & Pick<ChoiceObject, 'name' | 'value'>
    )>>> }
  )>>> }
);

export type HouseholdQueryVariables = {
  id: Scalars['ID']
};


export type HouseholdQuery = (
  { __typename?: 'Query' }
  & { household: Maybe<(
    { __typename?: 'HouseholdNode' }
    & HouseholdDetailedFragment
  )> }
);

export type HouseholdChoiceDataQueryVariables = {};


export type HouseholdChoiceDataQuery = (
  { __typename?: 'Query' }
  & { residenceStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, relationshipChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, roleChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, maritalStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, deduplicationBatchStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, deduplicationGoldenRecordStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type IndividualQueryVariables = {
  id: Scalars['ID']
};


export type IndividualQuery = (
  { __typename?: 'Query' }
  & { individual: Maybe<(
    { __typename?: 'IndividualNode' }
    & IndividualDetailedFragment
  )> }
);

export type LookUpPaymentRecordsQueryVariables = {
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type LookUpPaymentRecordsQuery = (
  { __typename?: 'Query' }
  & { allPaymentRecords: Maybe<(
    { __typename?: 'PaymentRecordNodeConnection' }
    & Pick<PaymentRecordNodeConnection, 'totalCount' | 'edgeCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'PaymentRecordNodeEdge' }
      & Pick<PaymentRecordNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'PaymentRecordNode' }
        & Pick<PaymentRecordNode, 'id' | 'caId' | 'deliveredQuantity'>
        & { verifications: (
          { __typename?: 'PaymentVerificationNodeConnection' }
          & { edges: Array<Maybe<(
            { __typename?: 'PaymentVerificationNodeEdge' }
            & { node: Maybe<(
              { __typename?: 'PaymentVerificationNode' }
              & Pick<PaymentVerificationNode, 'status'>
            )> }
          )>> }
        ), cashPlan: Maybe<(
          { __typename?: 'CashPlanNode' }
          & Pick<CashPlanNode, 'id' | 'name'>
        )> }
      )> }
    )>> }
  )> }
);

export type MeQueryVariables = {};


export type MeQuery = (
  { __typename?: 'Query' }
  & { me: Maybe<(
    { __typename?: 'UserObjectType' }
    & Pick<UserObjectType, 'id' | 'username' | 'email' | 'firstName' | 'lastName'>
    & { businessAreas: Maybe<(
      { __typename?: 'UserBusinessAreaNodeConnection' }
      & { edges: Array<Maybe<(
        { __typename?: 'UserBusinessAreaNodeEdge' }
        & { node: Maybe<(
          { __typename?: 'UserBusinessAreaNode' }
          & Pick<UserBusinessAreaNode, 'id' | 'name' | 'slug' | 'permissions'>
        )> }
      )>> }
    )> }
  )> }
);

export type PaymentRecordQueryVariables = {
  id: Scalars['ID']
};


export type PaymentRecordQuery = (
  { __typename?: 'Query' }
  & { paymentRecord: Maybe<(
    { __typename?: 'PaymentRecordNode' }
    & Pick<PaymentRecordNode, 'id' | 'status' | 'statusDate' | 'caId' | 'fullName' | 'distributionModality' | 'totalPersonsCovered' | 'currency' | 'entitlementQuantity' | 'deliveredQuantity' | 'deliveryDate' | 'entitlementCardIssueDate' | 'entitlementCardNumber' | 'deliveryType'>
    & { household: (
      { __typename?: 'HouseholdNode' }
      & Pick<HouseholdNode, 'id' | 'size'>
      & { headOfHousehold: (
        { __typename?: 'IndividualNode' }
        & Pick<IndividualNode, 'id' | 'phoneNo' | 'phoneNoAlternative'>
      ) }
    ), targetPopulation: (
      { __typename?: 'TargetPopulationNode' }
      & Pick<TargetPopulationNode, 'id' | 'name'>
    ), cashPlan: Maybe<(
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id' | 'caId'>
      & { program: (
        { __typename?: 'ProgramNode' }
        & Pick<ProgramNode, 'id' | 'name'>
      ), verifications: (
        { __typename?: 'CashPlanPaymentVerificationNodeConnection' }
        & { edges: Array<Maybe<(
          { __typename?: 'CashPlanPaymentVerificationNodeEdge' }
          & { node: Maybe<(
            { __typename?: 'CashPlanPaymentVerificationNode' }
            & Pick<CashPlanPaymentVerificationNode, 'id' | 'status' | 'verificationMethod'>
          )> }
        )>> }
      ) }
    )>, verifications: (
      { __typename?: 'PaymentVerificationNodeConnection' }
      & Pick<PaymentVerificationNodeConnection, 'totalCount'>
      & { edges: Array<Maybe<(
        { __typename?: 'PaymentVerificationNodeEdge' }
        & { node: Maybe<(
          { __typename?: 'PaymentVerificationNode' }
          & Pick<PaymentVerificationNode, 'id' | 'status' | 'statusDate' | 'receivedAmount'>
        )> }
      )>> }
    ), serviceProvider: (
      { __typename?: 'ServiceProviderNode' }
      & Pick<ServiceProviderNode, 'id' | 'fullName' | 'shortName'>
    ) }
  )> }
);

export type PaymentRecordVerificationQueryVariables = {
  id: Scalars['ID']
};


export type PaymentRecordVerificationQuery = (
  { __typename?: 'Query' }
  & { paymentRecordVerification: Maybe<(
    { __typename?: 'PaymentVerificationNode' }
    & Pick<PaymentVerificationNode, 'id' | 'status' | 'statusDate' | 'receivedAmount'>
    & { paymentRecord: (
      { __typename?: 'PaymentRecordNode' }
      & Pick<PaymentRecordNode, 'id' | 'status' | 'statusDate' | 'caId' | 'fullName' | 'distributionModality' | 'totalPersonsCovered' | 'currency' | 'entitlementQuantity' | 'deliveredQuantity' | 'deliveryDate' | 'deliveryType' | 'entitlementCardIssueDate' | 'entitlementCardNumber'>
      & { household: (
        { __typename?: 'HouseholdNode' }
        & Pick<HouseholdNode, 'unicefId' | 'id' | 'size'>
        & { headOfHousehold: (
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'id' | 'phoneNo' | 'phoneNoAlternative'>
        ) }
      ), targetPopulation: (
        { __typename?: 'TargetPopulationNode' }
        & Pick<TargetPopulationNode, 'id' | 'name'>
      ), cashPlan: Maybe<(
        { __typename?: 'CashPlanNode' }
        & Pick<CashPlanNode, 'id' | 'caId'>
        & { program: (
          { __typename?: 'ProgramNode' }
          & Pick<ProgramNode, 'id' | 'name'>
        ), verifications: (
          { __typename?: 'CashPlanPaymentVerificationNodeConnection' }
          & { edges: Array<Maybe<(
            { __typename?: 'CashPlanPaymentVerificationNodeEdge' }
            & { node: Maybe<(
              { __typename?: 'CashPlanPaymentVerificationNode' }
              & Pick<CashPlanPaymentVerificationNode, 'id' | 'status' | 'verificationMethod'>
            )> }
          )>> }
        ) }
      )>, serviceProvider: (
        { __typename?: 'ServiceProviderNode' }
        & Pick<ServiceProviderNode, 'id' | 'fullName' | 'shortName'>
      ) }
    ) }
  )> }
);

export type ProgramQueryVariables = {
  id: Scalars['ID']
};


export type ProgramQuery = (
  { __typename?: 'Query' }
  & { program: Maybe<(
    { __typename?: 'ProgramNode' }
    & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'caId' | 'description' | 'budget' | 'frequencyOfPayments' | 'cashPlus' | 'populationGoal' | 'scope' | 'sector' | 'totalNumberOfHouseholds' | 'administrativeAreasOfImplementation' | 'individualDataNeeded'>
  )> }
);

export type ProgrammeChoiceDataQueryVariables = {};


export type ProgrammeChoiceDataQuery = (
  { __typename?: 'Query' }
  & { programFrequencyOfPaymentsChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, programScopeChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, programSectorChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, programStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type SampleSizeQueryVariables = {
  input: GetCashplanVerificationSampleSizeInput
};


export type SampleSizeQuery = (
  { __typename?: 'Query' }
  & { sampleSize: Maybe<(
    { __typename?: 'GetCashplanVerificationSampleSizeObject' }
    & Pick<GetCashplanVerificationSampleSizeObject, 'paymentRecordCount' | 'sampleSize'>
  )> }
);

export type TargetPopulationQueryVariables = {
  id: Scalars['ID']
};


export type TargetPopulationQuery = (
  { __typename?: 'Query' }
  & { targetPopulation: Maybe<(
    { __typename?: 'TargetPopulationNode' }
    & TargetPopulationDetailedFragment
  )> }
);

export type UserChoiceDataQueryVariables = {};


export type UserChoiceDataQuery = (
  { __typename?: 'Query' }
  & { userRolesChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, userStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>>, userPartnerChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type AllImportedHouseholdsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  rdiId?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type AllImportedHouseholdsQuery = (
  { __typename?: 'Query' }
  & { allImportedHouseholds: Maybe<(
    { __typename?: 'ImportedHouseholdNodeConnection' }
    & Pick<ImportedHouseholdNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'ImportedHouseholdNodeEdge' }
      & Pick<ImportedHouseholdNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'ImportedHouseholdNode' }
        & ImportedHouseholdMinimalFragment
      )> }
    )>> }
  )> }
);

export type AllImportedIndividualsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  rdiId?: Maybe<Scalars['String']>,
  household?: Maybe<Scalars['ID']>,
  orderBy?: Maybe<Scalars['String']>,
  duplicatesOnly?: Maybe<Scalars['Boolean']>
};


export type AllImportedIndividualsQuery = (
  { __typename?: 'Query' }
  & { allImportedIndividuals: Maybe<(
    { __typename?: 'ImportedIndividualNodeConnection' }
    & Pick<ImportedIndividualNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'ImportedIndividualNodeEdge' }
      & Pick<ImportedIndividualNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'ImportedIndividualNode' }
        & ImportedIndividualMinimalFragment
      )> }
    )>> }
  )> }
);

export type AllKoboProjectsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  businessAreaSlug: Scalars['String']
};


export type AllKoboProjectsQuery = (
  { __typename?: 'Query' }
  & { allKoboProjects: Maybe<(
    { __typename?: 'KoboAssetObjectConnection' }
    & Pick<KoboAssetObjectConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'KoboAssetObjectEdge' }
      & Pick<KoboAssetObjectEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'KoboAssetObject' }
        & Pick<KoboAssetObject, 'name' | 'id'>
      )> }
    )>> }
  )> }
);

export type AllRegistrationDataImportsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>,
  name_Icontains?: Maybe<Scalars['String']>,
  importedBy_Id?: Maybe<Scalars['UUID']>,
  status?: Maybe<Scalars['String']>,
  importDate?: Maybe<Scalars['Date']>,
  businessArea?: Maybe<Scalars['String']>
};


export type AllRegistrationDataImportsQuery = (
  { __typename?: 'Query' }
  & { allRegistrationDataImports: Maybe<(
    { __typename?: 'RegistrationDataImportNodeConnection' }
    & Pick<RegistrationDataImportNodeConnection, 'totalCount'>
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'startCursor' | 'endCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'RegistrationDataImportNodeEdge' }
      & Pick<RegistrationDataImportNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'RegistrationDataImportNode' }
        & RegistrationMinimalFragment
      )> }
    )>> }
  )> }
);

export type CreateRegistrationKoboImportMutationVariables = {
  registrationDataImportData: RegistrationKoboImportMutationInput
};


export type CreateRegistrationKoboImportMutation = (
  { __typename?: 'Mutations' }
  & { registrationKoboImport: Maybe<(
    { __typename?: 'RegistrationKoboImportMutation' }
    & { registrationDataImport: Maybe<(
      { __typename?: 'RegistrationDataImportNode' }
      & Pick<RegistrationDataImportNode, 'id' | 'name' | 'dataSource' | 'datahubId'>
    )> }
  )> }
);

export type CreateRegistrationXlsxImportMutationVariables = {
  registrationDataImportData: RegistrationXlsxImportMutationInput
};


export type CreateRegistrationXlsxImportMutation = (
  { __typename?: 'Mutations' }
  & { registrationXlsxImport: Maybe<(
    { __typename?: 'RegistrationXlsxImportMutation' }
    & { registrationDataImport: Maybe<(
      { __typename?: 'RegistrationDataImportNode' }
      & Pick<RegistrationDataImportNode, 'id' | 'name' | 'dataSource' | 'datahubId'>
    )> }
  )> }
);

export type ImportedHouseholdQueryVariables = {
  id: Scalars['ID']
};


export type ImportedHouseholdQuery = (
  { __typename?: 'Query' }
  & { importedHousehold: Maybe<(
    { __typename?: 'ImportedHouseholdNode' }
    & ImportedHouseholdDetailedFragment
  )> }
);

export type ImportedIndividualQueryVariables = {
  id: Scalars['ID']
};


export type ImportedIndividualQuery = (
  { __typename?: 'Query' }
  & { importedIndividual: Maybe<(
    { __typename?: 'ImportedIndividualNode' }
    & ImportedIndividualDetailedFragment
  )> }
);

export type MergeRdiMutationVariables = {
  id: Scalars['ID']
};


export type MergeRdiMutation = (
  { __typename?: 'Mutations' }
  & { mergeRegistrationDataImport: Maybe<(
    { __typename?: 'MergeRegistrationDataImportMutation' }
    & { registrationDataImport: Maybe<(
      { __typename?: 'RegistrationDataImportNode' }
      & RegistrationDetailedFragment
    )> }
  )> }
);

export type RegistrationChoicesQueryVariables = {};


export type RegistrationChoicesQuery = (
  { __typename?: 'Query' }
  & { registrationDataStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);

export type RegistrationDataImportQueryVariables = {
  id: Scalars['ID']
};


export type RegistrationDataImportQuery = (
  { __typename?: 'Query' }
  & { registrationDataImport: Maybe<(
    { __typename?: 'RegistrationDataImportNode' }
    & RegistrationDetailedFragment
  )> }
);

export type RegistrationMinimalFragment = (
  { __typename?: 'RegistrationDataImportNode' }
  & Pick<RegistrationDataImportNode, 'id' | 'createdAt' | 'name' | 'status' | 'importDate' | 'dataSource' | 'numberOfHouseholds' | 'numberOfIndividuals'>
  & { importedBy: (
    { __typename?: 'UserNode' }
    & Pick<UserNode, 'id' | 'firstName' | 'lastName' | 'email'>
  ) }
);

export type RegistrationDetailedFragment = (
  { __typename?: 'RegistrationDataImportNode' }
  & Pick<RegistrationDataImportNode, 'numberOfIndividuals' | 'datahubId' | 'errorMessage'>
  & { batchDuplicatesCountAndPercentage: Maybe<(
    { __typename?: 'CountAndPercentageNode' }
    & Pick<CountAndPercentageNode, 'count' | 'percentage'>
  )>, batchPossibleDuplicatesCountAndPercentage: Maybe<(
    { __typename?: 'CountAndPercentageNode' }
    & Pick<CountAndPercentageNode, 'count' | 'percentage'>
  )>, batchUniqueCountAndPercentage: Maybe<(
    { __typename?: 'CountAndPercentageNode' }
    & Pick<CountAndPercentageNode, 'count' | 'percentage'>
  )>, goldenRecordUniqueCountAndPercentage: Maybe<(
    { __typename?: 'CountAndPercentageNode' }
    & Pick<CountAndPercentageNode, 'count' | 'percentage'>
  )>, goldenRecordDuplicatesCountAndPercentage: Maybe<(
    { __typename?: 'CountAndPercentageNode' }
    & Pick<CountAndPercentageNode, 'count' | 'percentage'>
  )>, goldenRecordPossibleDuplicatesCountAndPercentage: Maybe<(
    { __typename?: 'CountAndPercentageNode' }
    & Pick<CountAndPercentageNode, 'count' | 'percentage'>
  )> }
  & RegistrationMinimalFragment
);

export type ImportedHouseholdMinimalFragment = (
  { __typename?: 'ImportedHouseholdNode' }
  & Pick<ImportedHouseholdNode, 'id' | 'size' | 'admin1' | 'admin2' | 'firstRegistrationDate' | 'lastRegistrationDate' | 'hasDuplicates'>
  & { headOfHousehold: Maybe<(
    { __typename?: 'ImportedIndividualNode' }
    & Pick<ImportedIndividualNode, 'id' | 'fullName'>
  )> }
);

export type ImportedHouseholdDetailedFragment = (
  { __typename?: 'ImportedHouseholdNode' }
  & Pick<ImportedHouseholdNode, 'residenceStatus' | 'country' | 'countryOrigin'>
  & { registrationDataImport: (
    { __typename?: 'RegistrationDataImportDatahubNode' }
    & Pick<RegistrationDataImportDatahubNode, 'id' | 'hctId' | 'name'>
  ) }
  & ImportedHouseholdMinimalFragment
);

export type ImportedIndividualMinimalFragment = (
  { __typename?: 'ImportedIndividualNode' }
  & Pick<ImportedIndividualNode, 'id' | 'fullName' | 'birthDate' | 'sex' | 'role' | 'relationship' | 'deduplicationBatchStatus' | 'deduplicationGoldenRecordStatus'>
  & { deduplicationGoldenRecordResults: Maybe<Array<Maybe<(
    { __typename?: 'DeduplicationResultNode' }
    & Pick<DeduplicationResultNode, 'hitId' | 'fullName' | 'score' | 'proximityToScore' | 'age' | 'location'>
  )>>>, deduplicationBatchResults: Maybe<Array<Maybe<(
    { __typename?: 'DeduplicationResultNode' }
    & Pick<DeduplicationResultNode, 'hitId' | 'fullName' | 'score' | 'proximityToScore' | 'age' | 'location'>
  )>>>, registrationDataImport: (
    { __typename?: 'RegistrationDataImportDatahubNode' }
    & Pick<RegistrationDataImportDatahubNode, 'id' | 'hctId'>
  ) }
);

export type ImportedIndividualDetailedFragment = (
  { __typename?: 'ImportedIndividualNode' }
  & Pick<ImportedIndividualNode, 'givenName' | 'familyName' | 'middleName' | 'estimatedBirthDate' | 'maritalStatus' | 'pregnant' | 'role' | 'relationship' | 'phoneNo' | 'phoneNoAlternative'>
  & { documents: (
    { __typename?: 'ImportedDocumentNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'ImportedDocumentNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'ImportedDocumentNode' }
        & Pick<ImportedDocumentNode, 'id' | 'documentNumber'>
        & { type: (
          { __typename?: 'ImportedDocumentTypeNode' }
          & Pick<ImportedDocumentTypeNode, 'label'>
        ) }
      )> }
    )>> }
  ), identities: Array<(
    { __typename?: 'ImportedIndividualIdentityNode' }
    & Pick<ImportedIndividualIdentityNode, 'id' | 'documentNumber' | 'type'>
  )>, household: Maybe<(
    { __typename?: 'ImportedHouseholdNode' }
    & Pick<ImportedHouseholdNode, 'id' | 'admin1' | 'admin2' | 'address'>
  )>, registrationDataImport: (
    { __typename?: 'RegistrationDataImportDatahubNode' }
    & Pick<RegistrationDataImportDatahubNode, 'id' | 'hctId' | 'name'>
  ) }
  & ImportedIndividualMinimalFragment
);

export type SaveKoboImportDataMutationVariables = {
  businessAreaSlug: Scalars['String'],
  projectId: Scalars['Upload']
};


export type SaveKoboImportDataMutation = (
  { __typename?: 'Mutations' }
  & { saveKoboImportData: Maybe<(
    { __typename?: 'SaveKoboProjectImportDataMutation' }
    & { importData: Maybe<(
      { __typename?: 'ImportDataNode' }
      & Pick<ImportDataNode, 'id' | 'numberOfHouseholds' | 'numberOfIndividuals'>
    )>, errors: Maybe<Array<Maybe<(
      { __typename?: 'KoboErrorNode' }
      & Pick<KoboErrorNode, 'header' | 'message'>
    )>>> }
  )> }
);

export type UploadImportDataXlsxFileMutationVariables = {
  file: Scalars['Upload'],
  businessAreaSlug: Scalars['String']
};


export type UploadImportDataXlsxFileMutation = (
  { __typename?: 'Mutations' }
  & { uploadImportDataXlsxFile: Maybe<(
    { __typename?: 'UploadImportDataXLSXFile' }
    & { errors: Maybe<Array<Maybe<(
      { __typename?: 'XlsxRowErrorNode' }
      & Pick<XlsxRowErrorNode, 'header' | 'message' | 'rowNumber'>
    )>>>, importData: Maybe<(
      { __typename?: 'ImportDataNode' }
      & Pick<ImportDataNode, 'id' | 'numberOfIndividuals' | 'numberOfHouseholds'>
      & { registrationDataImport: Maybe<(
        { __typename?: 'RegistrationDataImportDatahubNode' }
        & Pick<RegistrationDataImportDatahubNode, 'id'>
      )> }
    )> }
  )> }
);

export type AllFieldsAttributesQueryVariables = {};


export type AllFieldsAttributesQuery = (
  { __typename?: 'Query' }
  & { allFieldsAttributes: Maybe<Array<Maybe<(
    { __typename?: 'FieldAttributeNode' }
    & Pick<FieldAttributeNode, 'id' | 'name' | 'labelEn' | 'associatedWith' | 'isFlexField'>
  )>>> }
);

export type CandidateHouseholdsListByTargetingCriteriaQueryVariables = {
  targetPopulation: Scalars['ID'],
  first?: Maybe<Scalars['Int']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
};


export type CandidateHouseholdsListByTargetingCriteriaQuery = (
  { __typename?: 'Query' }
  & { candidateHouseholdsListByTargetingCriteria: Maybe<(
    { __typename?: 'HouseholdNodeConnection' }
    & Pick<HouseholdNodeConnection, 'totalCount' | 'edgeCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'HouseholdNodeEdge' }
      & Pick<HouseholdNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'HouseholdNode' }
        & Pick<HouseholdNode, 'id' | 'size' | 'updatedAt' | 'address'>
        & { headOfHousehold: (
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'id' | 'givenName' | 'familyName'>
        ), adminArea: Maybe<(
          { __typename?: 'AdminAreaNode' }
          & Pick<AdminAreaNode, 'id' | 'title'>
        )>, selection: Maybe<(
          { __typename?: 'HouseholdSelection' }
          & Pick<HouseholdSelection, 'vulnerabilityScore'>
        )> }
      )> }
    )>> }
  )> }
);

export type FinalHouseholdsListByTargetingCriteriaQueryVariables = {
  targetPopulation: Scalars['ID'],
  targetingCriteria?: Maybe<TargetingCriteriaObjectType>,
  first?: Maybe<Scalars['Int']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
};


export type FinalHouseholdsListByTargetingCriteriaQuery = (
  { __typename?: 'Query' }
  & { finalHouseholdsListByTargetingCriteria: Maybe<(
    { __typename?: 'HouseholdNodeConnection' }
    & Pick<HouseholdNodeConnection, 'totalCount' | 'edgeCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'HouseholdNodeEdge' }
      & Pick<HouseholdNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'HouseholdNode' }
        & Pick<HouseholdNode, 'id' | 'size' | 'updatedAt' | 'address'>
        & { headOfHousehold: (
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'id' | 'givenName' | 'familyName'>
        ), adminArea: Maybe<(
          { __typename?: 'AdminAreaNode' }
          & Pick<AdminAreaNode, 'id' | 'title'>
        )>, selection: Maybe<(
          { __typename?: 'HouseholdSelection' }
          & Pick<HouseholdSelection, 'vulnerabilityScore'>
        )> }
      )> }
    )>> }
  )> }
);

export type FlexFieldsQueryVariables = {};


export type FlexFieldsQuery = (
  { __typename?: 'Query' }
  & { allGroupsWithFields: Maybe<Array<Maybe<(
    { __typename?: 'GroupAttributeNode' }
    & Pick<GroupAttributeNode, 'name' | 'labelEn'>
    & { flexAttributes: Maybe<Array<Maybe<(
      { __typename?: 'FieldAttributeNode' }
      & Pick<FieldAttributeNode, 'id' | 'labelEn' | 'associatedWith'>
    )>>> }
  )>>> }
);

export type GoldenRecordByTargetingCriteriaQueryVariables = {
  targetingCriteria: TargetingCriteriaObjectType,
  first?: Maybe<Scalars['Int']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
};


export type GoldenRecordByTargetingCriteriaQuery = (
  { __typename?: 'Query' }
  & { goldenRecordByTargetingCriteria: Maybe<(
    { __typename?: 'HouseholdNodeConnection' }
    & Pick<HouseholdNodeConnection, 'totalCount' | 'edgeCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'HouseholdNodeEdge' }
      & Pick<HouseholdNodeEdge, 'cursor'>
      & { node: Maybe<(
        { __typename?: 'HouseholdNode' }
        & Pick<HouseholdNode, 'id' | 'size' | 'updatedAt' | 'address'>
        & { headOfHousehold: (
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'id' | 'givenName' | 'familyName'>
        ), adminArea: Maybe<(
          { __typename?: 'AdminAreaNode' }
          & Pick<AdminAreaNode, 'id' | 'title'>
        )> }
      )> }
    )>> }
  )> }
);

export type ImportedIndividualFieldsQueryVariables = {};


export type ImportedIndividualFieldsQuery = (
  { __typename?: 'Query' }
  & { allFieldsAttributes: Maybe<Array<Maybe<(
    { __typename?: 'FieldAttributeNode' }
    & Pick<FieldAttributeNode, 'isFlexField' | 'id' | 'type' | 'name' | 'associatedWith' | 'labelEn' | 'hint'>
    & { labels: Maybe<Array<Maybe<(
      { __typename?: 'LabelNode' }
      & Pick<LabelNode, 'language' | 'label'>
    )>>>, choices: Maybe<Array<Maybe<(
      { __typename?: 'CoreFieldChoiceObject' }
      & Pick<CoreFieldChoiceObject, 'labelEn' | 'value' | 'admin' | 'listName'>
      & { labels: Maybe<Array<Maybe<(
        { __typename?: 'LabelNode' }
        & Pick<LabelNode, 'label' | 'language'>
      )>>> }
    )>>> }
  )>>> }
);

export const HouseholdMinimalFragmentDoc = gql`
    fragment householdMinimal on HouseholdNode {
  id
  createdAt
  residenceStatus
  size
  totalCashReceived
  firstRegistrationDate
  lastRegistrationDate
  status
  sanctionListPossibleMatch
  hasDuplicates
  unicefId
  geopoint
  village
  adminArea {
    id
    title
    adminAreaType {
      adminLevel
    }
  }
  headOfHousehold {
    id
    fullName
  }
  address
  individuals {
    totalCount
  }
  programs {
    edges {
      node {
        id
        name
      }
    }
  }
}
    `;
export const IndividualMinimalFragmentDoc = gql`
    fragment individualMinimal on IndividualNode {
  id
  lastRegistrationDate
  createdAt
  updatedAt
  fullName
  sex
  unicefId
  birthDate
  maritalStatus
  phoneNo
  sanctionListPossibleMatch
  deduplicationGoldenRecordStatus
  sanctionListLastCheck
  role
  relationship
  status
  documents {
    edges {
      node {
        id
        documentNumber
        type {
          country
          label
        }
      }
    }
  }
  household {
    id
    unicefId
    status
    adminArea {
      id
      title
      adminAreaType {
        adminLevel
      }
    }
    programs {
      edges {
        node {
          id
          name
        }
      }
    }
  }
}
    `;
export const HouseholdDetailedFragmentDoc = gql`
    fragment householdDetailed on HouseholdNode {
  ...householdMinimal
  countryOrigin
  country
  individuals {
    totalCount
    edges {
      node {
        ...individualMinimal
        birthDate
        relationship
      }
    }
  }
  programs {
    edges {
      node {
        id
        name
      }
    }
  }
  registrationDataImport {
    name
    dataSource
    importDate
    importedBy {
      firstName
      lastName
      email
      username
    }
  }
  paymentRecords {
    edges {
      node {
        id
        fullName
        cashPlan {
          id
          totalPersonsCovered
          program {
            id
            name
          }
          totalDeliveredQuantity
          assistanceMeasurement
        }
      }
    }
  }
  flexFields
}
    ${HouseholdMinimalFragmentDoc}
${IndividualMinimalFragmentDoc}`;
export const IndividualDetailedFragmentDoc = gql`
    fragment individualDetailed on IndividualNode {
  ...individualMinimal
  givenName
  familyName
  estimatedBirthDate
  pregnant
  status
  documents {
    edges {
      node {
        type {
          label
        }
        documentNumber
      }
    }
  }
  enrolledInNutritionProgramme
  administrationOfRutf
  identities {
    number
    type
  }
  household {
    status
    id
    address
    countryOrigin
    adminArea {
      id
      title
      level
    }
  }
  role
  relationship
  headingHousehold {
    id
    headOfHousehold {
      id
    }
  }
  flexFields
}
    ${IndividualMinimalFragmentDoc}`;
export const TargetPopulationMinimalFragmentDoc = gql`
    fragment targetPopulationMinimal on TargetPopulationNode {
  id
  name
  status
  createdAt
  updatedAt
  candidateListTotalHouseholds
  finalListTotalHouseholds
  createdBy {
    firstName
    lastName
  }
}
    `;
export const TargetPopulationDetailedFragmentDoc = gql`
    fragment targetPopulationDetailed on TargetPopulationNode {
  id
  name
  status
  candidateListTotalHouseholds
  candidateListTotalIndividuals
  finalListTotalHouseholds
  finalListTotalIndividuals
  steficonRule {
    id
    name
  }
  vulnerabilityScoreMin
  vulnerabilityScoreMax
  approvedAt
  finalizedAt
  finalizedBy {
    firstName
    lastName
  }
  program {
    id
    name
    startDate
    endDate
    status
    caId
    description
    budget
    frequencyOfPayments
    populationGoal
    sector
    totalNumberOfHouseholds
    individualDataNeeded
  }
  createdBy {
    firstName
    lastName
  }
  candidateListTargetingCriteria {
    targetPopulationCandidate {
      createdBy {
        firstName
        lastName
      }
    }
    rules {
      id
      individualsFiltersBlocks {
        individualBlockFilters {
          fieldName
          isFlexField
          arguments
          comparisionMethod
          fieldAttribute {
            name
            labelEn
            type
            choices {
              value
              labelEn
            }
          }
        }
      }
      filters {
        fieldName
        isFlexField
        arguments
        comparisionMethod
        fieldAttribute {
          name
          labelEn
          type
          choices {
            value
            labelEn
          }
        }
      }
    }
  }
  finalListTargetingCriteria {
    targetPopulationFinal {
      createdBy {
        firstName
        lastName
      }
    }
    rules {
      id
      filters {
        fieldName
        isFlexField
        arguments
        comparisionMethod
        fieldAttribute {
          name
          labelEn
          type
          choices {
            value
            labelEn
          }
        }
      }
    }
  }
  candidateStats {
    childMale
    childFemale
    adultMale
    adultFemale
  }
  finalStats {
    childMale
    childFemale
    adultMale
    adultFemale
  }
}
    `;
export const RegistrationMinimalFragmentDoc = gql`
    fragment registrationMinimal on RegistrationDataImportNode {
  id
  createdAt
  name
  status
  importDate
  importedBy {
    id
    firstName
    lastName
    email
  }
  dataSource
  numberOfHouseholds
  numberOfIndividuals
}
    `;
export const RegistrationDetailedFragmentDoc = gql`
    fragment registrationDetailed on RegistrationDataImportNode {
  ...registrationMinimal
  numberOfIndividuals
  datahubId
  errorMessage
  batchDuplicatesCountAndPercentage {
    count
    percentage
  }
  batchPossibleDuplicatesCountAndPercentage {
    count
    percentage
  }
  batchUniqueCountAndPercentage {
    count
    percentage
  }
  goldenRecordUniqueCountAndPercentage {
    count
    percentage
  }
  goldenRecordDuplicatesCountAndPercentage {
    count
    percentage
  }
  goldenRecordPossibleDuplicatesCountAndPercentage {
    count
    percentage
  }
}
    ${RegistrationMinimalFragmentDoc}`;
export const ImportedHouseholdMinimalFragmentDoc = gql`
    fragment importedHouseholdMinimal on ImportedHouseholdNode {
  id
  headOfHousehold {
    id
    fullName
  }
  size
  admin1
  admin2
  firstRegistrationDate
  lastRegistrationDate
  hasDuplicates
}
    `;
export const ImportedHouseholdDetailedFragmentDoc = gql`
    fragment importedHouseholdDetailed on ImportedHouseholdNode {
  ...importedHouseholdMinimal
  residenceStatus
  country
  countryOrigin
  registrationDataImport {
    id
    hctId
    name
  }
}
    ${ImportedHouseholdMinimalFragmentDoc}`;
export const ImportedIndividualMinimalFragmentDoc = gql`
    fragment importedIndividualMinimal on ImportedIndividualNode {
  id
  fullName
  birthDate
  sex
  role
  relationship
  deduplicationBatchStatus
  deduplicationGoldenRecordStatus
  deduplicationGoldenRecordResults {
    hitId
    fullName
    score
    proximityToScore
    age
    location
  }
  deduplicationBatchResults {
    hitId
    fullName
    score
    proximityToScore
    age
    location
  }
  registrationDataImport {
    id
    hctId
  }
}
    `;
export const ImportedIndividualDetailedFragmentDoc = gql`
    fragment importedIndividualDetailed on ImportedIndividualNode {
  ...importedIndividualMinimal
  givenName
  familyName
  middleName
  estimatedBirthDate
  maritalStatus
  pregnant
  documents {
    edges {
      node {
        id
        type {
          label
        }
        documentNumber
      }
    }
  }
  identities {
    id
    documentNumber
    type
  }
  role
  relationship
  household {
    id
    admin1
    admin2
    address
  }
  registrationDataImport {
    id
    hctId
    name
  }
  phoneNo
  phoneNoAlternative
}
    ${ImportedIndividualMinimalFragmentDoc}`;
export const ActivateCashPlanPaymentVerificationDocument = gql`
    mutation ActivateCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
  activateCashPlanPaymentVerification(cashPlanVerificationId: $cashPlanVerificationId) {
    cashPlan {
      id
      status
      statusDate
    }
  }
}
    `;
export type ActivateCashPlanPaymentVerificationMutationFn = ApolloReactCommon.MutationFunction<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables>;
export type ActivateCashPlanPaymentVerificationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables>, 'mutation'>;

    export const ActivateCashPlanPaymentVerificationComponent = (props: ActivateCashPlanPaymentVerificationComponentProps) => (
      <ApolloReactComponents.Mutation<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables> mutation={ActivateCashPlanPaymentVerificationDocument} {...props} />
    );
    
export type ActivateCashPlanPaymentVerificationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables> & TChildProps;
export function withActivateCashPlanPaymentVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ActivateCashPlanPaymentVerificationMutation,
  ActivateCashPlanPaymentVerificationMutationVariables,
  ActivateCashPlanPaymentVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables, ActivateCashPlanPaymentVerificationProps<TChildProps>>(ActivateCashPlanPaymentVerificationDocument, {
      alias: 'activateCashPlanPaymentVerification',
      ...operationOptions
    });
};

/**
 * __useActivateCashPlanPaymentVerificationMutation__
 *
 * To run a mutation, you first call `useActivateCashPlanPaymentVerificationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useActivateCashPlanPaymentVerificationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [activateCashPlanPaymentVerificationMutation, { data, loading, error }] = useActivateCashPlanPaymentVerificationMutation({
 *   variables: {
 *      cashPlanVerificationId: // value for 'cashPlanVerificationId'
 *   },
 * });
 */
export function useActivateCashPlanPaymentVerificationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables>) {
        return ApolloReactHooks.useMutation<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables>(ActivateCashPlanPaymentVerificationDocument, baseOptions);
      }
export type ActivateCashPlanPaymentVerificationMutationHookResult = ReturnType<typeof useActivateCashPlanPaymentVerificationMutation>;
export type ActivateCashPlanPaymentVerificationMutationResult = ApolloReactCommon.MutationResult<ActivateCashPlanPaymentVerificationMutation>;
export type ActivateCashPlanPaymentVerificationMutationOptions = ApolloReactCommon.BaseMutationOptions<ActivateCashPlanPaymentVerificationMutation, ActivateCashPlanPaymentVerificationMutationVariables>;
export const ApproveTpDocument = gql`
    mutation ApproveTP($id: ID!) {
  approveTargetPopulation(id: $id) {
    targetPopulation {
      ...targetPopulationDetailed
    }
  }
}
    ${TargetPopulationDetailedFragmentDoc}`;
export type ApproveTpMutationFn = ApolloReactCommon.MutationFunction<ApproveTpMutation, ApproveTpMutationVariables>;
export type ApproveTpComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<ApproveTpMutation, ApproveTpMutationVariables>, 'mutation'>;

    export const ApproveTpComponent = (props: ApproveTpComponentProps) => (
      <ApolloReactComponents.Mutation<ApproveTpMutation, ApproveTpMutationVariables> mutation={ApproveTpDocument} {...props} />
    );
    
export type ApproveTpProps<TChildProps = {}> = ApolloReactHoc.MutateProps<ApproveTpMutation, ApproveTpMutationVariables> & TChildProps;
export function withApproveTp<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ApproveTpMutation,
  ApproveTpMutationVariables,
  ApproveTpProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, ApproveTpMutation, ApproveTpMutationVariables, ApproveTpProps<TChildProps>>(ApproveTpDocument, {
      alias: 'approveTp',
      ...operationOptions
    });
};

/**
 * __useApproveTpMutation__
 *
 * To run a mutation, you first call `useApproveTpMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useApproveTpMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [approveTpMutation, { data, loading, error }] = useApproveTpMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useApproveTpMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<ApproveTpMutation, ApproveTpMutationVariables>) {
        return ApolloReactHooks.useMutation<ApproveTpMutation, ApproveTpMutationVariables>(ApproveTpDocument, baseOptions);
      }
export type ApproveTpMutationHookResult = ReturnType<typeof useApproveTpMutation>;
export type ApproveTpMutationResult = ApolloReactCommon.MutationResult<ApproveTpMutation>;
export type ApproveTpMutationOptions = ApolloReactCommon.BaseMutationOptions<ApproveTpMutation, ApproveTpMutationVariables>;
export const CheckAgainstSanctionListUploadDocument = gql`
    mutation CheckAgainstSanctionListUpload($file: Upload!) {
  checkAgainstSanctionList(file: $file) {
    errors {
      header
      message
      rowNumber
    }
  }
}
    `;
export type CheckAgainstSanctionListUploadMutationFn = ApolloReactCommon.MutationFunction<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables>;
export type CheckAgainstSanctionListUploadComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables>, 'mutation'>;

    export const CheckAgainstSanctionListUploadComponent = (props: CheckAgainstSanctionListUploadComponentProps) => (
      <ApolloReactComponents.Mutation<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables> mutation={CheckAgainstSanctionListUploadDocument} {...props} />
    );
    
export type CheckAgainstSanctionListUploadProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables> & TChildProps;
export function withCheckAgainstSanctionListUpload<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CheckAgainstSanctionListUploadMutation,
  CheckAgainstSanctionListUploadMutationVariables,
  CheckAgainstSanctionListUploadProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables, CheckAgainstSanctionListUploadProps<TChildProps>>(CheckAgainstSanctionListUploadDocument, {
      alias: 'checkAgainstSanctionListUpload',
      ...operationOptions
    });
};

/**
 * __useCheckAgainstSanctionListUploadMutation__
 *
 * To run a mutation, you first call `useCheckAgainstSanctionListUploadMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCheckAgainstSanctionListUploadMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [checkAgainstSanctionListUploadMutation, { data, loading, error }] = useCheckAgainstSanctionListUploadMutation({
 *   variables: {
 *      file: // value for 'file'
 *   },
 * });
 */
export function useCheckAgainstSanctionListUploadMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables>) {
        return ApolloReactHooks.useMutation<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables>(CheckAgainstSanctionListUploadDocument, baseOptions);
      }
export type CheckAgainstSanctionListUploadMutationHookResult = ReturnType<typeof useCheckAgainstSanctionListUploadMutation>;
export type CheckAgainstSanctionListUploadMutationResult = ApolloReactCommon.MutationResult<CheckAgainstSanctionListUploadMutation>;
export type CheckAgainstSanctionListUploadMutationOptions = ApolloReactCommon.BaseMutationOptions<CheckAgainstSanctionListUploadMutation, CheckAgainstSanctionListUploadMutationVariables>;
export const CreateCashPlanPaymentVerificationDocument = gql`
    mutation createCashPlanPaymentVerification($input: CreatePaymentVerificationInput!) {
  createCashPlanPaymentVerification(input: $input) {
    cashPlan {
      id
    }
  }
}
    `;
export type CreateCashPlanPaymentVerificationMutationFn = ApolloReactCommon.MutationFunction<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables>;
export type CreateCashPlanPaymentVerificationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables>, 'mutation'>;

    export const CreateCashPlanPaymentVerificationComponent = (props: CreateCashPlanPaymentVerificationComponentProps) => (
      <ApolloReactComponents.Mutation<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables> mutation={CreateCashPlanPaymentVerificationDocument} {...props} />
    );
    
export type CreateCashPlanPaymentVerificationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables> & TChildProps;
export function withCreateCashPlanPaymentVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateCashPlanPaymentVerificationMutation,
  CreateCashPlanPaymentVerificationMutationVariables,
  CreateCashPlanPaymentVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables, CreateCashPlanPaymentVerificationProps<TChildProps>>(CreateCashPlanPaymentVerificationDocument, {
      alias: 'createCashPlanPaymentVerification',
      ...operationOptions
    });
};

/**
 * __useCreateCashPlanPaymentVerificationMutation__
 *
 * To run a mutation, you first call `useCreateCashPlanPaymentVerificationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateCashPlanPaymentVerificationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createCashPlanPaymentVerificationMutation, { data, loading, error }] = useCreateCashPlanPaymentVerificationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateCashPlanPaymentVerificationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables>(CreateCashPlanPaymentVerificationDocument, baseOptions);
      }
export type CreateCashPlanPaymentVerificationMutationHookResult = ReturnType<typeof useCreateCashPlanPaymentVerificationMutation>;
export type CreateCashPlanPaymentVerificationMutationResult = ApolloReactCommon.MutationResult<CreateCashPlanPaymentVerificationMutation>;
export type CreateCashPlanPaymentVerificationMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateCashPlanPaymentVerificationMutation, CreateCashPlanPaymentVerificationMutationVariables>;
export const CreateGrievanceDocument = gql`
    mutation CreateGrievance($input: CreateGrievanceTicketInput!) {
  createGrievanceTicket(input: $input) {
    grievanceTickets {
      id
    }
  }
}
    `;
export type CreateGrievanceMutationFn = ApolloReactCommon.MutationFunction<CreateGrievanceMutation, CreateGrievanceMutationVariables>;
export type CreateGrievanceComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateGrievanceMutation, CreateGrievanceMutationVariables>, 'mutation'>;

    export const CreateGrievanceComponent = (props: CreateGrievanceComponentProps) => (
      <ApolloReactComponents.Mutation<CreateGrievanceMutation, CreateGrievanceMutationVariables> mutation={CreateGrievanceDocument} {...props} />
    );
    
export type CreateGrievanceProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateGrievanceMutation, CreateGrievanceMutationVariables> & TChildProps;
export function withCreateGrievance<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateGrievanceMutation,
  CreateGrievanceMutationVariables,
  CreateGrievanceProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateGrievanceMutation, CreateGrievanceMutationVariables, CreateGrievanceProps<TChildProps>>(CreateGrievanceDocument, {
      alias: 'createGrievance',
      ...operationOptions
    });
};

/**
 * __useCreateGrievanceMutation__
 *
 * To run a mutation, you first call `useCreateGrievanceMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateGrievanceMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createGrievanceMutation, { data, loading, error }] = useCreateGrievanceMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateGrievanceMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateGrievanceMutation, CreateGrievanceMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateGrievanceMutation, CreateGrievanceMutationVariables>(CreateGrievanceDocument, baseOptions);
      }
export type CreateGrievanceMutationHookResult = ReturnType<typeof useCreateGrievanceMutation>;
export type CreateGrievanceMutationResult = ApolloReactCommon.MutationResult<CreateGrievanceMutation>;
export type CreateGrievanceMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateGrievanceMutation, CreateGrievanceMutationVariables>;
export const CreateProgramDocument = gql`
    mutation CreateProgram($programData: CreateProgramInput!) {
  createProgram(programData: $programData) {
    program {
      id
      name
      status
      startDate
      endDate
      caId
      budget
      description
      frequencyOfPayments
      sector
      scope
      cashPlus
      populationGoal
      individualDataNeeded
    }
  }
}
    `;
export type CreateProgramMutationFn = ApolloReactCommon.MutationFunction<CreateProgramMutation, CreateProgramMutationVariables>;
export type CreateProgramComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateProgramMutation, CreateProgramMutationVariables>, 'mutation'>;

    export const CreateProgramComponent = (props: CreateProgramComponentProps) => (
      <ApolloReactComponents.Mutation<CreateProgramMutation, CreateProgramMutationVariables> mutation={CreateProgramDocument} {...props} />
    );
    
export type CreateProgramProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateProgramMutation, CreateProgramMutationVariables> & TChildProps;
export function withCreateProgram<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateProgramMutation,
  CreateProgramMutationVariables,
  CreateProgramProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateProgramMutation, CreateProgramMutationVariables, CreateProgramProps<TChildProps>>(CreateProgramDocument, {
      alias: 'createProgram',
      ...operationOptions
    });
};

/**
 * __useCreateProgramMutation__
 *
 * To run a mutation, you first call `useCreateProgramMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateProgramMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createProgramMutation, { data, loading, error }] = useCreateProgramMutation({
 *   variables: {
 *      programData: // value for 'programData'
 *   },
 * });
 */
export function useCreateProgramMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateProgramMutation, CreateProgramMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateProgramMutation, CreateProgramMutationVariables>(CreateProgramDocument, baseOptions);
      }
export type CreateProgramMutationHookResult = ReturnType<typeof useCreateProgramMutation>;
export type CreateProgramMutationResult = ApolloReactCommon.MutationResult<CreateProgramMutation>;
export type CreateProgramMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateProgramMutation, CreateProgramMutationVariables>;
export const CreateTpDocument = gql`
    mutation CreateTP($input: CreateTargetPopulationInput!) {
  createTargetPopulation(input: $input) {
    targetPopulation {
      id
      status
      candidateListTotalHouseholds
      candidateListTotalIndividuals
      finalListTotalHouseholds
      finalListTotalIndividuals
    }
  }
}
    `;
export type CreateTpMutationFn = ApolloReactCommon.MutationFunction<CreateTpMutation, CreateTpMutationVariables>;
export type CreateTpComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateTpMutation, CreateTpMutationVariables>, 'mutation'>;

    export const CreateTpComponent = (props: CreateTpComponentProps) => (
      <ApolloReactComponents.Mutation<CreateTpMutation, CreateTpMutationVariables> mutation={CreateTpDocument} {...props} />
    );
    
export type CreateTpProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateTpMutation, CreateTpMutationVariables> & TChildProps;
export function withCreateTp<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateTpMutation,
  CreateTpMutationVariables,
  CreateTpProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateTpMutation, CreateTpMutationVariables, CreateTpProps<TChildProps>>(CreateTpDocument, {
      alias: 'createTp',
      ...operationOptions
    });
};

/**
 * __useCreateTpMutation__
 *
 * To run a mutation, you first call `useCreateTpMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateTpMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createTpMutation, { data, loading, error }] = useCreateTpMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCreateTpMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateTpMutation, CreateTpMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateTpMutation, CreateTpMutationVariables>(CreateTpDocument, baseOptions);
      }
export type CreateTpMutationHookResult = ReturnType<typeof useCreateTpMutation>;
export type CreateTpMutationResult = ApolloReactCommon.MutationResult<CreateTpMutation>;
export type CreateTpMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateTpMutation, CreateTpMutationVariables>;
export const DeleteProgramDocument = gql`
    mutation DeleteProgram($programId: String!) {
  deleteProgram(programId: $programId) {
    ok
  }
}
    `;
export type DeleteProgramMutationFn = ApolloReactCommon.MutationFunction<DeleteProgramMutation, DeleteProgramMutationVariables>;
export type DeleteProgramComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<DeleteProgramMutation, DeleteProgramMutationVariables>, 'mutation'>;

    export const DeleteProgramComponent = (props: DeleteProgramComponentProps) => (
      <ApolloReactComponents.Mutation<DeleteProgramMutation, DeleteProgramMutationVariables> mutation={DeleteProgramDocument} {...props} />
    );
    
export type DeleteProgramProps<TChildProps = {}> = ApolloReactHoc.MutateProps<DeleteProgramMutation, DeleteProgramMutationVariables> & TChildProps;
export function withDeleteProgram<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  DeleteProgramMutation,
  DeleteProgramMutationVariables,
  DeleteProgramProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, DeleteProgramMutation, DeleteProgramMutationVariables, DeleteProgramProps<TChildProps>>(DeleteProgramDocument, {
      alias: 'deleteProgram',
      ...operationOptions
    });
};

/**
 * __useDeleteProgramMutation__
 *
 * To run a mutation, you first call `useDeleteProgramMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteProgramMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteProgramMutation, { data, loading, error }] = useDeleteProgramMutation({
 *   variables: {
 *      programId: // value for 'programId'
 *   },
 * });
 */
export function useDeleteProgramMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<DeleteProgramMutation, DeleteProgramMutationVariables>) {
        return ApolloReactHooks.useMutation<DeleteProgramMutation, DeleteProgramMutationVariables>(DeleteProgramDocument, baseOptions);
      }
export type DeleteProgramMutationHookResult = ReturnType<typeof useDeleteProgramMutation>;
export type DeleteProgramMutationResult = ApolloReactCommon.MutationResult<DeleteProgramMutation>;
export type DeleteProgramMutationOptions = ApolloReactCommon.BaseMutationOptions<DeleteProgramMutation, DeleteProgramMutationVariables>;
export const DeleteTargetPopulationDocument = gql`
    mutation DeleteTargetPopulation($input: DeleteTargetPopulationMutationInput!) {
  deleteTargetPopulation(input: $input) {
    clientMutationId
  }
}
    `;
export type DeleteTargetPopulationMutationFn = ApolloReactCommon.MutationFunction<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables>;
export type DeleteTargetPopulationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables>, 'mutation'>;

    export const DeleteTargetPopulationComponent = (props: DeleteTargetPopulationComponentProps) => (
      <ApolloReactComponents.Mutation<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables> mutation={DeleteTargetPopulationDocument} {...props} />
    );
    
export type DeleteTargetPopulationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables> & TChildProps;
export function withDeleteTargetPopulation<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  DeleteTargetPopulationMutation,
  DeleteTargetPopulationMutationVariables,
  DeleteTargetPopulationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables, DeleteTargetPopulationProps<TChildProps>>(DeleteTargetPopulationDocument, {
      alias: 'deleteTargetPopulation',
      ...operationOptions
    });
};

/**
 * __useDeleteTargetPopulationMutation__
 *
 * To run a mutation, you first call `useDeleteTargetPopulationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDeleteTargetPopulationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [deleteTargetPopulationMutation, { data, loading, error }] = useDeleteTargetPopulationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useDeleteTargetPopulationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables>) {
        return ApolloReactHooks.useMutation<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables>(DeleteTargetPopulationDocument, baseOptions);
      }
export type DeleteTargetPopulationMutationHookResult = ReturnType<typeof useDeleteTargetPopulationMutation>;
export type DeleteTargetPopulationMutationResult = ApolloReactCommon.MutationResult<DeleteTargetPopulationMutation>;
export type DeleteTargetPopulationMutationOptions = ApolloReactCommon.BaseMutationOptions<DeleteTargetPopulationMutation, DeleteTargetPopulationMutationVariables>;
export const DiscardCashPlanPaymentVerificationDocument = gql`
    mutation DiscardCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
  discardCashPlanPaymentVerification(cashPlanVerificationId: $cashPlanVerificationId) {
    cashPlan {
      id
      status
      statusDate
    }
  }
}
    `;
export type DiscardCashPlanPaymentVerificationMutationFn = ApolloReactCommon.MutationFunction<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables>;
export type DiscardCashPlanPaymentVerificationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables>, 'mutation'>;

    export const DiscardCashPlanPaymentVerificationComponent = (props: DiscardCashPlanPaymentVerificationComponentProps) => (
      <ApolloReactComponents.Mutation<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables> mutation={DiscardCashPlanPaymentVerificationDocument} {...props} />
    );
    
export type DiscardCashPlanPaymentVerificationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables> & TChildProps;
export function withDiscardCashPlanPaymentVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  DiscardCashPlanPaymentVerificationMutation,
  DiscardCashPlanPaymentVerificationMutationVariables,
  DiscardCashPlanPaymentVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables, DiscardCashPlanPaymentVerificationProps<TChildProps>>(DiscardCashPlanPaymentVerificationDocument, {
      alias: 'discardCashPlanPaymentVerification',
      ...operationOptions
    });
};

/**
 * __useDiscardCashPlanPaymentVerificationMutation__
 *
 * To run a mutation, you first call `useDiscardCashPlanPaymentVerificationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useDiscardCashPlanPaymentVerificationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [discardCashPlanPaymentVerificationMutation, { data, loading, error }] = useDiscardCashPlanPaymentVerificationMutation({
 *   variables: {
 *      cashPlanVerificationId: // value for 'cashPlanVerificationId'
 *   },
 * });
 */
export function useDiscardCashPlanPaymentVerificationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables>) {
        return ApolloReactHooks.useMutation<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables>(DiscardCashPlanPaymentVerificationDocument, baseOptions);
      }
export type DiscardCashPlanPaymentVerificationMutationHookResult = ReturnType<typeof useDiscardCashPlanPaymentVerificationMutation>;
export type DiscardCashPlanPaymentVerificationMutationResult = ApolloReactCommon.MutationResult<DiscardCashPlanPaymentVerificationMutation>;
export type DiscardCashPlanPaymentVerificationMutationOptions = ApolloReactCommon.BaseMutationOptions<DiscardCashPlanPaymentVerificationMutation, DiscardCashPlanPaymentVerificationMutationVariables>;
export const CopyTargetPopulationDocument = gql`
    mutation CopyTargetPopulation($input: CopyTargetPopulationMutationInput!) {
  copyTargetPopulation(input: $input) {
    clientMutationId
    targetPopulation {
      id
    }
  }
}
    `;
export type CopyTargetPopulationMutationFn = ApolloReactCommon.MutationFunction<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables>;
export type CopyTargetPopulationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables>, 'mutation'>;

    export const CopyTargetPopulationComponent = (props: CopyTargetPopulationComponentProps) => (
      <ApolloReactComponents.Mutation<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables> mutation={CopyTargetPopulationDocument} {...props} />
    );
    
export type CopyTargetPopulationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables> & TChildProps;
export function withCopyTargetPopulation<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CopyTargetPopulationMutation,
  CopyTargetPopulationMutationVariables,
  CopyTargetPopulationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables, CopyTargetPopulationProps<TChildProps>>(CopyTargetPopulationDocument, {
      alias: 'copyTargetPopulation',
      ...operationOptions
    });
};

/**
 * __useCopyTargetPopulationMutation__
 *
 * To run a mutation, you first call `useCopyTargetPopulationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCopyTargetPopulationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [copyTargetPopulationMutation, { data, loading, error }] = useCopyTargetPopulationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useCopyTargetPopulationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables>) {
        return ApolloReactHooks.useMutation<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables>(CopyTargetPopulationDocument, baseOptions);
      }
export type CopyTargetPopulationMutationHookResult = ReturnType<typeof useCopyTargetPopulationMutation>;
export type CopyTargetPopulationMutationResult = ApolloReactCommon.MutationResult<CopyTargetPopulationMutation>;
export type CopyTargetPopulationMutationOptions = ApolloReactCommon.BaseMutationOptions<CopyTargetPopulationMutation, CopyTargetPopulationMutationVariables>;
export const EditCashPlanPaymentVerificationDocument = gql`
    mutation editCashPlanPaymentVerification($input: EditCashPlanPaymentVerificationInput!) {
  editCashPlanPaymentVerification(input: $input) {
    cashPlan {
      id
    }
  }
}
    `;
export type EditCashPlanPaymentVerificationMutationFn = ApolloReactCommon.MutationFunction<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables>;
export type EditCashPlanPaymentVerificationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables>, 'mutation'>;

    export const EditCashPlanPaymentVerificationComponent = (props: EditCashPlanPaymentVerificationComponentProps) => (
      <ApolloReactComponents.Mutation<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables> mutation={EditCashPlanPaymentVerificationDocument} {...props} />
    );
    
export type EditCashPlanPaymentVerificationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables> & TChildProps;
export function withEditCashPlanPaymentVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  EditCashPlanPaymentVerificationMutation,
  EditCashPlanPaymentVerificationMutationVariables,
  EditCashPlanPaymentVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables, EditCashPlanPaymentVerificationProps<TChildProps>>(EditCashPlanPaymentVerificationDocument, {
      alias: 'editCashPlanPaymentVerification',
      ...operationOptions
    });
};

/**
 * __useEditCashPlanPaymentVerificationMutation__
 *
 * To run a mutation, you first call `useEditCashPlanPaymentVerificationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useEditCashPlanPaymentVerificationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [editCashPlanPaymentVerificationMutation, { data, loading, error }] = useEditCashPlanPaymentVerificationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useEditCashPlanPaymentVerificationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables>) {
        return ApolloReactHooks.useMutation<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables>(EditCashPlanPaymentVerificationDocument, baseOptions);
      }
export type EditCashPlanPaymentVerificationMutationHookResult = ReturnType<typeof useEditCashPlanPaymentVerificationMutation>;
export type EditCashPlanPaymentVerificationMutationResult = ApolloReactCommon.MutationResult<EditCashPlanPaymentVerificationMutation>;
export type EditCashPlanPaymentVerificationMutationOptions = ApolloReactCommon.BaseMutationOptions<EditCashPlanPaymentVerificationMutation, EditCashPlanPaymentVerificationMutationVariables>;
export const FinalizeTpDocument = gql`
    mutation FinalizeTP($id: ID!) {
  finalizeTargetPopulation(id: $id) {
    targetPopulation {
      ...targetPopulationDetailed
    }
  }
}
    ${TargetPopulationDetailedFragmentDoc}`;
export type FinalizeTpMutationFn = ApolloReactCommon.MutationFunction<FinalizeTpMutation, FinalizeTpMutationVariables>;
export type FinalizeTpComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<FinalizeTpMutation, FinalizeTpMutationVariables>, 'mutation'>;

    export const FinalizeTpComponent = (props: FinalizeTpComponentProps) => (
      <ApolloReactComponents.Mutation<FinalizeTpMutation, FinalizeTpMutationVariables> mutation={FinalizeTpDocument} {...props} />
    );
    
export type FinalizeTpProps<TChildProps = {}> = ApolloReactHoc.MutateProps<FinalizeTpMutation, FinalizeTpMutationVariables> & TChildProps;
export function withFinalizeTp<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  FinalizeTpMutation,
  FinalizeTpMutationVariables,
  FinalizeTpProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, FinalizeTpMutation, FinalizeTpMutationVariables, FinalizeTpProps<TChildProps>>(FinalizeTpDocument, {
      alias: 'finalizeTp',
      ...operationOptions
    });
};

/**
 * __useFinalizeTpMutation__
 *
 * To run a mutation, you first call `useFinalizeTpMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useFinalizeTpMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [finalizeTpMutation, { data, loading, error }] = useFinalizeTpMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useFinalizeTpMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<FinalizeTpMutation, FinalizeTpMutationVariables>) {
        return ApolloReactHooks.useMutation<FinalizeTpMutation, FinalizeTpMutationVariables>(FinalizeTpDocument, baseOptions);
      }
export type FinalizeTpMutationHookResult = ReturnType<typeof useFinalizeTpMutation>;
export type FinalizeTpMutationResult = ApolloReactCommon.MutationResult<FinalizeTpMutation>;
export type FinalizeTpMutationOptions = ApolloReactCommon.BaseMutationOptions<FinalizeTpMutation, FinalizeTpMutationVariables>;
export const FinishCashPlanPaymentVerificationDocument = gql`
    mutation FinishCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
  finishCashPlanPaymentVerification(cashPlanVerificationId: $cashPlanVerificationId) {
    cashPlan {
      id
      status
      statusDate
    }
  }
}
    `;
export type FinishCashPlanPaymentVerificationMutationFn = ApolloReactCommon.MutationFunction<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables>;
export type FinishCashPlanPaymentVerificationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables>, 'mutation'>;

    export const FinishCashPlanPaymentVerificationComponent = (props: FinishCashPlanPaymentVerificationComponentProps) => (
      <ApolloReactComponents.Mutation<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables> mutation={FinishCashPlanPaymentVerificationDocument} {...props} />
    );
    
export type FinishCashPlanPaymentVerificationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables> & TChildProps;
export function withFinishCashPlanPaymentVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  FinishCashPlanPaymentVerificationMutation,
  FinishCashPlanPaymentVerificationMutationVariables,
  FinishCashPlanPaymentVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables, FinishCashPlanPaymentVerificationProps<TChildProps>>(FinishCashPlanPaymentVerificationDocument, {
      alias: 'finishCashPlanPaymentVerification',
      ...operationOptions
    });
};

/**
 * __useFinishCashPlanPaymentVerificationMutation__
 *
 * To run a mutation, you first call `useFinishCashPlanPaymentVerificationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useFinishCashPlanPaymentVerificationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [finishCashPlanPaymentVerificationMutation, { data, loading, error }] = useFinishCashPlanPaymentVerificationMutation({
 *   variables: {
 *      cashPlanVerificationId: // value for 'cashPlanVerificationId'
 *   },
 * });
 */
export function useFinishCashPlanPaymentVerificationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables>) {
        return ApolloReactHooks.useMutation<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables>(FinishCashPlanPaymentVerificationDocument, baseOptions);
      }
export type FinishCashPlanPaymentVerificationMutationHookResult = ReturnType<typeof useFinishCashPlanPaymentVerificationMutation>;
export type FinishCashPlanPaymentVerificationMutationResult = ApolloReactCommon.MutationResult<FinishCashPlanPaymentVerificationMutation>;
export type FinishCashPlanPaymentVerificationMutationOptions = ApolloReactCommon.BaseMutationOptions<FinishCashPlanPaymentVerificationMutation, FinishCashPlanPaymentVerificationMutationVariables>;
export const ImportXlsxCashPlanVerificationDocument = gql`
    mutation importXlsxCashPlanVerification($cashPlanVerificationId: ID!, $file: Upload!) {
  importXlsxCashPlanVerification(cashPlanVerificationId: $cashPlanVerificationId, file: $file) {
    cashPlan {
      id
    }
    errors {
      sheet
      coordinates
      message
    }
  }
}
    `;
export type ImportXlsxCashPlanVerificationMutationFn = ApolloReactCommon.MutationFunction<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables>;
export type ImportXlsxCashPlanVerificationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables>, 'mutation'>;

    export const ImportXlsxCashPlanVerificationComponent = (props: ImportXlsxCashPlanVerificationComponentProps) => (
      <ApolloReactComponents.Mutation<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables> mutation={ImportXlsxCashPlanVerificationDocument} {...props} />
    );
    
export type ImportXlsxCashPlanVerificationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables> & TChildProps;
export function withImportXlsxCashPlanVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ImportXlsxCashPlanVerificationMutation,
  ImportXlsxCashPlanVerificationMutationVariables,
  ImportXlsxCashPlanVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables, ImportXlsxCashPlanVerificationProps<TChildProps>>(ImportXlsxCashPlanVerificationDocument, {
      alias: 'importXlsxCashPlanVerification',
      ...operationOptions
    });
};

/**
 * __useImportXlsxCashPlanVerificationMutation__
 *
 * To run a mutation, you first call `useImportXlsxCashPlanVerificationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useImportXlsxCashPlanVerificationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [importXlsxCashPlanVerificationMutation, { data, loading, error }] = useImportXlsxCashPlanVerificationMutation({
 *   variables: {
 *      cashPlanVerificationId: // value for 'cashPlanVerificationId'
 *      file: // value for 'file'
 *   },
 * });
 */
export function useImportXlsxCashPlanVerificationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables>) {
        return ApolloReactHooks.useMutation<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables>(ImportXlsxCashPlanVerificationDocument, baseOptions);
      }
export type ImportXlsxCashPlanVerificationMutationHookResult = ReturnType<typeof useImportXlsxCashPlanVerificationMutation>;
export type ImportXlsxCashPlanVerificationMutationResult = ApolloReactCommon.MutationResult<ImportXlsxCashPlanVerificationMutation>;
export type ImportXlsxCashPlanVerificationMutationOptions = ApolloReactCommon.BaseMutationOptions<ImportXlsxCashPlanVerificationMutation, ImportXlsxCashPlanVerificationMutationVariables>;
export const RerunDedupeDocument = gql`
    mutation RerunDedupe($registrationDataImportDatahubId: ID!) {
  rerunDedupe(registrationDataImportDatahubId: $registrationDataImportDatahubId) {
    ok
  }
}
    `;
export type RerunDedupeMutationFn = ApolloReactCommon.MutationFunction<RerunDedupeMutation, RerunDedupeMutationVariables>;
export type RerunDedupeComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<RerunDedupeMutation, RerunDedupeMutationVariables>, 'mutation'>;

    export const RerunDedupeComponent = (props: RerunDedupeComponentProps) => (
      <ApolloReactComponents.Mutation<RerunDedupeMutation, RerunDedupeMutationVariables> mutation={RerunDedupeDocument} {...props} />
    );
    
export type RerunDedupeProps<TChildProps = {}> = ApolloReactHoc.MutateProps<RerunDedupeMutation, RerunDedupeMutationVariables> & TChildProps;
export function withRerunDedupe<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  RerunDedupeMutation,
  RerunDedupeMutationVariables,
  RerunDedupeProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, RerunDedupeMutation, RerunDedupeMutationVariables, RerunDedupeProps<TChildProps>>(RerunDedupeDocument, {
      alias: 'rerunDedupe',
      ...operationOptions
    });
};

/**
 * __useRerunDedupeMutation__
 *
 * To run a mutation, you first call `useRerunDedupeMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useRerunDedupeMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [rerunDedupeMutation, { data, loading, error }] = useRerunDedupeMutation({
 *   variables: {
 *      registrationDataImportDatahubId: // value for 'registrationDataImportDatahubId'
 *   },
 * });
 */
export function useRerunDedupeMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<RerunDedupeMutation, RerunDedupeMutationVariables>) {
        return ApolloReactHooks.useMutation<RerunDedupeMutation, RerunDedupeMutationVariables>(RerunDedupeDocument, baseOptions);
      }
export type RerunDedupeMutationHookResult = ReturnType<typeof useRerunDedupeMutation>;
export type RerunDedupeMutationResult = ApolloReactCommon.MutationResult<RerunDedupeMutation>;
export type RerunDedupeMutationOptions = ApolloReactCommon.BaseMutationOptions<RerunDedupeMutation, RerunDedupeMutationVariables>;
export const SetSteficonRuleOnTargetPopulationDocument = gql`
    mutation setSteficonRuleOnTargetPopulation($input: SetSteficonRuleOnTargetPopulationMutationInput!) {
  setSteficonRuleOnTargetPopulation(input: $input) {
    targetPopulation {
      ...targetPopulationDetailed
    }
  }
}
    ${TargetPopulationDetailedFragmentDoc}`;
export type SetSteficonRuleOnTargetPopulationMutationFn = ApolloReactCommon.MutationFunction<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables>;
export type SetSteficonRuleOnTargetPopulationComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables>, 'mutation'>;

    export const SetSteficonRuleOnTargetPopulationComponent = (props: SetSteficonRuleOnTargetPopulationComponentProps) => (
      <ApolloReactComponents.Mutation<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables> mutation={SetSteficonRuleOnTargetPopulationDocument} {...props} />
    );
    
export type SetSteficonRuleOnTargetPopulationProps<TChildProps = {}> = ApolloReactHoc.MutateProps<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables> & TChildProps;
export function withSetSteficonRuleOnTargetPopulation<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  SetSteficonRuleOnTargetPopulationMutation,
  SetSteficonRuleOnTargetPopulationMutationVariables,
  SetSteficonRuleOnTargetPopulationProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables, SetSteficonRuleOnTargetPopulationProps<TChildProps>>(SetSteficonRuleOnTargetPopulationDocument, {
      alias: 'setSteficonRuleOnTargetPopulation',
      ...operationOptions
    });
};

/**
 * __useSetSteficonRuleOnTargetPopulationMutation__
 *
 * To run a mutation, you first call `useSetSteficonRuleOnTargetPopulationMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSetSteficonRuleOnTargetPopulationMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [setSteficonRuleOnTargetPopulationMutation, { data, loading, error }] = useSetSteficonRuleOnTargetPopulationMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSetSteficonRuleOnTargetPopulationMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables>) {
        return ApolloReactHooks.useMutation<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables>(SetSteficonRuleOnTargetPopulationDocument, baseOptions);
      }
export type SetSteficonRuleOnTargetPopulationMutationHookResult = ReturnType<typeof useSetSteficonRuleOnTargetPopulationMutation>;
export type SetSteficonRuleOnTargetPopulationMutationResult = ApolloReactCommon.MutationResult<SetSteficonRuleOnTargetPopulationMutation>;
export type SetSteficonRuleOnTargetPopulationMutationOptions = ApolloReactCommon.BaseMutationOptions<SetSteficonRuleOnTargetPopulationMutation, SetSteficonRuleOnTargetPopulationMutationVariables>;
export const UnapproveTpDocument = gql`
    mutation UnapproveTP($id: ID!) {
  unapproveTargetPopulation(id: $id) {
    targetPopulation {
      ...targetPopulationDetailed
    }
  }
}
    ${TargetPopulationDetailedFragmentDoc}`;
export type UnapproveTpMutationFn = ApolloReactCommon.MutationFunction<UnapproveTpMutation, UnapproveTpMutationVariables>;
export type UnapproveTpComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UnapproveTpMutation, UnapproveTpMutationVariables>, 'mutation'>;

    export const UnapproveTpComponent = (props: UnapproveTpComponentProps) => (
      <ApolloReactComponents.Mutation<UnapproveTpMutation, UnapproveTpMutationVariables> mutation={UnapproveTpDocument} {...props} />
    );
    
export type UnapproveTpProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UnapproveTpMutation, UnapproveTpMutationVariables> & TChildProps;
export function withUnapproveTp<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UnapproveTpMutation,
  UnapproveTpMutationVariables,
  UnapproveTpProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UnapproveTpMutation, UnapproveTpMutationVariables, UnapproveTpProps<TChildProps>>(UnapproveTpDocument, {
      alias: 'unapproveTp',
      ...operationOptions
    });
};

/**
 * __useUnapproveTpMutation__
 *
 * To run a mutation, you first call `useUnapproveTpMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUnapproveTpMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [unapproveTpMutation, { data, loading, error }] = useUnapproveTpMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useUnapproveTpMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UnapproveTpMutation, UnapproveTpMutationVariables>) {
        return ApolloReactHooks.useMutation<UnapproveTpMutation, UnapproveTpMutationVariables>(UnapproveTpDocument, baseOptions);
      }
export type UnapproveTpMutationHookResult = ReturnType<typeof useUnapproveTpMutation>;
export type UnapproveTpMutationResult = ApolloReactCommon.MutationResult<UnapproveTpMutation>;
export type UnapproveTpMutationOptions = ApolloReactCommon.BaseMutationOptions<UnapproveTpMutation, UnapproveTpMutationVariables>;
export const UpdatePaymentVerificationReceivedAndReceivedAmountDocument = gql`
    mutation updatePaymentVerificationReceivedAndReceivedAmount($paymentVerificationId: ID!, $receivedAmount: Decimal!, $received: Boolean!) {
  updatePaymentVerificationReceivedAndReceivedAmount(paymentVerificationId: $paymentVerificationId, receivedAmount: $receivedAmount, received: $received) {
    paymentVerification {
      id
      status
      receivedAmount
    }
  }
}
    `;
export type UpdatePaymentVerificationReceivedAndReceivedAmountMutationFn = ApolloReactCommon.MutationFunction<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables>;
export type UpdatePaymentVerificationReceivedAndReceivedAmountComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables>, 'mutation'>;

    export const UpdatePaymentVerificationReceivedAndReceivedAmountComponent = (props: UpdatePaymentVerificationReceivedAndReceivedAmountComponentProps) => (
      <ApolloReactComponents.Mutation<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables> mutation={UpdatePaymentVerificationReceivedAndReceivedAmountDocument} {...props} />
    );
    
export type UpdatePaymentVerificationReceivedAndReceivedAmountProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables> & TChildProps;
export function withUpdatePaymentVerificationReceivedAndReceivedAmount<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UpdatePaymentVerificationReceivedAndReceivedAmountMutation,
  UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables,
  UpdatePaymentVerificationReceivedAndReceivedAmountProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables, UpdatePaymentVerificationReceivedAndReceivedAmountProps<TChildProps>>(UpdatePaymentVerificationReceivedAndReceivedAmountDocument, {
      alias: 'updatePaymentVerificationReceivedAndReceivedAmount',
      ...operationOptions
    });
};

/**
 * __useUpdatePaymentVerificationReceivedAndReceivedAmountMutation__
 *
 * To run a mutation, you first call `useUpdatePaymentVerificationReceivedAndReceivedAmountMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePaymentVerificationReceivedAndReceivedAmountMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePaymentVerificationReceivedAndReceivedAmountMutation, { data, loading, error }] = useUpdatePaymentVerificationReceivedAndReceivedAmountMutation({
 *   variables: {
 *      paymentVerificationId: // value for 'paymentVerificationId'
 *      receivedAmount: // value for 'receivedAmount'
 *      received: // value for 'received'
 *   },
 * });
 */
export function useUpdatePaymentVerificationReceivedAndReceivedAmountMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables>) {
        return ApolloReactHooks.useMutation<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables>(UpdatePaymentVerificationReceivedAndReceivedAmountDocument, baseOptions);
      }
export type UpdatePaymentVerificationReceivedAndReceivedAmountMutationHookResult = ReturnType<typeof useUpdatePaymentVerificationReceivedAndReceivedAmountMutation>;
export type UpdatePaymentVerificationReceivedAndReceivedAmountMutationResult = ApolloReactCommon.MutationResult<UpdatePaymentVerificationReceivedAndReceivedAmountMutation>;
export type UpdatePaymentVerificationReceivedAndReceivedAmountMutationOptions = ApolloReactCommon.BaseMutationOptions<UpdatePaymentVerificationReceivedAndReceivedAmountMutation, UpdatePaymentVerificationReceivedAndReceivedAmountMutationVariables>;
export const UpdatePaymentVerificationStatusAndReceivedAmountDocument = gql`
    mutation updatePaymentVerificationStatusAndReceivedAmount($paymentVerificationId: ID!, $receivedAmount: Decimal!, $status: PaymentVerificationStatusForUpdate) {
  updatePaymentVerificationStatusAndReceivedAmount(paymentVerificationId: $paymentVerificationId, receivedAmount: $receivedAmount, status: $status) {
    paymentVerification {
      id
      status
      receivedAmount
    }
  }
}
    `;
export type UpdatePaymentVerificationStatusAndReceivedAmountMutationFn = ApolloReactCommon.MutationFunction<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables>;
export type UpdatePaymentVerificationStatusAndReceivedAmountComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables>, 'mutation'>;

    export const UpdatePaymentVerificationStatusAndReceivedAmountComponent = (props: UpdatePaymentVerificationStatusAndReceivedAmountComponentProps) => (
      <ApolloReactComponents.Mutation<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables> mutation={UpdatePaymentVerificationStatusAndReceivedAmountDocument} {...props} />
    );
    
export type UpdatePaymentVerificationStatusAndReceivedAmountProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables> & TChildProps;
export function withUpdatePaymentVerificationStatusAndReceivedAmount<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UpdatePaymentVerificationStatusAndReceivedAmountMutation,
  UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables,
  UpdatePaymentVerificationStatusAndReceivedAmountProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables, UpdatePaymentVerificationStatusAndReceivedAmountProps<TChildProps>>(UpdatePaymentVerificationStatusAndReceivedAmountDocument, {
      alias: 'updatePaymentVerificationStatusAndReceivedAmount',
      ...operationOptions
    });
};

/**
 * __useUpdatePaymentVerificationStatusAndReceivedAmountMutation__
 *
 * To run a mutation, you first call `useUpdatePaymentVerificationStatusAndReceivedAmountMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdatePaymentVerificationStatusAndReceivedAmountMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updatePaymentVerificationStatusAndReceivedAmountMutation, { data, loading, error }] = useUpdatePaymentVerificationStatusAndReceivedAmountMutation({
 *   variables: {
 *      paymentVerificationId: // value for 'paymentVerificationId'
 *      receivedAmount: // value for 'receivedAmount'
 *      status: // value for 'status'
 *   },
 * });
 */
export function useUpdatePaymentVerificationStatusAndReceivedAmountMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables>) {
        return ApolloReactHooks.useMutation<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables>(UpdatePaymentVerificationStatusAndReceivedAmountDocument, baseOptions);
      }
export type UpdatePaymentVerificationStatusAndReceivedAmountMutationHookResult = ReturnType<typeof useUpdatePaymentVerificationStatusAndReceivedAmountMutation>;
export type UpdatePaymentVerificationStatusAndReceivedAmountMutationResult = ApolloReactCommon.MutationResult<UpdatePaymentVerificationStatusAndReceivedAmountMutation>;
export type UpdatePaymentVerificationStatusAndReceivedAmountMutationOptions = ApolloReactCommon.BaseMutationOptions<UpdatePaymentVerificationStatusAndReceivedAmountMutation, UpdatePaymentVerificationStatusAndReceivedAmountMutationVariables>;
export const UpdateProgramDocument = gql`
    mutation UpdateProgram($programData: UpdateProgramInput!) {
  updateProgram(programData: $programData) {
    program {
      id
      name
      startDate
      endDate
      status
      caId
      description
      budget
      frequencyOfPayments
      cashPlus
      populationGoal
      scope
      sector
      totalNumberOfHouseholds
      administrativeAreasOfImplementation
      individualDataNeeded
    }
  }
}
    `;
export type UpdateProgramMutationFn = ApolloReactCommon.MutationFunction<UpdateProgramMutation, UpdateProgramMutationVariables>;
export type UpdateProgramComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UpdateProgramMutation, UpdateProgramMutationVariables>, 'mutation'>;

    export const UpdateProgramComponent = (props: UpdateProgramComponentProps) => (
      <ApolloReactComponents.Mutation<UpdateProgramMutation, UpdateProgramMutationVariables> mutation={UpdateProgramDocument} {...props} />
    );
    
export type UpdateProgramProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UpdateProgramMutation, UpdateProgramMutationVariables> & TChildProps;
export function withUpdateProgram<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UpdateProgramMutation,
  UpdateProgramMutationVariables,
  UpdateProgramProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UpdateProgramMutation, UpdateProgramMutationVariables, UpdateProgramProps<TChildProps>>(UpdateProgramDocument, {
      alias: 'updateProgram',
      ...operationOptions
    });
};

/**
 * __useUpdateProgramMutation__
 *
 * To run a mutation, you first call `useUpdateProgramMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateProgramMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateProgramMutation, { data, loading, error }] = useUpdateProgramMutation({
 *   variables: {
 *      programData: // value for 'programData'
 *   },
 * });
 */
export function useUpdateProgramMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UpdateProgramMutation, UpdateProgramMutationVariables>) {
        return ApolloReactHooks.useMutation<UpdateProgramMutation, UpdateProgramMutationVariables>(UpdateProgramDocument, baseOptions);
      }
export type UpdateProgramMutationHookResult = ReturnType<typeof useUpdateProgramMutation>;
export type UpdateProgramMutationResult = ApolloReactCommon.MutationResult<UpdateProgramMutation>;
export type UpdateProgramMutationOptions = ApolloReactCommon.BaseMutationOptions<UpdateProgramMutation, UpdateProgramMutationVariables>;
export const UpdateTpDocument = gql`
    mutation UpdateTP($input: UpdateTargetPopulationInput!) {
  updateTargetPopulation(input: $input) {
    targetPopulation {
      ...targetPopulationDetailed
    }
  }
}
    ${TargetPopulationDetailedFragmentDoc}`;
export type UpdateTpMutationFn = ApolloReactCommon.MutationFunction<UpdateTpMutation, UpdateTpMutationVariables>;
export type UpdateTpComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UpdateTpMutation, UpdateTpMutationVariables>, 'mutation'>;

    export const UpdateTpComponent = (props: UpdateTpComponentProps) => (
      <ApolloReactComponents.Mutation<UpdateTpMutation, UpdateTpMutationVariables> mutation={UpdateTpDocument} {...props} />
    );
    
export type UpdateTpProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UpdateTpMutation, UpdateTpMutationVariables> & TChildProps;
export function withUpdateTp<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UpdateTpMutation,
  UpdateTpMutationVariables,
  UpdateTpProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UpdateTpMutation, UpdateTpMutationVariables, UpdateTpProps<TChildProps>>(UpdateTpDocument, {
      alias: 'updateTp',
      ...operationOptions
    });
};

/**
 * __useUpdateTpMutation__
 *
 * To run a mutation, you first call `useUpdateTpMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUpdateTpMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [updateTpMutation, { data, loading, error }] = useUpdateTpMutation({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useUpdateTpMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UpdateTpMutation, UpdateTpMutationVariables>) {
        return ApolloReactHooks.useMutation<UpdateTpMutation, UpdateTpMutationVariables>(UpdateTpDocument, baseOptions);
      }
export type UpdateTpMutationHookResult = ReturnType<typeof useUpdateTpMutation>;
export type UpdateTpMutationResult = ApolloReactCommon.MutationResult<UpdateTpMutation>;
export type UpdateTpMutationOptions = ApolloReactCommon.BaseMutationOptions<UpdateTpMutation, UpdateTpMutationVariables>;
export const CashPlanVerificationStatusChoicesDocument = gql`
    query cashPlanVerificationStatusChoices {
  cashPlanVerificationStatusChoices {
    name
    value
  }
  paymentRecordDeliveryTypeChoices {
    name
    value
  }
}
    `;
export type CashPlanVerificationStatusChoicesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables>, 'query'>;

    export const CashPlanVerificationStatusChoicesComponent = (props: CashPlanVerificationStatusChoicesComponentProps) => (
      <ApolloReactComponents.Query<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables> query={CashPlanVerificationStatusChoicesDocument} {...props} />
    );
    
export type CashPlanVerificationStatusChoicesProps<TChildProps = {}> = ApolloReactHoc.DataProps<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables> & TChildProps;
export function withCashPlanVerificationStatusChoices<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CashPlanVerificationStatusChoicesQuery,
  CashPlanVerificationStatusChoicesQueryVariables,
  CashPlanVerificationStatusChoicesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables, CashPlanVerificationStatusChoicesProps<TChildProps>>(CashPlanVerificationStatusChoicesDocument, {
      alias: 'cashPlanVerificationStatusChoices',
      ...operationOptions
    });
};

/**
 * __useCashPlanVerificationStatusChoicesQuery__
 *
 * To run a query within a React component, call `useCashPlanVerificationStatusChoicesQuery` and pass it any options that fit your needs.
 * When your component renders, `useCashPlanVerificationStatusChoicesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCashPlanVerificationStatusChoicesQuery({
 *   variables: {
 *   },
 * });
 */
export function useCashPlanVerificationStatusChoicesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables>) {
        return ApolloReactHooks.useQuery<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables>(CashPlanVerificationStatusChoicesDocument, baseOptions);
      }
export function useCashPlanVerificationStatusChoicesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables>(CashPlanVerificationStatusChoicesDocument, baseOptions);
        }
export type CashPlanVerificationStatusChoicesQueryHookResult = ReturnType<typeof useCashPlanVerificationStatusChoicesQuery>;
export type CashPlanVerificationStatusChoicesLazyQueryHookResult = ReturnType<typeof useCashPlanVerificationStatusChoicesLazyQuery>;
export type CashPlanVerificationStatusChoicesQueryResult = ApolloReactCommon.QueryResult<CashPlanVerificationStatusChoicesQuery, CashPlanVerificationStatusChoicesQueryVariables>;
export const PaymentVerificationStatusChoicesDocument = gql`
    query paymentVerificationStatusChoices {
  paymentVerificationStatusChoices {
    name
    value
  }
}
    `;
export type PaymentVerificationStatusChoicesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables>, 'query'>;

    export const PaymentVerificationStatusChoicesComponent = (props: PaymentVerificationStatusChoicesComponentProps) => (
      <ApolloReactComponents.Query<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables> query={PaymentVerificationStatusChoicesDocument} {...props} />
    );
    
export type PaymentVerificationStatusChoicesProps<TChildProps = {}> = ApolloReactHoc.DataProps<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables> & TChildProps;
export function withPaymentVerificationStatusChoices<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  PaymentVerificationStatusChoicesQuery,
  PaymentVerificationStatusChoicesQueryVariables,
  PaymentVerificationStatusChoicesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables, PaymentVerificationStatusChoicesProps<TChildProps>>(PaymentVerificationStatusChoicesDocument, {
      alias: 'paymentVerificationStatusChoices',
      ...operationOptions
    });
};

/**
 * __usePaymentVerificationStatusChoicesQuery__
 *
 * To run a query within a React component, call `usePaymentVerificationStatusChoicesQuery` and pass it any options that fit your needs.
 * When your component renders, `usePaymentVerificationStatusChoicesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePaymentVerificationStatusChoicesQuery({
 *   variables: {
 *   },
 * });
 */
export function usePaymentVerificationStatusChoicesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables>) {
        return ApolloReactHooks.useQuery<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables>(PaymentVerificationStatusChoicesDocument, baseOptions);
      }
export function usePaymentVerificationStatusChoicesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables>(PaymentVerificationStatusChoicesDocument, baseOptions);
        }
export type PaymentVerificationStatusChoicesQueryHookResult = ReturnType<typeof usePaymentVerificationStatusChoicesQuery>;
export type PaymentVerificationStatusChoicesLazyQueryHookResult = ReturnType<typeof usePaymentVerificationStatusChoicesLazyQuery>;
export type PaymentVerificationStatusChoicesQueryResult = ApolloReactCommon.QueryResult<PaymentVerificationStatusChoicesQuery, PaymentVerificationStatusChoicesQueryVariables>;
export const CashPlanVerificationSamplingChoicesDocument = gql`
    query cashPlanVerificationSamplingChoices {
  cashPlanVerificationSamplingChoices {
    name
    value
  }
}
    `;
export type CashPlanVerificationSamplingChoicesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables>, 'query'>;

    export const CashPlanVerificationSamplingChoicesComponent = (props: CashPlanVerificationSamplingChoicesComponentProps) => (
      <ApolloReactComponents.Query<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables> query={CashPlanVerificationSamplingChoicesDocument} {...props} />
    );
    
export type CashPlanVerificationSamplingChoicesProps<TChildProps = {}> = ApolloReactHoc.DataProps<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables> & TChildProps;
export function withCashPlanVerificationSamplingChoices<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CashPlanVerificationSamplingChoicesQuery,
  CashPlanVerificationSamplingChoicesQueryVariables,
  CashPlanVerificationSamplingChoicesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables, CashPlanVerificationSamplingChoicesProps<TChildProps>>(CashPlanVerificationSamplingChoicesDocument, {
      alias: 'cashPlanVerificationSamplingChoices',
      ...operationOptions
    });
};

/**
 * __useCashPlanVerificationSamplingChoicesQuery__
 *
 * To run a query within a React component, call `useCashPlanVerificationSamplingChoicesQuery` and pass it any options that fit your needs.
 * When your component renders, `useCashPlanVerificationSamplingChoicesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCashPlanVerificationSamplingChoicesQuery({
 *   variables: {
 *   },
 * });
 */
export function useCashPlanVerificationSamplingChoicesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables>) {
        return ApolloReactHooks.useQuery<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables>(CashPlanVerificationSamplingChoicesDocument, baseOptions);
      }
export function useCashPlanVerificationSamplingChoicesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables>(CashPlanVerificationSamplingChoicesDocument, baseOptions);
        }
export type CashPlanVerificationSamplingChoicesQueryHookResult = ReturnType<typeof useCashPlanVerificationSamplingChoicesQuery>;
export type CashPlanVerificationSamplingChoicesLazyQueryHookResult = ReturnType<typeof useCashPlanVerificationSamplingChoicesLazyQuery>;
export type CashPlanVerificationSamplingChoicesQueryResult = ApolloReactCommon.QueryResult<CashPlanVerificationSamplingChoicesQuery, CashPlanVerificationSamplingChoicesQueryVariables>;
export const AllAdminAreasDocument = gql`
    query AllAdminAreas($title: String, $businessArea: String, $first: Int) {
  allAdminAreas(title_Icontains: $title, businessArea: $businessArea, first: $first) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      startCursor
    }
    edges {
      node {
        id
        title
      }
    }
  }
}
    `;
export type AllAdminAreasComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllAdminAreasQuery, AllAdminAreasQueryVariables>, 'query'>;

    export const AllAdminAreasComponent = (props: AllAdminAreasComponentProps) => (
      <ApolloReactComponents.Query<AllAdminAreasQuery, AllAdminAreasQueryVariables> query={AllAdminAreasDocument} {...props} />
    );
    
export type AllAdminAreasProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllAdminAreasQuery, AllAdminAreasQueryVariables> & TChildProps;
export function withAllAdminAreas<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllAdminAreasQuery,
  AllAdminAreasQueryVariables,
  AllAdminAreasProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllAdminAreasQuery, AllAdminAreasQueryVariables, AllAdminAreasProps<TChildProps>>(AllAdminAreasDocument, {
      alias: 'allAdminAreas',
      ...operationOptions
    });
};

/**
 * __useAllAdminAreasQuery__
 *
 * To run a query within a React component, call `useAllAdminAreasQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllAdminAreasQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllAdminAreasQuery({
 *   variables: {
 *      title: // value for 'title'
 *      businessArea: // value for 'businessArea'
 *      first: // value for 'first'
 *   },
 * });
 */
export function useAllAdminAreasQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllAdminAreasQuery, AllAdminAreasQueryVariables>) {
        return ApolloReactHooks.useQuery<AllAdminAreasQuery, AllAdminAreasQueryVariables>(AllAdminAreasDocument, baseOptions);
      }
export function useAllAdminAreasLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllAdminAreasQuery, AllAdminAreasQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllAdminAreasQuery, AllAdminAreasQueryVariables>(AllAdminAreasDocument, baseOptions);
        }
export type AllAdminAreasQueryHookResult = ReturnType<typeof useAllAdminAreasQuery>;
export type AllAdminAreasLazyQueryHookResult = ReturnType<typeof useAllAdminAreasLazyQuery>;
export type AllAdminAreasQueryResult = ApolloReactCommon.QueryResult<AllAdminAreasQuery, AllAdminAreasQueryVariables>;
export const AllBusinessAreasDocument = gql`
    query AllBusinessAreas {
  allBusinessAreas {
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      startCursor
    }
    edges {
      node {
        id
        name
        slug
      }
    }
  }
}
    `;
export type AllBusinessAreasComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllBusinessAreasQuery, AllBusinessAreasQueryVariables>, 'query'>;

    export const AllBusinessAreasComponent = (props: AllBusinessAreasComponentProps) => (
      <ApolloReactComponents.Query<AllBusinessAreasQuery, AllBusinessAreasQueryVariables> query={AllBusinessAreasDocument} {...props} />
    );
    
export type AllBusinessAreasProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllBusinessAreasQuery, AllBusinessAreasQueryVariables> & TChildProps;
export function withAllBusinessAreas<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllBusinessAreasQuery,
  AllBusinessAreasQueryVariables,
  AllBusinessAreasProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllBusinessAreasQuery, AllBusinessAreasQueryVariables, AllBusinessAreasProps<TChildProps>>(AllBusinessAreasDocument, {
      alias: 'allBusinessAreas',
      ...operationOptions
    });
};

/**
 * __useAllBusinessAreasQuery__
 *
 * To run a query within a React component, call `useAllBusinessAreasQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllBusinessAreasQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllBusinessAreasQuery({
 *   variables: {
 *   },
 * });
 */
export function useAllBusinessAreasQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllBusinessAreasQuery, AllBusinessAreasQueryVariables>) {
        return ApolloReactHooks.useQuery<AllBusinessAreasQuery, AllBusinessAreasQueryVariables>(AllBusinessAreasDocument, baseOptions);
      }
export function useAllBusinessAreasLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllBusinessAreasQuery, AllBusinessAreasQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllBusinessAreasQuery, AllBusinessAreasQueryVariables>(AllBusinessAreasDocument, baseOptions);
        }
export type AllBusinessAreasQueryHookResult = ReturnType<typeof useAllBusinessAreasQuery>;
export type AllBusinessAreasLazyQueryHookResult = ReturnType<typeof useAllBusinessAreasLazyQuery>;
export type AllBusinessAreasQueryResult = ApolloReactCommon.QueryResult<AllBusinessAreasQuery, AllBusinessAreasQueryVariables>;
export const AllCashPlansDocument = gql`
    query AllCashPlans($program: ID, $after: String, $before: String, $first: Int, $last: Int, $orderBy: String, $search: String, $assistanceThrough: String, $deliveryType: [String], $verificationStatus: [String], $startDateGte: DateTime, $endDateLte: DateTime) {
  allCashPlans(program: $program, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy, search: $search, assistanceThrough_Icontains: $assistanceThrough, deliveryType: $deliveryType, verificationStatus: $verificationStatus, startDate_Gte: $startDateGte, endDate_Lte: $endDateLte) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        id
        caId
        verificationStatus
        assistanceThrough
        deliveryType
        startDate
        endDate
        program {
          id
          name
        }
        totalPersonsCovered
        dispersionDate
        assistanceMeasurement
        status
        totalEntitledQuantity
        totalDeliveredQuantity
        totalUndeliveredQuantity
        assistanceMeasurement
        updatedAt
      }
    }
  }
}
    `;
export type AllCashPlansComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllCashPlansQuery, AllCashPlansQueryVariables>, 'query'>;

    export const AllCashPlansComponent = (props: AllCashPlansComponentProps) => (
      <ApolloReactComponents.Query<AllCashPlansQuery, AllCashPlansQueryVariables> query={AllCashPlansDocument} {...props} />
    );
    
export type AllCashPlansProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllCashPlansQuery, AllCashPlansQueryVariables> & TChildProps;
export function withAllCashPlans<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllCashPlansQuery,
  AllCashPlansQueryVariables,
  AllCashPlansProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllCashPlansQuery, AllCashPlansQueryVariables, AllCashPlansProps<TChildProps>>(AllCashPlansDocument, {
      alias: 'allCashPlans',
      ...operationOptions
    });
};

/**
 * __useAllCashPlansQuery__
 *
 * To run a query within a React component, call `useAllCashPlansQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllCashPlansQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllCashPlansQuery({
 *   variables: {
 *      program: // value for 'program'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *      search: // value for 'search'
 *      assistanceThrough: // value for 'assistanceThrough'
 *      deliveryType: // value for 'deliveryType'
 *      verificationStatus: // value for 'verificationStatus'
 *      startDateGte: // value for 'startDateGte'
 *      endDateLte: // value for 'endDateLte'
 *   },
 * });
 */
export function useAllCashPlansQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllCashPlansQuery, AllCashPlansQueryVariables>) {
        return ApolloReactHooks.useQuery<AllCashPlansQuery, AllCashPlansQueryVariables>(AllCashPlansDocument, baseOptions);
      }
export function useAllCashPlansLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllCashPlansQuery, AllCashPlansQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllCashPlansQuery, AllCashPlansQueryVariables>(AllCashPlansDocument, baseOptions);
        }
export type AllCashPlansQueryHookResult = ReturnType<typeof useAllCashPlansQuery>;
export type AllCashPlansLazyQueryHookResult = ReturnType<typeof useAllCashPlansLazyQuery>;
export type AllCashPlansQueryResult = ApolloReactCommon.QueryResult<AllCashPlansQuery, AllCashPlansQueryVariables>;
export const AllGrievanceTicketDocument = gql`
    query AllGrievanceTicket($before: String, $after: String, $first: Int, $last: Int, $id: UUID, $category: String, $businessArea: String!, $search: String, $status: [String], $fsp: [ID], $createdAtRange: String, $admin: [ID], $orderBy: String) {
  allGrievanceTicket(before: $before, after: $after, first: $first, last: $last, id: $id, category: $category, businessArea: $businessArea, search: $search, status: $status, fsp: $fsp, createdAtRange: $createdAtRange, orderBy: $orderBy, admin: $admin) {
    totalCount
    pageInfo {
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        id
        status
        assignedTo {
          id
          firstName
          lastName
        }
        category
        createdAt
        userModified
      }
    }
  }
}
    `;
export type AllGrievanceTicketComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables>, 'query'> & ({ variables: AllGrievanceTicketQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const AllGrievanceTicketComponent = (props: AllGrievanceTicketComponentProps) => (
      <ApolloReactComponents.Query<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables> query={AllGrievanceTicketDocument} {...props} />
    );
    
export type AllGrievanceTicketProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables> & TChildProps;
export function withAllGrievanceTicket<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllGrievanceTicketQuery,
  AllGrievanceTicketQueryVariables,
  AllGrievanceTicketProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables, AllGrievanceTicketProps<TChildProps>>(AllGrievanceTicketDocument, {
      alias: 'allGrievanceTicket',
      ...operationOptions
    });
};

/**
 * __useAllGrievanceTicketQuery__
 *
 * To run a query within a React component, call `useAllGrievanceTicketQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllGrievanceTicketQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllGrievanceTicketQuery({
 *   variables: {
 *      before: // value for 'before'
 *      after: // value for 'after'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      id: // value for 'id'
 *      category: // value for 'category'
 *      businessArea: // value for 'businessArea'
 *      search: // value for 'search'
 *      status: // value for 'status'
 *      fsp: // value for 'fsp'
 *      createdAtRange: // value for 'createdAtRange'
 *      admin: // value for 'admin'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useAllGrievanceTicketQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables>) {
        return ApolloReactHooks.useQuery<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables>(AllGrievanceTicketDocument, baseOptions);
      }
export function useAllGrievanceTicketLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables>(AllGrievanceTicketDocument, baseOptions);
        }
export type AllGrievanceTicketQueryHookResult = ReturnType<typeof useAllGrievanceTicketQuery>;
export type AllGrievanceTicketLazyQueryHookResult = ReturnType<typeof useAllGrievanceTicketLazyQuery>;
export type AllGrievanceTicketQueryResult = ApolloReactCommon.QueryResult<AllGrievanceTicketQuery, AllGrievanceTicketQueryVariables>;
export const AllHouseholdsDocument = gql`
    query AllHouseholds($after: String, $before: String, $first: Int, $last: Int, $businessArea: String, $orderBy: String, $familySize: String, $programs: [ID], $headOfHouseholdFullNameIcontains: String, $adminArea: ID, $search: String, $residenceStatus: String, $lastRegistrationDate: String, $admin2: [ID]) {
  allHouseholds(after: $after, before: $before, first: $first, last: $last, businessArea: $businessArea, size: $familySize, orderBy: $orderBy, programs: $programs, headOfHousehold_FullName_Icontains: $headOfHouseholdFullNameIcontains, adminArea: $adminArea, search: $search, residenceStatus: $residenceStatus, lastRegistrationDate: $lastRegistrationDate, admin2: $admin2) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        ...householdMinimal
      }
    }
  }
}
    ${HouseholdMinimalFragmentDoc}`;
export type AllHouseholdsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllHouseholdsQuery, AllHouseholdsQueryVariables>, 'query'>;

    export const AllHouseholdsComponent = (props: AllHouseholdsComponentProps) => (
      <ApolloReactComponents.Query<AllHouseholdsQuery, AllHouseholdsQueryVariables> query={AllHouseholdsDocument} {...props} />
    );
    
export type AllHouseholdsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllHouseholdsQuery, AllHouseholdsQueryVariables> & TChildProps;
export function withAllHouseholds<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllHouseholdsQuery,
  AllHouseholdsQueryVariables,
  AllHouseholdsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllHouseholdsQuery, AllHouseholdsQueryVariables, AllHouseholdsProps<TChildProps>>(AllHouseholdsDocument, {
      alias: 'allHouseholds',
      ...operationOptions
    });
};

/**
 * __useAllHouseholdsQuery__
 *
 * To run a query within a React component, call `useAllHouseholdsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllHouseholdsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllHouseholdsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      businessArea: // value for 'businessArea'
 *      orderBy: // value for 'orderBy'
 *      familySize: // value for 'familySize'
 *      programs: // value for 'programs'
 *      headOfHouseholdFullNameIcontains: // value for 'headOfHouseholdFullNameIcontains'
 *      adminArea: // value for 'adminArea'
 *      search: // value for 'search'
 *      residenceStatus: // value for 'residenceStatus'
 *      lastRegistrationDate: // value for 'lastRegistrationDate'
 *      admin2: // value for 'admin2'
 *   },
 * });
 */
export function useAllHouseholdsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllHouseholdsQuery, AllHouseholdsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllHouseholdsQuery, AllHouseholdsQueryVariables>(AllHouseholdsDocument, baseOptions);
      }
export function useAllHouseholdsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllHouseholdsQuery, AllHouseholdsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllHouseholdsQuery, AllHouseholdsQueryVariables>(AllHouseholdsDocument, baseOptions);
        }
export type AllHouseholdsQueryHookResult = ReturnType<typeof useAllHouseholdsQuery>;
export type AllHouseholdsLazyQueryHookResult = ReturnType<typeof useAllHouseholdsLazyQuery>;
export type AllHouseholdsQueryResult = ApolloReactCommon.QueryResult<AllHouseholdsQuery, AllHouseholdsQueryVariables>;
export const AllIndividualsDocument = gql`
    query AllIndividuals($before: String, $after: String, $first: Int, $last: Int, $fullNameContains: String, $sex: [String], $age: String, $orderBy: String, $search: String, $programme: String, $status: [String], $lastRegistrationDate: String, $householdId: UUID) {
  allIndividuals(before: $before, after: $after, first: $first, last: $last, fullName_Icontains: $fullNameContains, sex: $sex, age: $age, orderBy: $orderBy, search: $search, programme: $programme, status: $status, lastRegistrationDate: $lastRegistrationDate, household_Id: $householdId) {
    totalCount
    pageInfo {
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        ...individualMinimal
      }
    }
  }
}
    ${IndividualMinimalFragmentDoc}`;
export type AllIndividualsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllIndividualsQuery, AllIndividualsQueryVariables>, 'query'>;

    export const AllIndividualsComponent = (props: AllIndividualsComponentProps) => (
      <ApolloReactComponents.Query<AllIndividualsQuery, AllIndividualsQueryVariables> query={AllIndividualsDocument} {...props} />
    );
    
export type AllIndividualsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllIndividualsQuery, AllIndividualsQueryVariables> & TChildProps;
export function withAllIndividuals<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllIndividualsQuery,
  AllIndividualsQueryVariables,
  AllIndividualsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllIndividualsQuery, AllIndividualsQueryVariables, AllIndividualsProps<TChildProps>>(AllIndividualsDocument, {
      alias: 'allIndividuals',
      ...operationOptions
    });
};

/**
 * __useAllIndividualsQuery__
 *
 * To run a query within a React component, call `useAllIndividualsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllIndividualsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllIndividualsQuery({
 *   variables: {
 *      before: // value for 'before'
 *      after: // value for 'after'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      fullNameContains: // value for 'fullNameContains'
 *      sex: // value for 'sex'
 *      age: // value for 'age'
 *      orderBy: // value for 'orderBy'
 *      search: // value for 'search'
 *      programme: // value for 'programme'
 *      status: // value for 'status'
 *      lastRegistrationDate: // value for 'lastRegistrationDate'
 *      householdId: // value for 'householdId'
 *   },
 * });
 */
export function useAllIndividualsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllIndividualsQuery, AllIndividualsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllIndividualsQuery, AllIndividualsQueryVariables>(AllIndividualsDocument, baseOptions);
      }
export function useAllIndividualsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllIndividualsQuery, AllIndividualsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllIndividualsQuery, AllIndividualsQueryVariables>(AllIndividualsDocument, baseOptions);
        }
export type AllIndividualsQueryHookResult = ReturnType<typeof useAllIndividualsQuery>;
export type AllIndividualsLazyQueryHookResult = ReturnType<typeof useAllIndividualsLazyQuery>;
export type AllIndividualsQueryResult = ApolloReactCommon.QueryResult<AllIndividualsQuery, AllIndividualsQueryVariables>;
export const AllLogEntriesDocument = gql`
    query AllLogEntries($objectId: String!, $after: String, $before: String, $first: Int, $last: Int) {
  allLogEntries(after: $after, before: $before, first: $first, last: $last, objectId: $objectId) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        id
        action
        changesDisplayDict
        timestamp
        actor {
          id
          firstName
          lastName
        }
      }
    }
  }
}
    `;
export type AllLogEntriesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllLogEntriesQuery, AllLogEntriesQueryVariables>, 'query'> & ({ variables: AllLogEntriesQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const AllLogEntriesComponent = (props: AllLogEntriesComponentProps) => (
      <ApolloReactComponents.Query<AllLogEntriesQuery, AllLogEntriesQueryVariables> query={AllLogEntriesDocument} {...props} />
    );
    
export type AllLogEntriesProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllLogEntriesQuery, AllLogEntriesQueryVariables> & TChildProps;
export function withAllLogEntries<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllLogEntriesQuery,
  AllLogEntriesQueryVariables,
  AllLogEntriesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllLogEntriesQuery, AllLogEntriesQueryVariables, AllLogEntriesProps<TChildProps>>(AllLogEntriesDocument, {
      alias: 'allLogEntries',
      ...operationOptions
    });
};

/**
 * __useAllLogEntriesQuery__
 *
 * To run a query within a React component, call `useAllLogEntriesQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllLogEntriesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllLogEntriesQuery({
 *   variables: {
 *      objectId: // value for 'objectId'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *   },
 * });
 */
export function useAllLogEntriesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllLogEntriesQuery, AllLogEntriesQueryVariables>) {
        return ApolloReactHooks.useQuery<AllLogEntriesQuery, AllLogEntriesQueryVariables>(AllLogEntriesDocument, baseOptions);
      }
export function useAllLogEntriesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllLogEntriesQuery, AllLogEntriesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllLogEntriesQuery, AllLogEntriesQueryVariables>(AllLogEntriesDocument, baseOptions);
        }
export type AllLogEntriesQueryHookResult = ReturnType<typeof useAllLogEntriesQuery>;
export type AllLogEntriesLazyQueryHookResult = ReturnType<typeof useAllLogEntriesLazyQuery>;
export type AllLogEntriesQueryResult = ApolloReactCommon.QueryResult<AllLogEntriesQuery, AllLogEntriesQueryVariables>;
export const AllPaymentRecordsDocument = gql`
    query AllPaymentRecords($cashPlan: ID, $household: ID, $after: String, $before: String, $orderBy: String, $first: Int, $last: Int) {
  allPaymentRecords(cashPlan: $cashPlan, household: $household, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        id
        createdAt
        updatedAt
        fullName
        statusDate
        status
        caId
        totalPersonsCovered
        household {
          id
          size
        }
        entitlementQuantity
        deliveredQuantity
        deliveryDate
        cashPlan {
          id
          program {
            id
            name
          }
        }
      }
    }
    totalCount
    edgeCount
  }
}
    `;
export type AllPaymentRecordsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>, 'query'>;

    export const AllPaymentRecordsComponent = (props: AllPaymentRecordsComponentProps) => (
      <ApolloReactComponents.Query<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables> query={AllPaymentRecordsDocument} {...props} />
    );
    
export type AllPaymentRecordsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables> & TChildProps;
export function withAllPaymentRecords<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllPaymentRecordsQuery,
  AllPaymentRecordsQueryVariables,
  AllPaymentRecordsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables, AllPaymentRecordsProps<TChildProps>>(AllPaymentRecordsDocument, {
      alias: 'allPaymentRecords',
      ...operationOptions
    });
};

/**
 * __useAllPaymentRecordsQuery__
 *
 * To run a query within a React component, call `useAllPaymentRecordsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllPaymentRecordsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllPaymentRecordsQuery({
 *   variables: {
 *      cashPlan: // value for 'cashPlan'
 *      household: // value for 'household'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      orderBy: // value for 'orderBy'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *   },
 * });
 */
export function useAllPaymentRecordsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>(AllPaymentRecordsDocument, baseOptions);
      }
export function useAllPaymentRecordsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>(AllPaymentRecordsDocument, baseOptions);
        }
export type AllPaymentRecordsQueryHookResult = ReturnType<typeof useAllPaymentRecordsQuery>;
export type AllPaymentRecordsLazyQueryHookResult = ReturnType<typeof useAllPaymentRecordsLazyQuery>;
export type AllPaymentRecordsQueryResult = ApolloReactCommon.QueryResult<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>;
export const AllPaymentVerificationsDocument = gql`
    query AllPaymentVerifications($after: String, $before: String, $first: Int, $last: Int, $orderBy: String, $cashPlanPaymentVerification: ID, $search: String, $status: String) {
  allPaymentVerifications(after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy, cashPlanPaymentVerification: $cashPlanPaymentVerification, search: $search, status: $status) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        id
        paymentRecord {
          id
          deliveredQuantity
          household {
            unicefId
            id
            headOfHousehold {
              id
              fullName
              phoneNo
              phoneNoAlternative
            }
          }
        }
        status
        receivedAmount
      }
    }
  }
}
    `;
export type AllPaymentVerificationsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables>, 'query'>;

    export const AllPaymentVerificationsComponent = (props: AllPaymentVerificationsComponentProps) => (
      <ApolloReactComponents.Query<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables> query={AllPaymentVerificationsDocument} {...props} />
    );
    
export type AllPaymentVerificationsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables> & TChildProps;
export function withAllPaymentVerifications<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllPaymentVerificationsQuery,
  AllPaymentVerificationsQueryVariables,
  AllPaymentVerificationsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables, AllPaymentVerificationsProps<TChildProps>>(AllPaymentVerificationsDocument, {
      alias: 'allPaymentVerifications',
      ...operationOptions
    });
};

/**
 * __useAllPaymentVerificationsQuery__
 *
 * To run a query within a React component, call `useAllPaymentVerificationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllPaymentVerificationsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllPaymentVerificationsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *      cashPlanPaymentVerification: // value for 'cashPlanPaymentVerification'
 *      search: // value for 'search'
 *      status: // value for 'status'
 *   },
 * });
 */
export function useAllPaymentVerificationsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables>(AllPaymentVerificationsDocument, baseOptions);
      }
export function useAllPaymentVerificationsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables>(AllPaymentVerificationsDocument, baseOptions);
        }
export type AllPaymentVerificationsQueryHookResult = ReturnType<typeof useAllPaymentVerificationsQuery>;
export type AllPaymentVerificationsLazyQueryHookResult = ReturnType<typeof useAllPaymentVerificationsLazyQuery>;
export type AllPaymentVerificationsQueryResult = ApolloReactCommon.QueryResult<AllPaymentVerificationsQuery, AllPaymentVerificationsQueryVariables>;
export const AllProgramsDocument = gql`
    query AllPrograms($before: String, $after: String, $first: Int, $last: Int, $status: [String], $sector: [String], $businessArea: String!, $search: String, $numberOfHouseholds: String, $budget: String, $startDate: Date, $endDate: Date, $orderBy: String) {
  allPrograms(before: $before, after: $after, first: $first, last: $last, status: $status, sector: $sector, businessArea: $businessArea, search: $search, numberOfHouseholds: $numberOfHouseholds, budget: $budget, orderBy: $orderBy, startDate: $startDate, endDate: $endDate) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      startCursor
    }
    totalCount
    edgeCount
    edges {
      cursor
      node {
        id
        name
        startDate
        endDate
        status
        caId
        description
        budget
        frequencyOfPayments
        populationGoal
        sector
        totalNumberOfHouseholds
        individualDataNeeded
      }
    }
  }
}
    `;
export type AllProgramsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllProgramsQuery, AllProgramsQueryVariables>, 'query'> & ({ variables: AllProgramsQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const AllProgramsComponent = (props: AllProgramsComponentProps) => (
      <ApolloReactComponents.Query<AllProgramsQuery, AllProgramsQueryVariables> query={AllProgramsDocument} {...props} />
    );
    
export type AllProgramsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllProgramsQuery, AllProgramsQueryVariables> & TChildProps;
export function withAllPrograms<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllProgramsQuery,
  AllProgramsQueryVariables,
  AllProgramsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllProgramsQuery, AllProgramsQueryVariables, AllProgramsProps<TChildProps>>(AllProgramsDocument, {
      alias: 'allPrograms',
      ...operationOptions
    });
};

/**
 * __useAllProgramsQuery__
 *
 * To run a query within a React component, call `useAllProgramsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllProgramsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllProgramsQuery({
 *   variables: {
 *      before: // value for 'before'
 *      after: // value for 'after'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      status: // value for 'status'
 *      sector: // value for 'sector'
 *      businessArea: // value for 'businessArea'
 *      search: // value for 'search'
 *      numberOfHouseholds: // value for 'numberOfHouseholds'
 *      budget: // value for 'budget'
 *      startDate: // value for 'startDate'
 *      endDate: // value for 'endDate'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useAllProgramsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllProgramsQuery, AllProgramsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllProgramsQuery, AllProgramsQueryVariables>(AllProgramsDocument, baseOptions);
      }
export function useAllProgramsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllProgramsQuery, AllProgramsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllProgramsQuery, AllProgramsQueryVariables>(AllProgramsDocument, baseOptions);
        }
export type AllProgramsQueryHookResult = ReturnType<typeof useAllProgramsQuery>;
export type AllProgramsLazyQueryHookResult = ReturnType<typeof useAllProgramsLazyQuery>;
export type AllProgramsQueryResult = ApolloReactCommon.QueryResult<AllProgramsQuery, AllProgramsQueryVariables>;
export const AllRapidProFlowsDocument = gql`
    query AllRapidProFlows($businessAreaSlug: String!) {
  allRapidProFlows(businessAreaSlug: $businessAreaSlug) {
    id
    name
  }
}
    `;
export type AllRapidProFlowsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables>, 'query'> & ({ variables: AllRapidProFlowsQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const AllRapidProFlowsComponent = (props: AllRapidProFlowsComponentProps) => (
      <ApolloReactComponents.Query<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables> query={AllRapidProFlowsDocument} {...props} />
    );
    
export type AllRapidProFlowsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables> & TChildProps;
export function withAllRapidProFlows<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllRapidProFlowsQuery,
  AllRapidProFlowsQueryVariables,
  AllRapidProFlowsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables, AllRapidProFlowsProps<TChildProps>>(AllRapidProFlowsDocument, {
      alias: 'allRapidProFlows',
      ...operationOptions
    });
};

/**
 * __useAllRapidProFlowsQuery__
 *
 * To run a query within a React component, call `useAllRapidProFlowsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllRapidProFlowsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllRapidProFlowsQuery({
 *   variables: {
 *      businessAreaSlug: // value for 'businessAreaSlug'
 *   },
 * });
 */
export function useAllRapidProFlowsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables>(AllRapidProFlowsDocument, baseOptions);
      }
export function useAllRapidProFlowsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables>(AllRapidProFlowsDocument, baseOptions);
        }
export type AllRapidProFlowsQueryHookResult = ReturnType<typeof useAllRapidProFlowsQuery>;
export type AllRapidProFlowsLazyQueryHookResult = ReturnType<typeof useAllRapidProFlowsLazyQuery>;
export type AllRapidProFlowsQueryResult = ApolloReactCommon.QueryResult<AllRapidProFlowsQuery, AllRapidProFlowsQueryVariables>;
export const AllSteficonRulesDocument = gql`
    query AllSteficonRules {
  allSteficonRules {
    edges {
      node {
        id
        name
      }
    }
  }
}
    `;
export type AllSteficonRulesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllSteficonRulesQuery, AllSteficonRulesQueryVariables>, 'query'>;

    export const AllSteficonRulesComponent = (props: AllSteficonRulesComponentProps) => (
      <ApolloReactComponents.Query<AllSteficonRulesQuery, AllSteficonRulesQueryVariables> query={AllSteficonRulesDocument} {...props} />
    );
    
export type AllSteficonRulesProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllSteficonRulesQuery, AllSteficonRulesQueryVariables> & TChildProps;
export function withAllSteficonRules<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllSteficonRulesQuery,
  AllSteficonRulesQueryVariables,
  AllSteficonRulesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllSteficonRulesQuery, AllSteficonRulesQueryVariables, AllSteficonRulesProps<TChildProps>>(AllSteficonRulesDocument, {
      alias: 'allSteficonRules',
      ...operationOptions
    });
};

/**
 * __useAllSteficonRulesQuery__
 *
 * To run a query within a React component, call `useAllSteficonRulesQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllSteficonRulesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllSteficonRulesQuery({
 *   variables: {
 *   },
 * });
 */
export function useAllSteficonRulesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllSteficonRulesQuery, AllSteficonRulesQueryVariables>) {
        return ApolloReactHooks.useQuery<AllSteficonRulesQuery, AllSteficonRulesQueryVariables>(AllSteficonRulesDocument, baseOptions);
      }
export function useAllSteficonRulesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllSteficonRulesQuery, AllSteficonRulesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllSteficonRulesQuery, AllSteficonRulesQueryVariables>(AllSteficonRulesDocument, baseOptions);
        }
export type AllSteficonRulesQueryHookResult = ReturnType<typeof useAllSteficonRulesQuery>;
export type AllSteficonRulesLazyQueryHookResult = ReturnType<typeof useAllSteficonRulesLazyQuery>;
export type AllSteficonRulesQueryResult = ApolloReactCommon.QueryResult<AllSteficonRulesQuery, AllSteficonRulesQueryVariables>;
export const AllTargetPopulationsDocument = gql`
    query AllTargetPopulations($after: String, $before: String, $first: Int, $last: Int, $orderBy: String, $name: String, $status: String, $candidateListTotalHouseholdsMin: Int, $candidateListTotalHouseholdsMax: Int, $businessArea: String) {
  allTargetPopulation(after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy, name: $name, status: $status, candidateListTotalHouseholdsMin: $candidateListTotalHouseholdsMin, candidateListTotalHouseholdsMax: $candidateListTotalHouseholdsMax, businessArea: $businessArea) {
    edges {
      node {
        ...targetPopulationMinimal
      }
      cursor
    }
    totalCount
    edgeCount
  }
}
    ${TargetPopulationMinimalFragmentDoc}`;
export type AllTargetPopulationsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables>, 'query'>;

    export const AllTargetPopulationsComponent = (props: AllTargetPopulationsComponentProps) => (
      <ApolloReactComponents.Query<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables> query={AllTargetPopulationsDocument} {...props} />
    );
    
export type AllTargetPopulationsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables> & TChildProps;
export function withAllTargetPopulations<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllTargetPopulationsQuery,
  AllTargetPopulationsQueryVariables,
  AllTargetPopulationsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables, AllTargetPopulationsProps<TChildProps>>(AllTargetPopulationsDocument, {
      alias: 'allTargetPopulations',
      ...operationOptions
    });
};

/**
 * __useAllTargetPopulationsQuery__
 *
 * To run a query within a React component, call `useAllTargetPopulationsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllTargetPopulationsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllTargetPopulationsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *      name: // value for 'name'
 *      status: // value for 'status'
 *      candidateListTotalHouseholdsMin: // value for 'candidateListTotalHouseholdsMin'
 *      candidateListTotalHouseholdsMax: // value for 'candidateListTotalHouseholdsMax'
 *      businessArea: // value for 'businessArea'
 *   },
 * });
 */
export function useAllTargetPopulationsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables>(AllTargetPopulationsDocument, baseOptions);
      }
export function useAllTargetPopulationsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables>(AllTargetPopulationsDocument, baseOptions);
        }
export type AllTargetPopulationsQueryHookResult = ReturnType<typeof useAllTargetPopulationsQuery>;
export type AllTargetPopulationsLazyQueryHookResult = ReturnType<typeof useAllTargetPopulationsLazyQuery>;
export type AllTargetPopulationsQueryResult = ApolloReactCommon.QueryResult<AllTargetPopulationsQuery, AllTargetPopulationsQueryVariables>;
export const AllUsersDocument = gql`
    query AllUsers($search: String, $status: [String], $partner: [String], $roles: [String], $businessArea: String!, $first: Int, $last: Int, $after: String, $before: String, $orderBy: String) {
  allUsers(search: $search, status: $status, partner: $partner, roles: $roles, businessArea: $businessArea, first: $first, last: $last, after: $after, before: $before, orderBy: $orderBy) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      endCursor
      startCursor
    }
    edges {
      node {
        id
        firstName
        lastName
        username
        email
        isActive
        lastLogin
        status
        partner
        userRoles {
          businessArea {
            name
          }
          role {
            name
            permissions
          }
        }
      }
      cursor
    }
    totalCount
    edgeCount
  }
}
    `;
export type AllUsersComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllUsersQuery, AllUsersQueryVariables>, 'query'> & ({ variables: AllUsersQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const AllUsersComponent = (props: AllUsersComponentProps) => (
      <ApolloReactComponents.Query<AllUsersQuery, AllUsersQueryVariables> query={AllUsersDocument} {...props} />
    );
    
export type AllUsersProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllUsersQuery, AllUsersQueryVariables> & TChildProps;
export function withAllUsers<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllUsersQuery,
  AllUsersQueryVariables,
  AllUsersProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllUsersQuery, AllUsersQueryVariables, AllUsersProps<TChildProps>>(AllUsersDocument, {
      alias: 'allUsers',
      ...operationOptions
    });
};

/**
 * __useAllUsersQuery__
 *
 * To run a query within a React component, call `useAllUsersQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllUsersQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllUsersQuery({
 *   variables: {
 *      search: // value for 'search'
 *      status: // value for 'status'
 *      partner: // value for 'partner'
 *      roles: // value for 'roles'
 *      businessArea: // value for 'businessArea'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useAllUsersQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllUsersQuery, AllUsersQueryVariables>) {
        return ApolloReactHooks.useQuery<AllUsersQuery, AllUsersQueryVariables>(AllUsersDocument, baseOptions);
      }
export function useAllUsersLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllUsersQuery, AllUsersQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllUsersQuery, AllUsersQueryVariables>(AllUsersDocument, baseOptions);
        }
export type AllUsersQueryHookResult = ReturnType<typeof useAllUsersQuery>;
export type AllUsersLazyQueryHookResult = ReturnType<typeof useAllUsersLazyQuery>;
export type AllUsersQueryResult = ApolloReactCommon.QueryResult<AllUsersQuery, AllUsersQueryVariables>;
export const CashPlanDocument = gql`
    query CashPlan($id: ID!) {
  cashPlan(id: $id) {
    id
    name
    startDate
    endDate
    updatedAt
    status
    deliveryType
    fundsCommitment
    downPayment
    dispersionDate
    assistanceThrough
    caId
    dispersionDate
    verificationStatus
    bankReconciliationSuccess
    bankReconciliationError
    verifications {
      edges {
        node {
          id
          status
          sampleSize
          receivedCount
          notReceivedCount
          respondedCount
          verificationMethod
          sampling
          receivedCount
          receivedWithProblemsCount
          rapidProFlowId
          confidenceInterval
          marginOfError
          activationDate
          completionDate
          ageFilter {
            min
            max
          }
          excludedAdminAreasFilter
          sexFilter
        }
      }
    }
    program {
      id
      name
    }
    paymentRecords {
      totalCount
      edgeCount
    }
  }
}
    `;
export type CashPlanComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<CashPlanQuery, CashPlanQueryVariables>, 'query'> & ({ variables: CashPlanQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const CashPlanComponent = (props: CashPlanComponentProps) => (
      <ApolloReactComponents.Query<CashPlanQuery, CashPlanQueryVariables> query={CashPlanDocument} {...props} />
    );
    
export type CashPlanProps<TChildProps = {}> = ApolloReactHoc.DataProps<CashPlanQuery, CashPlanQueryVariables> & TChildProps;
export function withCashPlan<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CashPlanQuery,
  CashPlanQueryVariables,
  CashPlanProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, CashPlanQuery, CashPlanQueryVariables, CashPlanProps<TChildProps>>(CashPlanDocument, {
      alias: 'cashPlan',
      ...operationOptions
    });
};

/**
 * __useCashPlanQuery__
 *
 * To run a query within a React component, call `useCashPlanQuery` and pass it any options that fit your needs.
 * When your component renders, `useCashPlanQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCashPlanQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useCashPlanQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<CashPlanQuery, CashPlanQueryVariables>) {
        return ApolloReactHooks.useQuery<CashPlanQuery, CashPlanQueryVariables>(CashPlanDocument, baseOptions);
      }
export function useCashPlanLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<CashPlanQuery, CashPlanQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<CashPlanQuery, CashPlanQueryVariables>(CashPlanDocument, baseOptions);
        }
export type CashPlanQueryHookResult = ReturnType<typeof useCashPlanQuery>;
export type CashPlanLazyQueryHookResult = ReturnType<typeof useCashPlanLazyQuery>;
export type CashPlanQueryResult = ApolloReactCommon.QueryResult<CashPlanQuery, CashPlanQueryVariables>;
export const GrievancesChoiceDataDocument = gql`
    query GrievancesChoiceData {
  grievanceTicketStatusChoices {
    name
    value
  }
  grievanceTicketCategoryChoices {
    name
    value
  }
  grievanceTicketIssueTypeChoices {
    category
    label
    subCategories {
      name
      value
    }
  }
}
    `;
export type GrievancesChoiceDataComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables>, 'query'>;

    export const GrievancesChoiceDataComponent = (props: GrievancesChoiceDataComponentProps) => (
      <ApolloReactComponents.Query<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables> query={GrievancesChoiceDataDocument} {...props} />
    );
    
export type GrievancesChoiceDataProps<TChildProps = {}> = ApolloReactHoc.DataProps<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables> & TChildProps;
export function withGrievancesChoiceData<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  GrievancesChoiceDataQuery,
  GrievancesChoiceDataQueryVariables,
  GrievancesChoiceDataProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables, GrievancesChoiceDataProps<TChildProps>>(GrievancesChoiceDataDocument, {
      alias: 'grievancesChoiceData',
      ...operationOptions
    });
};

/**
 * __useGrievancesChoiceDataQuery__
 *
 * To run a query within a React component, call `useGrievancesChoiceDataQuery` and pass it any options that fit your needs.
 * When your component renders, `useGrievancesChoiceDataQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGrievancesChoiceDataQuery({
 *   variables: {
 *   },
 * });
 */
export function useGrievancesChoiceDataQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables>) {
        return ApolloReactHooks.useQuery<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables>(GrievancesChoiceDataDocument, baseOptions);
      }
export function useGrievancesChoiceDataLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables>(GrievancesChoiceDataDocument, baseOptions);
        }
export type GrievancesChoiceDataQueryHookResult = ReturnType<typeof useGrievancesChoiceDataQuery>;
export type GrievancesChoiceDataLazyQueryHookResult = ReturnType<typeof useGrievancesChoiceDataLazyQuery>;
export type GrievancesChoiceDataQueryResult = ApolloReactCommon.QueryResult<GrievancesChoiceDataQuery, GrievancesChoiceDataQueryVariables>;
export const HouseholdDocument = gql`
    query Household($id: ID!) {
  household(id: $id) {
    ...householdDetailed
  }
}
    ${HouseholdDetailedFragmentDoc}`;
export type HouseholdComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<HouseholdQuery, HouseholdQueryVariables>, 'query'> & ({ variables: HouseholdQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const HouseholdComponent = (props: HouseholdComponentProps) => (
      <ApolloReactComponents.Query<HouseholdQuery, HouseholdQueryVariables> query={HouseholdDocument} {...props} />
    );
    
export type HouseholdProps<TChildProps = {}> = ApolloReactHoc.DataProps<HouseholdQuery, HouseholdQueryVariables> & TChildProps;
export function withHousehold<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  HouseholdQuery,
  HouseholdQueryVariables,
  HouseholdProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, HouseholdQuery, HouseholdQueryVariables, HouseholdProps<TChildProps>>(HouseholdDocument, {
      alias: 'household',
      ...operationOptions
    });
};

/**
 * __useHouseholdQuery__
 *
 * To run a query within a React component, call `useHouseholdQuery` and pass it any options that fit your needs.
 * When your component renders, `useHouseholdQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useHouseholdQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useHouseholdQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<HouseholdQuery, HouseholdQueryVariables>) {
        return ApolloReactHooks.useQuery<HouseholdQuery, HouseholdQueryVariables>(HouseholdDocument, baseOptions);
      }
export function useHouseholdLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<HouseholdQuery, HouseholdQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<HouseholdQuery, HouseholdQueryVariables>(HouseholdDocument, baseOptions);
        }
export type HouseholdQueryHookResult = ReturnType<typeof useHouseholdQuery>;
export type HouseholdLazyQueryHookResult = ReturnType<typeof useHouseholdLazyQuery>;
export type HouseholdQueryResult = ApolloReactCommon.QueryResult<HouseholdQuery, HouseholdQueryVariables>;
export const HouseholdChoiceDataDocument = gql`
    query householdChoiceData {
  residenceStatusChoices {
    name
    value
  }
  relationshipChoices {
    name
    value
  }
  roleChoices {
    name
    value
  }
  maritalStatusChoices {
    name
    value
  }
  deduplicationBatchStatusChoices {
    name
    value
  }
  deduplicationGoldenRecordStatusChoices {
    name
    value
  }
}
    `;
export type HouseholdChoiceDataComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables>, 'query'>;

    export const HouseholdChoiceDataComponent = (props: HouseholdChoiceDataComponentProps) => (
      <ApolloReactComponents.Query<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables> query={HouseholdChoiceDataDocument} {...props} />
    );
    
export type HouseholdChoiceDataProps<TChildProps = {}> = ApolloReactHoc.DataProps<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables> & TChildProps;
export function withHouseholdChoiceData<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  HouseholdChoiceDataQuery,
  HouseholdChoiceDataQueryVariables,
  HouseholdChoiceDataProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables, HouseholdChoiceDataProps<TChildProps>>(HouseholdChoiceDataDocument, {
      alias: 'householdChoiceData',
      ...operationOptions
    });
};

/**
 * __useHouseholdChoiceDataQuery__
 *
 * To run a query within a React component, call `useHouseholdChoiceDataQuery` and pass it any options that fit your needs.
 * When your component renders, `useHouseholdChoiceDataQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useHouseholdChoiceDataQuery({
 *   variables: {
 *   },
 * });
 */
export function useHouseholdChoiceDataQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables>) {
        return ApolloReactHooks.useQuery<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables>(HouseholdChoiceDataDocument, baseOptions);
      }
export function useHouseholdChoiceDataLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables>(HouseholdChoiceDataDocument, baseOptions);
        }
export type HouseholdChoiceDataQueryHookResult = ReturnType<typeof useHouseholdChoiceDataQuery>;
export type HouseholdChoiceDataLazyQueryHookResult = ReturnType<typeof useHouseholdChoiceDataLazyQuery>;
export type HouseholdChoiceDataQueryResult = ApolloReactCommon.QueryResult<HouseholdChoiceDataQuery, HouseholdChoiceDataQueryVariables>;
export const IndividualDocument = gql`
    query Individual($id: ID!) {
  individual(id: $id) {
    ...individualDetailed
  }
}
    ${IndividualDetailedFragmentDoc}`;
export type IndividualComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<IndividualQuery, IndividualQueryVariables>, 'query'> & ({ variables: IndividualQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const IndividualComponent = (props: IndividualComponentProps) => (
      <ApolloReactComponents.Query<IndividualQuery, IndividualQueryVariables> query={IndividualDocument} {...props} />
    );
    
export type IndividualProps<TChildProps = {}> = ApolloReactHoc.DataProps<IndividualQuery, IndividualQueryVariables> & TChildProps;
export function withIndividual<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  IndividualQuery,
  IndividualQueryVariables,
  IndividualProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, IndividualQuery, IndividualQueryVariables, IndividualProps<TChildProps>>(IndividualDocument, {
      alias: 'individual',
      ...operationOptions
    });
};

/**
 * __useIndividualQuery__
 *
 * To run a query within a React component, call `useIndividualQuery` and pass it any options that fit your needs.
 * When your component renders, `useIndividualQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useIndividualQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useIndividualQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<IndividualQuery, IndividualQueryVariables>) {
        return ApolloReactHooks.useQuery<IndividualQuery, IndividualQueryVariables>(IndividualDocument, baseOptions);
      }
export function useIndividualLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<IndividualQuery, IndividualQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<IndividualQuery, IndividualQueryVariables>(IndividualDocument, baseOptions);
        }
export type IndividualQueryHookResult = ReturnType<typeof useIndividualQuery>;
export type IndividualLazyQueryHookResult = ReturnType<typeof useIndividualLazyQuery>;
export type IndividualQueryResult = ApolloReactCommon.QueryResult<IndividualQuery, IndividualQueryVariables>;
export const LookUpPaymentRecordsDocument = gql`
    query LookUpPaymentRecords($cashPlan: ID, $household: ID, $after: String, $before: String, $orderBy: String, $first: Int, $last: Int) {
  allPaymentRecords(cashPlan: $cashPlan, household: $household, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        id
        caId
        verifications {
          edges {
            node {
              status
            }
          }
        }
        cashPlan {
          id
          name
        }
        deliveredQuantity
      }
    }
    totalCount
    edgeCount
  }
}
    `;
export type LookUpPaymentRecordsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables>, 'query'>;

    export const LookUpPaymentRecordsComponent = (props: LookUpPaymentRecordsComponentProps) => (
      <ApolloReactComponents.Query<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables> query={LookUpPaymentRecordsDocument} {...props} />
    );
    
export type LookUpPaymentRecordsProps<TChildProps = {}> = ApolloReactHoc.DataProps<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables> & TChildProps;
export function withLookUpPaymentRecords<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  LookUpPaymentRecordsQuery,
  LookUpPaymentRecordsQueryVariables,
  LookUpPaymentRecordsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables, LookUpPaymentRecordsProps<TChildProps>>(LookUpPaymentRecordsDocument, {
      alias: 'lookUpPaymentRecords',
      ...operationOptions
    });
};

/**
 * __useLookUpPaymentRecordsQuery__
 *
 * To run a query within a React component, call `useLookUpPaymentRecordsQuery` and pass it any options that fit your needs.
 * When your component renders, `useLookUpPaymentRecordsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useLookUpPaymentRecordsQuery({
 *   variables: {
 *      cashPlan: // value for 'cashPlan'
 *      household: // value for 'household'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      orderBy: // value for 'orderBy'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *   },
 * });
 */
export function useLookUpPaymentRecordsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables>) {
        return ApolloReactHooks.useQuery<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables>(LookUpPaymentRecordsDocument, baseOptions);
      }
export function useLookUpPaymentRecordsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables>(LookUpPaymentRecordsDocument, baseOptions);
        }
export type LookUpPaymentRecordsQueryHookResult = ReturnType<typeof useLookUpPaymentRecordsQuery>;
export type LookUpPaymentRecordsLazyQueryHookResult = ReturnType<typeof useLookUpPaymentRecordsLazyQuery>;
export type LookUpPaymentRecordsQueryResult = ApolloReactCommon.QueryResult<LookUpPaymentRecordsQuery, LookUpPaymentRecordsQueryVariables>;
export const MeDocument = gql`
    query Me {
  me {
    id
    username
    email
    firstName
    lastName
    businessAreas {
      edges {
        node {
          id
          name
          slug
          permissions
        }
      }
    }
  }
}
    `;
export type MeComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<MeQuery, MeQueryVariables>, 'query'>;

    export const MeComponent = (props: MeComponentProps) => (
      <ApolloReactComponents.Query<MeQuery, MeQueryVariables> query={MeDocument} {...props} />
    );
    
export type MeProps<TChildProps = {}> = ApolloReactHoc.DataProps<MeQuery, MeQueryVariables> & TChildProps;
export function withMe<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  MeQuery,
  MeQueryVariables,
  MeProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, MeQuery, MeQueryVariables, MeProps<TChildProps>>(MeDocument, {
      alias: 'me',
      ...operationOptions
    });
};

/**
 * __useMeQuery__
 *
 * To run a query within a React component, call `useMeQuery` and pass it any options that fit your needs.
 * When your component renders, `useMeQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useMeQuery({
 *   variables: {
 *   },
 * });
 */
export function useMeQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<MeQuery, MeQueryVariables>) {
        return ApolloReactHooks.useQuery<MeQuery, MeQueryVariables>(MeDocument, baseOptions);
      }
export function useMeLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<MeQuery, MeQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<MeQuery, MeQueryVariables>(MeDocument, baseOptions);
        }
export type MeQueryHookResult = ReturnType<typeof useMeQuery>;
export type MeLazyQueryHookResult = ReturnType<typeof useMeLazyQuery>;
export type MeQueryResult = ApolloReactCommon.QueryResult<MeQuery, MeQueryVariables>;
export const PaymentRecordDocument = gql`
    query PaymentRecord($id: ID!) {
  paymentRecord(id: $id) {
    id
    status
    statusDate
    caId
    household {
      id
      size
      headOfHousehold {
        id
        phoneNo
        phoneNoAlternative
      }
    }
    fullName
    distributionModality
    totalPersonsCovered
    targetPopulation {
      id
      name
    }
    cashPlan {
      id
      caId
      program {
        id
        name
      }
      verifications {
        edges {
          node {
            id
            status
            verificationMethod
          }
        }
      }
    }
    verifications {
      totalCount
      edges {
        node {
          id
          status
          statusDate
          receivedAmount
        }
      }
    }
    currency
    entitlementQuantity
    deliveredQuantity
    deliveryDate
    deliveryDate
    entitlementCardIssueDate
    entitlementCardNumber
    serviceProvider {
      id
      fullName
      shortName
    }
    id
    status
    statusDate
    caId
    household {
      id
      size
      headOfHousehold {
        id
        phoneNo
        phoneNoAlternative
      }
    }
    fullName
    distributionModality
    totalPersonsCovered
    targetPopulation {
      id
      name
    }
    cashPlan {
      id
      caId
      program {
        id
        name
      }
      verifications {
        edges {
          node {
            id
            status
            verificationMethod
          }
        }
      }
    }
    currency
    entitlementQuantity
    deliveredQuantity
    deliveryDate
    deliveryDate
    deliveryType
    entitlementCardIssueDate
    entitlementCardNumber
    serviceProvider {
      id
      fullName
      shortName
    }
  }
}
    `;
export type PaymentRecordComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<PaymentRecordQuery, PaymentRecordQueryVariables>, 'query'> & ({ variables: PaymentRecordQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const PaymentRecordComponent = (props: PaymentRecordComponentProps) => (
      <ApolloReactComponents.Query<PaymentRecordQuery, PaymentRecordQueryVariables> query={PaymentRecordDocument} {...props} />
    );
    
export type PaymentRecordProps<TChildProps = {}> = ApolloReactHoc.DataProps<PaymentRecordQuery, PaymentRecordQueryVariables> & TChildProps;
export function withPaymentRecord<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  PaymentRecordQuery,
  PaymentRecordQueryVariables,
  PaymentRecordProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, PaymentRecordQuery, PaymentRecordQueryVariables, PaymentRecordProps<TChildProps>>(PaymentRecordDocument, {
      alias: 'paymentRecord',
      ...operationOptions
    });
};

/**
 * __usePaymentRecordQuery__
 *
 * To run a query within a React component, call `usePaymentRecordQuery` and pass it any options that fit your needs.
 * When your component renders, `usePaymentRecordQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePaymentRecordQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function usePaymentRecordQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<PaymentRecordQuery, PaymentRecordQueryVariables>) {
        return ApolloReactHooks.useQuery<PaymentRecordQuery, PaymentRecordQueryVariables>(PaymentRecordDocument, baseOptions);
      }
export function usePaymentRecordLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<PaymentRecordQuery, PaymentRecordQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<PaymentRecordQuery, PaymentRecordQueryVariables>(PaymentRecordDocument, baseOptions);
        }
export type PaymentRecordQueryHookResult = ReturnType<typeof usePaymentRecordQuery>;
export type PaymentRecordLazyQueryHookResult = ReturnType<typeof usePaymentRecordLazyQuery>;
export type PaymentRecordQueryResult = ApolloReactCommon.QueryResult<PaymentRecordQuery, PaymentRecordQueryVariables>;
export const PaymentRecordVerificationDocument = gql`
    query PaymentRecordVerification($id: ID!) {
  paymentRecordVerification(id: $id) {
    id
    status
    statusDate
    receivedAmount
    paymentRecord {
      id
      status
      statusDate
      caId
      household {
        unicefId
        id
        size
        headOfHousehold {
          id
          phoneNo
          phoneNoAlternative
        }
      }
      fullName
      distributionModality
      totalPersonsCovered
      targetPopulation {
        id
        name
      }
      cashPlan {
        id
        caId
        program {
          id
          name
        }
        verifications {
          edges {
            node {
              id
              status
              verificationMethod
            }
          }
        }
      }
      currency
      entitlementQuantity
      deliveredQuantity
      deliveryDate
      deliveryDate
      deliveryType
      entitlementCardIssueDate
      entitlementCardNumber
      serviceProvider {
        id
        fullName
        shortName
      }
    }
  }
}
    `;
export type PaymentRecordVerificationComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables>, 'query'> & ({ variables: PaymentRecordVerificationQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const PaymentRecordVerificationComponent = (props: PaymentRecordVerificationComponentProps) => (
      <ApolloReactComponents.Query<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables> query={PaymentRecordVerificationDocument} {...props} />
    );
    
export type PaymentRecordVerificationProps<TChildProps = {}> = ApolloReactHoc.DataProps<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables> & TChildProps;
export function withPaymentRecordVerification<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  PaymentRecordVerificationQuery,
  PaymentRecordVerificationQueryVariables,
  PaymentRecordVerificationProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables, PaymentRecordVerificationProps<TChildProps>>(PaymentRecordVerificationDocument, {
      alias: 'paymentRecordVerification',
      ...operationOptions
    });
};

/**
 * __usePaymentRecordVerificationQuery__
 *
 * To run a query within a React component, call `usePaymentRecordVerificationQuery` and pass it any options that fit your needs.
 * When your component renders, `usePaymentRecordVerificationQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = usePaymentRecordVerificationQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function usePaymentRecordVerificationQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables>) {
        return ApolloReactHooks.useQuery<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables>(PaymentRecordVerificationDocument, baseOptions);
      }
export function usePaymentRecordVerificationLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables>(PaymentRecordVerificationDocument, baseOptions);
        }
export type PaymentRecordVerificationQueryHookResult = ReturnType<typeof usePaymentRecordVerificationQuery>;
export type PaymentRecordVerificationLazyQueryHookResult = ReturnType<typeof usePaymentRecordVerificationLazyQuery>;
export type PaymentRecordVerificationQueryResult = ApolloReactCommon.QueryResult<PaymentRecordVerificationQuery, PaymentRecordVerificationQueryVariables>;
export const ProgramDocument = gql`
    query Program($id: ID!) {
  program(id: $id) {
    id
    name
    startDate
    endDate
    status
    caId
    description
    budget
    frequencyOfPayments
    cashPlus
    populationGoal
    scope
    sector
    totalNumberOfHouseholds
    administrativeAreasOfImplementation
    individualDataNeeded
  }
}
    `;
export type ProgramComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<ProgramQuery, ProgramQueryVariables>, 'query'> & ({ variables: ProgramQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const ProgramComponent = (props: ProgramComponentProps) => (
      <ApolloReactComponents.Query<ProgramQuery, ProgramQueryVariables> query={ProgramDocument} {...props} />
    );
    
export type ProgramProps<TChildProps = {}> = ApolloReactHoc.DataProps<ProgramQuery, ProgramQueryVariables> & TChildProps;
export function withProgram<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ProgramQuery,
  ProgramQueryVariables,
  ProgramProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, ProgramQuery, ProgramQueryVariables, ProgramProps<TChildProps>>(ProgramDocument, {
      alias: 'program',
      ...operationOptions
    });
};

/**
 * __useProgramQuery__
 *
 * To run a query within a React component, call `useProgramQuery` and pass it any options that fit your needs.
 * When your component renders, `useProgramQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useProgramQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useProgramQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<ProgramQuery, ProgramQueryVariables>) {
        return ApolloReactHooks.useQuery<ProgramQuery, ProgramQueryVariables>(ProgramDocument, baseOptions);
      }
export function useProgramLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<ProgramQuery, ProgramQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<ProgramQuery, ProgramQueryVariables>(ProgramDocument, baseOptions);
        }
export type ProgramQueryHookResult = ReturnType<typeof useProgramQuery>;
export type ProgramLazyQueryHookResult = ReturnType<typeof useProgramLazyQuery>;
export type ProgramQueryResult = ApolloReactCommon.QueryResult<ProgramQuery, ProgramQueryVariables>;
export const ProgrammeChoiceDataDocument = gql`
    query ProgrammeChoiceData {
  programFrequencyOfPaymentsChoices {
    name
    value
  }
  programScopeChoices {
    name
    value
  }
  programSectorChoices {
    name
    value
  }
  programStatusChoices {
    name
    value
  }
}
    `;
export type ProgrammeChoiceDataComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables>, 'query'>;

    export const ProgrammeChoiceDataComponent = (props: ProgrammeChoiceDataComponentProps) => (
      <ApolloReactComponents.Query<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables> query={ProgrammeChoiceDataDocument} {...props} />
    );
    
export type ProgrammeChoiceDataProps<TChildProps = {}> = ApolloReactHoc.DataProps<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables> & TChildProps;
export function withProgrammeChoiceData<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ProgrammeChoiceDataQuery,
  ProgrammeChoiceDataQueryVariables,
  ProgrammeChoiceDataProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables, ProgrammeChoiceDataProps<TChildProps>>(ProgrammeChoiceDataDocument, {
      alias: 'programmeChoiceData',
      ...operationOptions
    });
};

/**
 * __useProgrammeChoiceDataQuery__
 *
 * To run a query within a React component, call `useProgrammeChoiceDataQuery` and pass it any options that fit your needs.
 * When your component renders, `useProgrammeChoiceDataQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useProgrammeChoiceDataQuery({
 *   variables: {
 *   },
 * });
 */
export function useProgrammeChoiceDataQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables>) {
        return ApolloReactHooks.useQuery<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables>(ProgrammeChoiceDataDocument, baseOptions);
      }
export function useProgrammeChoiceDataLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables>(ProgrammeChoiceDataDocument, baseOptions);
        }
export type ProgrammeChoiceDataQueryHookResult = ReturnType<typeof useProgrammeChoiceDataQuery>;
export type ProgrammeChoiceDataLazyQueryHookResult = ReturnType<typeof useProgrammeChoiceDataLazyQuery>;
export type ProgrammeChoiceDataQueryResult = ApolloReactCommon.QueryResult<ProgrammeChoiceDataQuery, ProgrammeChoiceDataQueryVariables>;
export const SampleSizeDocument = gql`
    query SampleSize($input: GetCashplanVerificationSampleSizeInput!) {
  sampleSize(input: $input) {
    paymentRecordCount
    sampleSize
  }
}
    `;
export type SampleSizeComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<SampleSizeQuery, SampleSizeQueryVariables>, 'query'> & ({ variables: SampleSizeQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const SampleSizeComponent = (props: SampleSizeComponentProps) => (
      <ApolloReactComponents.Query<SampleSizeQuery, SampleSizeQueryVariables> query={SampleSizeDocument} {...props} />
    );
    
export type SampleSizeProps<TChildProps = {}> = ApolloReactHoc.DataProps<SampleSizeQuery, SampleSizeQueryVariables> & TChildProps;
export function withSampleSize<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  SampleSizeQuery,
  SampleSizeQueryVariables,
  SampleSizeProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, SampleSizeQuery, SampleSizeQueryVariables, SampleSizeProps<TChildProps>>(SampleSizeDocument, {
      alias: 'sampleSize',
      ...operationOptions
    });
};

/**
 * __useSampleSizeQuery__
 *
 * To run a query within a React component, call `useSampleSizeQuery` and pass it any options that fit your needs.
 * When your component renders, `useSampleSizeQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useSampleSizeQuery({
 *   variables: {
 *      input: // value for 'input'
 *   },
 * });
 */
export function useSampleSizeQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<SampleSizeQuery, SampleSizeQueryVariables>) {
        return ApolloReactHooks.useQuery<SampleSizeQuery, SampleSizeQueryVariables>(SampleSizeDocument, baseOptions);
      }
export function useSampleSizeLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<SampleSizeQuery, SampleSizeQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<SampleSizeQuery, SampleSizeQueryVariables>(SampleSizeDocument, baseOptions);
        }
export type SampleSizeQueryHookResult = ReturnType<typeof useSampleSizeQuery>;
export type SampleSizeLazyQueryHookResult = ReturnType<typeof useSampleSizeLazyQuery>;
export type SampleSizeQueryResult = ApolloReactCommon.QueryResult<SampleSizeQuery, SampleSizeQueryVariables>;
export const TargetPopulationDocument = gql`
    query targetPopulation($id: ID!) {
  targetPopulation(id: $id) {
    ...targetPopulationDetailed
  }
}
    ${TargetPopulationDetailedFragmentDoc}`;
export type TargetPopulationComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<TargetPopulationQuery, TargetPopulationQueryVariables>, 'query'> & ({ variables: TargetPopulationQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const TargetPopulationComponent = (props: TargetPopulationComponentProps) => (
      <ApolloReactComponents.Query<TargetPopulationQuery, TargetPopulationQueryVariables> query={TargetPopulationDocument} {...props} />
    );
    
export type TargetPopulationProps<TChildProps = {}> = ApolloReactHoc.DataProps<TargetPopulationQuery, TargetPopulationQueryVariables> & TChildProps;
export function withTargetPopulation<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  TargetPopulationQuery,
  TargetPopulationQueryVariables,
  TargetPopulationProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, TargetPopulationQuery, TargetPopulationQueryVariables, TargetPopulationProps<TChildProps>>(TargetPopulationDocument, {
      alias: 'targetPopulation',
      ...operationOptions
    });
};

/**
 * __useTargetPopulationQuery__
 *
 * To run a query within a React component, call `useTargetPopulationQuery` and pass it any options that fit your needs.
 * When your component renders, `useTargetPopulationQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useTargetPopulationQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useTargetPopulationQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<TargetPopulationQuery, TargetPopulationQueryVariables>) {
        return ApolloReactHooks.useQuery<TargetPopulationQuery, TargetPopulationQueryVariables>(TargetPopulationDocument, baseOptions);
      }
export function useTargetPopulationLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<TargetPopulationQuery, TargetPopulationQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<TargetPopulationQuery, TargetPopulationQueryVariables>(TargetPopulationDocument, baseOptions);
        }
export type TargetPopulationQueryHookResult = ReturnType<typeof useTargetPopulationQuery>;
export type TargetPopulationLazyQueryHookResult = ReturnType<typeof useTargetPopulationLazyQuery>;
export type TargetPopulationQueryResult = ApolloReactCommon.QueryResult<TargetPopulationQuery, TargetPopulationQueryVariables>;
export const UserChoiceDataDocument = gql`
    query userChoiceData {
  userRolesChoices {
    name
    value
  }
  userStatusChoices {
    name
    value
  }
  userPartnerChoices {
    name
    value
  }
}
    `;
export type UserChoiceDataComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<UserChoiceDataQuery, UserChoiceDataQueryVariables>, 'query'>;

    export const UserChoiceDataComponent = (props: UserChoiceDataComponentProps) => (
      <ApolloReactComponents.Query<UserChoiceDataQuery, UserChoiceDataQueryVariables> query={UserChoiceDataDocument} {...props} />
    );
    
export type UserChoiceDataProps<TChildProps = {}> = ApolloReactHoc.DataProps<UserChoiceDataQuery, UserChoiceDataQueryVariables> & TChildProps;
export function withUserChoiceData<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UserChoiceDataQuery,
  UserChoiceDataQueryVariables,
  UserChoiceDataProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, UserChoiceDataQuery, UserChoiceDataQueryVariables, UserChoiceDataProps<TChildProps>>(UserChoiceDataDocument, {
      alias: 'userChoiceData',
      ...operationOptions
    });
};

/**
 * __useUserChoiceDataQuery__
 *
 * To run a query within a React component, call `useUserChoiceDataQuery` and pass it any options that fit your needs.
 * When your component renders, `useUserChoiceDataQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useUserChoiceDataQuery({
 *   variables: {
 *   },
 * });
 */
export function useUserChoiceDataQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<UserChoiceDataQuery, UserChoiceDataQueryVariables>) {
        return ApolloReactHooks.useQuery<UserChoiceDataQuery, UserChoiceDataQueryVariables>(UserChoiceDataDocument, baseOptions);
      }
export function useUserChoiceDataLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<UserChoiceDataQuery, UserChoiceDataQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<UserChoiceDataQuery, UserChoiceDataQueryVariables>(UserChoiceDataDocument, baseOptions);
        }
export type UserChoiceDataQueryHookResult = ReturnType<typeof useUserChoiceDataQuery>;
export type UserChoiceDataLazyQueryHookResult = ReturnType<typeof useUserChoiceDataLazyQuery>;
export type UserChoiceDataQueryResult = ApolloReactCommon.QueryResult<UserChoiceDataQuery, UserChoiceDataQueryVariables>;
export const AllImportedHouseholdsDocument = gql`
    query AllImportedHouseholds($after: String, $before: String, $first: Int, $last: Int, $rdiId: String, $orderBy: String) {
  allImportedHouseholds(after: $after, before: $before, first: $first, last: $last, rdiId: $rdiId, orderBy: $orderBy) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        ...importedHouseholdMinimal
      }
    }
  }
}
    ${ImportedHouseholdMinimalFragmentDoc}`;
export type AllImportedHouseholdsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables>, 'query'>;

    export const AllImportedHouseholdsComponent = (props: AllImportedHouseholdsComponentProps) => (
      <ApolloReactComponents.Query<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables> query={AllImportedHouseholdsDocument} {...props} />
    );
    
export type AllImportedHouseholdsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables> & TChildProps;
export function withAllImportedHouseholds<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllImportedHouseholdsQuery,
  AllImportedHouseholdsQueryVariables,
  AllImportedHouseholdsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables, AllImportedHouseholdsProps<TChildProps>>(AllImportedHouseholdsDocument, {
      alias: 'allImportedHouseholds',
      ...operationOptions
    });
};

/**
 * __useAllImportedHouseholdsQuery__
 *
 * To run a query within a React component, call `useAllImportedHouseholdsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllImportedHouseholdsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllImportedHouseholdsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      rdiId: // value for 'rdiId'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useAllImportedHouseholdsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables>(AllImportedHouseholdsDocument, baseOptions);
      }
export function useAllImportedHouseholdsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables>(AllImportedHouseholdsDocument, baseOptions);
        }
export type AllImportedHouseholdsQueryHookResult = ReturnType<typeof useAllImportedHouseholdsQuery>;
export type AllImportedHouseholdsLazyQueryHookResult = ReturnType<typeof useAllImportedHouseholdsLazyQuery>;
export type AllImportedHouseholdsQueryResult = ApolloReactCommon.QueryResult<AllImportedHouseholdsQuery, AllImportedHouseholdsQueryVariables>;
export const AllImportedIndividualsDocument = gql`
    query AllImportedIndividuals($after: String, $before: String, $first: Int, $last: Int, $rdiId: String, $household: ID, $orderBy: String, $duplicatesOnly: Boolean) {
  allImportedIndividuals(after: $after, before: $before, first: $first, last: $last, rdiId: $rdiId, household: $household, orderBy: $orderBy, duplicatesOnly: $duplicatesOnly) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        ...importedIndividualMinimal
      }
    }
  }
}
    ${ImportedIndividualMinimalFragmentDoc}`;
export type AllImportedIndividualsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables>, 'query'>;

    export const AllImportedIndividualsComponent = (props: AllImportedIndividualsComponentProps) => (
      <ApolloReactComponents.Query<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables> query={AllImportedIndividualsDocument} {...props} />
    );
    
export type AllImportedIndividualsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables> & TChildProps;
export function withAllImportedIndividuals<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllImportedIndividualsQuery,
  AllImportedIndividualsQueryVariables,
  AllImportedIndividualsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables, AllImportedIndividualsProps<TChildProps>>(AllImportedIndividualsDocument, {
      alias: 'allImportedIndividuals',
      ...operationOptions
    });
};

/**
 * __useAllImportedIndividualsQuery__
 *
 * To run a query within a React component, call `useAllImportedIndividualsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllImportedIndividualsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllImportedIndividualsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      rdiId: // value for 'rdiId'
 *      household: // value for 'household'
 *      orderBy: // value for 'orderBy'
 *      duplicatesOnly: // value for 'duplicatesOnly'
 *   },
 * });
 */
export function useAllImportedIndividualsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables>(AllImportedIndividualsDocument, baseOptions);
      }
export function useAllImportedIndividualsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables>(AllImportedIndividualsDocument, baseOptions);
        }
export type AllImportedIndividualsQueryHookResult = ReturnType<typeof useAllImportedIndividualsQuery>;
export type AllImportedIndividualsLazyQueryHookResult = ReturnType<typeof useAllImportedIndividualsLazyQuery>;
export type AllImportedIndividualsQueryResult = ApolloReactCommon.QueryResult<AllImportedIndividualsQuery, AllImportedIndividualsQueryVariables>;
export const AllKoboProjectsDocument = gql`
    query AllKoboProjects($after: String, $before: String, $first: Int, $last: Int, $businessAreaSlug: String!) {
  allKoboProjects(after: $after, before: $before, first: $first, last: $last, businessAreaSlug: $businessAreaSlug) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        name
        id
      }
    }
  }
}
    `;
export type AllKoboProjectsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllKoboProjectsQuery, AllKoboProjectsQueryVariables>, 'query'> & ({ variables: AllKoboProjectsQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const AllKoboProjectsComponent = (props: AllKoboProjectsComponentProps) => (
      <ApolloReactComponents.Query<AllKoboProjectsQuery, AllKoboProjectsQueryVariables> query={AllKoboProjectsDocument} {...props} />
    );
    
export type AllKoboProjectsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllKoboProjectsQuery, AllKoboProjectsQueryVariables> & TChildProps;
export function withAllKoboProjects<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllKoboProjectsQuery,
  AllKoboProjectsQueryVariables,
  AllKoboProjectsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllKoboProjectsQuery, AllKoboProjectsQueryVariables, AllKoboProjectsProps<TChildProps>>(AllKoboProjectsDocument, {
      alias: 'allKoboProjects',
      ...operationOptions
    });
};

/**
 * __useAllKoboProjectsQuery__
 *
 * To run a query within a React component, call `useAllKoboProjectsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllKoboProjectsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllKoboProjectsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      businessAreaSlug: // value for 'businessAreaSlug'
 *   },
 * });
 */
export function useAllKoboProjectsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllKoboProjectsQuery, AllKoboProjectsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllKoboProjectsQuery, AllKoboProjectsQueryVariables>(AllKoboProjectsDocument, baseOptions);
      }
export function useAllKoboProjectsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllKoboProjectsQuery, AllKoboProjectsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllKoboProjectsQuery, AllKoboProjectsQueryVariables>(AllKoboProjectsDocument, baseOptions);
        }
export type AllKoboProjectsQueryHookResult = ReturnType<typeof useAllKoboProjectsQuery>;
export type AllKoboProjectsLazyQueryHookResult = ReturnType<typeof useAllKoboProjectsLazyQuery>;
export type AllKoboProjectsQueryResult = ApolloReactCommon.QueryResult<AllKoboProjectsQuery, AllKoboProjectsQueryVariables>;
export const AllRegistrationDataImportsDocument = gql`
    query AllRegistrationDataImports($after: String, $before: String, $first: Int, $last: Int, $orderBy: String, $name_Icontains: String, $importedBy_Id: UUID, $status: String, $importDate: Date, $businessArea: String) {
  allRegistrationDataImports(after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy, name_Icontains: $name_Icontains, importedBy_Id: $importedBy_Id, status: $status, importDate: $importDate, businessArea: $businessArea) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
    edges {
      cursor
      node {
        ...registrationMinimal
      }
    }
  }
}
    ${RegistrationMinimalFragmentDoc}`;
export type AllRegistrationDataImportsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables>, 'query'>;

    export const AllRegistrationDataImportsComponent = (props: AllRegistrationDataImportsComponentProps) => (
      <ApolloReactComponents.Query<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables> query={AllRegistrationDataImportsDocument} {...props} />
    );
    
export type AllRegistrationDataImportsProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables> & TChildProps;
export function withAllRegistrationDataImports<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllRegistrationDataImportsQuery,
  AllRegistrationDataImportsQueryVariables,
  AllRegistrationDataImportsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables, AllRegistrationDataImportsProps<TChildProps>>(AllRegistrationDataImportsDocument, {
      alias: 'allRegistrationDataImports',
      ...operationOptions
    });
};

/**
 * __useAllRegistrationDataImportsQuery__
 *
 * To run a query within a React component, call `useAllRegistrationDataImportsQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllRegistrationDataImportsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllRegistrationDataImportsQuery({
 *   variables: {
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      first: // value for 'first'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *      name_Icontains: // value for 'name_Icontains'
 *      importedBy_Id: // value for 'importedBy_Id'
 *      status: // value for 'status'
 *      importDate: // value for 'importDate'
 *      businessArea: // value for 'businessArea'
 *   },
 * });
 */
export function useAllRegistrationDataImportsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables>) {
        return ApolloReactHooks.useQuery<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables>(AllRegistrationDataImportsDocument, baseOptions);
      }
export function useAllRegistrationDataImportsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables>(AllRegistrationDataImportsDocument, baseOptions);
        }
export type AllRegistrationDataImportsQueryHookResult = ReturnType<typeof useAllRegistrationDataImportsQuery>;
export type AllRegistrationDataImportsLazyQueryHookResult = ReturnType<typeof useAllRegistrationDataImportsLazyQuery>;
export type AllRegistrationDataImportsQueryResult = ApolloReactCommon.QueryResult<AllRegistrationDataImportsQuery, AllRegistrationDataImportsQueryVariables>;
export const CreateRegistrationKoboImportDocument = gql`
    mutation CreateRegistrationKoboImport($registrationDataImportData: RegistrationKoboImportMutationInput!) {
  registrationKoboImport(registrationDataImportData: $registrationDataImportData) {
    registrationDataImport {
      id
      name
      dataSource
      datahubId
    }
  }
}
    `;
export type CreateRegistrationKoboImportMutationFn = ApolloReactCommon.MutationFunction<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables>;
export type CreateRegistrationKoboImportComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables>, 'mutation'>;

    export const CreateRegistrationKoboImportComponent = (props: CreateRegistrationKoboImportComponentProps) => (
      <ApolloReactComponents.Mutation<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables> mutation={CreateRegistrationKoboImportDocument} {...props} />
    );
    
export type CreateRegistrationKoboImportProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables> & TChildProps;
export function withCreateRegistrationKoboImport<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateRegistrationKoboImportMutation,
  CreateRegistrationKoboImportMutationVariables,
  CreateRegistrationKoboImportProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables, CreateRegistrationKoboImportProps<TChildProps>>(CreateRegistrationKoboImportDocument, {
      alias: 'createRegistrationKoboImport',
      ...operationOptions
    });
};

/**
 * __useCreateRegistrationKoboImportMutation__
 *
 * To run a mutation, you first call `useCreateRegistrationKoboImportMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateRegistrationKoboImportMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createRegistrationKoboImportMutation, { data, loading, error }] = useCreateRegistrationKoboImportMutation({
 *   variables: {
 *      registrationDataImportData: // value for 'registrationDataImportData'
 *   },
 * });
 */
export function useCreateRegistrationKoboImportMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables>(CreateRegistrationKoboImportDocument, baseOptions);
      }
export type CreateRegistrationKoboImportMutationHookResult = ReturnType<typeof useCreateRegistrationKoboImportMutation>;
export type CreateRegistrationKoboImportMutationResult = ApolloReactCommon.MutationResult<CreateRegistrationKoboImportMutation>;
export type CreateRegistrationKoboImportMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateRegistrationKoboImportMutation, CreateRegistrationKoboImportMutationVariables>;
export const CreateRegistrationXlsxImportDocument = gql`
    mutation CreateRegistrationXlsxImport($registrationDataImportData: RegistrationXlsxImportMutationInput!) {
  registrationXlsxImport(registrationDataImportData: $registrationDataImportData) {
    registrationDataImport {
      id
      name
      dataSource
      datahubId
    }
  }
}
    `;
export type CreateRegistrationXlsxImportMutationFn = ApolloReactCommon.MutationFunction<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables>;
export type CreateRegistrationXlsxImportComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables>, 'mutation'>;

    export const CreateRegistrationXlsxImportComponent = (props: CreateRegistrationXlsxImportComponentProps) => (
      <ApolloReactComponents.Mutation<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables> mutation={CreateRegistrationXlsxImportDocument} {...props} />
    );
    
export type CreateRegistrationXlsxImportProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables> & TChildProps;
export function withCreateRegistrationXlsxImport<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateRegistrationXlsxImportMutation,
  CreateRegistrationXlsxImportMutationVariables,
  CreateRegistrationXlsxImportProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables, CreateRegistrationXlsxImportProps<TChildProps>>(CreateRegistrationXlsxImportDocument, {
      alias: 'createRegistrationXlsxImport',
      ...operationOptions
    });
};

/**
 * __useCreateRegistrationXlsxImportMutation__
 *
 * To run a mutation, you first call `useCreateRegistrationXlsxImportMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateRegistrationXlsxImportMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createRegistrationXlsxImportMutation, { data, loading, error }] = useCreateRegistrationXlsxImportMutation({
 *   variables: {
 *      registrationDataImportData: // value for 'registrationDataImportData'
 *   },
 * });
 */
export function useCreateRegistrationXlsxImportMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables>(CreateRegistrationXlsxImportDocument, baseOptions);
      }
export type CreateRegistrationXlsxImportMutationHookResult = ReturnType<typeof useCreateRegistrationXlsxImportMutation>;
export type CreateRegistrationXlsxImportMutationResult = ApolloReactCommon.MutationResult<CreateRegistrationXlsxImportMutation>;
export type CreateRegistrationXlsxImportMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateRegistrationXlsxImportMutation, CreateRegistrationXlsxImportMutationVariables>;
export const ImportedHouseholdDocument = gql`
    query ImportedHousehold($id: ID!) {
  importedHousehold(id: $id) {
    ...importedHouseholdDetailed
  }
}
    ${ImportedHouseholdDetailedFragmentDoc}`;
export type ImportedHouseholdComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<ImportedHouseholdQuery, ImportedHouseholdQueryVariables>, 'query'> & ({ variables: ImportedHouseholdQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const ImportedHouseholdComponent = (props: ImportedHouseholdComponentProps) => (
      <ApolloReactComponents.Query<ImportedHouseholdQuery, ImportedHouseholdQueryVariables> query={ImportedHouseholdDocument} {...props} />
    );
    
export type ImportedHouseholdProps<TChildProps = {}> = ApolloReactHoc.DataProps<ImportedHouseholdQuery, ImportedHouseholdQueryVariables> & TChildProps;
export function withImportedHousehold<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ImportedHouseholdQuery,
  ImportedHouseholdQueryVariables,
  ImportedHouseholdProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, ImportedHouseholdQuery, ImportedHouseholdQueryVariables, ImportedHouseholdProps<TChildProps>>(ImportedHouseholdDocument, {
      alias: 'importedHousehold',
      ...operationOptions
    });
};

/**
 * __useImportedHouseholdQuery__
 *
 * To run a query within a React component, call `useImportedHouseholdQuery` and pass it any options that fit your needs.
 * When your component renders, `useImportedHouseholdQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useImportedHouseholdQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useImportedHouseholdQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<ImportedHouseholdQuery, ImportedHouseholdQueryVariables>) {
        return ApolloReactHooks.useQuery<ImportedHouseholdQuery, ImportedHouseholdQueryVariables>(ImportedHouseholdDocument, baseOptions);
      }
export function useImportedHouseholdLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<ImportedHouseholdQuery, ImportedHouseholdQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<ImportedHouseholdQuery, ImportedHouseholdQueryVariables>(ImportedHouseholdDocument, baseOptions);
        }
export type ImportedHouseholdQueryHookResult = ReturnType<typeof useImportedHouseholdQuery>;
export type ImportedHouseholdLazyQueryHookResult = ReturnType<typeof useImportedHouseholdLazyQuery>;
export type ImportedHouseholdQueryResult = ApolloReactCommon.QueryResult<ImportedHouseholdQuery, ImportedHouseholdQueryVariables>;
export const ImportedIndividualDocument = gql`
    query ImportedIndividual($id: ID!) {
  importedIndividual(id: $id) {
    ...importedIndividualDetailed
  }
}
    ${ImportedIndividualDetailedFragmentDoc}`;
export type ImportedIndividualComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<ImportedIndividualQuery, ImportedIndividualQueryVariables>, 'query'> & ({ variables: ImportedIndividualQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const ImportedIndividualComponent = (props: ImportedIndividualComponentProps) => (
      <ApolloReactComponents.Query<ImportedIndividualQuery, ImportedIndividualQueryVariables> query={ImportedIndividualDocument} {...props} />
    );
    
export type ImportedIndividualProps<TChildProps = {}> = ApolloReactHoc.DataProps<ImportedIndividualQuery, ImportedIndividualQueryVariables> & TChildProps;
export function withImportedIndividual<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ImportedIndividualQuery,
  ImportedIndividualQueryVariables,
  ImportedIndividualProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, ImportedIndividualQuery, ImportedIndividualQueryVariables, ImportedIndividualProps<TChildProps>>(ImportedIndividualDocument, {
      alias: 'importedIndividual',
      ...operationOptions
    });
};

/**
 * __useImportedIndividualQuery__
 *
 * To run a query within a React component, call `useImportedIndividualQuery` and pass it any options that fit your needs.
 * When your component renders, `useImportedIndividualQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useImportedIndividualQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useImportedIndividualQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<ImportedIndividualQuery, ImportedIndividualQueryVariables>) {
        return ApolloReactHooks.useQuery<ImportedIndividualQuery, ImportedIndividualQueryVariables>(ImportedIndividualDocument, baseOptions);
      }
export function useImportedIndividualLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<ImportedIndividualQuery, ImportedIndividualQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<ImportedIndividualQuery, ImportedIndividualQueryVariables>(ImportedIndividualDocument, baseOptions);
        }
export type ImportedIndividualQueryHookResult = ReturnType<typeof useImportedIndividualQuery>;
export type ImportedIndividualLazyQueryHookResult = ReturnType<typeof useImportedIndividualLazyQuery>;
export type ImportedIndividualQueryResult = ApolloReactCommon.QueryResult<ImportedIndividualQuery, ImportedIndividualQueryVariables>;
export const MergeRdiDocument = gql`
    mutation MergeRDI($id: ID!) {
  mergeRegistrationDataImport(id: $id) {
    registrationDataImport {
      ...registrationDetailed
    }
  }
}
    ${RegistrationDetailedFragmentDoc}`;
export type MergeRdiMutationFn = ApolloReactCommon.MutationFunction<MergeRdiMutation, MergeRdiMutationVariables>;
export type MergeRdiComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<MergeRdiMutation, MergeRdiMutationVariables>, 'mutation'>;

    export const MergeRdiComponent = (props: MergeRdiComponentProps) => (
      <ApolloReactComponents.Mutation<MergeRdiMutation, MergeRdiMutationVariables> mutation={MergeRdiDocument} {...props} />
    );
    
export type MergeRdiProps<TChildProps = {}> = ApolloReactHoc.MutateProps<MergeRdiMutation, MergeRdiMutationVariables> & TChildProps;
export function withMergeRdi<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  MergeRdiMutation,
  MergeRdiMutationVariables,
  MergeRdiProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, MergeRdiMutation, MergeRdiMutationVariables, MergeRdiProps<TChildProps>>(MergeRdiDocument, {
      alias: 'mergeRdi',
      ...operationOptions
    });
};

/**
 * __useMergeRdiMutation__
 *
 * To run a mutation, you first call `useMergeRdiMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useMergeRdiMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [mergeRdiMutation, { data, loading, error }] = useMergeRdiMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useMergeRdiMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<MergeRdiMutation, MergeRdiMutationVariables>) {
        return ApolloReactHooks.useMutation<MergeRdiMutation, MergeRdiMutationVariables>(MergeRdiDocument, baseOptions);
      }
export type MergeRdiMutationHookResult = ReturnType<typeof useMergeRdiMutation>;
export type MergeRdiMutationResult = ApolloReactCommon.MutationResult<MergeRdiMutation>;
export type MergeRdiMutationOptions = ApolloReactCommon.BaseMutationOptions<MergeRdiMutation, MergeRdiMutationVariables>;
export const RegistrationChoicesDocument = gql`
    query registrationChoices {
  registrationDataStatusChoices {
    name
    value
  }
}
    `;
export type RegistrationChoicesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<RegistrationChoicesQuery, RegistrationChoicesQueryVariables>, 'query'>;

    export const RegistrationChoicesComponent = (props: RegistrationChoicesComponentProps) => (
      <ApolloReactComponents.Query<RegistrationChoicesQuery, RegistrationChoicesQueryVariables> query={RegistrationChoicesDocument} {...props} />
    );
    
export type RegistrationChoicesProps<TChildProps = {}> = ApolloReactHoc.DataProps<RegistrationChoicesQuery, RegistrationChoicesQueryVariables> & TChildProps;
export function withRegistrationChoices<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  RegistrationChoicesQuery,
  RegistrationChoicesQueryVariables,
  RegistrationChoicesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, RegistrationChoicesQuery, RegistrationChoicesQueryVariables, RegistrationChoicesProps<TChildProps>>(RegistrationChoicesDocument, {
      alias: 'registrationChoices',
      ...operationOptions
    });
};

/**
 * __useRegistrationChoicesQuery__
 *
 * To run a query within a React component, call `useRegistrationChoicesQuery` and pass it any options that fit your needs.
 * When your component renders, `useRegistrationChoicesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useRegistrationChoicesQuery({
 *   variables: {
 *   },
 * });
 */
export function useRegistrationChoicesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<RegistrationChoicesQuery, RegistrationChoicesQueryVariables>) {
        return ApolloReactHooks.useQuery<RegistrationChoicesQuery, RegistrationChoicesQueryVariables>(RegistrationChoicesDocument, baseOptions);
      }
export function useRegistrationChoicesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<RegistrationChoicesQuery, RegistrationChoicesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<RegistrationChoicesQuery, RegistrationChoicesQueryVariables>(RegistrationChoicesDocument, baseOptions);
        }
export type RegistrationChoicesQueryHookResult = ReturnType<typeof useRegistrationChoicesQuery>;
export type RegistrationChoicesLazyQueryHookResult = ReturnType<typeof useRegistrationChoicesLazyQuery>;
export type RegistrationChoicesQueryResult = ApolloReactCommon.QueryResult<RegistrationChoicesQuery, RegistrationChoicesQueryVariables>;
export const RegistrationDataImportDocument = gql`
    query RegistrationDataImport($id: ID!) {
  registrationDataImport(id: $id) {
    ...registrationDetailed
  }
}
    ${RegistrationDetailedFragmentDoc}`;
export type RegistrationDataImportComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<RegistrationDataImportQuery, RegistrationDataImportQueryVariables>, 'query'> & ({ variables: RegistrationDataImportQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const RegistrationDataImportComponent = (props: RegistrationDataImportComponentProps) => (
      <ApolloReactComponents.Query<RegistrationDataImportQuery, RegistrationDataImportQueryVariables> query={RegistrationDataImportDocument} {...props} />
    );
    
export type RegistrationDataImportProps<TChildProps = {}> = ApolloReactHoc.DataProps<RegistrationDataImportQuery, RegistrationDataImportQueryVariables> & TChildProps;
export function withRegistrationDataImport<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  RegistrationDataImportQuery,
  RegistrationDataImportQueryVariables,
  RegistrationDataImportProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, RegistrationDataImportQuery, RegistrationDataImportQueryVariables, RegistrationDataImportProps<TChildProps>>(RegistrationDataImportDocument, {
      alias: 'registrationDataImport',
      ...operationOptions
    });
};

/**
 * __useRegistrationDataImportQuery__
 *
 * To run a query within a React component, call `useRegistrationDataImportQuery` and pass it any options that fit your needs.
 * When your component renders, `useRegistrationDataImportQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useRegistrationDataImportQuery({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useRegistrationDataImportQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<RegistrationDataImportQuery, RegistrationDataImportQueryVariables>) {
        return ApolloReactHooks.useQuery<RegistrationDataImportQuery, RegistrationDataImportQueryVariables>(RegistrationDataImportDocument, baseOptions);
      }
export function useRegistrationDataImportLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<RegistrationDataImportQuery, RegistrationDataImportQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<RegistrationDataImportQuery, RegistrationDataImportQueryVariables>(RegistrationDataImportDocument, baseOptions);
        }
export type RegistrationDataImportQueryHookResult = ReturnType<typeof useRegistrationDataImportQuery>;
export type RegistrationDataImportLazyQueryHookResult = ReturnType<typeof useRegistrationDataImportLazyQuery>;
export type RegistrationDataImportQueryResult = ApolloReactCommon.QueryResult<RegistrationDataImportQuery, RegistrationDataImportQueryVariables>;
export const SaveKoboImportDataDocument = gql`
    mutation SaveKoboImportData($businessAreaSlug: String!, $projectId: Upload!) {
  saveKoboImportData(businessAreaSlug: $businessAreaSlug, uid: $projectId) {
    importData {
      id
      numberOfHouseholds
      numberOfIndividuals
    }
    errors {
      header
      message
    }
  }
}
    `;
export type SaveKoboImportDataMutationFn = ApolloReactCommon.MutationFunction<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables>;
export type SaveKoboImportDataComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables>, 'mutation'>;

    export const SaveKoboImportDataComponent = (props: SaveKoboImportDataComponentProps) => (
      <ApolloReactComponents.Mutation<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables> mutation={SaveKoboImportDataDocument} {...props} />
    );
    
export type SaveKoboImportDataProps<TChildProps = {}> = ApolloReactHoc.MutateProps<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables> & TChildProps;
export function withSaveKoboImportData<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  SaveKoboImportDataMutation,
  SaveKoboImportDataMutationVariables,
  SaveKoboImportDataProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables, SaveKoboImportDataProps<TChildProps>>(SaveKoboImportDataDocument, {
      alias: 'saveKoboImportData',
      ...operationOptions
    });
};

/**
 * __useSaveKoboImportDataMutation__
 *
 * To run a mutation, you first call `useSaveKoboImportDataMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useSaveKoboImportDataMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [saveKoboImportDataMutation, { data, loading, error }] = useSaveKoboImportDataMutation({
 *   variables: {
 *      businessAreaSlug: // value for 'businessAreaSlug'
 *      projectId: // value for 'projectId'
 *   },
 * });
 */
export function useSaveKoboImportDataMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables>) {
        return ApolloReactHooks.useMutation<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables>(SaveKoboImportDataDocument, baseOptions);
      }
export type SaveKoboImportDataMutationHookResult = ReturnType<typeof useSaveKoboImportDataMutation>;
export type SaveKoboImportDataMutationResult = ApolloReactCommon.MutationResult<SaveKoboImportDataMutation>;
export type SaveKoboImportDataMutationOptions = ApolloReactCommon.BaseMutationOptions<SaveKoboImportDataMutation, SaveKoboImportDataMutationVariables>;
export const UploadImportDataXlsxFileDocument = gql`
    mutation UploadImportDataXlsxFile($file: Upload!, $businessAreaSlug: String!) {
  uploadImportDataXlsxFile(file: $file, businessAreaSlug: $businessAreaSlug) {
    errors {
      header
      message
      rowNumber
    }
    importData {
      id
      numberOfIndividuals
      numberOfHouseholds
      registrationDataImport {
        id
      }
    }
  }
}
    `;
export type UploadImportDataXlsxFileMutationFn = ApolloReactCommon.MutationFunction<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>;
export type UploadImportDataXlsxFileComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>, 'mutation'>;

    export const UploadImportDataXlsxFileComponent = (props: UploadImportDataXlsxFileComponentProps) => (
      <ApolloReactComponents.Mutation<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables> mutation={UploadImportDataXlsxFileDocument} {...props} />
    );
    
export type UploadImportDataXlsxFileProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables> & TChildProps;
export function withUploadImportDataXlsxFile<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UploadImportDataXlsxFileMutation,
  UploadImportDataXlsxFileMutationVariables,
  UploadImportDataXlsxFileProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables, UploadImportDataXlsxFileProps<TChildProps>>(UploadImportDataXlsxFileDocument, {
      alias: 'uploadImportDataXlsxFile',
      ...operationOptions
    });
};

/**
 * __useUploadImportDataXlsxFileMutation__
 *
 * To run a mutation, you first call `useUploadImportDataXlsxFileMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUploadImportDataXlsxFileMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [uploadImportDataXlsxFileMutation, { data, loading, error }] = useUploadImportDataXlsxFileMutation({
 *   variables: {
 *      file: // value for 'file'
 *      businessAreaSlug: // value for 'businessAreaSlug'
 *   },
 * });
 */
export function useUploadImportDataXlsxFileMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>) {
        return ApolloReactHooks.useMutation<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>(UploadImportDataXlsxFileDocument, baseOptions);
      }
export type UploadImportDataXlsxFileMutationHookResult = ReturnType<typeof useUploadImportDataXlsxFileMutation>;
export type UploadImportDataXlsxFileMutationResult = ApolloReactCommon.MutationResult<UploadImportDataXlsxFileMutation>;
export type UploadImportDataXlsxFileMutationOptions = ApolloReactCommon.BaseMutationOptions<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>;
export const AllFieldsAttributesDocument = gql`
    query AllFieldsAttributes {
  allFieldsAttributes {
    id
    name
    labelEn
    associatedWith
    isFlexField
  }
}
    `;
export type AllFieldsAttributesComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables>, 'query'>;

    export const AllFieldsAttributesComponent = (props: AllFieldsAttributesComponentProps) => (
      <ApolloReactComponents.Query<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables> query={AllFieldsAttributesDocument} {...props} />
    );
    
export type AllFieldsAttributesProps<TChildProps = {}> = ApolloReactHoc.DataProps<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables> & TChildProps;
export function withAllFieldsAttributes<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  AllFieldsAttributesQuery,
  AllFieldsAttributesQueryVariables,
  AllFieldsAttributesProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables, AllFieldsAttributesProps<TChildProps>>(AllFieldsAttributesDocument, {
      alias: 'allFieldsAttributes',
      ...operationOptions
    });
};

/**
 * __useAllFieldsAttributesQuery__
 *
 * To run a query within a React component, call `useAllFieldsAttributesQuery` and pass it any options that fit your needs.
 * When your component renders, `useAllFieldsAttributesQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useAllFieldsAttributesQuery({
 *   variables: {
 *   },
 * });
 */
export function useAllFieldsAttributesQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables>) {
        return ApolloReactHooks.useQuery<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables>(AllFieldsAttributesDocument, baseOptions);
      }
export function useAllFieldsAttributesLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables>(AllFieldsAttributesDocument, baseOptions);
        }
export type AllFieldsAttributesQueryHookResult = ReturnType<typeof useAllFieldsAttributesQuery>;
export type AllFieldsAttributesLazyQueryHookResult = ReturnType<typeof useAllFieldsAttributesLazyQuery>;
export type AllFieldsAttributesQueryResult = ApolloReactCommon.QueryResult<AllFieldsAttributesQuery, AllFieldsAttributesQueryVariables>;
export const CandidateHouseholdsListByTargetingCriteriaDocument = gql`
    query candidateHouseholdsListByTargetingCriteria($targetPopulation: ID!, $first: Int, $after: String, $before: String, $last: Int, $orderBy: String) {
  candidateHouseholdsListByTargetingCriteria(targetPopulation: $targetPopulation, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
    edges {
      node {
        id
        headOfHousehold {
          id
          givenName
          familyName
        }
        size
        adminArea {
          id
          title
        }
        updatedAt
        address
        selection {
          vulnerabilityScore
        }
      }
      cursor
    }
    totalCount
    edgeCount
  }
}
    `;
export type CandidateHouseholdsListByTargetingCriteriaComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables>, 'query'> & ({ variables: CandidateHouseholdsListByTargetingCriteriaQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const CandidateHouseholdsListByTargetingCriteriaComponent = (props: CandidateHouseholdsListByTargetingCriteriaComponentProps) => (
      <ApolloReactComponents.Query<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables> query={CandidateHouseholdsListByTargetingCriteriaDocument} {...props} />
    );
    
export type CandidateHouseholdsListByTargetingCriteriaProps<TChildProps = {}> = ApolloReactHoc.DataProps<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables> & TChildProps;
export function withCandidateHouseholdsListByTargetingCriteria<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CandidateHouseholdsListByTargetingCriteriaQuery,
  CandidateHouseholdsListByTargetingCriteriaQueryVariables,
  CandidateHouseholdsListByTargetingCriteriaProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables, CandidateHouseholdsListByTargetingCriteriaProps<TChildProps>>(CandidateHouseholdsListByTargetingCriteriaDocument, {
      alias: 'candidateHouseholdsListByTargetingCriteria',
      ...operationOptions
    });
};

/**
 * __useCandidateHouseholdsListByTargetingCriteriaQuery__
 *
 * To run a query within a React component, call `useCandidateHouseholdsListByTargetingCriteriaQuery` and pass it any options that fit your needs.
 * When your component renders, `useCandidateHouseholdsListByTargetingCriteriaQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useCandidateHouseholdsListByTargetingCriteriaQuery({
 *   variables: {
 *      targetPopulation: // value for 'targetPopulation'
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useCandidateHouseholdsListByTargetingCriteriaQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables>) {
        return ApolloReactHooks.useQuery<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables>(CandidateHouseholdsListByTargetingCriteriaDocument, baseOptions);
      }
export function useCandidateHouseholdsListByTargetingCriteriaLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables>(CandidateHouseholdsListByTargetingCriteriaDocument, baseOptions);
        }
export type CandidateHouseholdsListByTargetingCriteriaQueryHookResult = ReturnType<typeof useCandidateHouseholdsListByTargetingCriteriaQuery>;
export type CandidateHouseholdsListByTargetingCriteriaLazyQueryHookResult = ReturnType<typeof useCandidateHouseholdsListByTargetingCriteriaLazyQuery>;
export type CandidateHouseholdsListByTargetingCriteriaQueryResult = ApolloReactCommon.QueryResult<CandidateHouseholdsListByTargetingCriteriaQuery, CandidateHouseholdsListByTargetingCriteriaQueryVariables>;
export const FinalHouseholdsListByTargetingCriteriaDocument = gql`
    query FinalHouseholdsListByTargetingCriteria($targetPopulation: ID!, $targetingCriteria: TargetingCriteriaObjectType, $first: Int, $after: String, $before: String, $last: Int, $orderBy: String) {
  finalHouseholdsListByTargetingCriteria(targetPopulation: $targetPopulation, targetingCriteria: $targetingCriteria, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
    edges {
      node {
        id
        headOfHousehold {
          id
          givenName
          familyName
        }
        size
        adminArea {
          id
          title
        }
        updatedAt
        address
        selection {
          vulnerabilityScore
        }
      }
      cursor
    }
    totalCount
    edgeCount
  }
}
    `;
export type FinalHouseholdsListByTargetingCriteriaComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables>, 'query'> & ({ variables: FinalHouseholdsListByTargetingCriteriaQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const FinalHouseholdsListByTargetingCriteriaComponent = (props: FinalHouseholdsListByTargetingCriteriaComponentProps) => (
      <ApolloReactComponents.Query<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables> query={FinalHouseholdsListByTargetingCriteriaDocument} {...props} />
    );
    
export type FinalHouseholdsListByTargetingCriteriaProps<TChildProps = {}> = ApolloReactHoc.DataProps<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables> & TChildProps;
export function withFinalHouseholdsListByTargetingCriteria<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  FinalHouseholdsListByTargetingCriteriaQuery,
  FinalHouseholdsListByTargetingCriteriaQueryVariables,
  FinalHouseholdsListByTargetingCriteriaProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables, FinalHouseholdsListByTargetingCriteriaProps<TChildProps>>(FinalHouseholdsListByTargetingCriteriaDocument, {
      alias: 'finalHouseholdsListByTargetingCriteria',
      ...operationOptions
    });
};

/**
 * __useFinalHouseholdsListByTargetingCriteriaQuery__
 *
 * To run a query within a React component, call `useFinalHouseholdsListByTargetingCriteriaQuery` and pass it any options that fit your needs.
 * When your component renders, `useFinalHouseholdsListByTargetingCriteriaQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useFinalHouseholdsListByTargetingCriteriaQuery({
 *   variables: {
 *      targetPopulation: // value for 'targetPopulation'
 *      targetingCriteria: // value for 'targetingCriteria'
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useFinalHouseholdsListByTargetingCriteriaQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables>) {
        return ApolloReactHooks.useQuery<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables>(FinalHouseholdsListByTargetingCriteriaDocument, baseOptions);
      }
export function useFinalHouseholdsListByTargetingCriteriaLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables>(FinalHouseholdsListByTargetingCriteriaDocument, baseOptions);
        }
export type FinalHouseholdsListByTargetingCriteriaQueryHookResult = ReturnType<typeof useFinalHouseholdsListByTargetingCriteriaQuery>;
export type FinalHouseholdsListByTargetingCriteriaLazyQueryHookResult = ReturnType<typeof useFinalHouseholdsListByTargetingCriteriaLazyQuery>;
export type FinalHouseholdsListByTargetingCriteriaQueryResult = ApolloReactCommon.QueryResult<FinalHouseholdsListByTargetingCriteriaQuery, FinalHouseholdsListByTargetingCriteriaQueryVariables>;
export const FlexFieldsDocument = gql`
    query FlexFields {
  allGroupsWithFields {
    name
    labelEn
    flexAttributes {
      id
      labelEn
      associatedWith
    }
  }
}
    `;
export type FlexFieldsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<FlexFieldsQuery, FlexFieldsQueryVariables>, 'query'>;

    export const FlexFieldsComponent = (props: FlexFieldsComponentProps) => (
      <ApolloReactComponents.Query<FlexFieldsQuery, FlexFieldsQueryVariables> query={FlexFieldsDocument} {...props} />
    );
    
export type FlexFieldsProps<TChildProps = {}> = ApolloReactHoc.DataProps<FlexFieldsQuery, FlexFieldsQueryVariables> & TChildProps;
export function withFlexFields<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  FlexFieldsQuery,
  FlexFieldsQueryVariables,
  FlexFieldsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, FlexFieldsQuery, FlexFieldsQueryVariables, FlexFieldsProps<TChildProps>>(FlexFieldsDocument, {
      alias: 'flexFields',
      ...operationOptions
    });
};

/**
 * __useFlexFieldsQuery__
 *
 * To run a query within a React component, call `useFlexFieldsQuery` and pass it any options that fit your needs.
 * When your component renders, `useFlexFieldsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useFlexFieldsQuery({
 *   variables: {
 *   },
 * });
 */
export function useFlexFieldsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<FlexFieldsQuery, FlexFieldsQueryVariables>) {
        return ApolloReactHooks.useQuery<FlexFieldsQuery, FlexFieldsQueryVariables>(FlexFieldsDocument, baseOptions);
      }
export function useFlexFieldsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<FlexFieldsQuery, FlexFieldsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<FlexFieldsQuery, FlexFieldsQueryVariables>(FlexFieldsDocument, baseOptions);
        }
export type FlexFieldsQueryHookResult = ReturnType<typeof useFlexFieldsQuery>;
export type FlexFieldsLazyQueryHookResult = ReturnType<typeof useFlexFieldsLazyQuery>;
export type FlexFieldsQueryResult = ApolloReactCommon.QueryResult<FlexFieldsQuery, FlexFieldsQueryVariables>;
export const GoldenRecordByTargetingCriteriaDocument = gql`
    query GoldenRecordByTargetingCriteria($targetingCriteria: TargetingCriteriaObjectType!, $first: Int, $after: String, $before: String, $last: Int, $orderBy: String) {
  goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
    edges {
      node {
        id
        headOfHousehold {
          id
          givenName
          familyName
        }
        size
        adminArea {
          id
          title
        }
        updatedAt
        address
      }
      cursor
    }
    totalCount
    edgeCount
  }
}
    `;
export type GoldenRecordByTargetingCriteriaComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables>, 'query'> & ({ variables: GoldenRecordByTargetingCriteriaQueryVariables; skip?: boolean; } | { skip: boolean; });

    export const GoldenRecordByTargetingCriteriaComponent = (props: GoldenRecordByTargetingCriteriaComponentProps) => (
      <ApolloReactComponents.Query<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables> query={GoldenRecordByTargetingCriteriaDocument} {...props} />
    );
    
export type GoldenRecordByTargetingCriteriaProps<TChildProps = {}> = ApolloReactHoc.DataProps<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables> & TChildProps;
export function withGoldenRecordByTargetingCriteria<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  GoldenRecordByTargetingCriteriaQuery,
  GoldenRecordByTargetingCriteriaQueryVariables,
  GoldenRecordByTargetingCriteriaProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables, GoldenRecordByTargetingCriteriaProps<TChildProps>>(GoldenRecordByTargetingCriteriaDocument, {
      alias: 'goldenRecordByTargetingCriteria',
      ...operationOptions
    });
};

/**
 * __useGoldenRecordByTargetingCriteriaQuery__
 *
 * To run a query within a React component, call `useGoldenRecordByTargetingCriteriaQuery` and pass it any options that fit your needs.
 * When your component renders, `useGoldenRecordByTargetingCriteriaQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useGoldenRecordByTargetingCriteriaQuery({
 *   variables: {
 *      targetingCriteria: // value for 'targetingCriteria'
 *      first: // value for 'first'
 *      after: // value for 'after'
 *      before: // value for 'before'
 *      last: // value for 'last'
 *      orderBy: // value for 'orderBy'
 *   },
 * });
 */
export function useGoldenRecordByTargetingCriteriaQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables>) {
        return ApolloReactHooks.useQuery<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables>(GoldenRecordByTargetingCriteriaDocument, baseOptions);
      }
export function useGoldenRecordByTargetingCriteriaLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables>(GoldenRecordByTargetingCriteriaDocument, baseOptions);
        }
export type GoldenRecordByTargetingCriteriaQueryHookResult = ReturnType<typeof useGoldenRecordByTargetingCriteriaQuery>;
export type GoldenRecordByTargetingCriteriaLazyQueryHookResult = ReturnType<typeof useGoldenRecordByTargetingCriteriaLazyQuery>;
export type GoldenRecordByTargetingCriteriaQueryResult = ApolloReactCommon.QueryResult<GoldenRecordByTargetingCriteriaQuery, GoldenRecordByTargetingCriteriaQueryVariables>;
export const ImportedIndividualFieldsDocument = gql`
    query ImportedIndividualFields {
  allFieldsAttributes {
    isFlexField
    id
    type
    name
    associatedWith
    labels {
      language
      label
    }
    labelEn
    hint
    choices {
      labels {
        label
        language
      }
      labelEn
      value
      admin
      listName
    }
  }
}
    `;
export type ImportedIndividualFieldsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables>, 'query'>;

    export const ImportedIndividualFieldsComponent = (props: ImportedIndividualFieldsComponentProps) => (
      <ApolloReactComponents.Query<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables> query={ImportedIndividualFieldsDocument} {...props} />
    );
    
export type ImportedIndividualFieldsProps<TChildProps = {}> = ApolloReactHoc.DataProps<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables> & TChildProps;
export function withImportedIndividualFields<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ImportedIndividualFieldsQuery,
  ImportedIndividualFieldsQueryVariables,
  ImportedIndividualFieldsProps<TChildProps>>) {
    return ApolloReactHoc.withQuery<TProps, ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables, ImportedIndividualFieldsProps<TChildProps>>(ImportedIndividualFieldsDocument, {
      alias: 'importedIndividualFields',
      ...operationOptions
    });
};

/**
 * __useImportedIndividualFieldsQuery__
 *
 * To run a query within a React component, call `useImportedIndividualFieldsQuery` and pass it any options that fit your needs.
 * When your component renders, `useImportedIndividualFieldsQuery` returns an object from Apollo Client that contains loading, error, and data properties 
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useImportedIndividualFieldsQuery({
 *   variables: {
 *   },
 * });
 */
export function useImportedIndividualFieldsQuery(baseOptions?: ApolloReactHooks.QueryHookOptions<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables>) {
        return ApolloReactHooks.useQuery<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables>(ImportedIndividualFieldsDocument, baseOptions);
      }
export function useImportedIndividualFieldsLazyQuery(baseOptions?: ApolloReactHooks.LazyQueryHookOptions<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables>) {
          return ApolloReactHooks.useLazyQuery<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables>(ImportedIndividualFieldsDocument, baseOptions);
        }
export type ImportedIndividualFieldsQueryHookResult = ReturnType<typeof useImportedIndividualFieldsQuery>;
export type ImportedIndividualFieldsLazyQueryHookResult = ReturnType<typeof useImportedIndividualFieldsLazyQuery>;
export type ImportedIndividualFieldsQueryResult = ApolloReactCommon.QueryResult<ImportedIndividualFieldsQuery, ImportedIndividualFieldsQueryVariables>;


export type ResolverTypeWrapper<T> = Promise<T> | T;

export type ResolverFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => Promise<TResult> | TResult;


export type StitchingResolver<TResult, TParent, TContext, TArgs> = {
  fragment: string;
  resolve: ResolverFn<TResult, TParent, TContext, TArgs>;
};

export type Resolver<TResult, TParent = {}, TContext = {}, TArgs = {}> =
  | ResolverFn<TResult, TParent, TContext, TArgs>
  | StitchingResolver<TResult, TParent, TContext, TArgs>;

export type SubscriptionSubscribeFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => AsyncIterator<TResult> | Promise<AsyncIterator<TResult>>;

export type SubscriptionResolveFn<TResult, TParent, TContext, TArgs> = (
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

export interface SubscriptionSubscriberObject<TResult, TKey extends string, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<{ [key in TKey]: TResult }, TParent, TContext, TArgs>;
  resolve?: SubscriptionResolveFn<TResult, { [key in TKey]: TResult }, TContext, TArgs>;
}

export interface SubscriptionResolverObject<TResult, TParent, TContext, TArgs> {
  subscribe: SubscriptionSubscribeFn<any, TParent, TContext, TArgs>;
  resolve: SubscriptionResolveFn<TResult, any, TContext, TArgs>;
}

export type SubscriptionObject<TResult, TKey extends string, TParent, TContext, TArgs> =
  | SubscriptionSubscriberObject<TResult, TKey, TParent, TContext, TArgs>
  | SubscriptionResolverObject<TResult, TParent, TContext, TArgs>;

export type SubscriptionResolver<TResult, TKey extends string, TParent = {}, TContext = {}, TArgs = {}> =
  | ((...args: any[]) => SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>)
  | SubscriptionObject<TResult, TKey, TParent, TContext, TArgs>;

export type TypeResolveFn<TTypes, TParent = {}, TContext = {}> = (
  parent: TParent,
  context: TContext,
  info: GraphQLResolveInfo
) => Maybe<TTypes>;

export type NextResolverFn<T> = () => Promise<T>;

export type DirectiveResolverFn<TResult = {}, TParent = {}, TContext = {}, TArgs = {}> = (
  next: NextResolverFn<TResult>,
  parent: TParent,
  args: TArgs,
  context: TContext,
  info: GraphQLResolveInfo
) => TResult | Promise<TResult>;

/** Mapping between all available schema types and the resolvers types */
export type ResolversTypes = {
  Query: ResolverTypeWrapper<{}>,
  ID: ResolverTypeWrapper<Scalars['ID']>,
  GrievanceTicketNode: ResolverTypeWrapper<GrievanceTicketNode>,
  Node: ResolverTypeWrapper<Node>,
  DateTime: ResolverTypeWrapper<Scalars['DateTime']>,
  UserNode: ResolverTypeWrapper<UserNode>,
  Boolean: ResolverTypeWrapper<Scalars['Boolean']>,
  String: ResolverTypeWrapper<Scalars['String']>,
  UserStatus: UserStatus,
  UserPartner: UserPartner,
  UserRoleNode: ResolverTypeWrapper<UserRoleNode>,
  UserBusinessAreaNode: ResolverTypeWrapper<UserBusinessAreaNode>,
  Int: ResolverTypeWrapper<Scalars['Int']>,
  AdminAreaTypeNodeConnection: ResolverTypeWrapper<AdminAreaTypeNodeConnection>,
  PageInfo: ResolverTypeWrapper<PageInfo>,
  AdminAreaTypeNodeEdge: ResolverTypeWrapper<AdminAreaTypeNodeEdge>,
  AdminAreaTypeNode: ResolverTypeWrapper<AdminAreaTypeNode>,
  AdminAreaNodeConnection: ResolverTypeWrapper<AdminAreaNodeConnection>,
  AdminAreaNodeEdge: ResolverTypeWrapper<AdminAreaNodeEdge>,
  AdminAreaNode: ResolverTypeWrapper<AdminAreaNode>,
  HouseholdNodeConnection: ResolverTypeWrapper<HouseholdNodeConnection>,
  HouseholdNodeEdge: ResolverTypeWrapper<HouseholdNodeEdge>,
  HouseholdNode: ResolverTypeWrapper<HouseholdNode>,
  HouseholdStatus: HouseholdStatus,
  HouseholdConsentSharing: HouseholdConsentSharing,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  IndividualNodeConnection: ResolverTypeWrapper<IndividualNodeConnection>,
  IndividualNodeEdge: ResolverTypeWrapper<IndividualNodeEdge>,
  IndividualNode: ResolverTypeWrapper<IndividualNode>,
  IndividualStatus: IndividualStatus,
  IndividualSex: IndividualSex,
  Date: ResolverTypeWrapper<Scalars['Date']>,
  IndividualMaritalStatus: IndividualMaritalStatus,
  IndividualRelationship: IndividualRelationship,
  RegistrationDataImportNode: ResolverTypeWrapper<RegistrationDataImportNode>,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  UUID: ResolverTypeWrapper<Scalars['UUID']>,
  CountAndPercentageNode: ResolverTypeWrapper<CountAndPercentageNode>,
  Float: ResolverTypeWrapper<Scalars['Float']>,
  IndividualWorkStatus: IndividualWorkStatus,
  FlexFieldsScalar: ResolverTypeWrapper<Scalars['FlexFieldsScalar']>,
  IndividualDeduplicationGoldenRecordStatus: IndividualDeduplicationGoldenRecordStatus,
  IndividualDeduplicationBatchStatus: IndividualDeduplicationBatchStatus,
  DeduplicationResultNode: ResolverTypeWrapper<DeduplicationResultNode>,
  IndividualObservedDisability: IndividualObservedDisability,
  IndividualSeeingDisability: IndividualSeeingDisability,
  IndividualHearingDisability: IndividualHearingDisability,
  IndividualPhysicalDisability: IndividualPhysicalDisability,
  IndividualMemoryDisability: IndividualMemoryDisability,
  IndividualSelfcareDisability: IndividualSelfcareDisability,
  IndividualCommsDisability: IndividualCommsDisability,
  TicketComplaintDetailsNodeConnection: ResolverTypeWrapper<TicketComplaintDetailsNodeConnection>,
  TicketComplaintDetailsNodeEdge: ResolverTypeWrapper<TicketComplaintDetailsNodeEdge>,
  TicketComplaintDetailsNode: ResolverTypeWrapper<TicketComplaintDetailsNode>,
  PaymentRecordNode: ResolverTypeWrapper<PaymentRecordNode>,
  PaymentRecordStatus: PaymentRecordStatus,
  CashPlanNode: ResolverTypeWrapper<CashPlanNode>,
  CashPlanStatus: CashPlanStatus,
  ProgramNode: ResolverTypeWrapper<ProgramNode>,
  ProgramStatus: ProgramStatus,
  Decimal: ResolverTypeWrapper<Scalars['Decimal']>,
  ProgramFrequencyOfPayments: ProgramFrequencyOfPayments,
  ProgramSector: ProgramSector,
  ProgramScope: ProgramScope,
  CashPlanNodeConnection: ResolverTypeWrapper<CashPlanNodeConnection>,
  CashPlanNodeEdge: ResolverTypeWrapper<CashPlanNodeEdge>,
  TargetPopulationNodeConnection: ResolverTypeWrapper<TargetPopulationNodeConnection>,
  TargetPopulationNodeEdge: ResolverTypeWrapper<TargetPopulationNodeEdge>,
  TargetPopulationNode: ResolverTypeWrapper<TargetPopulationNode>,
  TargetPopulationStatus: TargetPopulationStatus,
  TargetingCriteriaNode: ResolverTypeWrapper<TargetingCriteriaNode>,
  TargetingCriteriaRuleNode: ResolverTypeWrapper<TargetingCriteriaRuleNode>,
  TargetingIndividualRuleFilterBlockNode: ResolverTypeWrapper<TargetingIndividualRuleFilterBlockNode>,
  TargetingIndividualBlockRuleFilterNode: ResolverTypeWrapper<TargetingIndividualBlockRuleFilterNode>,
  TargetingIndividualBlockRuleFilterComparisionMethod: TargetingIndividualBlockRuleFilterComparisionMethod,
  Arg: ResolverTypeWrapper<Scalars['Arg']>,
  FieldAttributeNode: ResolverTypeWrapper<FieldAttributeNode>,
  LabelNode: ResolverTypeWrapper<LabelNode>,
  CoreFieldChoiceObject: ResolverTypeWrapper<CoreFieldChoiceObject>,
  TargetingCriteriaRuleFilterNode: ResolverTypeWrapper<TargetingCriteriaRuleFilterNode>,
  TargetingCriteriaRuleFilterComparisionMethod: TargetingCriteriaRuleFilterComparisionMethod,
  SteficonRuleNode: ResolverTypeWrapper<SteficonRuleNode>,
  RuleLanguage: RuleLanguage,
  PaymentRecordNodeConnection: ResolverTypeWrapper<PaymentRecordNodeConnection>,
  PaymentRecordNodeEdge: ResolverTypeWrapper<PaymentRecordNodeEdge>,
  HouseholdSelection: ResolverTypeWrapper<HouseholdSelection>,
  StatsObjectType: ResolverTypeWrapper<StatsObjectType>,
  LogEntryObjectConnection: ResolverTypeWrapper<LogEntryObjectConnection>,
  LogEntryObjectEdge: ResolverTypeWrapper<LogEntryObjectEdge>,
  LogEntryObject: ResolverTypeWrapper<LogEntryObject>,
  LogEntryAction: LogEntryAction,
  JSONLazyString: ResolverTypeWrapper<Scalars['JSONLazyString']>,
  CashPlanDeliveryType: CashPlanDeliveryType,
  CashPlanVerificationStatus: CashPlanVerificationStatus,
  CashPlanPaymentVerificationNodeConnection: ResolverTypeWrapper<CashPlanPaymentVerificationNodeConnection>,
  CashPlanPaymentVerificationNodeEdge: ResolverTypeWrapper<CashPlanPaymentVerificationNodeEdge>,
  CashPlanPaymentVerificationNode: ResolverTypeWrapper<CashPlanPaymentVerificationNode>,
  CashPlanPaymentVerificationStatus: CashPlanPaymentVerificationStatus,
  CashPlanPaymentVerificationSampling: CashPlanPaymentVerificationSampling,
  CashPlanPaymentVerificationVerificationMethod: CashPlanPaymentVerificationVerificationMethod,
  AgeFilterObject: ResolverTypeWrapper<AgeFilterObject>,
  PaymentVerificationNodeConnection: ResolverTypeWrapper<PaymentVerificationNodeConnection>,
  PaymentVerificationNodeEdge: ResolverTypeWrapper<PaymentVerificationNodeEdge>,
  PaymentVerificationNode: ResolverTypeWrapper<PaymentVerificationNode>,
  PaymentVerificationStatus: PaymentVerificationStatus,
  PaymentRecordEntitlementCardStatus: PaymentRecordEntitlementCardStatus,
  PaymentRecordDeliveryType: PaymentRecordDeliveryType,
  ServiceProviderNode: ResolverTypeWrapper<ServiceProviderNode>,
  TicketSensitiveDetailsNodeConnection: ResolverTypeWrapper<TicketSensitiveDetailsNodeConnection>,
  TicketSensitiveDetailsNodeEdge: ResolverTypeWrapper<TicketSensitiveDetailsNodeEdge>,
  TicketSensitiveDetailsNode: ResolverTypeWrapper<TicketSensitiveDetailsNode>,
  TicketIndividualDataUpdateDetailsNodeConnection: ResolverTypeWrapper<TicketIndividualDataUpdateDetailsNodeConnection>,
  TicketIndividualDataUpdateDetailsNodeEdge: ResolverTypeWrapper<TicketIndividualDataUpdateDetailsNodeEdge>,
  TicketIndividualDataUpdateDetailsNode: ResolverTypeWrapper<TicketIndividualDataUpdateDetailsNode>,
  TicketDeleteIndividualDetailsNodeConnection: ResolverTypeWrapper<TicketDeleteIndividualDetailsNodeConnection>,
  TicketDeleteIndividualDetailsNodeEdge: ResolverTypeWrapper<TicketDeleteIndividualDetailsNodeEdge>,
  TicketDeleteIndividualDetailsNode: ResolverTypeWrapper<TicketDeleteIndividualDetailsNode>,
  DocumentNodeConnection: ResolverTypeWrapper<DocumentNodeConnection>,
  DocumentNodeEdge: ResolverTypeWrapper<DocumentNodeEdge>,
  DocumentNode: ResolverTypeWrapper<DocumentNode>,
  DocumentTypeNode: ResolverTypeWrapper<DocumentTypeNode>,
  DocumentTypeType: DocumentTypeType,
  IndividualIdentityNode: ResolverTypeWrapper<IndividualIdentityNode>,
  IndividualRoleInHouseholdNode: ResolverTypeWrapper<IndividualRoleInHouseholdNode>,
  IndividualRoleInHouseholdRole: IndividualRoleInHouseholdRole,
  GeoJSON: ResolverTypeWrapper<Scalars['GeoJSON']>,
  ProgramNodeConnection: ResolverTypeWrapper<ProgramNodeConnection>,
  ProgramNodeEdge: ResolverTypeWrapper<ProgramNodeEdge>,
  HouseholdOrgEnumerator: HouseholdOrgEnumerator,
  TicketHouseholdDataUpdateDetailsNodeConnection: ResolverTypeWrapper<TicketHouseholdDataUpdateDetailsNodeConnection>,
  TicketHouseholdDataUpdateDetailsNodeEdge: ResolverTypeWrapper<TicketHouseholdDataUpdateDetailsNodeEdge>,
  TicketHouseholdDataUpdateDetailsNode: ResolverTypeWrapper<TicketHouseholdDataUpdateDetailsNode>,
  TicketAddIndividualDetailsNodeConnection: ResolverTypeWrapper<TicketAddIndividualDetailsNodeConnection>,
  TicketAddIndividualDetailsNodeEdge: ResolverTypeWrapper<TicketAddIndividualDetailsNodeEdge>,
  TicketAddIndividualDetailsNode: ResolverTypeWrapper<TicketAddIndividualDetailsNode>,
  GrievanceTicketNodeConnection: ResolverTypeWrapper<GrievanceTicketNodeConnection>,
  GrievanceTicketNodeEdge: ResolverTypeWrapper<GrievanceTicketNodeEdge>,
  ServiceProviderNodeConnection: ResolverTypeWrapper<ServiceProviderNodeConnection>,
  ServiceProviderNodeEdge: ResolverTypeWrapper<ServiceProviderNodeEdge>,
  RegistrationDataImportNodeConnection: ResolverTypeWrapper<RegistrationDataImportNodeConnection>,
  RegistrationDataImportNodeEdge: ResolverTypeWrapper<RegistrationDataImportNodeEdge>,
  RoleNode: ResolverTypeWrapper<RoleNode>,
  TicketNoteNodeConnection: ResolverTypeWrapper<TicketNoteNodeConnection>,
  TicketNoteNodeEdge: ResolverTypeWrapper<TicketNoteNodeEdge>,
  TicketNoteNode: ResolverTypeWrapper<TicketNoteNode>,
  UserBusinessAreaNodeConnection: ResolverTypeWrapper<UserBusinessAreaNodeConnection>,
  UserBusinessAreaNodeEdge: ResolverTypeWrapper<UserBusinessAreaNodeEdge>,
  ChoiceObject: ResolverTypeWrapper<ChoiceObject>,
  IssueTypesObject: ResolverTypeWrapper<IssueTypesObject>,
  SteficonRuleNodeConnection: ResolverTypeWrapper<SteficonRuleNodeConnection>,
  SteficonRuleNodeEdge: ResolverTypeWrapper<SteficonRuleNodeEdge>,
  RapidProFlow: ResolverTypeWrapper<RapidProFlow>,
  RapidProFlowRun: ResolverTypeWrapper<RapidProFlowRun>,
  RapidProFlowResult: ResolverTypeWrapper<RapidProFlowResult>,
  GetCashplanVerificationSampleSizeInput: GetCashplanVerificationSampleSizeInput,
  FullListArguments: FullListArguments,
  RandomSamplingArguments: RandomSamplingArguments,
  AgeInput: AgeInput,
  GetCashplanVerificationSampleSizeObject: ResolverTypeWrapper<GetCashplanVerificationSampleSizeObject>,
  BusinessAreaNodeConnection: ResolverTypeWrapper<BusinessAreaNodeConnection>,
  BusinessAreaNodeEdge: ResolverTypeWrapper<BusinessAreaNodeEdge>,
  BusinessAreaNode: ResolverTypeWrapper<BusinessAreaNode>,
  GroupAttributeNode: ResolverTypeWrapper<GroupAttributeNode>,
  JSONString: ResolverTypeWrapper<Scalars['JSONString']>,
  KoboAssetObject: ResolverTypeWrapper<KoboAssetObject>,
  KoboAssetObjectConnection: ResolverTypeWrapper<KoboAssetObjectConnection>,
  KoboAssetObjectEdge: ResolverTypeWrapper<KoboAssetObjectEdge>,
  TargetingCriteriaObjectType: TargetingCriteriaObjectType,
  TargetingCriteriaRuleObjectType: TargetingCriteriaRuleObjectType,
  TargetingCriteriaRuleFilterObjectType: TargetingCriteriaRuleFilterObjectType,
  TargetingIndividualRuleFilterBlockObjectType: TargetingIndividualRuleFilterBlockObjectType,
  UserObjectType: ResolverTypeWrapper<UserObjectType>,
  UserNodeConnection: ResolverTypeWrapper<UserNodeConnection>,
  UserNodeEdge: ResolverTypeWrapper<UserNodeEdge>,
  ImportedHouseholdNode: ResolverTypeWrapper<ImportedHouseholdNode>,
  ImportedHouseholdConsentSharing: ImportedHouseholdConsentSharing,
  ImportedHouseholdResidenceStatus: ImportedHouseholdResidenceStatus,
  ImportedIndividualNode: ResolverTypeWrapper<ImportedIndividualNode>,
  ImportedIndividualSex: ImportedIndividualSex,
  ImportedIndividualMaritalStatus: ImportedIndividualMaritalStatus,
  RegistrationDataImportDatahubNode: ResolverTypeWrapper<RegistrationDataImportDatahubNode>,
  ImportDataNode: ResolverTypeWrapper<ImportDataNode>,
  ImportDataDataType: ImportDataDataType,
  RegistrationDataImportDatahubImportDone: RegistrationDataImportDatahubImportDone,
  ImportedHouseholdNodeConnection: ResolverTypeWrapper<ImportedHouseholdNodeConnection>,
  ImportedHouseholdNodeEdge: ResolverTypeWrapper<ImportedHouseholdNodeEdge>,
  ImportedIndividualNodeConnection: ResolverTypeWrapper<ImportedIndividualNodeConnection>,
  ImportedIndividualNodeEdge: ResolverTypeWrapper<ImportedIndividualNodeEdge>,
  ImportedIndividualWorkStatus: ImportedIndividualWorkStatus,
  ImportedIndividualDeduplicationBatchStatus: ImportedIndividualDeduplicationBatchStatus,
  ImportedIndividualDeduplicationGoldenRecordStatus: ImportedIndividualDeduplicationGoldenRecordStatus,
  ImportedIndividualObservedDisability: ImportedIndividualObservedDisability,
  ImportedIndividualSeeingDisability: ImportedIndividualSeeingDisability,
  ImportedIndividualHearingDisability: ImportedIndividualHearingDisability,
  ImportedIndividualPhysicalDisability: ImportedIndividualPhysicalDisability,
  ImportedIndividualMemoryDisability: ImportedIndividualMemoryDisability,
  ImportedIndividualSelfcareDisability: ImportedIndividualSelfcareDisability,
  ImportedIndividualCommsDisability: ImportedIndividualCommsDisability,
  ImportedDocumentNodeConnection: ResolverTypeWrapper<ImportedDocumentNodeConnection>,
  ImportedDocumentNodeEdge: ResolverTypeWrapper<ImportedDocumentNodeEdge>,
  ImportedDocumentNode: ResolverTypeWrapper<ImportedDocumentNode>,
  ImportedDocumentTypeNode: ResolverTypeWrapper<ImportedDocumentTypeNode>,
  ImportedDocumentTypeCountry: ImportedDocumentTypeCountry,
  ImportedDocumentTypeType: ImportedDocumentTypeType,
  ImportedIndividualIdentityNode: ResolverTypeWrapper<ImportedIndividualIdentityNode>,
  ImportedHouseholdOrgEnumerator: ImportedHouseholdOrgEnumerator,
  RegistrationDataImportDatahubNodeConnection: ResolverTypeWrapper<RegistrationDataImportDatahubNodeConnection>,
  RegistrationDataImportDatahubNodeEdge: ResolverTypeWrapper<RegistrationDataImportDatahubNodeEdge>,
  DjangoDebug: ResolverTypeWrapper<DjangoDebug>,
  DjangoDebugSQL: ResolverTypeWrapper<DjangoDebugSql>,
  Mutations: ResolverTypeWrapper<{}>,
  CreateGrievanceTicketInput: CreateGrievanceTicketInput,
  CreateGrievanceTicketExtrasInput: CreateGrievanceTicketExtrasInput,
  CategoryExtrasInput: CategoryExtrasInput,
  SensitiveGrievanceTicketExtras: SensitiveGrievanceTicketExtras,
  GrievanceComplaintTicketExtras: GrievanceComplaintTicketExtras,
  IssueTypeExtrasInput: IssueTypeExtrasInput,
  HouseholdDataUpdateIssueTypeExtras: HouseholdDataUpdateIssueTypeExtras,
  HouseholdUpdateDataObjectType: HouseholdUpdateDataObjectType,
  IndividualDataUpdateIssueTypeExtras: IndividualDataUpdateIssueTypeExtras,
  IndividualUpdateDataObjectType: IndividualUpdateDataObjectType,
  IndividualDeleteIssueTypeExtras: IndividualDeleteIssueTypeExtras,
  AddIndividualIssueTypeExtras: AddIndividualIssueTypeExtras,
  AddIndividualDataObjectType: AddIndividualDataObjectType,
  CreateGrievanceTicketMutation: ResolverTypeWrapper<CreateGrievanceTicketMutation>,
  CreatePaymentVerificationInput: CreatePaymentVerificationInput,
  RapidProArguments: RapidProArguments,
  CreatePaymentVerificationMutation: ResolverTypeWrapper<CreatePaymentVerificationMutation>,
  EditCashPlanPaymentVerificationInput: EditCashPlanPaymentVerificationInput,
  EditPaymentVerificationMutation: ResolverTypeWrapper<EditPaymentVerificationMutation>,
  Upload: ResolverTypeWrapper<Scalars['Upload']>,
  ImportXlsxCashPlanVerification: ResolverTypeWrapper<ImportXlsxCashPlanVerification>,
  XlsxErrorNode: ResolverTypeWrapper<XlsxErrorNode>,
  ActivateCashPlanVerificationMutation: ResolverTypeWrapper<ActivateCashPlanVerificationMutation>,
  FinishCashPlanVerificationMutation: ResolverTypeWrapper<FinishCashPlanVerificationMutation>,
  DiscardCashPlanVerificationMutation: ResolverTypeWrapper<DiscardCashPlanVerificationMutation>,
  PaymentVerificationStatusForUpdate: PaymentVerificationStatusForUpdate,
  UpdatePaymentVerificationStatusAndReceivedAmount: ResolverTypeWrapper<UpdatePaymentVerificationStatusAndReceivedAmount>,
  UpdatePaymentVerificationReceivedAndReceivedAmount: ResolverTypeWrapper<UpdatePaymentVerificationReceivedAndReceivedAmount>,
  CreateTargetPopulationInput: CreateTargetPopulationInput,
  CreateTargetPopulationMutation: ResolverTypeWrapper<CreateTargetPopulationMutation>,
  UpdateTargetPopulationInput: UpdateTargetPopulationInput,
  UpdateTargetPopulationMutation: ResolverTypeWrapper<UpdateTargetPopulationMutation>,
  CopyTargetPopulationMutationInput: CopyTargetPopulationMutationInput,
  CopyTargetPopulationInput: CopyTargetPopulationInput,
  CopyTargetPopulationMutationPayload: ResolverTypeWrapper<CopyTargetPopulationMutationPayload>,
  DeleteTargetPopulationMutationInput: DeleteTargetPopulationMutationInput,
  DeleteTargetPopulationMutationPayload: ResolverTypeWrapper<DeleteTargetPopulationMutationPayload>,
  ApproveTargetPopulationMutation: ResolverTypeWrapper<ApproveTargetPopulationMutation>,
  UnapproveTargetPopulationMutation: ResolverTypeWrapper<UnapproveTargetPopulationMutation>,
  FinalizeTargetPopulationMutation: ResolverTypeWrapper<FinalizeTargetPopulationMutation>,
  SetSteficonRuleOnTargetPopulationMutationInput: SetSteficonRuleOnTargetPopulationMutationInput,
  SetSteficonRuleOnTargetPopulationMutationPayload: ResolverTypeWrapper<SetSteficonRuleOnTargetPopulationMutationPayload>,
  CreateProgramInput: CreateProgramInput,
  CreateProgram: ResolverTypeWrapper<CreateProgram>,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: ResolverTypeWrapper<UpdateProgram>,
  DeleteProgram: ResolverTypeWrapper<DeleteProgram>,
  UploadImportDataXLSXFile: ResolverTypeWrapper<UploadImportDataXlsxFile>,
  XlsxRowErrorNode: ResolverTypeWrapper<XlsxRowErrorNode>,
  DeleteRegistrationDataImport: ResolverTypeWrapper<DeleteRegistrationDataImport>,
  RegistrationXlsxImportMutationInput: RegistrationXlsxImportMutationInput,
  RegistrationXlsxImportMutation: ResolverTypeWrapper<RegistrationXlsxImportMutation>,
  RegistrationKoboImportMutationInput: RegistrationKoboImportMutationInput,
  RegistrationKoboImportMutation: ResolverTypeWrapper<RegistrationKoboImportMutation>,
  SaveKoboProjectImportDataMutation: ResolverTypeWrapper<SaveKoboProjectImportDataMutation>,
  KoboErrorNode: ResolverTypeWrapper<KoboErrorNode>,
  MergeRegistrationDataImportMutation: ResolverTypeWrapper<MergeRegistrationDataImportMutation>,
  RegistrationDeduplicationMutation: ResolverTypeWrapper<RegistrationDeduplicationMutation>,
  CheckAgainstSanctionListMutation: ResolverTypeWrapper<CheckAgainstSanctionListMutation>,
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  Query: {},
  ID: Scalars['ID'],
  GrievanceTicketNode: GrievanceTicketNode,
  Node: Node,
  DateTime: Scalars['DateTime'],
  UserNode: UserNode,
  Boolean: Scalars['Boolean'],
  String: Scalars['String'],
  UserStatus: UserStatus,
  UserPartner: UserPartner,
  UserRoleNode: UserRoleNode,
  UserBusinessAreaNode: UserBusinessAreaNode,
  Int: Scalars['Int'],
  AdminAreaTypeNodeConnection: AdminAreaTypeNodeConnection,
  PageInfo: PageInfo,
  AdminAreaTypeNodeEdge: AdminAreaTypeNodeEdge,
  AdminAreaTypeNode: AdminAreaTypeNode,
  AdminAreaNodeConnection: AdminAreaNodeConnection,
  AdminAreaNodeEdge: AdminAreaNodeEdge,
  AdminAreaNode: AdminAreaNode,
  HouseholdNodeConnection: HouseholdNodeConnection,
  HouseholdNodeEdge: HouseholdNodeEdge,
  HouseholdNode: HouseholdNode,
  HouseholdStatus: HouseholdStatus,
  HouseholdConsentSharing: HouseholdConsentSharing,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  IndividualNodeConnection: IndividualNodeConnection,
  IndividualNodeEdge: IndividualNodeEdge,
  IndividualNode: IndividualNode,
  IndividualStatus: IndividualStatus,
  IndividualSex: IndividualSex,
  Date: Scalars['Date'],
  IndividualMaritalStatus: IndividualMaritalStatus,
  IndividualRelationship: IndividualRelationship,
  RegistrationDataImportNode: RegistrationDataImportNode,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  UUID: Scalars['UUID'],
  CountAndPercentageNode: CountAndPercentageNode,
  Float: Scalars['Float'],
  IndividualWorkStatus: IndividualWorkStatus,
  FlexFieldsScalar: Scalars['FlexFieldsScalar'],
  IndividualDeduplicationGoldenRecordStatus: IndividualDeduplicationGoldenRecordStatus,
  IndividualDeduplicationBatchStatus: IndividualDeduplicationBatchStatus,
  DeduplicationResultNode: DeduplicationResultNode,
  IndividualObservedDisability: IndividualObservedDisability,
  IndividualSeeingDisability: IndividualSeeingDisability,
  IndividualHearingDisability: IndividualHearingDisability,
  IndividualPhysicalDisability: IndividualPhysicalDisability,
  IndividualMemoryDisability: IndividualMemoryDisability,
  IndividualSelfcareDisability: IndividualSelfcareDisability,
  IndividualCommsDisability: IndividualCommsDisability,
  TicketComplaintDetailsNodeConnection: TicketComplaintDetailsNodeConnection,
  TicketComplaintDetailsNodeEdge: TicketComplaintDetailsNodeEdge,
  TicketComplaintDetailsNode: TicketComplaintDetailsNode,
  PaymentRecordNode: PaymentRecordNode,
  PaymentRecordStatus: PaymentRecordStatus,
  CashPlanNode: CashPlanNode,
  CashPlanStatus: CashPlanStatus,
  ProgramNode: ProgramNode,
  ProgramStatus: ProgramStatus,
  Decimal: Scalars['Decimal'],
  ProgramFrequencyOfPayments: ProgramFrequencyOfPayments,
  ProgramSector: ProgramSector,
  ProgramScope: ProgramScope,
  CashPlanNodeConnection: CashPlanNodeConnection,
  CashPlanNodeEdge: CashPlanNodeEdge,
  TargetPopulationNodeConnection: TargetPopulationNodeConnection,
  TargetPopulationNodeEdge: TargetPopulationNodeEdge,
  TargetPopulationNode: TargetPopulationNode,
  TargetPopulationStatus: TargetPopulationStatus,
  TargetingCriteriaNode: TargetingCriteriaNode,
  TargetingCriteriaRuleNode: TargetingCriteriaRuleNode,
  TargetingIndividualRuleFilterBlockNode: TargetingIndividualRuleFilterBlockNode,
  TargetingIndividualBlockRuleFilterNode: TargetingIndividualBlockRuleFilterNode,
  TargetingIndividualBlockRuleFilterComparisionMethod: TargetingIndividualBlockRuleFilterComparisionMethod,
  Arg: Scalars['Arg'],
  FieldAttributeNode: FieldAttributeNode,
  LabelNode: LabelNode,
  CoreFieldChoiceObject: CoreFieldChoiceObject,
  TargetingCriteriaRuleFilterNode: TargetingCriteriaRuleFilterNode,
  TargetingCriteriaRuleFilterComparisionMethod: TargetingCriteriaRuleFilterComparisionMethod,
  SteficonRuleNode: SteficonRuleNode,
  RuleLanguage: RuleLanguage,
  PaymentRecordNodeConnection: PaymentRecordNodeConnection,
  PaymentRecordNodeEdge: PaymentRecordNodeEdge,
  HouseholdSelection: HouseholdSelection,
  StatsObjectType: StatsObjectType,
  LogEntryObjectConnection: LogEntryObjectConnection,
  LogEntryObjectEdge: LogEntryObjectEdge,
  LogEntryObject: LogEntryObject,
  LogEntryAction: LogEntryAction,
  JSONLazyString: Scalars['JSONLazyString'],
  CashPlanDeliveryType: CashPlanDeliveryType,
  CashPlanVerificationStatus: CashPlanVerificationStatus,
  CashPlanPaymentVerificationNodeConnection: CashPlanPaymentVerificationNodeConnection,
  CashPlanPaymentVerificationNodeEdge: CashPlanPaymentVerificationNodeEdge,
  CashPlanPaymentVerificationNode: CashPlanPaymentVerificationNode,
  CashPlanPaymentVerificationStatus: CashPlanPaymentVerificationStatus,
  CashPlanPaymentVerificationSampling: CashPlanPaymentVerificationSampling,
  CashPlanPaymentVerificationVerificationMethod: CashPlanPaymentVerificationVerificationMethod,
  AgeFilterObject: AgeFilterObject,
  PaymentVerificationNodeConnection: PaymentVerificationNodeConnection,
  PaymentVerificationNodeEdge: PaymentVerificationNodeEdge,
  PaymentVerificationNode: PaymentVerificationNode,
  PaymentVerificationStatus: PaymentVerificationStatus,
  PaymentRecordEntitlementCardStatus: PaymentRecordEntitlementCardStatus,
  PaymentRecordDeliveryType: PaymentRecordDeliveryType,
  ServiceProviderNode: ServiceProviderNode,
  TicketSensitiveDetailsNodeConnection: TicketSensitiveDetailsNodeConnection,
  TicketSensitiveDetailsNodeEdge: TicketSensitiveDetailsNodeEdge,
  TicketSensitiveDetailsNode: TicketSensitiveDetailsNode,
  TicketIndividualDataUpdateDetailsNodeConnection: TicketIndividualDataUpdateDetailsNodeConnection,
  TicketIndividualDataUpdateDetailsNodeEdge: TicketIndividualDataUpdateDetailsNodeEdge,
  TicketIndividualDataUpdateDetailsNode: TicketIndividualDataUpdateDetailsNode,
  TicketDeleteIndividualDetailsNodeConnection: TicketDeleteIndividualDetailsNodeConnection,
  TicketDeleteIndividualDetailsNodeEdge: TicketDeleteIndividualDetailsNodeEdge,
  TicketDeleteIndividualDetailsNode: TicketDeleteIndividualDetailsNode,
  DocumentNodeConnection: DocumentNodeConnection,
  DocumentNodeEdge: DocumentNodeEdge,
  DocumentNode: DocumentNode,
  DocumentTypeNode: DocumentTypeNode,
  DocumentTypeType: DocumentTypeType,
  IndividualIdentityNode: IndividualIdentityNode,
  IndividualRoleInHouseholdNode: IndividualRoleInHouseholdNode,
  IndividualRoleInHouseholdRole: IndividualRoleInHouseholdRole,
  GeoJSON: Scalars['GeoJSON'],
  ProgramNodeConnection: ProgramNodeConnection,
  ProgramNodeEdge: ProgramNodeEdge,
  HouseholdOrgEnumerator: HouseholdOrgEnumerator,
  TicketHouseholdDataUpdateDetailsNodeConnection: TicketHouseholdDataUpdateDetailsNodeConnection,
  TicketHouseholdDataUpdateDetailsNodeEdge: TicketHouseholdDataUpdateDetailsNodeEdge,
  TicketHouseholdDataUpdateDetailsNode: TicketHouseholdDataUpdateDetailsNode,
  TicketAddIndividualDetailsNodeConnection: TicketAddIndividualDetailsNodeConnection,
  TicketAddIndividualDetailsNodeEdge: TicketAddIndividualDetailsNodeEdge,
  TicketAddIndividualDetailsNode: TicketAddIndividualDetailsNode,
  GrievanceTicketNodeConnection: GrievanceTicketNodeConnection,
  GrievanceTicketNodeEdge: GrievanceTicketNodeEdge,
  ServiceProviderNodeConnection: ServiceProviderNodeConnection,
  ServiceProviderNodeEdge: ServiceProviderNodeEdge,
  RegistrationDataImportNodeConnection: RegistrationDataImportNodeConnection,
  RegistrationDataImportNodeEdge: RegistrationDataImportNodeEdge,
  RoleNode: RoleNode,
  TicketNoteNodeConnection: TicketNoteNodeConnection,
  TicketNoteNodeEdge: TicketNoteNodeEdge,
  TicketNoteNode: TicketNoteNode,
  UserBusinessAreaNodeConnection: UserBusinessAreaNodeConnection,
  UserBusinessAreaNodeEdge: UserBusinessAreaNodeEdge,
  ChoiceObject: ChoiceObject,
  IssueTypesObject: IssueTypesObject,
  SteficonRuleNodeConnection: SteficonRuleNodeConnection,
  SteficonRuleNodeEdge: SteficonRuleNodeEdge,
  RapidProFlow: RapidProFlow,
  RapidProFlowRun: RapidProFlowRun,
  RapidProFlowResult: RapidProFlowResult,
  GetCashplanVerificationSampleSizeInput: GetCashplanVerificationSampleSizeInput,
  FullListArguments: FullListArguments,
  RandomSamplingArguments: RandomSamplingArguments,
  AgeInput: AgeInput,
  GetCashplanVerificationSampleSizeObject: GetCashplanVerificationSampleSizeObject,
  BusinessAreaNodeConnection: BusinessAreaNodeConnection,
  BusinessAreaNodeEdge: BusinessAreaNodeEdge,
  BusinessAreaNode: BusinessAreaNode,
  GroupAttributeNode: GroupAttributeNode,
  JSONString: Scalars['JSONString'],
  KoboAssetObject: KoboAssetObject,
  KoboAssetObjectConnection: KoboAssetObjectConnection,
  KoboAssetObjectEdge: KoboAssetObjectEdge,
  TargetingCriteriaObjectType: TargetingCriteriaObjectType,
  TargetingCriteriaRuleObjectType: TargetingCriteriaRuleObjectType,
  TargetingCriteriaRuleFilterObjectType: TargetingCriteriaRuleFilterObjectType,
  TargetingIndividualRuleFilterBlockObjectType: TargetingIndividualRuleFilterBlockObjectType,
  UserObjectType: UserObjectType,
  UserNodeConnection: UserNodeConnection,
  UserNodeEdge: UserNodeEdge,
  ImportedHouseholdNode: ImportedHouseholdNode,
  ImportedHouseholdConsentSharing: ImportedHouseholdConsentSharing,
  ImportedHouseholdResidenceStatus: ImportedHouseholdResidenceStatus,
  ImportedIndividualNode: ImportedIndividualNode,
  ImportedIndividualSex: ImportedIndividualSex,
  ImportedIndividualMaritalStatus: ImportedIndividualMaritalStatus,
  RegistrationDataImportDatahubNode: RegistrationDataImportDatahubNode,
  ImportDataNode: ImportDataNode,
  ImportDataDataType: ImportDataDataType,
  RegistrationDataImportDatahubImportDone: RegistrationDataImportDatahubImportDone,
  ImportedHouseholdNodeConnection: ImportedHouseholdNodeConnection,
  ImportedHouseholdNodeEdge: ImportedHouseholdNodeEdge,
  ImportedIndividualNodeConnection: ImportedIndividualNodeConnection,
  ImportedIndividualNodeEdge: ImportedIndividualNodeEdge,
  ImportedIndividualWorkStatus: ImportedIndividualWorkStatus,
  ImportedIndividualDeduplicationBatchStatus: ImportedIndividualDeduplicationBatchStatus,
  ImportedIndividualDeduplicationGoldenRecordStatus: ImportedIndividualDeduplicationGoldenRecordStatus,
  ImportedIndividualObservedDisability: ImportedIndividualObservedDisability,
  ImportedIndividualSeeingDisability: ImportedIndividualSeeingDisability,
  ImportedIndividualHearingDisability: ImportedIndividualHearingDisability,
  ImportedIndividualPhysicalDisability: ImportedIndividualPhysicalDisability,
  ImportedIndividualMemoryDisability: ImportedIndividualMemoryDisability,
  ImportedIndividualSelfcareDisability: ImportedIndividualSelfcareDisability,
  ImportedIndividualCommsDisability: ImportedIndividualCommsDisability,
  ImportedDocumentNodeConnection: ImportedDocumentNodeConnection,
  ImportedDocumentNodeEdge: ImportedDocumentNodeEdge,
  ImportedDocumentNode: ImportedDocumentNode,
  ImportedDocumentTypeNode: ImportedDocumentTypeNode,
  ImportedDocumentTypeCountry: ImportedDocumentTypeCountry,
  ImportedDocumentTypeType: ImportedDocumentTypeType,
  ImportedIndividualIdentityNode: ImportedIndividualIdentityNode,
  ImportedHouseholdOrgEnumerator: ImportedHouseholdOrgEnumerator,
  RegistrationDataImportDatahubNodeConnection: RegistrationDataImportDatahubNodeConnection,
  RegistrationDataImportDatahubNodeEdge: RegistrationDataImportDatahubNodeEdge,
  DjangoDebug: DjangoDebug,
  DjangoDebugSQL: DjangoDebugSql,
  Mutations: {},
  CreateGrievanceTicketInput: CreateGrievanceTicketInput,
  CreateGrievanceTicketExtrasInput: CreateGrievanceTicketExtrasInput,
  CategoryExtrasInput: CategoryExtrasInput,
  SensitiveGrievanceTicketExtras: SensitiveGrievanceTicketExtras,
  GrievanceComplaintTicketExtras: GrievanceComplaintTicketExtras,
  IssueTypeExtrasInput: IssueTypeExtrasInput,
  HouseholdDataUpdateIssueTypeExtras: HouseholdDataUpdateIssueTypeExtras,
  HouseholdUpdateDataObjectType: HouseholdUpdateDataObjectType,
  IndividualDataUpdateIssueTypeExtras: IndividualDataUpdateIssueTypeExtras,
  IndividualUpdateDataObjectType: IndividualUpdateDataObjectType,
  IndividualDeleteIssueTypeExtras: IndividualDeleteIssueTypeExtras,
  AddIndividualIssueTypeExtras: AddIndividualIssueTypeExtras,
  AddIndividualDataObjectType: AddIndividualDataObjectType,
  CreateGrievanceTicketMutation: CreateGrievanceTicketMutation,
  CreatePaymentVerificationInput: CreatePaymentVerificationInput,
  RapidProArguments: RapidProArguments,
  CreatePaymentVerificationMutation: CreatePaymentVerificationMutation,
  EditCashPlanPaymentVerificationInput: EditCashPlanPaymentVerificationInput,
  EditPaymentVerificationMutation: EditPaymentVerificationMutation,
  Upload: Scalars['Upload'],
  ImportXlsxCashPlanVerification: ImportXlsxCashPlanVerification,
  XlsxErrorNode: XlsxErrorNode,
  ActivateCashPlanVerificationMutation: ActivateCashPlanVerificationMutation,
  FinishCashPlanVerificationMutation: FinishCashPlanVerificationMutation,
  DiscardCashPlanVerificationMutation: DiscardCashPlanVerificationMutation,
  PaymentVerificationStatusForUpdate: PaymentVerificationStatusForUpdate,
  UpdatePaymentVerificationStatusAndReceivedAmount: UpdatePaymentVerificationStatusAndReceivedAmount,
  UpdatePaymentVerificationReceivedAndReceivedAmount: UpdatePaymentVerificationReceivedAndReceivedAmount,
  CreateTargetPopulationInput: CreateTargetPopulationInput,
  CreateTargetPopulationMutation: CreateTargetPopulationMutation,
  UpdateTargetPopulationInput: UpdateTargetPopulationInput,
  UpdateTargetPopulationMutation: UpdateTargetPopulationMutation,
  CopyTargetPopulationMutationInput: CopyTargetPopulationMutationInput,
  CopyTargetPopulationInput: CopyTargetPopulationInput,
  CopyTargetPopulationMutationPayload: CopyTargetPopulationMutationPayload,
  DeleteTargetPopulationMutationInput: DeleteTargetPopulationMutationInput,
  DeleteTargetPopulationMutationPayload: DeleteTargetPopulationMutationPayload,
  ApproveTargetPopulationMutation: ApproveTargetPopulationMutation,
  UnapproveTargetPopulationMutation: UnapproveTargetPopulationMutation,
  FinalizeTargetPopulationMutation: FinalizeTargetPopulationMutation,
  SetSteficonRuleOnTargetPopulationMutationInput: SetSteficonRuleOnTargetPopulationMutationInput,
  SetSteficonRuleOnTargetPopulationMutationPayload: SetSteficonRuleOnTargetPopulationMutationPayload,
  CreateProgramInput: CreateProgramInput,
  CreateProgram: CreateProgram,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: UpdateProgram,
  DeleteProgram: DeleteProgram,
  UploadImportDataXLSXFile: UploadImportDataXlsxFile,
  XlsxRowErrorNode: XlsxRowErrorNode,
  DeleteRegistrationDataImport: DeleteRegistrationDataImport,
  RegistrationXlsxImportMutationInput: RegistrationXlsxImportMutationInput,
  RegistrationXlsxImportMutation: RegistrationXlsxImportMutation,
  RegistrationKoboImportMutationInput: RegistrationKoboImportMutationInput,
  RegistrationKoboImportMutation: RegistrationKoboImportMutation,
  SaveKoboProjectImportDataMutation: SaveKoboProjectImportDataMutation,
  KoboErrorNode: KoboErrorNode,
  MergeRegistrationDataImportMutation: MergeRegistrationDataImportMutation,
  RegistrationDeduplicationMutation: RegistrationDeduplicationMutation,
  CheckAgainstSanctionListMutation: CheckAgainstSanctionListMutation,
};

export type ActivateCashPlanVerificationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['ActivateCashPlanVerificationMutation'] = ResolversParentTypes['ActivateCashPlanVerificationMutation']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export type AdminAreaNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaNode'] = ResolversParentTypes['AdminAreaNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  title?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  parent?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType>,
  adminAreaType?: Resolver<ResolversTypes['AdminAreaTypeNode'], ParentType, ContextType>,
  lft?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  rght?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  treeId?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  level?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  children?: Resolver<ResolversTypes['AdminAreaNodeConnection'], ParentType, ContextType, AdminAreaNodeChildrenArgs>,
  householdSet?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, AdminAreaNodeHouseholdSetArgs>,
  programs?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, AdminAreaNodeProgramsArgs>,
};

export type AdminAreaNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaNodeConnection'] = ResolversParentTypes['AdminAreaNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['AdminAreaNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type AdminAreaNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaNodeEdge'] = ResolversParentTypes['AdminAreaNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type AdminAreaTypeNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaTypeNode'] = ResolversParentTypes['AdminAreaTypeNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  displayName?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  adminLevel?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  businessArea?: Resolver<Maybe<ResolversTypes['UserBusinessAreaNode']>, ParentType, ContextType>,
  locations?: Resolver<ResolversTypes['AdminAreaNodeConnection'], ParentType, ContextType, AdminAreaTypeNodeLocationsArgs>,
};

export type AdminAreaTypeNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaTypeNodeConnection'] = ResolversParentTypes['AdminAreaTypeNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['AdminAreaTypeNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type AdminAreaTypeNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaTypeNodeEdge'] = ResolversParentTypes['AdminAreaTypeNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['AdminAreaTypeNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type AgeFilterObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['AgeFilterObject'] = ResolversParentTypes['AgeFilterObject']> = {
  min?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  max?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type ApproveTargetPopulationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['ApproveTargetPopulationMutation'] = ResolversParentTypes['ApproveTargetPopulationMutation']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
};

export interface ArgScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['Arg'], any> {
  name: 'Arg'
}

export type BusinessAreaNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['BusinessAreaNode'] = ResolversParentTypes['BusinessAreaNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  code?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  longName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  regionCode?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  regionName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  koboToken?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  rapidProHost?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  rapidProApiKey?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  slug?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  hasDataSharingAgreement?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  adminAreaTypes?: Resolver<ResolversTypes['AdminAreaTypeNodeConnection'], ParentType, ContextType, BusinessAreaNodeAdminAreaTypesArgs>,
  userRoles?: Resolver<Array<ResolversTypes['UserRoleNode']>, ParentType, ContextType>,
  tickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, BusinessAreaNodeTicketsArgs>,
  householdSet?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, BusinessAreaNodeHouseholdSetArgs>,
  paymentrecordSet?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, BusinessAreaNodePaymentrecordSetArgs>,
  serviceproviderSet?: Resolver<ResolversTypes['ServiceProviderNodeConnection'], ParentType, ContextType, BusinessAreaNodeServiceproviderSetArgs>,
  programSet?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, BusinessAreaNodeProgramSetArgs>,
  cashplanSet?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, BusinessAreaNodeCashplanSetArgs>,
  targetpopulationSet?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, BusinessAreaNodeTargetpopulationSetArgs>,
  registrationdataimportSet?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, BusinessAreaNodeRegistrationdataimportSetArgs>,
};

export type BusinessAreaNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['BusinessAreaNodeConnection'] = ResolversParentTypes['BusinessAreaNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['BusinessAreaNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type BusinessAreaNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['BusinessAreaNodeEdge'] = ResolversParentTypes['BusinessAreaNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['BusinessAreaNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type CashPlanNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['CashPlanNode'] = ResolversParentTypes['CashPlanNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  caId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  caHashId?: Resolver<Maybe<ResolversTypes['UUID']>, ParentType, ContextType>,
  status?: Resolver<ResolversTypes['CashPlanStatus'], ParentType, ContextType>,
  statusDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  distributionLevel?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  startDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  endDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  dispersionDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  coverageDuration?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  coverageUnit?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  comments?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  program?: Resolver<ResolversTypes['ProgramNode'], ParentType, ContextType>,
  deliveryType?: Resolver<Maybe<ResolversTypes['CashPlanDeliveryType']>, ParentType, ContextType>,
  assistanceMeasurement?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  assistanceThrough?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  visionId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fundsCommitment?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  downPayment?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  validationAlertsCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  totalPersonsCovered?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  totalPersonsCoveredRevised?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  totalEntitledQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  totalEntitledQuantityRevised?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  totalDeliveredQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  totalUndeliveredQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  verificationStatus?: Resolver<ResolversTypes['CashPlanVerificationStatus'], ParentType, ContextType>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, CashPlanNodePaymentRecordsArgs>,
  verifications?: Resolver<ResolversTypes['CashPlanPaymentVerificationNodeConnection'], ParentType, ContextType, CashPlanNodeVerificationsArgs>,
  bankReconciliationSuccess?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  bankReconciliationError?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type CashPlanNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['CashPlanNodeConnection'] = ResolversParentTypes['CashPlanNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['CashPlanNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type CashPlanNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['CashPlanNodeEdge'] = ResolversParentTypes['CashPlanNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type CashPlanPaymentVerificationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['CashPlanPaymentVerificationNode'] = ResolversParentTypes['CashPlanPaymentVerificationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['CashPlanPaymentVerificationStatus'], ParentType, ContextType>,
  cashPlan?: Resolver<ResolversTypes['CashPlanNode'], ParentType, ContextType>,
  sampling?: Resolver<ResolversTypes['CashPlanPaymentVerificationSampling'], ParentType, ContextType>,
  verificationMethod?: Resolver<ResolversTypes['CashPlanPaymentVerificationVerificationMethod'], ParentType, ContextType>,
  sampleSize?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  respondedCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  receivedCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  notReceivedCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  receivedWithProblemsCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  confidenceInterval?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  marginOfError?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  rapidProFlowId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  rapidProFlowStartUuid?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  ageFilter?: Resolver<Maybe<ResolversTypes['AgeFilterObject']>, ParentType, ContextType>,
  excludedAdminAreasFilter?: Resolver<Maybe<Array<Maybe<ResolversTypes['String']>>>, ParentType, ContextType>,
  sexFilter?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  activationDate?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  completionDate?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  paymentRecordVerifications?: Resolver<ResolversTypes['PaymentVerificationNodeConnection'], ParentType, ContextType, CashPlanPaymentVerificationNodePaymentRecordVerificationsArgs>,
};

export type CashPlanPaymentVerificationNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['CashPlanPaymentVerificationNodeConnection'] = ResolversParentTypes['CashPlanPaymentVerificationNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['CashPlanPaymentVerificationNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type CashPlanPaymentVerificationNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['CashPlanPaymentVerificationNodeEdge'] = ResolversParentTypes['CashPlanPaymentVerificationNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['CashPlanPaymentVerificationNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type CheckAgainstSanctionListMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['CheckAgainstSanctionListMutation'] = ResolversParentTypes['CheckAgainstSanctionListMutation']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  errors?: Resolver<Maybe<Array<Maybe<ResolversTypes['XlsxRowErrorNode']>>>, ParentType, ContextType>,
};

export type ChoiceObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['ChoiceObject'] = ResolversParentTypes['ChoiceObject']> = {
  name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  value?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type CopyTargetPopulationMutationPayloadResolvers<ContextType = any, ParentType extends ResolversParentTypes['CopyTargetPopulationMutationPayload'] = ResolversParentTypes['CopyTargetPopulationMutationPayload']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
  clientMutationId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type CoreFieldChoiceObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['CoreFieldChoiceObject'] = ResolversParentTypes['CoreFieldChoiceObject']> = {
  labels?: Resolver<Maybe<Array<Maybe<ResolversTypes['LabelNode']>>>, ParentType, ContextType>,
  labelEn?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  value?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  admin?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  listName?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type CountAndPercentageNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['CountAndPercentageNode'] = ResolversParentTypes['CountAndPercentageNode']> = {
  count?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  percentage?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
};

export type CreateGrievanceTicketMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateGrievanceTicketMutation'] = ResolversParentTypes['CreateGrievanceTicketMutation']> = {
  grievanceTickets?: Resolver<Maybe<Array<Maybe<ResolversTypes['GrievanceTicketNode']>>>, ParentType, ContextType>,
};

export type CreatePaymentVerificationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreatePaymentVerificationMutation'] = ResolversParentTypes['CreatePaymentVerificationMutation']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export type CreateProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateProgram'] = ResolversParentTypes['CreateProgram']> = {
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
};

export type CreateTargetPopulationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateTargetPopulationMutation'] = ResolversParentTypes['CreateTargetPopulationMutation']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
};

export interface DateScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['Date'], any> {
  name: 'Date'
}

export interface DateTimeScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['DateTime'], any> {
  name: 'DateTime'
}

export interface DecimalScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['Decimal'], any> {
  name: 'Decimal'
}

export type DeduplicationResultNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeduplicationResultNode'] = ResolversParentTypes['DeduplicationResultNode']> = {
  hitId?: Resolver<Maybe<ResolversTypes['ID']>, ParentType, ContextType>,
  fullName?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  score?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  proximityToScore?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  location?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  age?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type DeleteProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteProgram'] = ResolversParentTypes['DeleteProgram']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type DeleteRegistrationDataImportResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteRegistrationDataImport'] = ResolversParentTypes['DeleteRegistrationDataImport']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type DeleteTargetPopulationMutationPayloadResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteTargetPopulationMutationPayload'] = ResolversParentTypes['DeleteTargetPopulationMutationPayload']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  clientMutationId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type DiscardCashPlanVerificationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['DiscardCashPlanVerificationMutation'] = ResolversParentTypes['DiscardCashPlanVerificationMutation']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export type DjangoDebugResolvers<ContextType = any, ParentType extends ResolversParentTypes['DjangoDebug'] = ResolversParentTypes['DjangoDebug']> = {
  sql?: Resolver<Maybe<Array<Maybe<ResolversTypes['DjangoDebugSQL']>>>, ParentType, ContextType>,
};

export type DjangoDebugSqlResolvers<ContextType = any, ParentType extends ResolversParentTypes['DjangoDebugSQL'] = ResolversParentTypes['DjangoDebugSQL']> = {
  vendor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  alias?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  sql?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  duration?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  rawSql?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  params?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  startTime?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  stopTime?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  isSlow?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  isSelect?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  transId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  transStatus?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  isoLevel?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  encoding?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type DocumentNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['DocumentNode'] = ResolversParentTypes['DocumentNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  documentNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  photo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  individual?: Resolver<ResolversTypes['IndividualNode'], ParentType, ContextType>,
  type?: Resolver<ResolversTypes['DocumentTypeNode'], ParentType, ContextType>,
};

export type DocumentNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['DocumentNodeConnection'] = ResolversParentTypes['DocumentNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['DocumentNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type DocumentNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['DocumentNodeEdge'] = ResolversParentTypes['DocumentNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['DocumentNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type DocumentTypeNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['DocumentTypeNode'] = ResolversParentTypes['DocumentTypeNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  label?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  type?: Resolver<ResolversTypes['DocumentTypeType'], ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['DocumentNodeConnection'], ParentType, ContextType, DocumentTypeNodeDocumentsArgs>,
};

export type EditPaymentVerificationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['EditPaymentVerificationMutation'] = ResolversParentTypes['EditPaymentVerificationMutation']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export type FieldAttributeNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['FieldAttributeNode'] = ResolversParentTypes['FieldAttributeNode']> = {
  id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  type?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  labels?: Resolver<Maybe<Array<Maybe<ResolversTypes['LabelNode']>>>, ParentType, ContextType>,
  labelEn?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  hint?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  required?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  choices?: Resolver<Maybe<Array<Maybe<ResolversTypes['CoreFieldChoiceObject']>>>, ParentType, ContextType>,
  associatedWith?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  isFlexField?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type FinalizeTargetPopulationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['FinalizeTargetPopulationMutation'] = ResolversParentTypes['FinalizeTargetPopulationMutation']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
};

export type FinishCashPlanVerificationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['FinishCashPlanVerificationMutation'] = ResolversParentTypes['FinishCashPlanVerificationMutation']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export interface FlexFieldsScalarScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['FlexFieldsScalar'], any> {
  name: 'FlexFieldsScalar'
}

export interface GeoJsonScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['GeoJSON'], any> {
  name: 'GeoJSON'
}

export type GetCashplanVerificationSampleSizeObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['GetCashplanVerificationSampleSizeObject'] = ResolversParentTypes['GetCashplanVerificationSampleSizeObject']> = {
  paymentRecordCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  sampleSize?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type GrievanceTicketNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['GrievanceTicketNode'] = ResolversParentTypes['GrievanceTicketNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  userModified?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  createdBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  assignedTo?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  status?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  category?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  issueType?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  description?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  admin?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  area?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  language?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  linkedTickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, GrievanceTicketNodeLinkedTicketsArgs>,
  grievanceticketSet?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, GrievanceTicketNodeGrievanceticketSetArgs>,
  complaintTicketDetails?: Resolver<Maybe<ResolversTypes['TicketComplaintDetailsNode']>, ParentType, ContextType>,
  sensitiveTicketDetails?: Resolver<Maybe<ResolversTypes['TicketSensitiveDetailsNode']>, ParentType, ContextType>,
  householdDataUpdateTicketDetails?: Resolver<Maybe<ResolversTypes['TicketHouseholdDataUpdateDetailsNode']>, ParentType, ContextType>,
  individualDataUpdateTicketDetails?: Resolver<Maybe<ResolversTypes['TicketIndividualDataUpdateDetailsNode']>, ParentType, ContextType>,
  addIndividualTicketDetails?: Resolver<Maybe<ResolversTypes['TicketAddIndividualDetailsNode']>, ParentType, ContextType>,
  deleteIndividualTicketDetails?: Resolver<Maybe<ResolversTypes['TicketDeleteIndividualDetailsNode']>, ParentType, ContextType>,
};

export type GrievanceTicketNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['GrievanceTicketNodeConnection'] = ResolversParentTypes['GrievanceTicketNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['GrievanceTicketNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type GrievanceTicketNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['GrievanceTicketNodeEdge'] = ResolversParentTypes['GrievanceTicketNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['GrievanceTicketNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type GroupAttributeNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['GroupAttributeNode'] = ResolversParentTypes['GroupAttributeNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  label?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  flexAttributes?: Resolver<Maybe<Array<Maybe<ResolversTypes['FieldAttributeNode']>>>, ParentType, ContextType, GroupAttributeNodeFlexAttributesArgs>,
  labelEn?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type HouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNode'] = ResolversParentTypes['HouseholdNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  lastSyncAt?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  status?: Resolver<ResolversTypes['HouseholdStatus'], ParentType, ContextType>,
  consentSign?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  consentSharing?: Resolver<ResolversTypes['HouseholdConsentSharing'], ParentType, ContextType>,
  residenceStatus?: Resolver<ResolversTypes['HouseholdResidenceStatus'], ParentType, ContextType>,
  countryOrigin?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  size?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  address?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  adminArea?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType>,
  representatives?: Resolver<ResolversTypes['IndividualNodeConnection'], ParentType, ContextType, HouseholdNodeRepresentativesArgs>,
  geopoint?: Resolver<Maybe<ResolversTypes['GeoJSON']>, ParentType, ContextType>,
  femaleAgeGroup05Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup611Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup1217Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAdultsCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  pregnantCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup05Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup611Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup1217Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAdultsCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup05DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup611DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup1217DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAdultsDisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup05DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup611DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup1217DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAdultsDisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportNode'], ParentType, ContextType>,
  programs?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, HouseholdNodeProgramsArgs>,
  returnee?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  flexFields?: Resolver<Maybe<ResolversTypes['FlexFieldsScalar']>, ParentType, ContextType>,
  firstRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  lastRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  headOfHousehold?: Resolver<ResolversTypes['IndividualNode'], ParentType, ContextType>,
  fchildHoh?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  childHoh?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  unicefId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  start?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  end?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  deviceid?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  nameEnumerator?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  orgEnumerator?: Resolver<ResolversTypes['HouseholdOrgEnumerator'], ParentType, ContextType>,
  orgNameEnumerator?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  village?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  complaintTicketDetails?: Resolver<ResolversTypes['TicketComplaintDetailsNodeConnection'], ParentType, ContextType, HouseholdNodeComplaintTicketDetailsArgs>,
  sensitiveTicketDetails?: Resolver<ResolversTypes['TicketSensitiveDetailsNodeConnection'], ParentType, ContextType, HouseholdNodeSensitiveTicketDetailsArgs>,
  householdDataUpdateTicketDetails?: Resolver<ResolversTypes['TicketHouseholdDataUpdateDetailsNodeConnection'], ParentType, ContextType, HouseholdNodeHouseholdDataUpdateTicketDetailsArgs>,
  addIndividualTicketDetails?: Resolver<ResolversTypes['TicketAddIndividualDetailsNodeConnection'], ParentType, ContextType, HouseholdNodeAddIndividualTicketDetailsArgs>,
  individualsAndRoles?: Resolver<Array<ResolversTypes['IndividualRoleInHouseholdNode']>, ParentType, ContextType>,
  individuals?: Resolver<ResolversTypes['IndividualNodeConnection'], ParentType, ContextType, HouseholdNodeIndividualsArgs>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, HouseholdNodePaymentRecordsArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, HouseholdNodeTargetPopulationsArgs>,
  selections?: Resolver<Array<ResolversTypes['HouseholdSelection']>, ParentType, ContextType>,
  totalCashReceived?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  selection?: Resolver<Maybe<ResolversTypes['HouseholdSelection']>, ParentType, ContextType>,
  sanctionListPossibleMatch?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  hasDuplicates?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type HouseholdNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNodeConnection'] = ResolversParentTypes['HouseholdNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['HouseholdNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  individualsCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type HouseholdNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNodeEdge'] = ResolversParentTypes['HouseholdNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type HouseholdSelectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdSelection'] = ResolversParentTypes['HouseholdSelection']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
  targetPopulation?: Resolver<ResolversTypes['TargetPopulationNode'], ParentType, ContextType>,
  vulnerabilityScore?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  final?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
};

export type ImportDataNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportDataNode'] = ResolversParentTypes['ImportDataNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  file?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  dataType?: Resolver<ResolversTypes['ImportDataDataType'], ParentType, ContextType>,
  numberOfHouseholds?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  numberOfIndividuals?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNode']>, ParentType, ContextType>,
};

export type ImportedDocumentNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedDocumentNode'] = ResolversParentTypes['ImportedDocumentNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  documentNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  photo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  individual?: Resolver<ResolversTypes['ImportedIndividualNode'], ParentType, ContextType>,
  type?: Resolver<ResolversTypes['ImportedDocumentTypeNode'], ParentType, ContextType>,
};

export type ImportedDocumentNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedDocumentNodeConnection'] = ResolversParentTypes['ImportedDocumentNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['ImportedDocumentNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type ImportedDocumentNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedDocumentNodeEdge'] = ResolversParentTypes['ImportedDocumentNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['ImportedDocumentNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type ImportedDocumentTypeNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedDocumentTypeNode'] = ResolversParentTypes['ImportedDocumentTypeNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['ImportedDocumentTypeCountry']>, ParentType, ContextType>,
  label?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  type?: Resolver<ResolversTypes['ImportedDocumentTypeType'], ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['ImportedDocumentNodeConnection'], ParentType, ContextType, ImportedDocumentTypeNodeDocumentsArgs>,
};

export type ImportedHouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedHouseholdNode'] = ResolversParentTypes['ImportedHouseholdNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  consentSign?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  consentSharing?: Resolver<ResolversTypes['ImportedHouseholdConsentSharing'], ParentType, ContextType>,
  residenceStatus?: Resolver<ResolversTypes['ImportedHouseholdResidenceStatus'], ParentType, ContextType>,
  countryOrigin?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  size?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  address?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  admin1?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  admin2?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  geopoint?: Resolver<Maybe<ResolversTypes['GeoJSON']>, ParentType, ContextType>,
  femaleAgeGroup05Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup611Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup1217Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAdultsCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  pregnantCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup05Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup611Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup1217Count?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAdultsCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup05DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup611DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAgeGroup1217DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  femaleAdultsDisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup05DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup611DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAgeGroup1217DisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  maleAdultsDisabledCount?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  headOfHousehold?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType>,
  fchildHoh?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  childHoh?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportDatahubNode'], ParentType, ContextType>,
  firstRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  lastRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  returnee?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  flexFields?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  start?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  end?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  deviceid?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  nameEnumerator?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  orgEnumerator?: Resolver<ResolversTypes['ImportedHouseholdOrgEnumerator'], ParentType, ContextType>,
  orgNameEnumerator?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  village?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  individuals?: Resolver<ResolversTypes['ImportedIndividualNodeConnection'], ParentType, ContextType, ImportedHouseholdNodeIndividualsArgs>,
  hasDuplicates?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type ImportedHouseholdNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedHouseholdNodeConnection'] = ResolversParentTypes['ImportedHouseholdNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['ImportedHouseholdNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type ImportedHouseholdNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedHouseholdNodeEdge'] = ResolversParentTypes['ImportedHouseholdNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type ImportedIndividualIdentityNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedIndividualIdentityNode'] = ResolversParentTypes['ImportedIndividualIdentityNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  individual?: Resolver<ResolversTypes['ImportedIndividualNode'], ParentType, ContextType>,
  documentNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  type?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type ImportedIndividualNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedIndividualNode'] = ResolversParentTypes['ImportedIndividualNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  individualId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  photo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  givenName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  middleName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  familyName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  relationship?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  sex?: Resolver<ResolversTypes['ImportedIndividualSex'], ParentType, ContextType>,
  birthDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  estimatedBirthDate?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  maritalStatus?: Resolver<ResolversTypes['ImportedIndividualMaritalStatus'], ParentType, ContextType>,
  phoneNo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  phoneNoAlternative?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType>,
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportDatahubNode'], ParentType, ContextType>,
  disability?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  workStatus?: Resolver<Maybe<ResolversTypes['ImportedIndividualWorkStatus']>, ParentType, ContextType>,
  firstRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  lastRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  deduplicationBatchStatus?: Resolver<Maybe<ResolversTypes['ImportedIndividualDeduplicationBatchStatus']>, ParentType, ContextType>,
  deduplicationGoldenRecordStatus?: Resolver<Maybe<ResolversTypes['ImportedIndividualDeduplicationGoldenRecordStatus']>, ParentType, ContextType>,
  deduplicationBatchResults?: Resolver<Maybe<Array<Maybe<ResolversTypes['DeduplicationResultNode']>>>, ParentType, ContextType>,
  deduplicationGoldenRecordResults?: Resolver<Maybe<Array<Maybe<ResolversTypes['DeduplicationResultNode']>>>, ParentType, ContextType>,
  flexFields?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  pregnant?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  observedDisability?: Resolver<ResolversTypes['ImportedIndividualObservedDisability'], ParentType, ContextType>,
  seeingDisability?: Resolver<Maybe<ResolversTypes['ImportedIndividualSeeingDisability']>, ParentType, ContextType>,
  hearingDisability?: Resolver<Maybe<ResolversTypes['ImportedIndividualHearingDisability']>, ParentType, ContextType>,
  physicalDisability?: Resolver<Maybe<ResolversTypes['ImportedIndividualPhysicalDisability']>, ParentType, ContextType>,
  memoryDisability?: Resolver<Maybe<ResolversTypes['ImportedIndividualMemoryDisability']>, ParentType, ContextType>,
  selfcareDisability?: Resolver<Maybe<ResolversTypes['ImportedIndividualSelfcareDisability']>, ParentType, ContextType>,
  commsDisability?: Resolver<Maybe<ResolversTypes['ImportedIndividualCommsDisability']>, ParentType, ContextType>,
  whoAnswersPhone?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  whoAnswersAltPhone?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  importedhousehold?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['ImportedDocumentNodeConnection'], ParentType, ContextType, ImportedIndividualNodeDocumentsArgs>,
  identities?: Resolver<Array<ResolversTypes['ImportedIndividualIdentityNode']>, ParentType, ContextType>,
  role?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type ImportedIndividualNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedIndividualNodeConnection'] = ResolversParentTypes['ImportedIndividualNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['ImportedIndividualNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type ImportedIndividualNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedIndividualNodeEdge'] = ResolversParentTypes['ImportedIndividualNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type ImportXlsxCashPlanVerificationResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportXlsxCashPlanVerification'] = ResolversParentTypes['ImportXlsxCashPlanVerification']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
  errors?: Resolver<Maybe<Array<Maybe<ResolversTypes['XlsxErrorNode']>>>, ParentType, ContextType>,
};

export type IndividualIdentityNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['IndividualIdentityNode'] = ResolversParentTypes['IndividualIdentityNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  individual?: Resolver<ResolversTypes['IndividualNode'], ParentType, ContextType>,
  number?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  type?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type IndividualNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['IndividualNode'] = ResolversParentTypes['IndividualNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  lastSyncAt?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  status?: Resolver<ResolversTypes['IndividualStatus'], ParentType, ContextType>,
  individualId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  photo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  givenName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  middleName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  familyName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  sex?: Resolver<ResolversTypes['IndividualSex'], ParentType, ContextType>,
  birthDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  estimatedBirthDate?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  maritalStatus?: Resolver<ResolversTypes['IndividualMaritalStatus'], ParentType, ContextType>,
  phoneNo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  phoneNoAlternative?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  relationship?: Resolver<Maybe<ResolversTypes['IndividualRelationship']>, ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportNode'], ParentType, ContextType>,
  disability?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  workStatus?: Resolver<Maybe<ResolversTypes['IndividualWorkStatus']>, ParentType, ContextType>,
  firstRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  lastRegistrationDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  flexFields?: Resolver<Maybe<ResolversTypes['FlexFieldsScalar']>, ParentType, ContextType>,
  enrolledInNutritionProgramme?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  administrationOfRutf?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  unicefId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  deduplicationGoldenRecordStatus?: Resolver<ResolversTypes['IndividualDeduplicationGoldenRecordStatus'], ParentType, ContextType>,
  deduplicationBatchStatus?: Resolver<ResolversTypes['IndividualDeduplicationBatchStatus'], ParentType, ContextType>,
  deduplicationGoldenRecordResults?: Resolver<Maybe<Array<Maybe<ResolversTypes['DeduplicationResultNode']>>>, ParentType, ContextType>,
  deduplicationBatchResults?: Resolver<Maybe<Array<Maybe<ResolversTypes['DeduplicationResultNode']>>>, ParentType, ContextType>,
  importedIndividualId?: Resolver<Maybe<ResolversTypes['UUID']>, ParentType, ContextType>,
  sanctionListPossibleMatch?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  sanctionListLastCheck?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  pregnant?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  observedDisability?: Resolver<ResolversTypes['IndividualObservedDisability'], ParentType, ContextType>,
  seeingDisability?: Resolver<Maybe<ResolversTypes['IndividualSeeingDisability']>, ParentType, ContextType>,
  hearingDisability?: Resolver<Maybe<ResolversTypes['IndividualHearingDisability']>, ParentType, ContextType>,
  physicalDisability?: Resolver<Maybe<ResolversTypes['IndividualPhysicalDisability']>, ParentType, ContextType>,
  memoryDisability?: Resolver<Maybe<ResolversTypes['IndividualMemoryDisability']>, ParentType, ContextType>,
  selfcareDisability?: Resolver<Maybe<ResolversTypes['IndividualSelfcareDisability']>, ParentType, ContextType>,
  commsDisability?: Resolver<Maybe<ResolversTypes['IndividualCommsDisability']>, ParentType, ContextType>,
  whoAnswersPhone?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  whoAnswersAltPhone?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  complaintTicketDetails?: Resolver<ResolversTypes['TicketComplaintDetailsNodeConnection'], ParentType, ContextType, IndividualNodeComplaintTicketDetailsArgs>,
  sensitiveTicketDetails?: Resolver<ResolversTypes['TicketSensitiveDetailsNodeConnection'], ParentType, ContextType, IndividualNodeSensitiveTicketDetailsArgs>,
  individualDataUpdateTicketDetails?: Resolver<ResolversTypes['TicketIndividualDataUpdateDetailsNodeConnection'], ParentType, ContextType, IndividualNodeIndividualDataUpdateTicketDetailsArgs>,
  deleteIndividualTicketDetails?: Resolver<ResolversTypes['TicketDeleteIndividualDetailsNodeConnection'], ParentType, ContextType, IndividualNodeDeleteIndividualTicketDetailsArgs>,
  representedHouseholds?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, IndividualNodeRepresentedHouseholdsArgs>,
  headingHousehold?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['DocumentNodeConnection'], ParentType, ContextType, IndividualNodeDocumentsArgs>,
  identities?: Resolver<Array<ResolversTypes['IndividualIdentityNode']>, ParentType, ContextType>,
  householdsAndRoles?: Resolver<Array<ResolversTypes['IndividualRoleInHouseholdNode']>, ParentType, ContextType>,
  role?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type IndividualNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['IndividualNodeConnection'] = ResolversParentTypes['IndividualNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['IndividualNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type IndividualNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['IndividualNodeEdge'] = ResolversParentTypes['IndividualNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type IndividualRoleInHouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['IndividualRoleInHouseholdNode'] = ResolversParentTypes['IndividualRoleInHouseholdNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  lastSyncAt?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  individual?: Resolver<ResolversTypes['IndividualNode'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
  role?: Resolver<Maybe<ResolversTypes['IndividualRoleInHouseholdRole']>, ParentType, ContextType>,
};

export type IssueTypesObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['IssueTypesObject'] = ResolversParentTypes['IssueTypesObject']> = {
  category?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  label?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  subCategories?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
};

export interface JsonLazyStringScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['JSONLazyString'], any> {
  name: 'JSONLazyString'
}

export interface JsonStringScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['JSONString'], any> {
  name: 'JSONString'
}

export type KoboAssetObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['KoboAssetObject'] = ResolversParentTypes['KoboAssetObject']> = {
  id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  sector?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  assetType?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  dateModified?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  deploymentActive?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  hasDeployment?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  xlsLink?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type KoboAssetObjectConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['KoboAssetObjectConnection'] = ResolversParentTypes['KoboAssetObjectConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['KoboAssetObjectEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type KoboAssetObjectEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['KoboAssetObjectEdge'] = ResolversParentTypes['KoboAssetObjectEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['KoboAssetObject']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type KoboErrorNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['KoboErrorNode'] = ResolversParentTypes['KoboErrorNode']> = {
  header?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  message?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type LabelNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['LabelNode'] = ResolversParentTypes['LabelNode']> = {
  language?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  label?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type LogEntryObjectResolvers<ContextType = any, ParentType extends ResolversParentTypes['LogEntryObject'] = ResolversParentTypes['LogEntryObject']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  objectPk?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  objectId?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  objectRepr?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  action?: Resolver<ResolversTypes['LogEntryAction'], ParentType, ContextType>,
  changes?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  actor?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  remoteAddr?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  timestamp?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  changesDisplayDict?: Resolver<Maybe<ResolversTypes['JSONLazyString']>, ParentType, ContextType>,
};

export type LogEntryObjectConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['LogEntryObjectConnection'] = ResolversParentTypes['LogEntryObjectConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['LogEntryObjectEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type LogEntryObjectEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['LogEntryObjectEdge'] = ResolversParentTypes['LogEntryObjectEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['LogEntryObject']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type MergeRegistrationDataImportMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['MergeRegistrationDataImportMutation'] = ResolversParentTypes['MergeRegistrationDataImportMutation']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
};

export type MutationsResolvers<ContextType = any, ParentType extends ResolversParentTypes['Mutations'] = ResolversParentTypes['Mutations']> = {
  createGrievanceTicket?: Resolver<Maybe<ResolversTypes['CreateGrievanceTicketMutation']>, ParentType, ContextType, RequireFields<MutationsCreateGrievanceTicketArgs, 'input'>>,
  createCashPlanPaymentVerification?: Resolver<Maybe<ResolversTypes['CreatePaymentVerificationMutation']>, ParentType, ContextType, RequireFields<MutationsCreateCashPlanPaymentVerificationArgs, 'input'>>,
  editCashPlanPaymentVerification?: Resolver<Maybe<ResolversTypes['EditPaymentVerificationMutation']>, ParentType, ContextType, RequireFields<MutationsEditCashPlanPaymentVerificationArgs, 'input'>>,
  importXlsxCashPlanVerification?: Resolver<Maybe<ResolversTypes['ImportXlsxCashPlanVerification']>, ParentType, ContextType, RequireFields<MutationsImportXlsxCashPlanVerificationArgs, 'cashPlanVerificationId' | 'file'>>,
  activateCashPlanPaymentVerification?: Resolver<Maybe<ResolversTypes['ActivateCashPlanVerificationMutation']>, ParentType, ContextType, RequireFields<MutationsActivateCashPlanPaymentVerificationArgs, 'cashPlanVerificationId'>>,
  finishCashPlanPaymentVerification?: Resolver<Maybe<ResolversTypes['FinishCashPlanVerificationMutation']>, ParentType, ContextType, RequireFields<MutationsFinishCashPlanPaymentVerificationArgs, 'cashPlanVerificationId'>>,
  discardCashPlanPaymentVerification?: Resolver<Maybe<ResolversTypes['DiscardCashPlanVerificationMutation']>, ParentType, ContextType, RequireFields<MutationsDiscardCashPlanPaymentVerificationArgs, 'cashPlanVerificationId'>>,
  updatePaymentVerificationStatusAndReceivedAmount?: Resolver<Maybe<ResolversTypes['UpdatePaymentVerificationStatusAndReceivedAmount']>, ParentType, ContextType, RequireFields<MutationsUpdatePaymentVerificationStatusAndReceivedAmountArgs, 'paymentVerificationId' | 'receivedAmount'>>,
  updatePaymentVerificationReceivedAndReceivedAmount?: Resolver<Maybe<ResolversTypes['UpdatePaymentVerificationReceivedAndReceivedAmount']>, ParentType, ContextType, RequireFields<MutationsUpdatePaymentVerificationReceivedAndReceivedAmountArgs, 'paymentVerificationId' | 'received' | 'receivedAmount'>>,
  createTargetPopulation?: Resolver<Maybe<ResolversTypes['CreateTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsCreateTargetPopulationArgs, 'input'>>,
  updateTargetPopulation?: Resolver<Maybe<ResolversTypes['UpdateTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsUpdateTargetPopulationArgs, 'input'>>,
  copyTargetPopulation?: Resolver<Maybe<ResolversTypes['CopyTargetPopulationMutationPayload']>, ParentType, ContextType, RequireFields<MutationsCopyTargetPopulationArgs, 'input'>>,
  deleteTargetPopulation?: Resolver<Maybe<ResolversTypes['DeleteTargetPopulationMutationPayload']>, ParentType, ContextType, RequireFields<MutationsDeleteTargetPopulationArgs, 'input'>>,
  approveTargetPopulation?: Resolver<Maybe<ResolversTypes['ApproveTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsApproveTargetPopulationArgs, 'id'>>,
  unapproveTargetPopulation?: Resolver<Maybe<ResolversTypes['UnapproveTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsUnapproveTargetPopulationArgs, 'id'>>,
  finalizeTargetPopulation?: Resolver<Maybe<ResolversTypes['FinalizeTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsFinalizeTargetPopulationArgs, 'id'>>,
  setSteficonRuleOnTargetPopulation?: Resolver<Maybe<ResolversTypes['SetSteficonRuleOnTargetPopulationMutationPayload']>, ParentType, ContextType, RequireFields<MutationsSetSteficonRuleOnTargetPopulationArgs, 'input'>>,
  createProgram?: Resolver<Maybe<ResolversTypes['CreateProgram']>, ParentType, ContextType, RequireFields<MutationsCreateProgramArgs, 'programData'>>,
  updateProgram?: Resolver<Maybe<ResolversTypes['UpdateProgram']>, ParentType, ContextType, MutationsUpdateProgramArgs>,
  deleteProgram?: Resolver<Maybe<ResolversTypes['DeleteProgram']>, ParentType, ContextType, RequireFields<MutationsDeleteProgramArgs, 'programId'>>,
  uploadImportDataXlsxFile?: Resolver<Maybe<ResolversTypes['UploadImportDataXLSXFile']>, ParentType, ContextType, RequireFields<MutationsUploadImportDataXlsxFileArgs, 'businessAreaSlug' | 'file'>>,
  deleteRegistrationDataImport?: Resolver<Maybe<ResolversTypes['DeleteRegistrationDataImport']>, ParentType, ContextType, RequireFields<MutationsDeleteRegistrationDataImportArgs, 'registrationDataImportId'>>,
  registrationXlsxImport?: Resolver<Maybe<ResolversTypes['RegistrationXlsxImportMutation']>, ParentType, ContextType, RequireFields<MutationsRegistrationXlsxImportArgs, 'registrationDataImportData'>>,
  registrationKoboImport?: Resolver<Maybe<ResolversTypes['RegistrationKoboImportMutation']>, ParentType, ContextType, RequireFields<MutationsRegistrationKoboImportArgs, 'registrationDataImportData'>>,
  saveKoboImportData?: Resolver<Maybe<ResolversTypes['SaveKoboProjectImportDataMutation']>, ParentType, ContextType, RequireFields<MutationsSaveKoboImportDataArgs, 'businessAreaSlug' | 'uid'>>,
  mergeRegistrationDataImport?: Resolver<Maybe<ResolversTypes['MergeRegistrationDataImportMutation']>, ParentType, ContextType, RequireFields<MutationsMergeRegistrationDataImportArgs, 'id'>>,
  rerunDedupe?: Resolver<Maybe<ResolversTypes['RegistrationDeduplicationMutation']>, ParentType, ContextType, RequireFields<MutationsRerunDedupeArgs, 'registrationDataImportDatahubId'>>,
  checkAgainstSanctionList?: Resolver<Maybe<ResolversTypes['CheckAgainstSanctionListMutation']>, ParentType, ContextType, RequireFields<MutationsCheckAgainstSanctionListArgs, 'file'>>,
};

export type NodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['Node'] = ResolversParentTypes['Node']> = {
  __resolveType: TypeResolveFn<'GrievanceTicketNode' | 'UserNode' | 'UserBusinessAreaNode' | 'AdminAreaTypeNode' | 'AdminAreaNode' | 'HouseholdNode' | 'IndividualNode' | 'RegistrationDataImportNode' | 'TicketComplaintDetailsNode' | 'PaymentRecordNode' | 'CashPlanNode' | 'ProgramNode' | 'TargetPopulationNode' | 'SteficonRuleNode' | 'CashPlanPaymentVerificationNode' | 'PaymentVerificationNode' | 'ServiceProviderNode' | 'TicketSensitiveDetailsNode' | 'TicketIndividualDataUpdateDetailsNode' | 'TicketDeleteIndividualDetailsNode' | 'DocumentNode' | 'TicketHouseholdDataUpdateDetailsNode' | 'TicketAddIndividualDetailsNode' | 'TicketNoteNode' | 'BusinessAreaNode' | 'ImportedHouseholdNode' | 'ImportedIndividualNode' | 'RegistrationDataImportDatahubNode' | 'ImportDataNode' | 'ImportedDocumentNode', ParentType, ContextType>,
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
};

export type PageInfoResolvers<ContextType = any, ParentType extends ResolversParentTypes['PageInfo'] = ResolversParentTypes['PageInfo']> = {
  hasNextPage?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  hasPreviousPage?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  startCursor?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  endCursor?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type PaymentRecordNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentRecordNode'] = ResolversParentTypes['PaymentRecordNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['PaymentRecordStatus'], ParentType, ContextType>,
  statusDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  caId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  caHashId?: Resolver<Maybe<ResolversTypes['UUID']>, ParentType, ContextType>,
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  totalPersonsCovered?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  distributionModality?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  targetPopulation?: Resolver<ResolversTypes['TargetPopulationNode'], ParentType, ContextType>,
  targetPopulationCashAssistId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  entitlementCardNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  entitlementCardStatus?: Resolver<ResolversTypes['PaymentRecordEntitlementCardStatus'], ParentType, ContextType>,
  entitlementCardIssueDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  deliveryType?: Resolver<ResolversTypes['PaymentRecordDeliveryType'], ParentType, ContextType>,
  currency?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  entitlementQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  deliveredQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  deliveryDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  serviceProvider?: Resolver<ResolversTypes['ServiceProviderNode'], ParentType, ContextType>,
  transactionReferenceId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  visionId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  complaintTicketDetails?: Resolver<ResolversTypes['TicketComplaintDetailsNodeConnection'], ParentType, ContextType, PaymentRecordNodeComplaintTicketDetailsArgs>,
  sensitiveTicketDetails?: Resolver<ResolversTypes['TicketSensitiveDetailsNodeConnection'], ParentType, ContextType, PaymentRecordNodeSensitiveTicketDetailsArgs>,
  verifications?: Resolver<ResolversTypes['PaymentVerificationNodeConnection'], ParentType, ContextType, PaymentRecordNodeVerificationsArgs>,
};

export type PaymentRecordNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentRecordNodeConnection'] = ResolversParentTypes['PaymentRecordNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['PaymentRecordNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type PaymentRecordNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentRecordNodeEdge'] = ResolversParentTypes['PaymentRecordNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['PaymentRecordNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type PaymentVerificationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentVerificationNode'] = ResolversParentTypes['PaymentVerificationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  cashPlanPaymentVerification?: Resolver<ResolversTypes['CashPlanPaymentVerificationNode'], ParentType, ContextType>,
  paymentRecord?: Resolver<ResolversTypes['PaymentRecordNode'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['PaymentVerificationStatus'], ParentType, ContextType>,
  statusDate?: Resolver<Maybe<ResolversTypes['Date']>, ParentType, ContextType>,
  receivedAmount?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
};

export type PaymentVerificationNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentVerificationNodeConnection'] = ResolversParentTypes['PaymentVerificationNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['PaymentVerificationNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type PaymentVerificationNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentVerificationNodeEdge'] = ResolversParentTypes['PaymentVerificationNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['PaymentVerificationNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type ProgramNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ProgramNode'] = ResolversParentTypes['ProgramNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  lastSyncAt?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['ProgramStatus'], ParentType, ContextType>,
  startDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  endDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  description?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  caId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  caHashId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  adminAreas?: Resolver<ResolversTypes['AdminAreaNodeConnection'], ParentType, ContextType, ProgramNodeAdminAreasArgs>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  budget?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  frequencyOfPayments?: Resolver<ResolversTypes['ProgramFrequencyOfPayments'], ParentType, ContextType>,
  sector?: Resolver<ResolversTypes['ProgramSector'], ParentType, ContextType>,
  scope?: Resolver<ResolversTypes['ProgramScope'], ParentType, ContextType>,
  cashPlus?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  populationGoal?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  administrativeAreasOfImplementation?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  individualDataNeeded?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, ProgramNodeHouseholdsArgs>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, ProgramNodeCashPlansArgs>,
  targetpopulationSet?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, ProgramNodeTargetpopulationSetArgs>,
  totalEntitledQuantity?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  totalDeliveredQuantity?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  totalUndeliveredQuantity?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  totalNumberOfHouseholds?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  history?: Resolver<Maybe<ResolversTypes['LogEntryObjectConnection']>, ParentType, ContextType, ProgramNodeHistoryArgs>,
};

export type ProgramNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['ProgramNodeConnection'] = ResolversParentTypes['ProgramNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['ProgramNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type ProgramNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ProgramNodeEdge'] = ResolversParentTypes['ProgramNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type QueryResolvers<ContextType = any, ParentType extends ResolversParentTypes['Query'] = ResolversParentTypes['Query']> = {
  grievanceTicket?: Resolver<Maybe<ResolversTypes['GrievanceTicketNode']>, ParentType, ContextType, RequireFields<QueryGrievanceTicketArgs, 'id'>>,
  allGrievanceTicket?: Resolver<Maybe<ResolversTypes['GrievanceTicketNodeConnection']>, ParentType, ContextType, RequireFields<QueryAllGrievanceTicketArgs, 'businessArea'>>,
  grievanceTicketStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  grievanceTicketCategoryChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  grievanceTicketIssueTypeChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['IssueTypesObject']>>>, ParentType, ContextType>,
  allSteficonRules?: Resolver<Maybe<ResolversTypes['SteficonRuleNodeConnection']>, ParentType, ContextType, QueryAllSteficonRulesArgs>,
  paymentRecord?: Resolver<Maybe<ResolversTypes['PaymentRecordNode']>, ParentType, ContextType, RequireFields<QueryPaymentRecordArgs, 'id'>>,
  paymentRecordVerification?: Resolver<Maybe<ResolversTypes['PaymentVerificationNode']>, ParentType, ContextType, RequireFields<QueryPaymentRecordVerificationArgs, 'id'>>,
  allPaymentRecords?: Resolver<Maybe<ResolversTypes['PaymentRecordNodeConnection']>, ParentType, ContextType, QueryAllPaymentRecordsArgs>,
  allPaymentVerifications?: Resolver<Maybe<ResolversTypes['PaymentVerificationNodeConnection']>, ParentType, ContextType, QueryAllPaymentVerificationsArgs>,
  paymentRecordStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  paymentRecordEntitlementCardStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  paymentRecordDeliveryTypeChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  cashPlanVerificationStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  cashPlanVerificationSamplingChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  cashPlanVerificationVerificationMethodChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  paymentVerificationStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  allRapidProFlows?: Resolver<Maybe<Array<Maybe<ResolversTypes['RapidProFlow']>>>, ParentType, ContextType, RequireFields<QueryAllRapidProFlowsArgs, 'businessAreaSlug'>>,
  sampleSize?: Resolver<Maybe<ResolversTypes['GetCashplanVerificationSampleSizeObject']>, ParentType, ContextType, QuerySampleSizeArgs>,
  adminArea?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType, RequireFields<QueryAdminAreaArgs, 'id'>>,
  allAdminAreas?: Resolver<Maybe<ResolversTypes['AdminAreaNodeConnection']>, ParentType, ContextType, QueryAllAdminAreasArgs>,
  allBusinessAreas?: Resolver<Maybe<ResolversTypes['BusinessAreaNodeConnection']>, ParentType, ContextType, QueryAllBusinessAreasArgs>,
  allFieldsAttributes?: Resolver<Maybe<Array<Maybe<ResolversTypes['FieldAttributeNode']>>>, ParentType, ContextType, QueryAllFieldsAttributesArgs>,
  allGroupsWithFields?: Resolver<Maybe<Array<Maybe<ResolversTypes['GroupAttributeNode']>>>, ParentType, ContextType>,
  koboProject?: Resolver<Maybe<ResolversTypes['KoboAssetObject']>, ParentType, ContextType, RequireFields<QueryKoboProjectArgs, 'uid' | 'businessAreaSlug'>>,
  allKoboProjects?: Resolver<Maybe<ResolversTypes['KoboAssetObjectConnection']>, ParentType, ContextType, RequireFields<QueryAllKoboProjectsArgs, 'businessAreaSlug'>>,
  cashAssistUrlPrefix?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType, RequireFields<QueryProgramArgs, 'id'>>,
  allPrograms?: Resolver<Maybe<ResolversTypes['ProgramNodeConnection']>, ParentType, ContextType, RequireFields<QueryAllProgramsArgs, 'businessArea'>>,
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType, RequireFields<QueryCashPlanArgs, 'id'>>,
  allCashPlans?: Resolver<Maybe<ResolversTypes['CashPlanNodeConnection']>, ParentType, ContextType, QueryAllCashPlansArgs>,
  programStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  programFrequencyOfPaymentsChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  programSectorChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  programScopeChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  cashPlanStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType, RequireFields<QueryTargetPopulationArgs, 'id'>>,
  allTargetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNodeConnection']>, ParentType, ContextType, QueryAllTargetPopulationArgs>,
  goldenRecordByTargetingCriteria?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, RequireFields<QueryGoldenRecordByTargetingCriteriaArgs, 'targetingCriteria'>>,
  candidateHouseholdsListByTargetingCriteria?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, RequireFields<QueryCandidateHouseholdsListByTargetingCriteriaArgs, 'targetPopulation'>>,
  finalHouseholdsListByTargetingCriteria?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, RequireFields<QueryFinalHouseholdsListByTargetingCriteriaArgs, 'targetPopulation'>>,
  targetPopulationStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType, RequireFields<QueryHouseholdArgs, 'id'>>,
  allHouseholds?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, QueryAllHouseholdsArgs>,
  individual?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType, RequireFields<QueryIndividualArgs, 'id'>>,
  allIndividuals?: Resolver<Maybe<ResolversTypes['IndividualNodeConnection']>, ParentType, ContextType, QueryAllIndividualsArgs>,
  residenceStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  sexChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  maritalStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  relationshipChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  roleChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  me?: Resolver<Maybe<ResolversTypes['UserObjectType']>, ParentType, ContextType>,
  allUsers?: Resolver<Maybe<ResolversTypes['UserNodeConnection']>, ParentType, ContextType, RequireFields<QueryAllUsersArgs, 'businessArea'>>,
  allLogEntries?: Resolver<Maybe<ResolversTypes['LogEntryObjectConnection']>, ParentType, ContextType, RequireFields<QueryAllLogEntriesArgs, 'objectId'>>,
  userRolesChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  userStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  userPartnerChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  hasAvailableUsersToExport?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType, RequireFields<QueryHasAvailableUsersToExportArgs, 'businessAreaSlug'>>,
  importedHousehold?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType, RequireFields<QueryImportedHouseholdArgs, 'id'>>,
  allImportedHouseholds?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNodeConnection']>, ParentType, ContextType, QueryAllImportedHouseholdsArgs>,
  registrationDataImportDatahub?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNode']>, ParentType, ContextType, RequireFields<QueryRegistrationDataImportDatahubArgs, 'id'>>,
  allRegistrationDataImportsDatahub?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNodeConnection']>, ParentType, ContextType, QueryAllRegistrationDataImportsDatahubArgs>,
  importedIndividual?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType, RequireFields<QueryImportedIndividualArgs, 'id'>>,
  allImportedIndividuals?: Resolver<Maybe<ResolversTypes['ImportedIndividualNodeConnection']>, ParentType, ContextType, QueryAllImportedIndividualsArgs>,
  importData?: Resolver<Maybe<ResolversTypes['ImportDataNode']>, ParentType, ContextType, RequireFields<QueryImportDataArgs, 'id'>>,
  deduplicationBatchStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  deduplicationGoldenRecordStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType, RequireFields<QueryRegistrationDataImportArgs, 'id'>>,
  allRegistrationDataImports?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNodeConnection']>, ParentType, ContextType, QueryAllRegistrationDataImportsArgs>,
  registrationDataStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  _debug?: Resolver<Maybe<ResolversTypes['DjangoDebug']>, ParentType, ContextType>,
};

export type RapidProFlowResolvers<ContextType = any, ParentType extends ResolversParentTypes['RapidProFlow'] = ResolversParentTypes['RapidProFlow']> = {
  id?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  type?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  archived?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  labels?: Resolver<Maybe<Array<Maybe<ResolversTypes['String']>>>, ParentType, ContextType>,
  expires?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  runs?: Resolver<Maybe<Array<Maybe<ResolversTypes['RapidProFlowRun']>>>, ParentType, ContextType>,
  results?: Resolver<Maybe<Array<Maybe<ResolversTypes['RapidProFlowResult']>>>, ParentType, ContextType>,
  createdOn?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  modifiedOn?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
};

export type RapidProFlowResultResolvers<ContextType = any, ParentType extends ResolversParentTypes['RapidProFlowResult'] = ResolversParentTypes['RapidProFlowResult']> = {
  key?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  name?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  categories?: Resolver<Maybe<Array<Maybe<ResolversTypes['String']>>>, ParentType, ContextType>,
  nodeUuids?: Resolver<Maybe<Array<Maybe<ResolversTypes['String']>>>, ParentType, ContextType>,
};

export type RapidProFlowRunResolvers<ContextType = any, ParentType extends ResolversParentTypes['RapidProFlowRun'] = ResolversParentTypes['RapidProFlowRun']> = {
  active?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  completed?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  interrupted?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  expired?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type RegistrationDataImportDatahubNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportDatahubNode'] = ResolversParentTypes['RegistrationDataImportDatahubNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  importDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  hctId?: Resolver<Maybe<ResolversTypes['UUID']>, ParentType, ContextType>,
  importData?: Resolver<Maybe<ResolversTypes['ImportDataNode']>, ParentType, ContextType>,
  importDone?: Resolver<ResolversTypes['RegistrationDataImportDatahubImportDone'], ParentType, ContextType>,
  businessAreaSlug?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  households?: Resolver<ResolversTypes['ImportedHouseholdNodeConnection'], ParentType, ContextType, RegistrationDataImportDatahubNodeHouseholdsArgs>,
  individuals?: Resolver<ResolversTypes['ImportedIndividualNodeConnection'], ParentType, ContextType, RegistrationDataImportDatahubNodeIndividualsArgs>,
};

export type RegistrationDataImportDatahubNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportDatahubNodeConnection'] = ResolversParentTypes['RegistrationDataImportDatahubNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['RegistrationDataImportDatahubNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type RegistrationDataImportDatahubNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportDatahubNodeEdge'] = ResolversParentTypes['RegistrationDataImportDatahubNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type RegistrationDataImportNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportNode'] = ResolversParentTypes['RegistrationDataImportNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['RegistrationDataImportStatus'], ParentType, ContextType>,
  importDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  importedBy?: Resolver<ResolversTypes['UserNode'], ParentType, ContextType>,
  dataSource?: Resolver<ResolversTypes['RegistrationDataImportDataSource'], ParentType, ContextType>,
  numberOfIndividuals?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  numberOfHouseholds?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  datahubId?: Resolver<Maybe<ResolversTypes['UUID']>, ParentType, ContextType>,
  errorMessage?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  businessArea?: Resolver<Maybe<ResolversTypes['UserBusinessAreaNode']>, ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, RegistrationDataImportNodeHouseholdsArgs>,
  individuals?: Resolver<ResolversTypes['IndividualNodeConnection'], ParentType, ContextType, RegistrationDataImportNodeIndividualsArgs>,
  batchDuplicatesCountAndPercentage?: Resolver<Maybe<ResolversTypes['CountAndPercentageNode']>, ParentType, ContextType>,
  goldenRecordDuplicatesCountAndPercentage?: Resolver<Maybe<ResolversTypes['CountAndPercentageNode']>, ParentType, ContextType>,
  batchPossibleDuplicatesCountAndPercentage?: Resolver<Maybe<ResolversTypes['CountAndPercentageNode']>, ParentType, ContextType>,
  goldenRecordPossibleDuplicatesCountAndPercentage?: Resolver<Maybe<ResolversTypes['CountAndPercentageNode']>, ParentType, ContextType>,
  batchUniqueCountAndPercentage?: Resolver<Maybe<ResolversTypes['CountAndPercentageNode']>, ParentType, ContextType>,
  goldenRecordUniqueCountAndPercentage?: Resolver<Maybe<ResolversTypes['CountAndPercentageNode']>, ParentType, ContextType>,
};

export type RegistrationDataImportNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportNodeConnection'] = ResolversParentTypes['RegistrationDataImportNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['RegistrationDataImportNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type RegistrationDataImportNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportNodeEdge'] = ResolversParentTypes['RegistrationDataImportNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type RegistrationDeduplicationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDeduplicationMutation'] = ResolversParentTypes['RegistrationDeduplicationMutation']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type RegistrationKoboImportMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationKoboImportMutation'] = ResolversParentTypes['RegistrationKoboImportMutation']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
};

export type RegistrationXlsxImportMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationXlsxImportMutation'] = ResolversParentTypes['RegistrationXlsxImportMutation']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
};

export type RoleNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RoleNode'] = ResolversParentTypes['RoleNode']> = {
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  permissions?: Resolver<Array<Maybe<ResolversTypes['String']>>, ParentType, ContextType>,
  userRoles?: Resolver<Array<ResolversTypes['UserRoleNode']>, ParentType, ContextType>,
};

export type SaveKoboProjectImportDataMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['SaveKoboProjectImportDataMutation'] = ResolversParentTypes['SaveKoboProjectImportDataMutation']> = {
  importData?: Resolver<Maybe<ResolversTypes['ImportDataNode']>, ParentType, ContextType>,
  errors?: Resolver<Maybe<Array<Maybe<ResolversTypes['KoboErrorNode']>>>, ParentType, ContextType>,
};

export type ServiceProviderNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ServiceProviderNode'] = ResolversParentTypes['ServiceProviderNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  caId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  shortName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  country?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  visionId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, ServiceProviderNodePaymentRecordsArgs>,
};

export type ServiceProviderNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['ServiceProviderNodeConnection'] = ResolversParentTypes['ServiceProviderNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['ServiceProviderNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type ServiceProviderNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ServiceProviderNodeEdge'] = ResolversParentTypes['ServiceProviderNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['ServiceProviderNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type SetSteficonRuleOnTargetPopulationMutationPayloadResolvers<ContextType = any, ParentType extends ResolversParentTypes['SetSteficonRuleOnTargetPopulationMutationPayload'] = ResolversParentTypes['SetSteficonRuleOnTargetPopulationMutationPayload']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
  clientMutationId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type StatsObjectTypeResolvers<ContextType = any, ParentType extends ResolversParentTypes['StatsObjectType'] = ResolversParentTypes['StatsObjectType']> = {
  childMale?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  childFemale?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  adultMale?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  adultFemale?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type SteficonRuleNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['SteficonRuleNode'] = ResolversParentTypes['SteficonRuleNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  definition?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  enabled?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  deprecated?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  language?: Resolver<ResolversTypes['RuleLanguage'], ParentType, ContextType>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, SteficonRuleNodeTargetPopulationsArgs>,
};

export type SteficonRuleNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['SteficonRuleNodeConnection'] = ResolversParentTypes['SteficonRuleNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['SteficonRuleNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type SteficonRuleNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['SteficonRuleNodeEdge'] = ResolversParentTypes['SteficonRuleNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['SteficonRuleNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TargetingCriteriaNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetingCriteriaNode'] = ResolversParentTypes['TargetingCriteriaNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  targetPopulationCandidate?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
  targetPopulationFinal?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
  rules?: Resolver<Maybe<Array<Maybe<ResolversTypes['TargetingCriteriaRuleNode']>>>, ParentType, ContextType>,
};

export type TargetingCriteriaRuleFilterNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetingCriteriaRuleFilterNode'] = ResolversParentTypes['TargetingCriteriaRuleFilterNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  comparisionMethod?: Resolver<ResolversTypes['TargetingCriteriaRuleFilterComparisionMethod'], ParentType, ContextType>,
  targetingCriteriaRule?: Resolver<ResolversTypes['TargetingCriteriaRuleNode'], ParentType, ContextType>,
  isFlexField?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  fieldName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  arguments?: Resolver<Maybe<Array<Maybe<ResolversTypes['Arg']>>>, ParentType, ContextType>,
  fieldAttribute?: Resolver<Maybe<ResolversTypes['FieldAttributeNode']>, ParentType, ContextType>,
};

export type TargetingCriteriaRuleNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetingCriteriaRuleNode'] = ResolversParentTypes['TargetingCriteriaRuleNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  targetingCriteria?: Resolver<ResolversTypes['TargetingCriteriaNode'], ParentType, ContextType>,
  individualsFiltersBlocks?: Resolver<Maybe<Array<Maybe<ResolversTypes['TargetingIndividualRuleFilterBlockNode']>>>, ParentType, ContextType>,
  filters?: Resolver<Maybe<Array<Maybe<ResolversTypes['TargetingCriteriaRuleFilterNode']>>>, ParentType, ContextType>,
};

export type TargetingIndividualBlockRuleFilterNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetingIndividualBlockRuleFilterNode'] = ResolversParentTypes['TargetingIndividualBlockRuleFilterNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  comparisionMethod?: Resolver<ResolversTypes['TargetingIndividualBlockRuleFilterComparisionMethod'], ParentType, ContextType>,
  individualsFiltersBlock?: Resolver<ResolversTypes['TargetingIndividualRuleFilterBlockNode'], ParentType, ContextType>,
  isFlexField?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  fieldName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  arguments?: Resolver<Maybe<Array<Maybe<ResolversTypes['Arg']>>>, ParentType, ContextType>,
  fieldAttribute?: Resolver<Maybe<ResolversTypes['FieldAttributeNode']>, ParentType, ContextType>,
};

export type TargetingIndividualRuleFilterBlockNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetingIndividualRuleFilterBlockNode'] = ResolversParentTypes['TargetingIndividualRuleFilterBlockNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  targetingCriteriaRule?: Resolver<ResolversTypes['TargetingCriteriaRuleNode'], ParentType, ContextType>,
  individualBlockFilters?: Resolver<Maybe<Array<Maybe<ResolversTypes['TargetingIndividualBlockRuleFilterNode']>>>, ParentType, ContextType>,
};

export type TargetPopulationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetPopulationNode'] = ResolversParentTypes['TargetPopulationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  isRemoved?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  caId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  caHashId?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  createdBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  approvedAt?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  approvedBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  finalizedAt?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  finalizedBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  businessArea?: Resolver<Maybe<ResolversTypes['UserBusinessAreaNode']>, ParentType, ContextType>,
  status?: Resolver<ResolversTypes['TargetPopulationStatus'], ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, TargetPopulationNodeHouseholdsArgs>,
  candidateListTotalHouseholds?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  candidateListTotalIndividuals?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  finalListTotalHouseholds?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  finalListTotalIndividuals?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  selectionComputationMetadata?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
  candidateListTargetingCriteria?: Resolver<Maybe<ResolversTypes['TargetingCriteriaNode']>, ParentType, ContextType>,
  finalListTargetingCriteria?: Resolver<Maybe<ResolversTypes['TargetingCriteriaNode']>, ParentType, ContextType>,
  sentToDatahub?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  steficonRule?: Resolver<Maybe<ResolversTypes['SteficonRuleNode']>, ParentType, ContextType>,
  vulnerabilityScoreMin?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  vulnerabilityScoreMax?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, TargetPopulationNodePaymentRecordsArgs>,
  selections?: Resolver<Array<ResolversTypes['HouseholdSelection']>, ParentType, ContextType>,
  totalHouseholds?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  totalFamilySize?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  finalList?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, TargetPopulationNodeFinalListArgs>,
  candidateStats?: Resolver<Maybe<ResolversTypes['StatsObjectType']>, ParentType, ContextType>,
  finalStats?: Resolver<Maybe<ResolversTypes['StatsObjectType']>, ParentType, ContextType>,
};

export type TargetPopulationNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetPopulationNodeConnection'] = ResolversParentTypes['TargetPopulationNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TargetPopulationNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TargetPopulationNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetPopulationNodeEdge'] = ResolversParentTypes['TargetPopulationNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketAddIndividualDetailsNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketAddIndividualDetailsNode'] = ResolversParentTypes['TicketAddIndividualDetailsNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  individualData?: Resolver<Maybe<ResolversTypes['Arg']>, ParentType, ContextType>,
};

export type TicketAddIndividualDetailsNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketAddIndividualDetailsNodeConnection'] = ResolversParentTypes['TicketAddIndividualDetailsNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketAddIndividualDetailsNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketAddIndividualDetailsNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketAddIndividualDetailsNodeEdge'] = ResolversParentTypes['TicketAddIndividualDetailsNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketAddIndividualDetailsNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketComplaintDetailsNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketComplaintDetailsNode'] = ResolversParentTypes['TicketComplaintDetailsNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  paymentRecord?: Resolver<Maybe<ResolversTypes['PaymentRecordNode']>, ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  individual?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
};

export type TicketComplaintDetailsNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketComplaintDetailsNodeConnection'] = ResolversParentTypes['TicketComplaintDetailsNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketComplaintDetailsNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketComplaintDetailsNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketComplaintDetailsNodeEdge'] = ResolversParentTypes['TicketComplaintDetailsNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketComplaintDetailsNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketDeleteIndividualDetailsNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketDeleteIndividualDetailsNode'] = ResolversParentTypes['TicketDeleteIndividualDetailsNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  individual?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
  individualData?: Resolver<Maybe<ResolversTypes['Arg']>, ParentType, ContextType>,
};

export type TicketDeleteIndividualDetailsNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketDeleteIndividualDetailsNodeConnection'] = ResolversParentTypes['TicketDeleteIndividualDetailsNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketDeleteIndividualDetailsNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketDeleteIndividualDetailsNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketDeleteIndividualDetailsNodeEdge'] = ResolversParentTypes['TicketDeleteIndividualDetailsNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketDeleteIndividualDetailsNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketHouseholdDataUpdateDetailsNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketHouseholdDataUpdateDetailsNode'] = ResolversParentTypes['TicketHouseholdDataUpdateDetailsNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  householdData?: Resolver<Maybe<ResolversTypes['Arg']>, ParentType, ContextType>,
};

export type TicketHouseholdDataUpdateDetailsNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketHouseholdDataUpdateDetailsNodeConnection'] = ResolversParentTypes['TicketHouseholdDataUpdateDetailsNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketHouseholdDataUpdateDetailsNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketHouseholdDataUpdateDetailsNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketHouseholdDataUpdateDetailsNodeEdge'] = ResolversParentTypes['TicketHouseholdDataUpdateDetailsNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketHouseholdDataUpdateDetailsNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketIndividualDataUpdateDetailsNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketIndividualDataUpdateDetailsNode'] = ResolversParentTypes['TicketIndividualDataUpdateDetailsNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  individual?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
  individualData?: Resolver<Maybe<ResolversTypes['Arg']>, ParentType, ContextType>,
};

export type TicketIndividualDataUpdateDetailsNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketIndividualDataUpdateDetailsNodeConnection'] = ResolversParentTypes['TicketIndividualDataUpdateDetailsNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketIndividualDataUpdateDetailsNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketIndividualDataUpdateDetailsNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketIndividualDataUpdateDetailsNodeEdge'] = ResolversParentTypes['TicketIndividualDataUpdateDetailsNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketIndividualDataUpdateDetailsNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketNoteNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketNoteNode'] = ResolversParentTypes['TicketNoteNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  description?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  createdBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
};

export type TicketNoteNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketNoteNodeConnection'] = ResolversParentTypes['TicketNoteNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketNoteNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketNoteNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketNoteNodeEdge'] = ResolversParentTypes['TicketNoteNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketNoteNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type TicketSensitiveDetailsNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketSensitiveDetailsNode'] = ResolversParentTypes['TicketSensitiveDetailsNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  paymentRecord?: Resolver<Maybe<ResolversTypes['PaymentRecordNode']>, ParentType, ContextType>,
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  individual?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
};

export type TicketSensitiveDetailsNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketSensitiveDetailsNodeConnection'] = ResolversParentTypes['TicketSensitiveDetailsNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['TicketSensitiveDetailsNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type TicketSensitiveDetailsNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TicketSensitiveDetailsNodeEdge'] = ResolversParentTypes['TicketSensitiveDetailsNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['TicketSensitiveDetailsNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type UnapproveTargetPopulationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['UnapproveTargetPopulationMutation'] = ResolversParentTypes['UnapproveTargetPopulationMutation']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
};

export type UpdatePaymentVerificationReceivedAndReceivedAmountResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdatePaymentVerificationReceivedAndReceivedAmount'] = ResolversParentTypes['UpdatePaymentVerificationReceivedAndReceivedAmount']> = {
  paymentVerification?: Resolver<Maybe<ResolversTypes['PaymentVerificationNode']>, ParentType, ContextType>,
};

export type UpdatePaymentVerificationStatusAndReceivedAmountResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdatePaymentVerificationStatusAndReceivedAmount'] = ResolversParentTypes['UpdatePaymentVerificationStatusAndReceivedAmount']> = {
  paymentVerification?: Resolver<Maybe<ResolversTypes['PaymentVerificationNode']>, ParentType, ContextType>,
};

export type UpdateProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateProgram'] = ResolversParentTypes['UpdateProgram']> = {
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
};

export type UpdateTargetPopulationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateTargetPopulationMutation'] = ResolversParentTypes['UpdateTargetPopulationMutation']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
};

export interface UploadScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['Upload'], any> {
  name: 'Upload'
}

export type UploadImportDataXlsxFileResolvers<ContextType = any, ParentType extends ResolversParentTypes['UploadImportDataXLSXFile'] = ResolversParentTypes['UploadImportDataXLSXFile']> = {
  importData?: Resolver<Maybe<ResolversTypes['ImportDataNode']>, ParentType, ContextType>,
  errors?: Resolver<Maybe<Array<Maybe<ResolversTypes['XlsxRowErrorNode']>>>, ParentType, ContextType>,
};

export type UserBusinessAreaNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserBusinessAreaNode'] = ResolversParentTypes['UserBusinessAreaNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  code?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  longName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  regionCode?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  regionName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  koboToken?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  rapidProHost?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  rapidProApiKey?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  slug?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  hasDataSharingAgreement?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  adminAreaTypes?: Resolver<ResolversTypes['AdminAreaTypeNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeAdminAreaTypesArgs>,
  userRoles?: Resolver<Array<ResolversTypes['UserRoleNode']>, ParentType, ContextType>,
  tickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeTicketsArgs>,
  householdSet?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeHouseholdSetArgs>,
  paymentrecordSet?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, UserBusinessAreaNodePaymentrecordSetArgs>,
  serviceproviderSet?: Resolver<ResolversTypes['ServiceProviderNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeServiceproviderSetArgs>,
  programSet?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeProgramSetArgs>,
  cashplanSet?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeCashplanSetArgs>,
  targetpopulationSet?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeTargetpopulationSetArgs>,
  registrationdataimportSet?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, UserBusinessAreaNodeRegistrationdataimportSetArgs>,
  permissions?: Resolver<Maybe<Array<Maybe<ResolversTypes['String']>>>, ParentType, ContextType>,
};

export type UserBusinessAreaNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserBusinessAreaNodeConnection'] = ResolversParentTypes['UserBusinessAreaNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['UserBusinessAreaNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type UserBusinessAreaNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserBusinessAreaNodeEdge'] = ResolversParentTypes['UserBusinessAreaNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['UserBusinessAreaNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type UserNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserNode'] = ResolversParentTypes['UserNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  lastLogin?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  isSuperuser?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  username?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  firstName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  lastName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  email?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  isStaff?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  isActive?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  dateJoined?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['UserStatus'], ParentType, ContextType>,
  partner?: Resolver<ResolversTypes['UserPartner'], ParentType, ContextType>,
  availableForExport?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  userRoles?: Resolver<Array<ResolversTypes['UserRoleNode']>, ParentType, ContextType>,
  createdTickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, UserNodeCreatedTicketsArgs>,
  assignedTickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, UserNodeAssignedTicketsArgs>,
  ticketNotes?: Resolver<ResolversTypes['TicketNoteNodeConnection'], ParentType, ContextType, UserNodeTicketNotesArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserNodeTargetPopulationsArgs>,
  approvedTargetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserNodeApprovedTargetPopulationsArgs>,
  finalizedTargetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserNodeFinalizedTargetPopulationsArgs>,
  registrationDataImports?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, UserNodeRegistrationDataImportsArgs>,
  businessAreas?: Resolver<Maybe<ResolversTypes['UserBusinessAreaNodeConnection']>, ParentType, ContextType, UserNodeBusinessAreasArgs>,
};

export type UserNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserNodeConnection'] = ResolversParentTypes['UserNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['UserNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type UserNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserNodeEdge'] = ResolversParentTypes['UserNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type UserObjectTypeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserObjectType'] = ResolversParentTypes['UserObjectType']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  lastLogin?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  isSuperuser?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  username?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  firstName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  lastName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  email?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  isStaff?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  isActive?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  dateJoined?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['UserStatus'], ParentType, ContextType>,
  partner?: Resolver<ResolversTypes['UserPartner'], ParentType, ContextType>,
  availableForExport?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  userRoles?: Resolver<Array<ResolversTypes['UserRoleNode']>, ParentType, ContextType>,
  createdTickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, UserObjectTypeCreatedTicketsArgs>,
  assignedTickets?: Resolver<ResolversTypes['GrievanceTicketNodeConnection'], ParentType, ContextType, UserObjectTypeAssignedTicketsArgs>,
  ticketNotes?: Resolver<ResolversTypes['TicketNoteNodeConnection'], ParentType, ContextType, UserObjectTypeTicketNotesArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserObjectTypeTargetPopulationsArgs>,
  approvedTargetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserObjectTypeApprovedTargetPopulationsArgs>,
  finalizedTargetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserObjectTypeFinalizedTargetPopulationsArgs>,
  registrationDataImports?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, UserObjectTypeRegistrationDataImportsArgs>,
  businessAreas?: Resolver<Maybe<ResolversTypes['UserBusinessAreaNodeConnection']>, ParentType, ContextType, UserObjectTypeBusinessAreasArgs>,
};

export type UserRoleNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserRoleNode'] = ResolversParentTypes['UserRoleNode']> = {
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  businessArea?: Resolver<ResolversTypes['UserBusinessAreaNode'], ParentType, ContextType>,
  role?: Resolver<ResolversTypes['RoleNode'], ParentType, ContextType>,
};

export interface UuidScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['UUID'], any> {
  name: 'UUID'
}

export type XlsxErrorNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['XlsxErrorNode'] = ResolversParentTypes['XlsxErrorNode']> = {
  sheet?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  coordinates?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  message?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type XlsxRowErrorNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['XlsxRowErrorNode'] = ResolversParentTypes['XlsxRowErrorNode']> = {
  rowNumber?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  header?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  message?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type Resolvers<ContextType = any> = {
  ActivateCashPlanVerificationMutation?: ActivateCashPlanVerificationMutationResolvers<ContextType>,
  AdminAreaNode?: AdminAreaNodeResolvers<ContextType>,
  AdminAreaNodeConnection?: AdminAreaNodeConnectionResolvers<ContextType>,
  AdminAreaNodeEdge?: AdminAreaNodeEdgeResolvers<ContextType>,
  AdminAreaTypeNode?: AdminAreaTypeNodeResolvers<ContextType>,
  AdminAreaTypeNodeConnection?: AdminAreaTypeNodeConnectionResolvers<ContextType>,
  AdminAreaTypeNodeEdge?: AdminAreaTypeNodeEdgeResolvers<ContextType>,
  AgeFilterObject?: AgeFilterObjectResolvers<ContextType>,
  ApproveTargetPopulationMutation?: ApproveTargetPopulationMutationResolvers<ContextType>,
  Arg?: GraphQLScalarType,
  BusinessAreaNode?: BusinessAreaNodeResolvers<ContextType>,
  BusinessAreaNodeConnection?: BusinessAreaNodeConnectionResolvers<ContextType>,
  BusinessAreaNodeEdge?: BusinessAreaNodeEdgeResolvers<ContextType>,
  CashPlanNode?: CashPlanNodeResolvers<ContextType>,
  CashPlanNodeConnection?: CashPlanNodeConnectionResolvers<ContextType>,
  CashPlanNodeEdge?: CashPlanNodeEdgeResolvers<ContextType>,
  CashPlanPaymentVerificationNode?: CashPlanPaymentVerificationNodeResolvers<ContextType>,
  CashPlanPaymentVerificationNodeConnection?: CashPlanPaymentVerificationNodeConnectionResolvers<ContextType>,
  CashPlanPaymentVerificationNodeEdge?: CashPlanPaymentVerificationNodeEdgeResolvers<ContextType>,
  CheckAgainstSanctionListMutation?: CheckAgainstSanctionListMutationResolvers<ContextType>,
  ChoiceObject?: ChoiceObjectResolvers<ContextType>,
  CopyTargetPopulationMutationPayload?: CopyTargetPopulationMutationPayloadResolvers<ContextType>,
  CoreFieldChoiceObject?: CoreFieldChoiceObjectResolvers<ContextType>,
  CountAndPercentageNode?: CountAndPercentageNodeResolvers<ContextType>,
  CreateGrievanceTicketMutation?: CreateGrievanceTicketMutationResolvers<ContextType>,
  CreatePaymentVerificationMutation?: CreatePaymentVerificationMutationResolvers<ContextType>,
  CreateProgram?: CreateProgramResolvers<ContextType>,
  CreateTargetPopulationMutation?: CreateTargetPopulationMutationResolvers<ContextType>,
  Date?: GraphQLScalarType,
  DateTime?: GraphQLScalarType,
  Decimal?: GraphQLScalarType,
  DeduplicationResultNode?: DeduplicationResultNodeResolvers<ContextType>,
  DeleteProgram?: DeleteProgramResolvers<ContextType>,
  DeleteRegistrationDataImport?: DeleteRegistrationDataImportResolvers<ContextType>,
  DeleteTargetPopulationMutationPayload?: DeleteTargetPopulationMutationPayloadResolvers<ContextType>,
  DiscardCashPlanVerificationMutation?: DiscardCashPlanVerificationMutationResolvers<ContextType>,
  DjangoDebug?: DjangoDebugResolvers<ContextType>,
  DjangoDebugSQL?: DjangoDebugSqlResolvers<ContextType>,
  DocumentNode?: DocumentNodeResolvers<ContextType>,
  DocumentNodeConnection?: DocumentNodeConnectionResolvers<ContextType>,
  DocumentNodeEdge?: DocumentNodeEdgeResolvers<ContextType>,
  DocumentTypeNode?: DocumentTypeNodeResolvers<ContextType>,
  EditPaymentVerificationMutation?: EditPaymentVerificationMutationResolvers<ContextType>,
  FieldAttributeNode?: FieldAttributeNodeResolvers<ContextType>,
  FinalizeTargetPopulationMutation?: FinalizeTargetPopulationMutationResolvers<ContextType>,
  FinishCashPlanVerificationMutation?: FinishCashPlanVerificationMutationResolvers<ContextType>,
  FlexFieldsScalar?: GraphQLScalarType,
  GeoJSON?: GraphQLScalarType,
  GetCashplanVerificationSampleSizeObject?: GetCashplanVerificationSampleSizeObjectResolvers<ContextType>,
  GrievanceTicketNode?: GrievanceTicketNodeResolvers<ContextType>,
  GrievanceTicketNodeConnection?: GrievanceTicketNodeConnectionResolvers<ContextType>,
  GrievanceTicketNodeEdge?: GrievanceTicketNodeEdgeResolvers<ContextType>,
  GroupAttributeNode?: GroupAttributeNodeResolvers<ContextType>,
  HouseholdNode?: HouseholdNodeResolvers<ContextType>,
  HouseholdNodeConnection?: HouseholdNodeConnectionResolvers<ContextType>,
  HouseholdNodeEdge?: HouseholdNodeEdgeResolvers<ContextType>,
  HouseholdSelection?: HouseholdSelectionResolvers<ContextType>,
  ImportDataNode?: ImportDataNodeResolvers<ContextType>,
  ImportedDocumentNode?: ImportedDocumentNodeResolvers<ContextType>,
  ImportedDocumentNodeConnection?: ImportedDocumentNodeConnectionResolvers<ContextType>,
  ImportedDocumentNodeEdge?: ImportedDocumentNodeEdgeResolvers<ContextType>,
  ImportedDocumentTypeNode?: ImportedDocumentTypeNodeResolvers<ContextType>,
  ImportedHouseholdNode?: ImportedHouseholdNodeResolvers<ContextType>,
  ImportedHouseholdNodeConnection?: ImportedHouseholdNodeConnectionResolvers<ContextType>,
  ImportedHouseholdNodeEdge?: ImportedHouseholdNodeEdgeResolvers<ContextType>,
  ImportedIndividualIdentityNode?: ImportedIndividualIdentityNodeResolvers<ContextType>,
  ImportedIndividualNode?: ImportedIndividualNodeResolvers<ContextType>,
  ImportedIndividualNodeConnection?: ImportedIndividualNodeConnectionResolvers<ContextType>,
  ImportedIndividualNodeEdge?: ImportedIndividualNodeEdgeResolvers<ContextType>,
  ImportXlsxCashPlanVerification?: ImportXlsxCashPlanVerificationResolvers<ContextType>,
  IndividualIdentityNode?: IndividualIdentityNodeResolvers<ContextType>,
  IndividualNode?: IndividualNodeResolvers<ContextType>,
  IndividualNodeConnection?: IndividualNodeConnectionResolvers<ContextType>,
  IndividualNodeEdge?: IndividualNodeEdgeResolvers<ContextType>,
  IndividualRoleInHouseholdNode?: IndividualRoleInHouseholdNodeResolvers<ContextType>,
  IssueTypesObject?: IssueTypesObjectResolvers<ContextType>,
  JSONLazyString?: GraphQLScalarType,
  JSONString?: GraphQLScalarType,
  KoboAssetObject?: KoboAssetObjectResolvers<ContextType>,
  KoboAssetObjectConnection?: KoboAssetObjectConnectionResolvers<ContextType>,
  KoboAssetObjectEdge?: KoboAssetObjectEdgeResolvers<ContextType>,
  KoboErrorNode?: KoboErrorNodeResolvers<ContextType>,
  LabelNode?: LabelNodeResolvers<ContextType>,
  LogEntryObject?: LogEntryObjectResolvers<ContextType>,
  LogEntryObjectConnection?: LogEntryObjectConnectionResolvers<ContextType>,
  LogEntryObjectEdge?: LogEntryObjectEdgeResolvers<ContextType>,
  MergeRegistrationDataImportMutation?: MergeRegistrationDataImportMutationResolvers<ContextType>,
  Mutations?: MutationsResolvers<ContextType>,
  Node?: NodeResolvers,
  PageInfo?: PageInfoResolvers<ContextType>,
  PaymentRecordNode?: PaymentRecordNodeResolvers<ContextType>,
  PaymentRecordNodeConnection?: PaymentRecordNodeConnectionResolvers<ContextType>,
  PaymentRecordNodeEdge?: PaymentRecordNodeEdgeResolvers<ContextType>,
  PaymentVerificationNode?: PaymentVerificationNodeResolvers<ContextType>,
  PaymentVerificationNodeConnection?: PaymentVerificationNodeConnectionResolvers<ContextType>,
  PaymentVerificationNodeEdge?: PaymentVerificationNodeEdgeResolvers<ContextType>,
  ProgramNode?: ProgramNodeResolvers<ContextType>,
  ProgramNodeConnection?: ProgramNodeConnectionResolvers<ContextType>,
  ProgramNodeEdge?: ProgramNodeEdgeResolvers<ContextType>,
  Query?: QueryResolvers<ContextType>,
  RapidProFlow?: RapidProFlowResolvers<ContextType>,
  RapidProFlowResult?: RapidProFlowResultResolvers<ContextType>,
  RapidProFlowRun?: RapidProFlowRunResolvers<ContextType>,
  RegistrationDataImportDatahubNode?: RegistrationDataImportDatahubNodeResolvers<ContextType>,
  RegistrationDataImportDatahubNodeConnection?: RegistrationDataImportDatahubNodeConnectionResolvers<ContextType>,
  RegistrationDataImportDatahubNodeEdge?: RegistrationDataImportDatahubNodeEdgeResolvers<ContextType>,
  RegistrationDataImportNode?: RegistrationDataImportNodeResolvers<ContextType>,
  RegistrationDataImportNodeConnection?: RegistrationDataImportNodeConnectionResolvers<ContextType>,
  RegistrationDataImportNodeEdge?: RegistrationDataImportNodeEdgeResolvers<ContextType>,
  RegistrationDeduplicationMutation?: RegistrationDeduplicationMutationResolvers<ContextType>,
  RegistrationKoboImportMutation?: RegistrationKoboImportMutationResolvers<ContextType>,
  RegistrationXlsxImportMutation?: RegistrationXlsxImportMutationResolvers<ContextType>,
  RoleNode?: RoleNodeResolvers<ContextType>,
  SaveKoboProjectImportDataMutation?: SaveKoboProjectImportDataMutationResolvers<ContextType>,
  ServiceProviderNode?: ServiceProviderNodeResolvers<ContextType>,
  ServiceProviderNodeConnection?: ServiceProviderNodeConnectionResolvers<ContextType>,
  ServiceProviderNodeEdge?: ServiceProviderNodeEdgeResolvers<ContextType>,
  SetSteficonRuleOnTargetPopulationMutationPayload?: SetSteficonRuleOnTargetPopulationMutationPayloadResolvers<ContextType>,
  StatsObjectType?: StatsObjectTypeResolvers<ContextType>,
  SteficonRuleNode?: SteficonRuleNodeResolvers<ContextType>,
  SteficonRuleNodeConnection?: SteficonRuleNodeConnectionResolvers<ContextType>,
  SteficonRuleNodeEdge?: SteficonRuleNodeEdgeResolvers<ContextType>,
  TargetingCriteriaNode?: TargetingCriteriaNodeResolvers<ContextType>,
  TargetingCriteriaRuleFilterNode?: TargetingCriteriaRuleFilterNodeResolvers<ContextType>,
  TargetingCriteriaRuleNode?: TargetingCriteriaRuleNodeResolvers<ContextType>,
  TargetingIndividualBlockRuleFilterNode?: TargetingIndividualBlockRuleFilterNodeResolvers<ContextType>,
  TargetingIndividualRuleFilterBlockNode?: TargetingIndividualRuleFilterBlockNodeResolvers<ContextType>,
  TargetPopulationNode?: TargetPopulationNodeResolvers<ContextType>,
  TargetPopulationNodeConnection?: TargetPopulationNodeConnectionResolvers<ContextType>,
  TargetPopulationNodeEdge?: TargetPopulationNodeEdgeResolvers<ContextType>,
  TicketAddIndividualDetailsNode?: TicketAddIndividualDetailsNodeResolvers<ContextType>,
  TicketAddIndividualDetailsNodeConnection?: TicketAddIndividualDetailsNodeConnectionResolvers<ContextType>,
  TicketAddIndividualDetailsNodeEdge?: TicketAddIndividualDetailsNodeEdgeResolvers<ContextType>,
  TicketComplaintDetailsNode?: TicketComplaintDetailsNodeResolvers<ContextType>,
  TicketComplaintDetailsNodeConnection?: TicketComplaintDetailsNodeConnectionResolvers<ContextType>,
  TicketComplaintDetailsNodeEdge?: TicketComplaintDetailsNodeEdgeResolvers<ContextType>,
  TicketDeleteIndividualDetailsNode?: TicketDeleteIndividualDetailsNodeResolvers<ContextType>,
  TicketDeleteIndividualDetailsNodeConnection?: TicketDeleteIndividualDetailsNodeConnectionResolvers<ContextType>,
  TicketDeleteIndividualDetailsNodeEdge?: TicketDeleteIndividualDetailsNodeEdgeResolvers<ContextType>,
  TicketHouseholdDataUpdateDetailsNode?: TicketHouseholdDataUpdateDetailsNodeResolvers<ContextType>,
  TicketHouseholdDataUpdateDetailsNodeConnection?: TicketHouseholdDataUpdateDetailsNodeConnectionResolvers<ContextType>,
  TicketHouseholdDataUpdateDetailsNodeEdge?: TicketHouseholdDataUpdateDetailsNodeEdgeResolvers<ContextType>,
  TicketIndividualDataUpdateDetailsNode?: TicketIndividualDataUpdateDetailsNodeResolvers<ContextType>,
  TicketIndividualDataUpdateDetailsNodeConnection?: TicketIndividualDataUpdateDetailsNodeConnectionResolvers<ContextType>,
  TicketIndividualDataUpdateDetailsNodeEdge?: TicketIndividualDataUpdateDetailsNodeEdgeResolvers<ContextType>,
  TicketNoteNode?: TicketNoteNodeResolvers<ContextType>,
  TicketNoteNodeConnection?: TicketNoteNodeConnectionResolvers<ContextType>,
  TicketNoteNodeEdge?: TicketNoteNodeEdgeResolvers<ContextType>,
  TicketSensitiveDetailsNode?: TicketSensitiveDetailsNodeResolvers<ContextType>,
  TicketSensitiveDetailsNodeConnection?: TicketSensitiveDetailsNodeConnectionResolvers<ContextType>,
  TicketSensitiveDetailsNodeEdge?: TicketSensitiveDetailsNodeEdgeResolvers<ContextType>,
  UnapproveTargetPopulationMutation?: UnapproveTargetPopulationMutationResolvers<ContextType>,
  UpdatePaymentVerificationReceivedAndReceivedAmount?: UpdatePaymentVerificationReceivedAndReceivedAmountResolvers<ContextType>,
  UpdatePaymentVerificationStatusAndReceivedAmount?: UpdatePaymentVerificationStatusAndReceivedAmountResolvers<ContextType>,
  UpdateProgram?: UpdateProgramResolvers<ContextType>,
  UpdateTargetPopulationMutation?: UpdateTargetPopulationMutationResolvers<ContextType>,
  Upload?: GraphQLScalarType,
  UploadImportDataXLSXFile?: UploadImportDataXlsxFileResolvers<ContextType>,
  UserBusinessAreaNode?: UserBusinessAreaNodeResolvers<ContextType>,
  UserBusinessAreaNodeConnection?: UserBusinessAreaNodeConnectionResolvers<ContextType>,
  UserBusinessAreaNodeEdge?: UserBusinessAreaNodeEdgeResolvers<ContextType>,
  UserNode?: UserNodeResolvers<ContextType>,
  UserNodeConnection?: UserNodeConnectionResolvers<ContextType>,
  UserNodeEdge?: UserNodeEdgeResolvers<ContextType>,
  UserObjectType?: UserObjectTypeResolvers<ContextType>,
  UserRoleNode?: UserRoleNodeResolvers<ContextType>,
  UUID?: GraphQLScalarType,
  XlsxErrorNode?: XlsxErrorNodeResolvers<ContextType>,
  XlsxRowErrorNode?: XlsxRowErrorNodeResolvers<ContextType>,
};


/**
 * @deprecated
 * Use "Resolvers" root object instead. If you wish to get "IResolvers", add "typesPrefix: I" to your config.
*/
export type IResolvers<ContextType = any> = Resolvers<ContextType>;

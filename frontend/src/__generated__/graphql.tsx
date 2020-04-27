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
  GeoJSON: any,
  UUID: any,
  Arg: any,
  Decimal: any,
  JSONLazyString: any,
  JSONString: any,
  Upload: any,
};

export type AdminAreaNode = Node & {
   __typename?: 'AdminAreaNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  title: Scalars['String'],
  parent?: Maybe<AdminAreaNode>,
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

export type ApproveRegistrationDataImportMutation = {
   __typename?: 'ApproveRegistrationDataImportMutation',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
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
  slug: Scalars['String'],
  userSet: UserNodeConnection,
  programSet: ProgramNodeConnection,
  registrationdataimportSet: RegistrationDataImportNodeConnection,
};


export type BusinessAreaNodeUserSetArgs = {
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

export type CashPlanNode = Node & {
   __typename?: 'CashPlanNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  program: ProgramNode,
  name: Scalars['String'],
  startDate: Scalars['DateTime'],
  endDate: Scalars['DateTime'],
  disbursementDate: Scalars['DateTime'],
  numberOfHouseholds: Scalars['Int'],
  createdDate: Scalars['DateTime'],
  createdBy?: Maybe<UserNode>,
  coverageDuration: Scalars['Int'],
  coverageUnits: Scalars['String'],
  targetPopulation: TargetPopulationNode,
  cashAssistId: Scalars['String'],
  distributionModality: Scalars['String'],
  fsp: Scalars['String'],
  status: CashPlanStatus,
  currency: Scalars['String'],
  totalEntitledQuantity: Scalars['Float'],
  totalDeliveredQuantity: Scalars['Float'],
  totalUndeliveredQuantity: Scalars['Float'],
  dispersionDate: Scalars['Date'],
  deliveryType: Scalars['String'],
  assistanceThrough: Scalars['String'],
  fcId: Scalars['String'],
  dpId: Scalars['String'],
  paymentRecords: PaymentRecordNodeConnection,
};


export type CashPlanNodePaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>
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

export enum CashPlanStatus {
  NotStarted = 'NOT_STARTED',
  Started = 'STARTED',
  Complete = 'COMPLETE'
}

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

export type CreateProgram = {
   __typename?: 'CreateProgram',
  program?: Maybe<ProgramNode>,
};

export type CreateProgramInput = {
  name?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['Date']>,
  endDate?: Maybe<Scalars['Date']>,
  description?: Maybe<Scalars['String']>,
  programCaId?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  scope?: Maybe<Scalars['String']>,
  cashPlus?: Maybe<Scalars['Boolean']>,
  populationGoal?: Maybe<Scalars['Int']>,
  administrativeAreasOfImplementation?: Maybe<Scalars['String']>,
  businessAreaSlug?: Maybe<Scalars['String']>,
};

export type CreateRegistrationDataImport = {
   __typename?: 'CreateRegistrationDataImport',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type CreateRegistrationDataImportExcelInput = {
  importDataId?: Maybe<Scalars['ID']>,
  name?: Maybe<Scalars['String']>,
};

export type CreateTargetPopulationInput = {
  name: Scalars['String'],
  targetingCriteria: TargetingCriteriaObjectType,
};

export type CreateTargetPopulationMutation = {
   __typename?: 'CreateTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
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
  type: Scalars['String'],
  label: Scalars['String'],
  documents: DocumentNodeConnection,
};


export type DocumentTypeNodeDocumentsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
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


export type HouseholdNode = Node & {
   __typename?: 'HouseholdNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  consent: Scalars['String'],
  residenceStatus: HouseholdResidenceStatus,
  countryOrigin?: Maybe<Scalars['String']>,
  country?: Maybe<Scalars['String']>,
  size: Scalars['Int'],
  address: Scalars['String'],
  adminArea?: Maybe<AdminAreaNode>,
  geopoint?: Maybe<Scalars['GeoJSON']>,
  unhcrId: Scalars['String'],
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
  registrationDate?: Maybe<Scalars['Date']>,
  headOfHousehold?: Maybe<IndividualNode>,
  individuals: IndividualNodeConnection,
  paymentRecords: PaymentRecordNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
  totalCashReceived?: Maybe<Scalars['Decimal']>,
};


export type HouseholdNodeProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
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
  orderBy?: Maybe<Scalars['String']>
};

export type HouseholdNodeConnection = {
   __typename?: 'HouseholdNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<HouseholdNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type HouseholdNodeEdge = {
   __typename?: 'HouseholdNodeEdge',
  node?: Maybe<HouseholdNode>,
  cursor: Scalars['String'],
};

export enum HouseholdResidenceStatus {
  Refugee = 'REFUGEE',
  Migrant = 'MIGRANT',
  Citizen = 'CITIZEN',
  Idp = 'IDP',
  Other = 'OTHER'
}

export type ImportDataNode = Node & {
   __typename?: 'ImportDataNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  xlsxFile: Scalars['String'],
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
  type: Scalars['String'],
  label: Scalars['String'],
  documents: ImportedDocumentNodeConnection,
};


export type ImportedDocumentTypeNodeDocumentsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};

export type ImportedHouseholdNode = Node & {
   __typename?: 'ImportedHouseholdNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  consent: Scalars['String'],
  residenceStatus: ImportedHouseholdResidenceStatus,
  countryOrigin?: Maybe<Scalars['String']>,
  size: Scalars['Int'],
  address: Scalars['String'],
  country?: Maybe<Scalars['String']>,
  admin1: Scalars['String'],
  admin2: Scalars['String'],
  geopoint?: Maybe<Scalars['GeoJSON']>,
  unhcrId: Scalars['String'],
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
  registrationDataImport: RegistrationDataImportDatahubNode,
  registrationDate?: Maybe<Scalars['Date']>,
  returnee: Scalars['Boolean'],
  flexFields: Scalars['JSONString'],
  individuals: ImportedIndividualNodeConnection,
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

export enum ImportedHouseholdResidenceStatus {
  Refugee = 'REFUGEE',
  Migrant = 'MIGRANT',
  Citizen = 'CITIZEN',
  Idp = 'IDP',
  Other = 'OTHER'
}

export enum ImportedIndividualMaritalStatus {
  Single = 'SINGLE',
  Married = 'MARRIED',
  Widow = 'WIDOW',
  Divorced = 'DIVORCED',
  Separated = 'SEPARATED'
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
  relationship?: Maybe<ImportedIndividualRelationship>,
  role?: Maybe<ImportedIndividualRole>,
  sex: ImportedIndividualSex,
  birthDate: Scalars['Date'],
  estimatedBirthDate?: Maybe<Scalars['Boolean']>,
  maritalStatus: ImportedIndividualMaritalStatus,
  phoneNo: Scalars['String'],
  phoneNoAlternative: Scalars['String'],
  household: ImportedHouseholdNode,
  registrationDataImport: RegistrationDataImportDatahubNode,
  disability: Scalars['Boolean'],
  flexFields: Scalars['JSONString'],
  importedhousehold?: Maybe<ImportedHouseholdNode>,
  documents: ImportedDocumentNodeConnection,
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

export enum ImportedIndividualRelationship {
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

export enum ImportedIndividualRole {
  Primary = 'PRIMARY',
  Alternate = 'ALTERNATE',
  NoRole = 'NO_ROLE'
}

export enum ImportedIndividualSex {
  Male = 'MALE',
  Female = 'FEMALE'
}

export enum IndividualMaritalStatus {
  Single = 'SINGLE',
  Married = 'MARRIED',
  Widow = 'WIDOW',
  Divorced = 'DIVORCED',
  Separated = 'SEPARATED'
}

export type IndividualNode = Node & {
   __typename?: 'IndividualNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  individualId: Scalars['String'],
  photo: Scalars['String'],
  fullName: Scalars['String'],
  givenName: Scalars['String'],
  middleName: Scalars['String'],
  familyName: Scalars['String'],
  relationship?: Maybe<IndividualRelationship>,
  role?: Maybe<IndividualRole>,
  sex: IndividualSex,
  birthDate: Scalars['Date'],
  estimatedBirthDate?: Maybe<Scalars['Boolean']>,
  maritalStatus: IndividualMaritalStatus,
  phoneNo: Scalars['String'],
  phoneNoAlternative: Scalars['String'],
  household: HouseholdNode,
  registrationDataImport: RegistrationDataImportNode,
  disability: Scalars['Boolean'],
  headingHousehold?: Maybe<HouseholdNode>,
  documents: DocumentNodeConnection,
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

export enum IndividualRole {
  Primary = 'PRIMARY',
  Alternate = 'ALTERNATE',
  NoRole = 'NO_ROLE'
}

export enum IndividualSex {
  Male = 'MALE',
  Female = 'FEMALE'
}



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
  createTargetPopulation?: Maybe<CreateTargetPopulationMutation>,
  updateTargetPopulation?: Maybe<UpdateTargetPopulationMutation>,
  copyTargetPopulation?: Maybe<CopyTargetPopulationMutationPayload>,
  deleteTargetPopulation?: Maybe<DeleteTargetPopulationMutationPayload>,
  approveTargetPopulation?: Maybe<ApproveTargetPopulationMutation>,
  unapproveTargetPopulation?: Maybe<UnapproveTargetPopulationMutation>,
  finalizeTargetPopulation?: Maybe<FinalizeTargetPopulationMutation>,
  createProgram?: Maybe<CreateProgram>,
  updateProgram?: Maybe<UpdateProgram>,
  deleteProgram?: Maybe<DeleteProgram>,
  uploadImportDataXlsxFile?: Maybe<UploadImportDataXlsxFile>,
  deleteRegistrationDataImport?: Maybe<DeleteRegistrationDataImport>,
  createRegistrationDataImport?: Maybe<CreateRegistrationDataImport>,
  approveRegistrationDataImport?: Maybe<ApproveRegistrationDataImportMutation>,
  unapproveRegistrationDataImport?: Maybe<UnapproveRegistrationDataImportMutation>,
  mergeRegistrationDataImport?: Maybe<MergeRegistrationDataImportMutation>,
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
  id: Scalars['ID'],
  programId: Scalars['ID']
};


export type MutationsUnapproveTargetPopulationArgs = {
  id: Scalars['ID']
};


export type MutationsFinalizeTargetPopulationArgs = {
  id: Scalars['ID']
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
  file: Scalars['Upload']
};


export type MutationsDeleteRegistrationDataImportArgs = {
  registrationDataImportId: Scalars['String']
};


export type MutationsCreateRegistrationDataImportArgs = {
  registrationDataImportData: CreateRegistrationDataImportExcelInput
};


export type MutationsApproveRegistrationDataImportArgs = {
  id: Scalars['ID']
};


export type MutationsUnapproveRegistrationDataImportArgs = {
  id: Scalars['ID']
};


export type MutationsMergeRegistrationDataImportArgs = {
  id: Scalars['ID']
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

export enum PaymentEntitlementDeliveryType {
  Cash = 'CASH',
  DepositToCard = 'DEPOSIT_TO_CARD',
  Transfer = 'TRANSFER'
}

export type PaymentEntitlementNode = {
   __typename?: 'PaymentEntitlementNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  deliveryType: PaymentEntitlementDeliveryType,
  entitlementQuantity?: Maybe<Scalars['Decimal']>,
  deliveredQuantity?: Maybe<Scalars['Decimal']>,
  entitlementCardIssueDate?: Maybe<Scalars['Date']>,
  entitlementCardNumber: Scalars['String'],
  currency: Scalars['String'],
  deliveryDate?: Maybe<Scalars['DateTime']>,
  transactionReferenceId: Scalars['String'],
  fsp: Scalars['String'],
  paymentRecord?: Maybe<PaymentRecordNode>,
};

export type PaymentRecordNode = Node & {
   __typename?: 'PaymentRecordNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  status: PaymentRecordStatus,
  name: Scalars['String'],
  statusDate: Scalars['DateTime'],
  cashAssistId: Scalars['String'],
  cashPlan: CashPlanNode,
  household: HouseholdNode,
  headOfHousehold: Scalars['String'],
  totalPersonCovered: Scalars['Int'],
  distributionModality: Scalars['String'],
  targetPopulation: TargetPopulationNode,
  entitlement?: Maybe<PaymentEntitlementNode>,
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

export enum ProgramFrequencyOfPayments {
  Regular = 'REGULAR',
  OneOff = 'ONE_OFF'
}

export type ProgramNode = Node & {
   __typename?: 'ProgramNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  status: ProgramStatus,
  startDate: Scalars['Date'],
  endDate: Scalars['Date'],
  description: Scalars['String'],
  programCaId: Scalars['String'],
  adminAreas: AdminAreaNodeConnection,
  businessArea: BusinessAreaNode,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments: ProgramFrequencyOfPayments,
  sector: ProgramSector,
  scope: ProgramScope,
  cashPlus: Scalars['Boolean'],
  populationGoal: Scalars['Int'],
  administrativeAreasOfImplementation: Scalars['String'],
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
  Full = 'FULL',
  Partial = 'PARTIAL',
  NoIntegration = 'NO_INTEGRATION'
}

export enum ProgramSector {
  ChildProtection = 'CHILD_PROTECTION',
  Education = 'EDUCATION',
  Gender = 'GENDER',
  Health = 'HEALTH',
  HivAids = 'HIV_AIDS',
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
  paymentRecord?: Maybe<PaymentRecordNode>,
  allPaymentRecords?: Maybe<PaymentRecordNodeConnection>,
  paymentRecordStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  allPaymentEntitlements?: Maybe<Array<Maybe<PaymentEntitlementNode>>>,
  adminArea?: Maybe<AdminAreaNode>,
  allAdminAreas?: Maybe<AdminAreaNodeConnection>,
  allBusinessAreas?: Maybe<BusinessAreaNodeConnection>,
  allLogEntries?: Maybe<LogEntryObjectConnection>,
  allFieldsAttributes?: Maybe<Array<Maybe<FieldAttributeNode>>>,
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
  importedHousehold?: Maybe<ImportedHouseholdNode>,
  allImportedHouseholds?: Maybe<ImportedHouseholdNodeConnection>,
  registrationDataImportDatahub?: Maybe<RegistrationDataImportDatahubNode>,
  allRegistrationDataImportsDatahub?: Maybe<RegistrationDataImportDatahubNodeConnection>,
  importedIndividual?: Maybe<ImportedIndividualNode>,
  allImportedIndividuals?: Maybe<ImportedIndividualNodeConnection>,
  importData?: Maybe<ImportDataNode>,
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
  allRegistrationDataImports?: Maybe<RegistrationDataImportNodeConnection>,
  registrationDataStatusChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  _debug?: Maybe<DjangoDebug>,
};


export type QueryPaymentRecordArgs = {
  id: Scalars['ID']
};


export type QueryAllPaymentRecordsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  cashPlan?: Maybe<Scalars['ID']>,
  household?: Maybe<Scalars['ID']>,
  orderBy?: Maybe<Scalars['String']>
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


export type QueryAllLogEntriesArgs = {
  objectId: Scalars['String'],
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryAllFieldsAttributesArgs = {
  flexField?: Maybe<Scalars['Boolean']>
};


export type QueryProgramArgs = {
  id: Scalars['ID']
};


export type QueryAllProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>,
  status?: Maybe<Scalars['String']>,
  businessArea?: Maybe<Scalars['String']>
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
  orderBy?: Maybe<Scalars['String']>
};


export type QueryGoldenRecordByTargetingCriteriaArgs = {
  targetingCriteria: TargetingCriteriaObjectType,
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryCandidateHouseholdsListByTargetingCriteriaArgs = {
  targetPopulation: Scalars['ID'],
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryFinalHouseholdsListByTargetingCriteriaArgs = {
  targetPopulation: Scalars['ID'],
  targetingCriteria?: Maybe<TargetingCriteriaObjectType>,
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
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
  programme?: Maybe<Scalars['String']>,
  businessArea?: Maybe<Scalars['String']>,
  fullName?: Maybe<Scalars['String']>,
  fullName_Icontains?: Maybe<Scalars['String']>,
  sex?: Maybe<Array<Maybe<Scalars['ID']>>>,
  age?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
};


export type QueryAllUsersArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  fullName?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
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
  orderBy?: Maybe<Scalars['String']>
};

export type RegistrationDataImportDatahubNode = Node & {
   __typename?: 'RegistrationDataImportDatahubNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  importDate: Scalars['DateTime'],
  hctId?: Maybe<Scalars['UUID']>,
  importData?: Maybe<ImportDataNode>,
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
  A_3RdParty = 'A_3RD_PARTY',
  Xml = 'XML',
  Other = 'OTHER'
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
  businessArea?: Maybe<BusinessAreaNode>,
  households: HouseholdNodeConnection,
  individuals: IndividualNodeConnection,
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
  Approved = 'APPROVED',
  Merged = 'MERGED',
  Merging = 'MERGING'
}

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
};

export type TargetingCriteriaRuleNode = {
   __typename?: 'TargetingCriteriaRuleNode',
  id: Scalars['UUID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  targetingCriteria: TargetingCriteriaNode,
  filters?: Maybe<Array<Maybe<TargetingCriteriaRuleFilterNode>>>,
};

export type TargetingCriteriaRuleObjectType = {
  filters?: Maybe<Array<Maybe<TargetingCriteriaRuleFilterObjectType>>>,
};

export type TargetPopulationNode = Node & {
   __typename?: 'TargetPopulationNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  isRemoved: Scalars['Boolean'],
  name: Scalars['String'],
  createdBy?: Maybe<UserNode>,
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
  paymentRecords: PaymentRecordNodeConnection,
  cashPlans: CashPlanNodeConnection,
  totalHouseholds?: Maybe<Scalars['Int']>,
  totalFamilySize?: Maybe<Scalars['Int']>,
  finalList?: Maybe<HouseholdNodeConnection>,
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


export type TargetPopulationNodeCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
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

export type UnapproveRegistrationDataImportMutation = {
   __typename?: 'UnapproveRegistrationDataImportMutation',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type UnapproveTargetPopulationMutation = {
   __typename?: 'UnapproveTargetPopulationMutation',
  targetPopulation?: Maybe<TargetPopulationNode>,
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
  programCaId?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  scope?: Maybe<Scalars['String']>,
  cashPlus?: Maybe<Scalars['Boolean']>,
  populationGoal?: Maybe<Scalars['Int']>,
  administrativeAreasOfImplementation?: Maybe<Scalars['String']>,
  businessAreaSlug?: Maybe<Scalars['String']>,
};

export type UpdateTargetPopulationInput = {
  id: Scalars['ID'],
  name?: Maybe<Scalars['String']>,
  targetingCriteria?: Maybe<TargetingCriteriaObjectType>,
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

export type UserNode = Node & {
   __typename?: 'UserNode',
  lastLogin?: Maybe<Scalars['DateTime']>,
  isSuperuser: Scalars['Boolean'],
  username: Scalars['String'],
  firstName: Scalars['String'],
  lastName: Scalars['String'],
  email: Scalars['String'],
  isStaff: Scalars['Boolean'],
  isActive: Scalars['Boolean'],
  dateJoined: Scalars['DateTime'],
  id: Scalars['ID'],
  businessAreas: BusinessAreaNodeConnection,
  cashPlans: CashPlanNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
  registrationDataImports: RegistrationDataImportNodeConnection,
};


export type UserNodeBusinessAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>
};


export type UserNodeCashPlansArgs = {
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
  orderBy?: Maybe<Scalars['String']>
};


export type UserNodeRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
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
  lastLogin?: Maybe<Scalars['DateTime']>,
  isSuperuser: Scalars['Boolean'],
  username: Scalars['String'],
  firstName: Scalars['String'],
  lastName: Scalars['String'],
  email: Scalars['String'],
  isStaff: Scalars['Boolean'],
  isActive: Scalars['Boolean'],
  dateJoined: Scalars['DateTime'],
  id: Scalars['UUID'],
  businessAreas: BusinessAreaNodeConnection,
  cashPlans: CashPlanNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
  registrationDataImports: RegistrationDataImportNodeConnection,
};


export type UserObjectTypeBusinessAreasArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  id?: Maybe<Scalars['UUID']>
};


export type UserObjectTypeCashPlansArgs = {
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
  orderBy?: Maybe<Scalars['String']>
};


export type UserObjectTypeRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type XlsxRowErrorNode = {
   __typename?: 'XlsxRowErrorNode',
  rowNumber?: Maybe<Scalars['Int']>,
  header?: Maybe<Scalars['String']>,
  message?: Maybe<Scalars['String']>,
};

export type HouseholdMinimalFragment = (
  { __typename?: 'HouseholdNode' }
  & Pick<HouseholdNode, 'id' | 'createdAt' | 'residenceStatus' | 'size' | 'totalCashReceived' | 'registrationDate' | 'address'>
  & { headOfHousehold: Maybe<(
    { __typename?: 'IndividualNode' }
    & Pick<IndividualNode, 'id' | 'fullName'>
  )>, adminArea: Maybe<(
    { __typename?: 'AdminAreaNode' }
    & Pick<AdminAreaNode, 'id' | 'title'>
  )>, individuals: (
    { __typename?: 'IndividualNodeConnection' }
    & Pick<IndividualNodeConnection, 'totalCount'>
  ) }
);

export type HouseholdDetailedFragment = (
  { __typename?: 'HouseholdNode' }
  & Pick<HouseholdNode, 'countryOrigin'>
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
        & Pick<ProgramNode, 'name'>
      )> }
    )>> }
  ), paymentRecords: (
    { __typename?: 'PaymentRecordNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'PaymentRecordNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'PaymentRecordNode' }
        & Pick<PaymentRecordNode, 'id' | 'headOfHousehold'>
        & { cashPlan: (
          { __typename?: 'CashPlanNode' }
          & Pick<CashPlanNode, 'id' | 'numberOfHouseholds' | 'totalDeliveredQuantity' | 'currency'>
          & { program: (
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
          ) }
        ) }
      )> }
    )>> }
  ) }
  & HouseholdMinimalFragment
);

export type IndividualMinimalFragment = (
  { __typename?: 'IndividualNode' }
  & Pick<IndividualNode, 'id' | 'createdAt' | 'updatedAt' | 'fullName' | 'sex' | 'birthDate' | 'maritalStatus' | 'phoneNo'>
  & { documents: (
    { __typename?: 'DocumentNodeConnection' }
    & { edges: Array<Maybe<(
      { __typename?: 'DocumentNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'DocumentNode' }
        & Pick<DocumentNode, 'id' | 'documentNumber'>
        & { type: (
          { __typename?: 'DocumentTypeNode' }
          & Pick<DocumentTypeNode, 'country' | 'type' | 'label'>
        ) }
      )> }
    )>> }
  ), household: (
    { __typename?: 'HouseholdNode' }
    & Pick<HouseholdNode, 'id'>
    & { adminArea: Maybe<(
      { __typename?: 'AdminAreaNode' }
      & Pick<AdminAreaNode, 'id' | 'title'>
    )> }
  ) }
);

export type IndividualDetailedFragment = (
  { __typename?: 'IndividualNode' }
  & Pick<IndividualNode, 'givenName' | 'familyName' | 'estimatedBirthDate'>
  & { household: (
    { __typename?: 'HouseholdNode' }
    & Pick<HouseholdNode, 'id' | 'address' | 'countryOrigin'>
    & { adminArea: Maybe<(
      { __typename?: 'AdminAreaNode' }
      & Pick<AdminAreaNode, 'id' | 'title' | 'level'>
    )> }
  ), headingHousehold: Maybe<(
    { __typename?: 'HouseholdNode' }
    & Pick<HouseholdNode, 'id'>
    & { headOfHousehold: Maybe<(
      { __typename?: 'IndividualNode' }
      & Pick<IndividualNode, 'id'>
    )> }
  )> }
  & IndividualMinimalFragment
);

export type ApproveTpMutationVariables = {
  id: Scalars['ID'],
  programId: Scalars['ID']
};


export type ApproveTpMutation = (
  { __typename?: 'Mutations' }
  & { approveTargetPopulation: Maybe<(
    { __typename?: 'ApproveTargetPopulationMutation' }
    & { targetPopulation: Maybe<(
      { __typename?: 'TargetPopulationNode' }
      & Pick<TargetPopulationNode, 'id' | 'name' | 'status'>
      & { candidateListTargetingCriteria: Maybe<(
        { __typename?: 'TargetingCriteriaNode' }
        & { targetPopulationCandidate: Maybe<(
          { __typename?: 'TargetPopulationNode' }
          & { createdBy: Maybe<(
            { __typename?: 'UserNode' }
            & Pick<UserNode, 'firstName' | 'lastName'>
          )>, program: Maybe<(
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
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
      )>, finalListTargetingCriteria: Maybe<(
        { __typename?: 'TargetingCriteriaNode' }
        & { targetPopulationFinal: Maybe<(
          { __typename?: 'TargetPopulationNode' }
          & { createdBy: Maybe<(
            { __typename?: 'UserNode' }
            & Pick<UserNode, 'firstName' | 'lastName'>
          )>, program: Maybe<(
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
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
      )> }
    )> }
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
      & Pick<ProgramNode, 'id' | 'name' | 'status' | 'startDate' | 'endDate' | 'programCaId' | 'budget' | 'description' | 'frequencyOfPayments' | 'sector' | 'scope' | 'cashPlus' | 'populationGoal'>
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
      & Pick<TargetPopulationNode, 'id' | 'status'>
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

export type UpdateProgramMutationVariables = {
  programData: UpdateProgramInput
};


export type UpdateProgramMutation = (
  { __typename?: 'Mutations' }
  & { updateProgram: Maybe<(
    { __typename?: 'UpdateProgram' }
    & { program: Maybe<(
      { __typename?: 'ProgramNode' }
      & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'programCaId' | 'description' | 'budget' | 'frequencyOfPayments' | 'cashPlus' | 'populationGoal' | 'scope' | 'sector' | 'totalNumberOfHouseholds' | 'administrativeAreasOfImplementation'>
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
      & Pick<TargetPopulationNode, 'id' | 'name' | 'status'>
      & { candidateListTargetingCriteria: Maybe<(
        { __typename?: 'TargetingCriteriaNode' }
        & { targetPopulationCandidate: Maybe<(
          { __typename?: 'TargetPopulationNode' }
          & { createdBy: Maybe<(
            { __typename?: 'UserNode' }
            & Pick<UserNode, 'firstName' | 'lastName'>
          )>, program: Maybe<(
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
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
      )>, finalListTargetingCriteria: Maybe<(
        { __typename?: 'TargetingCriteriaNode' }
        & { targetPopulationFinal: Maybe<(
          { __typename?: 'TargetPopulationNode' }
          & { createdBy: Maybe<(
            { __typename?: 'UserNode' }
            & Pick<UserNode, 'firstName' | 'lastName'>
          )>, program: Maybe<(
            { __typename?: 'ProgramNode' }
            & Pick<ProgramNode, 'id' | 'name'>
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
      )> }
    )> }
  )> }
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
  program: Scalars['ID'],
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>
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
        & Pick<CashPlanNode, 'id' | 'cashAssistId' | 'numberOfHouseholds' | 'disbursementDate' | 'currency' | 'status' | 'totalEntitledQuantity' | 'totalDeliveredQuantity' | 'totalUndeliveredQuantity'>
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
  residenceStatus?: Maybe<Scalars['String']>
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
  sex?: Maybe<Array<Maybe<Scalars['ID']>>>,
  age?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>,
  search?: Maybe<Scalars['String']>
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
  cashPlan: Scalars['ID'],
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
        & Pick<PaymentRecordNode, 'id' | 'createdAt' | 'updatedAt' | 'name' | 'statusDate' | 'status' | 'headOfHousehold' | 'cashAssistId' | 'totalPersonCovered'>
        & { household: (
          { __typename?: 'HouseholdNode' }
          & Pick<HouseholdNode, 'id' | 'size'>
        ), entitlement: Maybe<(
          { __typename?: 'PaymentEntitlementNode' }
          & Pick<PaymentEntitlementNode, 'id' | 'entitlementQuantity' | 'deliveredQuantity' | 'deliveryDate'>
        )> }
      )> }
    )>> }
  )> }
);

export type AllProgramsQueryVariables = {
  businessArea?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>
};


export type AllProgramsQuery = (
  { __typename?: 'Query' }
  & { allPrograms: Maybe<(
    { __typename?: 'ProgramNodeConnection' }
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'endCursor' | 'startCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'ProgramNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'ProgramNode' }
        & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'programCaId' | 'description' | 'budget' | 'frequencyOfPayments' | 'populationGoal' | 'sector' | 'totalNumberOfHouseholds'>
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
  status?: Maybe<Scalars['String']>
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
        & Pick<TargetPopulationNode, 'id' | 'name' | 'status' | 'createdAt' | 'updatedAt' | 'candidateListTotalHouseholds' | 'finalListTotalHouseholds'>
        & { createdBy: Maybe<(
          { __typename?: 'UserNode' }
          & Pick<UserNode, 'firstName' | 'lastName'>
        )> }
      )> }
    )>> }
  )> }
);

export type AllUsersQueryVariables = {
  fullName?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>
};


export type AllUsersQuery = (
  { __typename?: 'Query' }
  & { allUsers: Maybe<(
    { __typename?: 'UserNodeConnection' }
    & { pageInfo: (
      { __typename?: 'PageInfo' }
      & Pick<PageInfo, 'hasNextPage' | 'hasPreviousPage' | 'endCursor' | 'startCursor'>
    ), edges: Array<Maybe<(
      { __typename?: 'UserNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'UserNode' }
        & Pick<UserNode, 'id' | 'firstName' | 'lastName'>
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
    & Pick<CashPlanNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'deliveryType' | 'fcId' | 'dpId' | 'dispersionDate' | 'assistanceThrough' | 'cashAssistId'>
    & { targetPopulation: (
      { __typename?: 'TargetPopulationNode' }
      & Pick<TargetPopulationNode, 'name'>
    ), program: (
      { __typename?: 'ProgramNode' }
      & Pick<ProgramNode, 'id' | 'name'>
    ), paymentRecords: (
      { __typename?: 'PaymentRecordNodeConnection' }
      & Pick<PaymentRecordNodeConnection, 'totalCount' | 'edgeCount'>
    ) }
  )> }
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

export type MeQueryVariables = {};


export type MeQuery = (
  { __typename?: 'Query' }
  & { me: Maybe<(
    { __typename?: 'UserObjectType' }
    & Pick<UserObjectType, 'id' | 'username' | 'email' | 'firstName' | 'lastName'>
    & { businessAreas: (
      { __typename?: 'BusinessAreaNodeConnection' }
      & { edges: Array<Maybe<(
        { __typename?: 'BusinessAreaNodeEdge' }
        & { node: Maybe<(
          { __typename?: 'BusinessAreaNode' }
          & Pick<BusinessAreaNode, 'id' | 'name' | 'slug'>
        )> }
      )>> }
    ) }
  )> }
);

export type PaymentRecordQueryVariables = {
  id: Scalars['ID']
};


export type PaymentRecordQuery = (
  { __typename?: 'Query' }
  & { paymentRecord: Maybe<(
    { __typename?: 'PaymentRecordNode' }
    & Pick<PaymentRecordNode, 'id' | 'status' | 'statusDate' | 'cashAssistId' | 'headOfHousehold' | 'distributionModality' | 'totalPersonCovered'>
    & { household: (
      { __typename?: 'HouseholdNode' }
      & Pick<HouseholdNode, 'id' | 'size'>
    ), targetPopulation: (
      { __typename?: 'TargetPopulationNode' }
      & Pick<TargetPopulationNode, 'id' | 'name'>
    ), cashPlan: (
      { __typename?: 'CashPlanNode' }
      & Pick<CashPlanNode, 'id' | 'cashAssistId'>
      & { program: (
        { __typename?: 'ProgramNode' }
        & Pick<ProgramNode, 'id' | 'name'>
      ) }
    ), entitlement: Maybe<(
      { __typename?: 'PaymentEntitlementNode' }
      & Pick<PaymentEntitlementNode, 'id' | 'currency' | 'entitlementQuantity' | 'deliveredQuantity' | 'deliveryType' | 'deliveryDate' | 'entitlementCardIssueDate' | 'transactionReferenceId' | 'fsp' | 'entitlementCardNumber'>
    )> }
  )> }
);

export type ProgramQueryVariables = {
  id: Scalars['ID']
};


export type ProgramQuery = (
  { __typename?: 'Query' }
  & { program: Maybe<(
    { __typename?: 'ProgramNode' }
    & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'programCaId' | 'description' | 'budget' | 'frequencyOfPayments' | 'cashPlus' | 'populationGoal' | 'scope' | 'sector' | 'totalNumberOfHouseholds' | 'administrativeAreasOfImplementation'>
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

export type TargetPopulationQueryVariables = {
  id: Scalars['ID']
};


export type TargetPopulationQuery = (
  { __typename?: 'Query' }
  & { targetPopulation: Maybe<(
    { __typename?: 'TargetPopulationNode' }
    & Pick<TargetPopulationNode, 'id' | 'name' | 'status'>
    & { candidateListTargetingCriteria: Maybe<(
      { __typename?: 'TargetingCriteriaNode' }
      & { targetPopulationCandidate: Maybe<(
        { __typename?: 'TargetPopulationNode' }
        & { createdBy: Maybe<(
          { __typename?: 'UserNode' }
          & Pick<UserNode, 'firstName' | 'lastName'>
        )>, program: Maybe<(
          { __typename?: 'ProgramNode' }
          & Pick<ProgramNode, 'id' | 'name'>
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
    )>, finalListTargetingCriteria: Maybe<(
      { __typename?: 'TargetingCriteriaNode' }
      & { targetPopulationFinal: Maybe<(
        { __typename?: 'TargetPopulationNode' }
        & { createdBy: Maybe<(
          { __typename?: 'UserNode' }
          & Pick<UserNode, 'firstName' | 'lastName'>
        )>, program: Maybe<(
          { __typename?: 'ProgramNode' }
          & Pick<ProgramNode, 'id' | 'name'>
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
    )> }
  )> }
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
  orderBy?: Maybe<Scalars['String']>
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

export type AllRegistrationDataImportsQueryVariables = {
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  orderBy?: Maybe<Scalars['String']>,
  name_Icontains?: Maybe<Scalars['String']>,
  importedBy_Id?: Maybe<Scalars['UUID']>,
  status?: Maybe<Scalars['String']>,
  importDate?: Maybe<Scalars['Date']>
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

export type ApproveRdiMutationVariables = {
  id: Scalars['ID']
};


export type ApproveRdiMutation = (
  { __typename?: 'Mutations' }
  & { approveRegistrationDataImport: Maybe<(
    { __typename?: 'ApproveRegistrationDataImportMutation' }
    & { registrationDataImport: Maybe<(
      { __typename?: 'RegistrationDataImportNode' }
      & RegistrationDetailedFragment
    )> }
  )> }
);

export type CreateRegistrationDataImportMutationVariables = {
  registrationDataImportData: CreateRegistrationDataImportExcelInput
};


export type CreateRegistrationDataImportMutation = (
  { __typename?: 'Mutations' }
  & { createRegistrationDataImport: Maybe<(
    { __typename?: 'CreateRegistrationDataImport' }
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
  & Pick<RegistrationDataImportNode, 'id' | 'createdAt' | 'name' | 'status' | 'importDate' | 'dataSource' | 'numberOfHouseholds'>
  & { importedBy: (
    { __typename?: 'UserNode' }
    & Pick<UserNode, 'id' | 'firstName' | 'lastName'>
  ) }
);

export type RegistrationDetailedFragment = (
  { __typename?: 'RegistrationDataImportNode' }
  & Pick<RegistrationDataImportNode, 'numberOfIndividuals'>
  & RegistrationMinimalFragment
);

export type ImportedHouseholdMinimalFragment = (
  { __typename?: 'ImportedHouseholdNode' }
  & Pick<ImportedHouseholdNode, 'id' | 'size' | 'admin1' | 'admin2' | 'registrationDate'>
  & { headOfHousehold: Maybe<(
    { __typename?: 'ImportedIndividualNode' }
    & Pick<ImportedIndividualNode, 'id' | 'fullName'>
  )> }
);

export type ImportedHouseholdDetailedFragment = (
  { __typename?: 'ImportedHouseholdNode' }
  & Pick<ImportedHouseholdNode, 'residenceStatus' | 'countryOrigin'>
  & { registrationDataImport: (
    { __typename?: 'RegistrationDataImportDatahubNode' }
    & Pick<RegistrationDataImportDatahubNode, 'id' | 'hctId' | 'name'>
  ) }
  & ImportedHouseholdMinimalFragment
);

export type ImportedIndividualMinimalFragment = (
  { __typename?: 'ImportedIndividualNode' }
  & Pick<ImportedIndividualNode, 'id' | 'fullName' | 'birthDate' | 'sex'>
);

export type ImportedIndividualDetailedFragment = (
  { __typename?: 'ImportedIndividualNode' }
  & Pick<ImportedIndividualNode, 'givenName' | 'familyName' | 'middleName' | 'estimatedBirthDate' | 'phoneNo' | 'phoneNoAlternative'>
  & { household: (
    { __typename?: 'ImportedHouseholdNode' }
    & Pick<ImportedHouseholdNode, 'id' | 'admin1' | 'admin2' | 'address'>
  ), registrationDataImport: (
    { __typename?: 'RegistrationDataImportDatahubNode' }
    & Pick<RegistrationDataImportDatahubNode, 'id' | 'hctId' | 'name'>
  ) }
  & ImportedIndividualMinimalFragment
);

export type UnapproveRdiMutationVariables = {
  id: Scalars['ID']
};


export type UnapproveRdiMutation = (
  { __typename?: 'Mutations' }
  & { unapproveRegistrationDataImport: Maybe<(
    { __typename?: 'UnapproveRegistrationDataImportMutation' }
    & { registrationDataImport: Maybe<(
      { __typename?: 'RegistrationDataImportNode' }
      & RegistrationDetailedFragment
    )> }
  )> }
);

export type UploadImportDataXlsxFileMutationVariables = {
  file: Scalars['Upload']
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

export type CandidateHouseholdsListByTargetingCriteriaQueryVariables = {
  targetPopulation: Scalars['ID'],
  first?: Maybe<Scalars['Int']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  last?: Maybe<Scalars['Int']>
};


export type CandidateHouseholdsListByTargetingCriteriaQuery = (
  { __typename?: 'Query' }
  & { candidateHouseholdsListByTargetingCriteria: Maybe<(
    { __typename?: 'HouseholdNodeConnection' }
    & Pick<HouseholdNodeConnection, 'totalCount' | 'edgeCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'HouseholdNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'HouseholdNode' }
        & Pick<HouseholdNode, 'id' | 'size' | 'updatedAt'>
        & { headOfHousehold: Maybe<(
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'givenName' | 'familyName'>
        )>, adminArea: Maybe<(
          { __typename?: 'AdminAreaNode' }
          & Pick<AdminAreaNode, 'id' | 'title'>
        )> }
      )> }
    )>> }
  )> }
);

export type GoldenRecordByTargetingCriteriaQueryVariables = {
  targetingCriteria: TargetingCriteriaObjectType,
  first?: Maybe<Scalars['Int']>,
  after?: Maybe<Scalars['String']>,
  before?: Maybe<Scalars['String']>,
  last?: Maybe<Scalars['Int']>
};


export type GoldenRecordByTargetingCriteriaQuery = (
  { __typename?: 'Query' }
  & { goldenRecordByTargetingCriteria: Maybe<(
    { __typename?: 'HouseholdNodeConnection' }
    & Pick<HouseholdNodeConnection, 'totalCount' | 'edgeCount'>
    & { edges: Array<Maybe<(
      { __typename?: 'HouseholdNodeEdge' }
      & { node: Maybe<(
        { __typename?: 'HouseholdNode' }
        & Pick<HouseholdNode, 'id' | 'size' | 'updatedAt'>
        & { headOfHousehold: Maybe<(
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'givenName' | 'familyName'>
        )>, adminArea: Maybe<(
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
    & Pick<FieldAttributeNode, 'isFlexField' | 'id' | 'type' | 'name' | 'labelEn' | 'hint'>
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
  registrationDate
  headOfHousehold {
    id
    fullName
  }
  address
  adminArea {
    id
    title
  }
  individuals {
    totalCount
  }
}
    `;
export const IndividualMinimalFragmentDoc = gql`
    fragment individualMinimal on IndividualNode {
  id
  createdAt
  updatedAt
  fullName
  sex
  birthDate
  maritalStatus
  phoneNo
  documents {
    edges {
      node {
        id
        documentNumber
        type {
          country
          type
          label
        }
      }
    }
  }
  household {
    id
    adminArea {
      id
      title
    }
  }
}
    `;
export const HouseholdDetailedFragmentDoc = gql`
    fragment householdDetailed on HouseholdNode {
  ...householdMinimal
  countryOrigin
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
        name
      }
    }
  }
  paymentRecords {
    edges {
      node {
        id
        headOfHousehold
        cashPlan {
          id
          numberOfHouseholds
          program {
            id
            name
          }
          totalDeliveredQuantity
          currency
        }
      }
    }
  }
}
    ${HouseholdMinimalFragmentDoc}
${IndividualMinimalFragmentDoc}`;
export const IndividualDetailedFragmentDoc = gql`
    fragment individualDetailed on IndividualNode {
  ...individualMinimal
  givenName
  familyName
  estimatedBirthDate
  household {
    id
    address
    countryOrigin
    adminArea {
      id
      title
      level
    }
  }
  headingHousehold {
    id
    headOfHousehold {
      id
    }
  }
}
    ${IndividualMinimalFragmentDoc}`;
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
  }
  dataSource
  numberOfHouseholds
}
    `;
export const RegistrationDetailedFragmentDoc = gql`
    fragment registrationDetailed on RegistrationDataImportNode {
  ...registrationMinimal
  numberOfIndividuals
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
  registrationDate
}
    `;
export const ImportedHouseholdDetailedFragmentDoc = gql`
    fragment importedHouseholdDetailed on ImportedHouseholdNode {
  ...importedHouseholdMinimal
  residenceStatus
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
}
    `;
export const ImportedIndividualDetailedFragmentDoc = gql`
    fragment importedIndividualDetailed on ImportedIndividualNode {
  ...importedIndividualMinimal
  givenName
  familyName
  middleName
  estimatedBirthDate
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
export const ApproveTpDocument = gql`
    mutation ApproveTP($id: ID!, $programId: ID!) {
  approveTargetPopulation(id: $id, programId: $programId) {
    targetPopulation {
      id
      name
      status
      candidateListTargetingCriteria {
        targetPopulationCandidate {
          createdBy {
            firstName
            lastName
          }
          program {
            id
            name
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
      finalListTargetingCriteria {
        targetPopulationFinal {
          createdBy {
            firstName
            lastName
          }
          program {
            id
            name
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
    }
  }
}
    `;
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
 *      programId: // value for 'programId'
 *   },
 * });
 */
export function useApproveTpMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<ApproveTpMutation, ApproveTpMutationVariables>) {
        return ApolloReactHooks.useMutation<ApproveTpMutation, ApproveTpMutationVariables>(ApproveTpDocument, baseOptions);
      }
export type ApproveTpMutationHookResult = ReturnType<typeof useApproveTpMutation>;
export type ApproveTpMutationResult = ApolloReactCommon.MutationResult<ApproveTpMutation>;
export type ApproveTpMutationOptions = ApolloReactCommon.BaseMutationOptions<ApproveTpMutation, ApproveTpMutationVariables>;
export const CreateProgramDocument = gql`
    mutation CreateProgram($programData: CreateProgramInput!) {
  createProgram(programData: $programData) {
    program {
      id
      name
      status
      startDate
      endDate
      programCaId
      budget
      description
      frequencyOfPayments
      sector
      scope
      cashPlus
      populationGoal
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
export const UpdateProgramDocument = gql`
    mutation UpdateProgram($programData: UpdateProgramInput!) {
  updateProgram(programData: $programData) {
    program {
      id
      name
      startDate
      endDate
      status
      programCaId
      description
      budget
      frequencyOfPayments
      cashPlus
      populationGoal
      scope
      sector
      totalNumberOfHouseholds
      administrativeAreasOfImplementation
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
      id
      name
      status
      candidateListTargetingCriteria {
        targetPopulationCandidate {
          createdBy {
            firstName
            lastName
          }
          program {
            id
            name
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
      finalListTargetingCriteria {
        targetPopulationFinal {
          createdBy {
            firstName
            lastName
          }
          program {
            id
            name
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
    }
  }
}
    `;
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
    query AllCashPlans($program: ID!, $after: String, $before: String, $first: Int, $last: Int, $orderBy: String) {
  allCashPlans(program: $program, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
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
        cashAssistId
        numberOfHouseholds
        disbursementDate
        currency
        status
        totalEntitledQuantity
        totalDeliveredQuantity
        totalUndeliveredQuantity
      }
    }
  }
}
    `;
export type AllCashPlansComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllCashPlansQuery, AllCashPlansQueryVariables>, 'query'> & ({ variables: AllCashPlansQueryVariables; skip?: boolean; } | { skip: boolean; });

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
export const AllHouseholdsDocument = gql`
    query AllHouseholds($after: String, $before: String, $first: Int, $last: Int, $businessArea: String, $orderBy: String, $familySize: String, $programs: [ID], $headOfHouseholdFullNameIcontains: String, $adminArea: ID, $search: String, $residenceStatus: String) {
  allHouseholds(after: $after, before: $before, first: $first, last: $last, businessArea: $businessArea, size: $familySize, orderBy: $orderBy, programs: $programs, headOfHousehold_FullName_Icontains: $headOfHouseholdFullNameIcontains, adminArea: $adminArea, search: $search, residenceStatus: $residenceStatus) {
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
    query AllIndividuals($before: String, $after: String, $first: Int, $last: Int, $fullNameContains: String, $sex: [ID], $age: String, $orderBy: String, $search: String) {
  allIndividuals(before: $before, after: $after, first: $first, last: $last, fullName_Icontains: $fullNameContains, sex: $sex, age: $age, orderBy: $orderBy, search: $search) {
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
    query AllPaymentRecords($cashPlan: ID!, $after: String, $before: String, $orderBy: String, $first: Int, $last: Int) {
  allPaymentRecords(cashPlan: $cashPlan, after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy) {
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
        name
        statusDate
        status
        headOfHousehold
        cashAssistId
        totalPersonCovered
        household {
          id
          size
        }
        entitlement {
          id
          entitlementQuantity
          deliveredQuantity
          deliveryDate
        }
      }
    }
    totalCount
    edgeCount
  }
}
    `;
export type AllPaymentRecordsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllPaymentRecordsQuery, AllPaymentRecordsQueryVariables>, 'query'> & ({ variables: AllPaymentRecordsQueryVariables; skip?: boolean; } | { skip: boolean; });

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
export const AllProgramsDocument = gql`
    query AllPrograms($businessArea: String, $status: String) {
  allPrograms(businessArea: $businessArea, status: $status) {
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
        startDate
        endDate
        status
        programCaId
        description
        budget
        frequencyOfPayments
        populationGoal
        sector
        totalNumberOfHouseholds
      }
    }
  }
}
    `;
export type AllProgramsComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllProgramsQuery, AllProgramsQueryVariables>, 'query'>;

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
 *      businessArea: // value for 'businessArea'
 *      status: // value for 'status'
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
export const AllTargetPopulationsDocument = gql`
    query AllTargetPopulations($after: String, $before: String, $first: Int, $last: Int, $orderBy: String, $name: String, $status: String) {
  allTargetPopulation(after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy, name: $name, status: $status) {
    edges {
      node {
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
      cursor
    }
    totalCount
    edgeCount
  }
}
    `;
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
    query AllUsers($fullName: String, $first: Int) {
  allUsers(fullName: $fullName, first: $first) {
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
      }
    }
  }
}
    `;
export type AllUsersComponentProps = Omit<ApolloReactComponents.QueryComponentOptions<AllUsersQuery, AllUsersQueryVariables>, 'query'>;

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
 *      fullName: // value for 'fullName'
 *      first: // value for 'first'
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
    status
    deliveryType
    fcId
    dpId
    dispersionDate
    assistanceThrough
    cashAssistId
    dispersionDate
    targetPopulation {
      name
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
    cashAssistId
    household {
      id
      size
    }
    headOfHousehold
    distributionModality
    totalPersonCovered
    targetPopulation {
      id
      name
    }
    cashPlan {
      id
      cashAssistId
      program {
        id
        name
      }
    }
    entitlement {
      id
      currency
      entitlementQuantity
      deliveredQuantity
      deliveryType
      deliveryDate
      entitlementCardIssueDate
      transactionReferenceId
      fsp
      entitlementCardNumber
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
export const ProgramDocument = gql`
    query Program($id: ID!) {
  program(id: $id) {
    id
    name
    startDate
    endDate
    status
    programCaId
    description
    budget
    frequencyOfPayments
    cashPlus
    populationGoal
    scope
    sector
    totalNumberOfHouseholds
    administrativeAreasOfImplementation
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
export const TargetPopulationDocument = gql`
    query targetPopulation($id: ID!) {
  targetPopulation(id: $id) {
    id
    name
    status
    candidateListTargetingCriteria {
      targetPopulationCandidate {
        createdBy {
          firstName
          lastName
        }
        program {
          id
          name
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
    finalListTargetingCriteria {
      targetPopulationFinal {
        createdBy {
          firstName
          lastName
        }
        program {
          id
          name
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
  }
}
    `;
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
    query AllImportedIndividuals($after: String, $before: String, $first: Int, $last: Int, $rdiId: String, $household: ID, $orderBy: String) {
  allImportedIndividuals(after: $after, before: $before, first: $first, last: $last, rdiId: $rdiId, household: $household, orderBy: $orderBy) {
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
export const AllRegistrationDataImportsDocument = gql`
    query AllRegistrationDataImports($after: String, $before: String, $first: Int, $last: Int, $orderBy: String, $name_Icontains: String, $importedBy_Id: UUID, $status: String, $importDate: Date) {
  allRegistrationDataImports(after: $after, before: $before, first: $first, last: $last, orderBy: $orderBy, name_Icontains: $name_Icontains, importedBy_Id: $importedBy_Id, status: $status, importDate: $importDate) {
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
export const ApproveRdiDocument = gql`
    mutation ApproveRDI($id: ID!) {
  approveRegistrationDataImport(id: $id) {
    registrationDataImport {
      ...registrationDetailed
    }
  }
}
    ${RegistrationDetailedFragmentDoc}`;
export type ApproveRdiMutationFn = ApolloReactCommon.MutationFunction<ApproveRdiMutation, ApproveRdiMutationVariables>;
export type ApproveRdiComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<ApproveRdiMutation, ApproveRdiMutationVariables>, 'mutation'>;

    export const ApproveRdiComponent = (props: ApproveRdiComponentProps) => (
      <ApolloReactComponents.Mutation<ApproveRdiMutation, ApproveRdiMutationVariables> mutation={ApproveRdiDocument} {...props} />
    );
    
export type ApproveRdiProps<TChildProps = {}> = ApolloReactHoc.MutateProps<ApproveRdiMutation, ApproveRdiMutationVariables> & TChildProps;
export function withApproveRdi<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  ApproveRdiMutation,
  ApproveRdiMutationVariables,
  ApproveRdiProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, ApproveRdiMutation, ApproveRdiMutationVariables, ApproveRdiProps<TChildProps>>(ApproveRdiDocument, {
      alias: 'approveRdi',
      ...operationOptions
    });
};

/**
 * __useApproveRdiMutation__
 *
 * To run a mutation, you first call `useApproveRdiMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useApproveRdiMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [approveRdiMutation, { data, loading, error }] = useApproveRdiMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useApproveRdiMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<ApproveRdiMutation, ApproveRdiMutationVariables>) {
        return ApolloReactHooks.useMutation<ApproveRdiMutation, ApproveRdiMutationVariables>(ApproveRdiDocument, baseOptions);
      }
export type ApproveRdiMutationHookResult = ReturnType<typeof useApproveRdiMutation>;
export type ApproveRdiMutationResult = ApolloReactCommon.MutationResult<ApproveRdiMutation>;
export type ApproveRdiMutationOptions = ApolloReactCommon.BaseMutationOptions<ApproveRdiMutation, ApproveRdiMutationVariables>;
export const CreateRegistrationDataImportDocument = gql`
    mutation CreateRegistrationDataImport($registrationDataImportData: CreateRegistrationDataImportExcelInput!) {
  createRegistrationDataImport(registrationDataImportData: $registrationDataImportData) {
    registrationDataImport {
      id
      name
      dataSource
      datahubId
    }
  }
}
    `;
export type CreateRegistrationDataImportMutationFn = ApolloReactCommon.MutationFunction<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables>;
export type CreateRegistrationDataImportComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables>, 'mutation'>;

    export const CreateRegistrationDataImportComponent = (props: CreateRegistrationDataImportComponentProps) => (
      <ApolloReactComponents.Mutation<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables> mutation={CreateRegistrationDataImportDocument} {...props} />
    );
    
export type CreateRegistrationDataImportProps<TChildProps = {}> = ApolloReactHoc.MutateProps<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables> & TChildProps;
export function withCreateRegistrationDataImport<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  CreateRegistrationDataImportMutation,
  CreateRegistrationDataImportMutationVariables,
  CreateRegistrationDataImportProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables, CreateRegistrationDataImportProps<TChildProps>>(CreateRegistrationDataImportDocument, {
      alias: 'createRegistrationDataImport',
      ...operationOptions
    });
};

/**
 * __useCreateRegistrationDataImportMutation__
 *
 * To run a mutation, you first call `useCreateRegistrationDataImportMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useCreateRegistrationDataImportMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [createRegistrationDataImportMutation, { data, loading, error }] = useCreateRegistrationDataImportMutation({
 *   variables: {
 *      registrationDataImportData: // value for 'registrationDataImportData'
 *   },
 * });
 */
export function useCreateRegistrationDataImportMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables>) {
        return ApolloReactHooks.useMutation<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables>(CreateRegistrationDataImportDocument, baseOptions);
      }
export type CreateRegistrationDataImportMutationHookResult = ReturnType<typeof useCreateRegistrationDataImportMutation>;
export type CreateRegistrationDataImportMutationResult = ApolloReactCommon.MutationResult<CreateRegistrationDataImportMutation>;
export type CreateRegistrationDataImportMutationOptions = ApolloReactCommon.BaseMutationOptions<CreateRegistrationDataImportMutation, CreateRegistrationDataImportMutationVariables>;
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
export const UnapproveRdiDocument = gql`
    mutation UnapproveRDI($id: ID!) {
  unapproveRegistrationDataImport(id: $id) {
    registrationDataImport {
      ...registrationDetailed
    }
  }
}
    ${RegistrationDetailedFragmentDoc}`;
export type UnapproveRdiMutationFn = ApolloReactCommon.MutationFunction<UnapproveRdiMutation, UnapproveRdiMutationVariables>;
export type UnapproveRdiComponentProps = Omit<ApolloReactComponents.MutationComponentOptions<UnapproveRdiMutation, UnapproveRdiMutationVariables>, 'mutation'>;

    export const UnapproveRdiComponent = (props: UnapproveRdiComponentProps) => (
      <ApolloReactComponents.Mutation<UnapproveRdiMutation, UnapproveRdiMutationVariables> mutation={UnapproveRdiDocument} {...props} />
    );
    
export type UnapproveRdiProps<TChildProps = {}> = ApolloReactHoc.MutateProps<UnapproveRdiMutation, UnapproveRdiMutationVariables> & TChildProps;
export function withUnapproveRdi<TProps, TChildProps = {}>(operationOptions?: ApolloReactHoc.OperationOption<
  TProps,
  UnapproveRdiMutation,
  UnapproveRdiMutationVariables,
  UnapproveRdiProps<TChildProps>>) {
    return ApolloReactHoc.withMutation<TProps, UnapproveRdiMutation, UnapproveRdiMutationVariables, UnapproveRdiProps<TChildProps>>(UnapproveRdiDocument, {
      alias: 'unapproveRdi',
      ...operationOptions
    });
};

/**
 * __useUnapproveRdiMutation__
 *
 * To run a mutation, you first call `useUnapproveRdiMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useUnapproveRdiMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [unapproveRdiMutation, { data, loading, error }] = useUnapproveRdiMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useUnapproveRdiMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UnapproveRdiMutation, UnapproveRdiMutationVariables>) {
        return ApolloReactHooks.useMutation<UnapproveRdiMutation, UnapproveRdiMutationVariables>(UnapproveRdiDocument, baseOptions);
      }
export type UnapproveRdiMutationHookResult = ReturnType<typeof useUnapproveRdiMutation>;
export type UnapproveRdiMutationResult = ApolloReactCommon.MutationResult<UnapproveRdiMutation>;
export type UnapproveRdiMutationOptions = ApolloReactCommon.BaseMutationOptions<UnapproveRdiMutation, UnapproveRdiMutationVariables>;
export const UploadImportDataXlsxFileDocument = gql`
    mutation UploadImportDataXlsxFile($file: Upload!) {
  uploadImportDataXlsxFile(file: $file) {
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
 *   },
 * });
 */
export function useUploadImportDataXlsxFileMutation(baseOptions?: ApolloReactHooks.MutationHookOptions<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>) {
        return ApolloReactHooks.useMutation<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>(UploadImportDataXlsxFileDocument, baseOptions);
      }
export type UploadImportDataXlsxFileMutationHookResult = ReturnType<typeof useUploadImportDataXlsxFileMutation>;
export type UploadImportDataXlsxFileMutationResult = ApolloReactCommon.MutationResult<UploadImportDataXlsxFileMutation>;
export type UploadImportDataXlsxFileMutationOptions = ApolloReactCommon.BaseMutationOptions<UploadImportDataXlsxFileMutation, UploadImportDataXlsxFileMutationVariables>;
export const CandidateHouseholdsListByTargetingCriteriaDocument = gql`
    query candidateHouseholdsListByTargetingCriteria($targetPopulation: ID!, $first: Int, $after: String, $before: String, $last: Int) {
  candidateHouseholdsListByTargetingCriteria(targetPopulation: $targetPopulation, after: $after, before: $before, first: $first, last: $last) {
    edges {
      node {
        id
        headOfHousehold {
          givenName
          familyName
        }
        size
        adminArea {
          id
          title
        }
        updatedAt
      }
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
export const GoldenRecordByTargetingCriteriaDocument = gql`
    query GoldenRecordByTargetingCriteria($targetingCriteria: TargetingCriteriaObjectType!, $first: Int, $after: String, $before: String, $last: Int) {
  goldenRecordByTargetingCriteria(targetingCriteria: $targetingCriteria, after: $after, before: $before, first: $first, last: $last) {
    edges {
      node {
        id
        headOfHousehold {
          givenName
          familyName
        }
        size
        adminArea {
          id
          title
        }
        updatedAt
      }
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
  PaymentRecordNode: ResolverTypeWrapper<PaymentRecordNode>,
  Node: ResolverTypeWrapper<Node>,
  DateTime: ResolverTypeWrapper<Scalars['DateTime']>,
  PaymentRecordStatus: PaymentRecordStatus,
  String: ResolverTypeWrapper<Scalars['String']>,
  CashPlanNode: ResolverTypeWrapper<CashPlanNode>,
  ProgramNode: ResolverTypeWrapper<ProgramNode>,
  ProgramStatus: ProgramStatus,
  Date: ResolverTypeWrapper<Scalars['Date']>,
  Int: ResolverTypeWrapper<Scalars['Int']>,
  AdminAreaNodeConnection: ResolverTypeWrapper<AdminAreaNodeConnection>,
  PageInfo: ResolverTypeWrapper<PageInfo>,
  Boolean: ResolverTypeWrapper<Scalars['Boolean']>,
  AdminAreaNodeEdge: ResolverTypeWrapper<AdminAreaNodeEdge>,
  AdminAreaNode: ResolverTypeWrapper<AdminAreaNode>,
  HouseholdNodeConnection: ResolverTypeWrapper<HouseholdNodeConnection>,
  HouseholdNodeEdge: ResolverTypeWrapper<HouseholdNodeEdge>,
  HouseholdNode: ResolverTypeWrapper<HouseholdNode>,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  GeoJSON: ResolverTypeWrapper<Scalars['GeoJSON']>,
  RegistrationDataImportNode: ResolverTypeWrapper<RegistrationDataImportNode>,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  UserNode: ResolverTypeWrapper<UserNode>,
  UUID: ResolverTypeWrapper<Scalars['UUID']>,
  BusinessAreaNodeConnection: ResolverTypeWrapper<BusinessAreaNodeConnection>,
  BusinessAreaNodeEdge: ResolverTypeWrapper<BusinessAreaNodeEdge>,
  BusinessAreaNode: ResolverTypeWrapper<BusinessAreaNode>,
  UserNodeConnection: ResolverTypeWrapper<UserNodeConnection>,
  UserNodeEdge: ResolverTypeWrapper<UserNodeEdge>,
  ProgramNodeConnection: ResolverTypeWrapper<ProgramNodeConnection>,
  ProgramNodeEdge: ResolverTypeWrapper<ProgramNodeEdge>,
  RegistrationDataImportNodeConnection: ResolverTypeWrapper<RegistrationDataImportNodeConnection>,
  RegistrationDataImportNodeEdge: ResolverTypeWrapper<RegistrationDataImportNodeEdge>,
  CashPlanNodeConnection: ResolverTypeWrapper<CashPlanNodeConnection>,
  CashPlanNodeEdge: ResolverTypeWrapper<CashPlanNodeEdge>,
  TargetPopulationNodeConnection: ResolverTypeWrapper<TargetPopulationNodeConnection>,
  TargetPopulationNodeEdge: ResolverTypeWrapper<TargetPopulationNodeEdge>,
  TargetPopulationNode: ResolverTypeWrapper<TargetPopulationNode>,
  TargetPopulationStatus: TargetPopulationStatus,
  TargetingCriteriaNode: ResolverTypeWrapper<TargetingCriteriaNode>,
  TargetingCriteriaRuleNode: ResolverTypeWrapper<TargetingCriteriaRuleNode>,
  TargetingCriteriaRuleFilterNode: ResolverTypeWrapper<TargetingCriteriaRuleFilterNode>,
  TargetingCriteriaRuleFilterComparisionMethod: TargetingCriteriaRuleFilterComparisionMethod,
  Arg: ResolverTypeWrapper<Scalars['Arg']>,
  FieldAttributeNode: ResolverTypeWrapper<FieldAttributeNode>,
  LabelNode: ResolverTypeWrapper<LabelNode>,
  CoreFieldChoiceObject: ResolverTypeWrapper<CoreFieldChoiceObject>,
  PaymentRecordNodeConnection: ResolverTypeWrapper<PaymentRecordNodeConnection>,
  PaymentRecordNodeEdge: ResolverTypeWrapper<PaymentRecordNodeEdge>,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  IndividualNodeConnection: ResolverTypeWrapper<IndividualNodeConnection>,
  IndividualNodeEdge: ResolverTypeWrapper<IndividualNodeEdge>,
  IndividualNode: ResolverTypeWrapper<IndividualNode>,
  IndividualRelationship: IndividualRelationship,
  IndividualRole: IndividualRole,
  IndividualSex: IndividualSex,
  IndividualMaritalStatus: IndividualMaritalStatus,
  DocumentNodeConnection: ResolverTypeWrapper<DocumentNodeConnection>,
  DocumentNodeEdge: ResolverTypeWrapper<DocumentNodeEdge>,
  DocumentNode: ResolverTypeWrapper<DocumentNode>,
  DocumentTypeNode: ResolverTypeWrapper<DocumentTypeNode>,
  Decimal: ResolverTypeWrapper<Scalars['Decimal']>,
  ProgramFrequencyOfPayments: ProgramFrequencyOfPayments,
  ProgramSector: ProgramSector,
  ProgramScope: ProgramScope,
  LogEntryObjectConnection: ResolverTypeWrapper<LogEntryObjectConnection>,
  LogEntryObjectEdge: ResolverTypeWrapper<LogEntryObjectEdge>,
  LogEntryObject: ResolverTypeWrapper<LogEntryObject>,
  LogEntryAction: LogEntryAction,
  JSONLazyString: ResolverTypeWrapper<Scalars['JSONLazyString']>,
  CashPlanStatus: CashPlanStatus,
  Float: ResolverTypeWrapper<Scalars['Float']>,
  PaymentEntitlementNode: ResolverTypeWrapper<PaymentEntitlementNode>,
  PaymentEntitlementDeliveryType: PaymentEntitlementDeliveryType,
  ChoiceObject: ResolverTypeWrapper<ChoiceObject>,
  TargetingCriteriaObjectType: TargetingCriteriaObjectType,
  TargetingCriteriaRuleObjectType: TargetingCriteriaRuleObjectType,
  TargetingCriteriaRuleFilterObjectType: TargetingCriteriaRuleFilterObjectType,
  UserObjectType: ResolverTypeWrapper<UserObjectType>,
  ImportedHouseholdNode: ResolverTypeWrapper<ImportedHouseholdNode>,
  ImportedHouseholdResidenceStatus: ImportedHouseholdResidenceStatus,
  ImportedIndividualNode: ResolverTypeWrapper<ImportedIndividualNode>,
  ImportedIndividualRelationship: ImportedIndividualRelationship,
  ImportedIndividualRole: ImportedIndividualRole,
  ImportedIndividualSex: ImportedIndividualSex,
  ImportedIndividualMaritalStatus: ImportedIndividualMaritalStatus,
  RegistrationDataImportDatahubNode: ResolverTypeWrapper<RegistrationDataImportDatahubNode>,
  ImportDataNode: ResolverTypeWrapper<ImportDataNode>,
  ImportedHouseholdNodeConnection: ResolverTypeWrapper<ImportedHouseholdNodeConnection>,
  ImportedHouseholdNodeEdge: ResolverTypeWrapper<ImportedHouseholdNodeEdge>,
  ImportedIndividualNodeConnection: ResolverTypeWrapper<ImportedIndividualNodeConnection>,
  ImportedIndividualNodeEdge: ResolverTypeWrapper<ImportedIndividualNodeEdge>,
  JSONString: ResolverTypeWrapper<Scalars['JSONString']>,
  ImportedDocumentNodeConnection: ResolverTypeWrapper<ImportedDocumentNodeConnection>,
  ImportedDocumentNodeEdge: ResolverTypeWrapper<ImportedDocumentNodeEdge>,
  ImportedDocumentNode: ResolverTypeWrapper<ImportedDocumentNode>,
  ImportedDocumentTypeNode: ResolverTypeWrapper<ImportedDocumentTypeNode>,
  ImportedDocumentTypeCountry: ImportedDocumentTypeCountry,
  RegistrationDataImportDatahubNodeConnection: ResolverTypeWrapper<RegistrationDataImportDatahubNodeConnection>,
  RegistrationDataImportDatahubNodeEdge: ResolverTypeWrapper<RegistrationDataImportDatahubNodeEdge>,
  DjangoDebug: ResolverTypeWrapper<DjangoDebug>,
  DjangoDebugSQL: ResolverTypeWrapper<DjangoDebugSql>,
  Mutations: ResolverTypeWrapper<{}>,
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
  CreateProgramInput: CreateProgramInput,
  CreateProgram: ResolverTypeWrapper<CreateProgram>,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: ResolverTypeWrapper<UpdateProgram>,
  DeleteProgram: ResolverTypeWrapper<DeleteProgram>,
  Upload: ResolverTypeWrapper<Scalars['Upload']>,
  UploadImportDataXLSXFile: ResolverTypeWrapper<UploadImportDataXlsxFile>,
  XlsxRowErrorNode: ResolverTypeWrapper<XlsxRowErrorNode>,
  DeleteRegistrationDataImport: ResolverTypeWrapper<DeleteRegistrationDataImport>,
  CreateRegistrationDataImportExcelInput: CreateRegistrationDataImportExcelInput,
  CreateRegistrationDataImport: ResolverTypeWrapper<CreateRegistrationDataImport>,
  ApproveRegistrationDataImportMutation: ResolverTypeWrapper<ApproveRegistrationDataImportMutation>,
  UnapproveRegistrationDataImportMutation: ResolverTypeWrapper<UnapproveRegistrationDataImportMutation>,
  MergeRegistrationDataImportMutation: ResolverTypeWrapper<MergeRegistrationDataImportMutation>,
};

/** Mapping between all available schema types and the resolvers parents */
export type ResolversParentTypes = {
  Query: {},
  ID: Scalars['ID'],
  PaymentRecordNode: PaymentRecordNode,
  Node: Node,
  DateTime: Scalars['DateTime'],
  PaymentRecordStatus: PaymentRecordStatus,
  String: Scalars['String'],
  CashPlanNode: CashPlanNode,
  ProgramNode: ProgramNode,
  ProgramStatus: ProgramStatus,
  Date: Scalars['Date'],
  Int: Scalars['Int'],
  AdminAreaNodeConnection: AdminAreaNodeConnection,
  PageInfo: PageInfo,
  Boolean: Scalars['Boolean'],
  AdminAreaNodeEdge: AdminAreaNodeEdge,
  AdminAreaNode: AdminAreaNode,
  HouseholdNodeConnection: HouseholdNodeConnection,
  HouseholdNodeEdge: HouseholdNodeEdge,
  HouseholdNode: HouseholdNode,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  GeoJSON: Scalars['GeoJSON'],
  RegistrationDataImportNode: RegistrationDataImportNode,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  UserNode: UserNode,
  UUID: Scalars['UUID'],
  BusinessAreaNodeConnection: BusinessAreaNodeConnection,
  BusinessAreaNodeEdge: BusinessAreaNodeEdge,
  BusinessAreaNode: BusinessAreaNode,
  UserNodeConnection: UserNodeConnection,
  UserNodeEdge: UserNodeEdge,
  ProgramNodeConnection: ProgramNodeConnection,
  ProgramNodeEdge: ProgramNodeEdge,
  RegistrationDataImportNodeConnection: RegistrationDataImportNodeConnection,
  RegistrationDataImportNodeEdge: RegistrationDataImportNodeEdge,
  CashPlanNodeConnection: CashPlanNodeConnection,
  CashPlanNodeEdge: CashPlanNodeEdge,
  TargetPopulationNodeConnection: TargetPopulationNodeConnection,
  TargetPopulationNodeEdge: TargetPopulationNodeEdge,
  TargetPopulationNode: TargetPopulationNode,
  TargetPopulationStatus: TargetPopulationStatus,
  TargetingCriteriaNode: TargetingCriteriaNode,
  TargetingCriteriaRuleNode: TargetingCriteriaRuleNode,
  TargetingCriteriaRuleFilterNode: TargetingCriteriaRuleFilterNode,
  TargetingCriteriaRuleFilterComparisionMethod: TargetingCriteriaRuleFilterComparisionMethod,
  Arg: Scalars['Arg'],
  FieldAttributeNode: FieldAttributeNode,
  LabelNode: LabelNode,
  CoreFieldChoiceObject: CoreFieldChoiceObject,
  PaymentRecordNodeConnection: PaymentRecordNodeConnection,
  PaymentRecordNodeEdge: PaymentRecordNodeEdge,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  IndividualNodeConnection: IndividualNodeConnection,
  IndividualNodeEdge: IndividualNodeEdge,
  IndividualNode: IndividualNode,
  IndividualRelationship: IndividualRelationship,
  IndividualRole: IndividualRole,
  IndividualSex: IndividualSex,
  IndividualMaritalStatus: IndividualMaritalStatus,
  DocumentNodeConnection: DocumentNodeConnection,
  DocumentNodeEdge: DocumentNodeEdge,
  DocumentNode: DocumentNode,
  DocumentTypeNode: DocumentTypeNode,
  Decimal: Scalars['Decimal'],
  ProgramFrequencyOfPayments: ProgramFrequencyOfPayments,
  ProgramSector: ProgramSector,
  ProgramScope: ProgramScope,
  LogEntryObjectConnection: LogEntryObjectConnection,
  LogEntryObjectEdge: LogEntryObjectEdge,
  LogEntryObject: LogEntryObject,
  LogEntryAction: LogEntryAction,
  JSONLazyString: Scalars['JSONLazyString'],
  CashPlanStatus: CashPlanStatus,
  Float: Scalars['Float'],
  PaymentEntitlementNode: PaymentEntitlementNode,
  PaymentEntitlementDeliveryType: PaymentEntitlementDeliveryType,
  ChoiceObject: ChoiceObject,
  TargetingCriteriaObjectType: TargetingCriteriaObjectType,
  TargetingCriteriaRuleObjectType: TargetingCriteriaRuleObjectType,
  TargetingCriteriaRuleFilterObjectType: TargetingCriteriaRuleFilterObjectType,
  UserObjectType: UserObjectType,
  ImportedHouseholdNode: ImportedHouseholdNode,
  ImportedHouseholdResidenceStatus: ImportedHouseholdResidenceStatus,
  ImportedIndividualNode: ImportedIndividualNode,
  ImportedIndividualRelationship: ImportedIndividualRelationship,
  ImportedIndividualRole: ImportedIndividualRole,
  ImportedIndividualSex: ImportedIndividualSex,
  ImportedIndividualMaritalStatus: ImportedIndividualMaritalStatus,
  RegistrationDataImportDatahubNode: RegistrationDataImportDatahubNode,
  ImportDataNode: ImportDataNode,
  ImportedHouseholdNodeConnection: ImportedHouseholdNodeConnection,
  ImportedHouseholdNodeEdge: ImportedHouseholdNodeEdge,
  ImportedIndividualNodeConnection: ImportedIndividualNodeConnection,
  ImportedIndividualNodeEdge: ImportedIndividualNodeEdge,
  JSONString: Scalars['JSONString'],
  ImportedDocumentNodeConnection: ImportedDocumentNodeConnection,
  ImportedDocumentNodeEdge: ImportedDocumentNodeEdge,
  ImportedDocumentNode: ImportedDocumentNode,
  ImportedDocumentTypeNode: ImportedDocumentTypeNode,
  ImportedDocumentTypeCountry: ImportedDocumentTypeCountry,
  RegistrationDataImportDatahubNodeConnection: RegistrationDataImportDatahubNodeConnection,
  RegistrationDataImportDatahubNodeEdge: RegistrationDataImportDatahubNodeEdge,
  DjangoDebug: DjangoDebug,
  DjangoDebugSQL: DjangoDebugSql,
  Mutations: {},
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
  CreateProgramInput: CreateProgramInput,
  CreateProgram: CreateProgram,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: UpdateProgram,
  DeleteProgram: DeleteProgram,
  Upload: Scalars['Upload'],
  UploadImportDataXLSXFile: UploadImportDataXlsxFile,
  XlsxRowErrorNode: XlsxRowErrorNode,
  DeleteRegistrationDataImport: DeleteRegistrationDataImport,
  CreateRegistrationDataImportExcelInput: CreateRegistrationDataImportExcelInput,
  CreateRegistrationDataImport: CreateRegistrationDataImport,
  ApproveRegistrationDataImportMutation: ApproveRegistrationDataImportMutation,
  UnapproveRegistrationDataImportMutation: UnapproveRegistrationDataImportMutation,
  MergeRegistrationDataImportMutation: MergeRegistrationDataImportMutation,
};

export type AdminAreaNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['AdminAreaNode'] = ResolversParentTypes['AdminAreaNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  title?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  parent?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType>,
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

export type ApproveRegistrationDataImportMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['ApproveRegistrationDataImportMutation'] = ResolversParentTypes['ApproveRegistrationDataImportMutation']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
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
  slug?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  userSet?: Resolver<ResolversTypes['UserNodeConnection'], ParentType, ContextType, BusinessAreaNodeUserSetArgs>,
  programSet?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, BusinessAreaNodeProgramSetArgs>,
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
  program?: Resolver<ResolversTypes['ProgramNode'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  startDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  endDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  disbursementDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  numberOfHouseholds?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  createdDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  createdBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  coverageDuration?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  coverageUnits?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  targetPopulation?: Resolver<ResolversTypes['TargetPopulationNode'], ParentType, ContextType>,
  cashAssistId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  distributionModality?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fsp?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['CashPlanStatus'], ParentType, ContextType>,
  currency?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  totalEntitledQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  totalDeliveredQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  totalUndeliveredQuantity?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  dispersionDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  deliveryType?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  assistanceThrough?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fcId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  dpId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, CashPlanNodePaymentRecordsArgs>,
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

export type CreateProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateProgram'] = ResolversParentTypes['CreateProgram']> = {
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
};

export type CreateRegistrationDataImportResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateRegistrationDataImport'] = ResolversParentTypes['CreateRegistrationDataImport']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
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
  type?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  label?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['DocumentNodeConnection'], ParentType, ContextType, DocumentTypeNodeDocumentsArgs>,
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

export interface GeoJsonScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['GeoJSON'], any> {
  name: 'GeoJSON'
}

export type HouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNode'] = ResolversParentTypes['HouseholdNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  residenceStatus?: Resolver<ResolversTypes['HouseholdResidenceStatus'], ParentType, ContextType>,
  countryOrigin?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  size?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  address?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  adminArea?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType>,
  geopoint?: Resolver<Maybe<ResolversTypes['GeoJSON']>, ParentType, ContextType>,
  unhcrId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
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
  registrationDate?: Resolver<Maybe<ResolversTypes['Date']>, ParentType, ContextType>,
  headOfHousehold?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
  individuals?: Resolver<ResolversTypes['IndividualNodeConnection'], ParentType, ContextType, HouseholdNodeIndividualsArgs>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, HouseholdNodePaymentRecordsArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, HouseholdNodeTargetPopulationsArgs>,
  totalCashReceived?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
};

export type HouseholdNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNodeConnection'] = ResolversParentTypes['HouseholdNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['HouseholdNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type HouseholdNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNodeEdge'] = ResolversParentTypes['HouseholdNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
};

export type ImportDataNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportDataNode'] = ResolversParentTypes['ImportDataNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  xlsxFile?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
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
  type?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  label?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['ImportedDocumentNodeConnection'], ParentType, ContextType, ImportedDocumentTypeNodeDocumentsArgs>,
};

export type ImportedHouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedHouseholdNode'] = ResolversParentTypes['ImportedHouseholdNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  residenceStatus?: Resolver<ResolversTypes['ImportedHouseholdResidenceStatus'], ParentType, ContextType>,
  countryOrigin?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  size?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  address?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  country?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  admin1?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  admin2?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  geopoint?: Resolver<Maybe<ResolversTypes['GeoJSON']>, ParentType, ContextType>,
  unhcrId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
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
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportDatahubNode'], ParentType, ContextType>,
  registrationDate?: Resolver<Maybe<ResolversTypes['Date']>, ParentType, ContextType>,
  returnee?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  flexFields?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  individuals?: Resolver<ResolversTypes['ImportedIndividualNodeConnection'], ParentType, ContextType, ImportedHouseholdNodeIndividualsArgs>,
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
  relationship?: Resolver<Maybe<ResolversTypes['ImportedIndividualRelationship']>, ParentType, ContextType>,
  role?: Resolver<Maybe<ResolversTypes['ImportedIndividualRole']>, ParentType, ContextType>,
  sex?: Resolver<ResolversTypes['ImportedIndividualSex'], ParentType, ContextType>,
  birthDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  estimatedBirthDate?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  maritalStatus?: Resolver<ResolversTypes['ImportedIndividualMaritalStatus'], ParentType, ContextType>,
  phoneNo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  phoneNoAlternative?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['ImportedHouseholdNode'], ParentType, ContextType>,
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportDatahubNode'], ParentType, ContextType>,
  disability?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  flexFields?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  importedhousehold?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['ImportedDocumentNodeConnection'], ParentType, ContextType, ImportedIndividualNodeDocumentsArgs>,
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

export type IndividualNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['IndividualNode'] = ResolversParentTypes['IndividualNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  individualId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  photo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  givenName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  middleName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  familyName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  relationship?: Resolver<Maybe<ResolversTypes['IndividualRelationship']>, ParentType, ContextType>,
  role?: Resolver<Maybe<ResolversTypes['IndividualRole']>, ParentType, ContextType>,
  sex?: Resolver<ResolversTypes['IndividualSex'], ParentType, ContextType>,
  birthDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  estimatedBirthDate?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
  maritalStatus?: Resolver<ResolversTypes['IndividualMaritalStatus'], ParentType, ContextType>,
  phoneNo?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  phoneNoAlternative?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
  registrationDataImport?: Resolver<ResolversTypes['RegistrationDataImportNode'], ParentType, ContextType>,
  disability?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  headingHousehold?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
  documents?: Resolver<ResolversTypes['DocumentNodeConnection'], ParentType, ContextType, IndividualNodeDocumentsArgs>,
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

export interface JsonLazyStringScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['JSONLazyString'], any> {
  name: 'JSONLazyString'
}

export interface JsonStringScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['JSONString'], any> {
  name: 'JSONString'
}

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
  createTargetPopulation?: Resolver<Maybe<ResolversTypes['CreateTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsCreateTargetPopulationArgs, 'input'>>,
  updateTargetPopulation?: Resolver<Maybe<ResolversTypes['UpdateTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsUpdateTargetPopulationArgs, 'input'>>,
  copyTargetPopulation?: Resolver<Maybe<ResolversTypes['CopyTargetPopulationMutationPayload']>, ParentType, ContextType, RequireFields<MutationsCopyTargetPopulationArgs, 'input'>>,
  deleteTargetPopulation?: Resolver<Maybe<ResolversTypes['DeleteTargetPopulationMutationPayload']>, ParentType, ContextType, RequireFields<MutationsDeleteTargetPopulationArgs, 'input'>>,
  approveTargetPopulation?: Resolver<Maybe<ResolversTypes['ApproveTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsApproveTargetPopulationArgs, 'id' | 'programId'>>,
  unapproveTargetPopulation?: Resolver<Maybe<ResolversTypes['UnapproveTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsUnapproveTargetPopulationArgs, 'id'>>,
  finalizeTargetPopulation?: Resolver<Maybe<ResolversTypes['FinalizeTargetPopulationMutation']>, ParentType, ContextType, RequireFields<MutationsFinalizeTargetPopulationArgs, 'id'>>,
  createProgram?: Resolver<Maybe<ResolversTypes['CreateProgram']>, ParentType, ContextType, RequireFields<MutationsCreateProgramArgs, 'programData'>>,
  updateProgram?: Resolver<Maybe<ResolversTypes['UpdateProgram']>, ParentType, ContextType, MutationsUpdateProgramArgs>,
  deleteProgram?: Resolver<Maybe<ResolversTypes['DeleteProgram']>, ParentType, ContextType, RequireFields<MutationsDeleteProgramArgs, 'programId'>>,
  uploadImportDataXlsxFile?: Resolver<Maybe<ResolversTypes['UploadImportDataXLSXFile']>, ParentType, ContextType, RequireFields<MutationsUploadImportDataXlsxFileArgs, 'file'>>,
  deleteRegistrationDataImport?: Resolver<Maybe<ResolversTypes['DeleteRegistrationDataImport']>, ParentType, ContextType, RequireFields<MutationsDeleteRegistrationDataImportArgs, 'registrationDataImportId'>>,
  createRegistrationDataImport?: Resolver<Maybe<ResolversTypes['CreateRegistrationDataImport']>, ParentType, ContextType, RequireFields<MutationsCreateRegistrationDataImportArgs, 'registrationDataImportData'>>,
  approveRegistrationDataImport?: Resolver<Maybe<ResolversTypes['ApproveRegistrationDataImportMutation']>, ParentType, ContextType, RequireFields<MutationsApproveRegistrationDataImportArgs, 'id'>>,
  unapproveRegistrationDataImport?: Resolver<Maybe<ResolversTypes['UnapproveRegistrationDataImportMutation']>, ParentType, ContextType, RequireFields<MutationsUnapproveRegistrationDataImportArgs, 'id'>>,
  mergeRegistrationDataImport?: Resolver<Maybe<ResolversTypes['MergeRegistrationDataImportMutation']>, ParentType, ContextType, RequireFields<MutationsMergeRegistrationDataImportArgs, 'id'>>,
};

export type NodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['Node'] = ResolversParentTypes['Node']> = {
  __resolveType: TypeResolveFn<'PaymentRecordNode' | 'CashPlanNode' | 'ProgramNode' | 'AdminAreaNode' | 'HouseholdNode' | 'RegistrationDataImportNode' | 'UserNode' | 'BusinessAreaNode' | 'TargetPopulationNode' | 'IndividualNode' | 'DocumentNode' | 'ImportedHouseholdNode' | 'ImportedIndividualNode' | 'RegistrationDataImportDatahubNode' | 'ImportDataNode' | 'ImportedDocumentNode', ParentType, ContextType>,
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
};

export type PageInfoResolvers<ContextType = any, ParentType extends ResolversParentTypes['PageInfo'] = ResolversParentTypes['PageInfo']> = {
  hasNextPage?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  hasPreviousPage?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  startCursor?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  endCursor?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type PaymentEntitlementNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentEntitlementNode'] = ResolversParentTypes['PaymentEntitlementNode']> = {
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  deliveryType?: Resolver<ResolversTypes['PaymentEntitlementDeliveryType'], ParentType, ContextType>,
  entitlementQuantity?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  deliveredQuantity?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  entitlementCardIssueDate?: Resolver<Maybe<ResolversTypes['Date']>, ParentType, ContextType>,
  entitlementCardNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  currency?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  deliveryDate?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  transactionReferenceId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fsp?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  paymentRecord?: Resolver<Maybe<ResolversTypes['PaymentRecordNode']>, ParentType, ContextType>,
};

export type PaymentRecordNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['PaymentRecordNode'] = ResolversParentTypes['PaymentRecordNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['PaymentRecordStatus'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  statusDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  cashAssistId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  cashPlan?: Resolver<ResolversTypes['CashPlanNode'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
  headOfHousehold?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  totalPersonCovered?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  distributionModality?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  targetPopulation?: Resolver<ResolversTypes['TargetPopulationNode'], ParentType, ContextType>,
  entitlement?: Resolver<Maybe<ResolversTypes['PaymentEntitlementNode']>, ParentType, ContextType>,
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

export type ProgramNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ProgramNode'] = ResolversParentTypes['ProgramNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['ProgramStatus'], ParentType, ContextType>,
  startDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  endDate?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  description?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  programCaId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  adminAreas?: Resolver<ResolversTypes['AdminAreaNodeConnection'], ParentType, ContextType, ProgramNodeAdminAreasArgs>,
  businessArea?: Resolver<ResolversTypes['BusinessAreaNode'], ParentType, ContextType>,
  budget?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  frequencyOfPayments?: Resolver<ResolversTypes['ProgramFrequencyOfPayments'], ParentType, ContextType>,
  sector?: Resolver<ResolversTypes['ProgramSector'], ParentType, ContextType>,
  scope?: Resolver<ResolversTypes['ProgramScope'], ParentType, ContextType>,
  cashPlus?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  populationGoal?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  administrativeAreasOfImplementation?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
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
  paymentRecord?: Resolver<Maybe<ResolversTypes['PaymentRecordNode']>, ParentType, ContextType, RequireFields<QueryPaymentRecordArgs, 'id'>>,
  allPaymentRecords?: Resolver<Maybe<ResolversTypes['PaymentRecordNodeConnection']>, ParentType, ContextType, QueryAllPaymentRecordsArgs>,
  paymentRecordStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  allPaymentEntitlements?: Resolver<Maybe<Array<Maybe<ResolversTypes['PaymentEntitlementNode']>>>, ParentType, ContextType>,
  adminArea?: Resolver<Maybe<ResolversTypes['AdminAreaNode']>, ParentType, ContextType, RequireFields<QueryAdminAreaArgs, 'id'>>,
  allAdminAreas?: Resolver<Maybe<ResolversTypes['AdminAreaNodeConnection']>, ParentType, ContextType, QueryAllAdminAreasArgs>,
  allBusinessAreas?: Resolver<Maybe<ResolversTypes['BusinessAreaNodeConnection']>, ParentType, ContextType, QueryAllBusinessAreasArgs>,
  allLogEntries?: Resolver<Maybe<ResolversTypes['LogEntryObjectConnection']>, ParentType, ContextType, RequireFields<QueryAllLogEntriesArgs, 'objectId'>>,
  allFieldsAttributes?: Resolver<Maybe<Array<Maybe<ResolversTypes['FieldAttributeNode']>>>, ParentType, ContextType, QueryAllFieldsAttributesArgs>,
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType, RequireFields<QueryProgramArgs, 'id'>>,
  allPrograms?: Resolver<Maybe<ResolversTypes['ProgramNodeConnection']>, ParentType, ContextType, QueryAllProgramsArgs>,
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
  allUsers?: Resolver<Maybe<ResolversTypes['UserNodeConnection']>, ParentType, ContextType, QueryAllUsersArgs>,
  importedHousehold?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType, RequireFields<QueryImportedHouseholdArgs, 'id'>>,
  allImportedHouseholds?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNodeConnection']>, ParentType, ContextType, QueryAllImportedHouseholdsArgs>,
  registrationDataImportDatahub?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNode']>, ParentType, ContextType, RequireFields<QueryRegistrationDataImportDatahubArgs, 'id'>>,
  allRegistrationDataImportsDatahub?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNodeConnection']>, ParentType, ContextType, QueryAllRegistrationDataImportsDatahubArgs>,
  importedIndividual?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType, RequireFields<QueryImportedIndividualArgs, 'id'>>,
  allImportedIndividuals?: Resolver<Maybe<ResolversTypes['ImportedIndividualNodeConnection']>, ParentType, ContextType, QueryAllImportedIndividualsArgs>,
  importData?: Resolver<Maybe<ResolversTypes['ImportDataNode']>, ParentType, ContextType, RequireFields<QueryImportDataArgs, 'id'>>,
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType, RequireFields<QueryRegistrationDataImportArgs, 'id'>>,
  allRegistrationDataImports?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNodeConnection']>, ParentType, ContextType, QueryAllRegistrationDataImportsArgs>,
  registrationDataStatusChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  _debug?: Resolver<Maybe<ResolversTypes['DjangoDebug']>, ParentType, ContextType>,
};

export type RegistrationDataImportDatahubNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportDatahubNode'] = ResolversParentTypes['RegistrationDataImportDatahubNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  importDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  hctId?: Resolver<Maybe<ResolversTypes['UUID']>, ParentType, ContextType>,
  importData?: Resolver<Maybe<ResolversTypes['ImportDataNode']>, ParentType, ContextType>,
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
  businessArea?: Resolver<Maybe<ResolversTypes['BusinessAreaNode']>, ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, RegistrationDataImportNodeHouseholdsArgs>,
  individuals?: Resolver<ResolversTypes['IndividualNodeConnection'], ParentType, ContextType, RegistrationDataImportNodeIndividualsArgs>,
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
  filters?: Resolver<Maybe<Array<Maybe<ResolversTypes['TargetingCriteriaRuleFilterNode']>>>, ParentType, ContextType>,
};

export type TargetPopulationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetPopulationNode'] = ResolversParentTypes['TargetPopulationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  isRemoved?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  createdBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
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
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, TargetPopulationNodePaymentRecordsArgs>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, TargetPopulationNodeCashPlansArgs>,
  totalHouseholds?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  totalFamilySize?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  finalList?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, TargetPopulationNodeFinalListArgs>,
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

export type UnapproveRegistrationDataImportMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['UnapproveRegistrationDataImportMutation'] = ResolversParentTypes['UnapproveRegistrationDataImportMutation']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
};

export type UnapproveTargetPopulationMutationResolvers<ContextType = any, ParentType extends ResolversParentTypes['UnapproveTargetPopulationMutation'] = ResolversParentTypes['UnapproveTargetPopulationMutation']> = {
  targetPopulation?: Resolver<Maybe<ResolversTypes['TargetPopulationNode']>, ParentType, ContextType>,
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

export type UserNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['UserNode'] = ResolversParentTypes['UserNode']> = {
  lastLogin?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  isSuperuser?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  username?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  firstName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  lastName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  email?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  isStaff?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  isActive?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  dateJoined?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  businessAreas?: Resolver<ResolversTypes['BusinessAreaNodeConnection'], ParentType, ContextType, UserNodeBusinessAreasArgs>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, UserNodeCashPlansArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserNodeTargetPopulationsArgs>,
  registrationDataImports?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, UserNodeRegistrationDataImportsArgs>,
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
  lastLogin?: Resolver<Maybe<ResolversTypes['DateTime']>, ParentType, ContextType>,
  isSuperuser?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  username?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  firstName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  lastName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  email?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  isStaff?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  isActive?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  dateJoined?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  id?: Resolver<ResolversTypes['UUID'], ParentType, ContextType>,
  businessAreas?: Resolver<ResolversTypes['BusinessAreaNodeConnection'], ParentType, ContextType, UserObjectTypeBusinessAreasArgs>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, UserObjectTypeCashPlansArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserObjectTypeTargetPopulationsArgs>,
  registrationDataImports?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, UserObjectTypeRegistrationDataImportsArgs>,
};

export interface UuidScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['UUID'], any> {
  name: 'UUID'
}

export type XlsxRowErrorNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['XlsxRowErrorNode'] = ResolversParentTypes['XlsxRowErrorNode']> = {
  rowNumber?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  header?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  message?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
};

export type Resolvers<ContextType = any> = {
  AdminAreaNode?: AdminAreaNodeResolvers<ContextType>,
  AdminAreaNodeConnection?: AdminAreaNodeConnectionResolvers<ContextType>,
  AdminAreaNodeEdge?: AdminAreaNodeEdgeResolvers<ContextType>,
  ApproveRegistrationDataImportMutation?: ApproveRegistrationDataImportMutationResolvers<ContextType>,
  ApproveTargetPopulationMutation?: ApproveTargetPopulationMutationResolvers<ContextType>,
  Arg?: GraphQLScalarType,
  BusinessAreaNode?: BusinessAreaNodeResolvers<ContextType>,
  BusinessAreaNodeConnection?: BusinessAreaNodeConnectionResolvers<ContextType>,
  BusinessAreaNodeEdge?: BusinessAreaNodeEdgeResolvers<ContextType>,
  CashPlanNode?: CashPlanNodeResolvers<ContextType>,
  CashPlanNodeConnection?: CashPlanNodeConnectionResolvers<ContextType>,
  CashPlanNodeEdge?: CashPlanNodeEdgeResolvers<ContextType>,
  ChoiceObject?: ChoiceObjectResolvers<ContextType>,
  CopyTargetPopulationMutationPayload?: CopyTargetPopulationMutationPayloadResolvers<ContextType>,
  CoreFieldChoiceObject?: CoreFieldChoiceObjectResolvers<ContextType>,
  CreateProgram?: CreateProgramResolvers<ContextType>,
  CreateRegistrationDataImport?: CreateRegistrationDataImportResolvers<ContextType>,
  CreateTargetPopulationMutation?: CreateTargetPopulationMutationResolvers<ContextType>,
  Date?: GraphQLScalarType,
  DateTime?: GraphQLScalarType,
  Decimal?: GraphQLScalarType,
  DeleteProgram?: DeleteProgramResolvers<ContextType>,
  DeleteRegistrationDataImport?: DeleteRegistrationDataImportResolvers<ContextType>,
  DeleteTargetPopulationMutationPayload?: DeleteTargetPopulationMutationPayloadResolvers<ContextType>,
  DjangoDebug?: DjangoDebugResolvers<ContextType>,
  DjangoDebugSQL?: DjangoDebugSqlResolvers<ContextType>,
  DocumentNode?: DocumentNodeResolvers<ContextType>,
  DocumentNodeConnection?: DocumentNodeConnectionResolvers<ContextType>,
  DocumentNodeEdge?: DocumentNodeEdgeResolvers<ContextType>,
  DocumentTypeNode?: DocumentTypeNodeResolvers<ContextType>,
  FieldAttributeNode?: FieldAttributeNodeResolvers<ContextType>,
  FinalizeTargetPopulationMutation?: FinalizeTargetPopulationMutationResolvers<ContextType>,
  GeoJSON?: GraphQLScalarType,
  HouseholdNode?: HouseholdNodeResolvers<ContextType>,
  HouseholdNodeConnection?: HouseholdNodeConnectionResolvers<ContextType>,
  HouseholdNodeEdge?: HouseholdNodeEdgeResolvers<ContextType>,
  ImportDataNode?: ImportDataNodeResolvers<ContextType>,
  ImportedDocumentNode?: ImportedDocumentNodeResolvers<ContextType>,
  ImportedDocumentNodeConnection?: ImportedDocumentNodeConnectionResolvers<ContextType>,
  ImportedDocumentNodeEdge?: ImportedDocumentNodeEdgeResolvers<ContextType>,
  ImportedDocumentTypeNode?: ImportedDocumentTypeNodeResolvers<ContextType>,
  ImportedHouseholdNode?: ImportedHouseholdNodeResolvers<ContextType>,
  ImportedHouseholdNodeConnection?: ImportedHouseholdNodeConnectionResolvers<ContextType>,
  ImportedHouseholdNodeEdge?: ImportedHouseholdNodeEdgeResolvers<ContextType>,
  ImportedIndividualNode?: ImportedIndividualNodeResolvers<ContextType>,
  ImportedIndividualNodeConnection?: ImportedIndividualNodeConnectionResolvers<ContextType>,
  ImportedIndividualNodeEdge?: ImportedIndividualNodeEdgeResolvers<ContextType>,
  IndividualNode?: IndividualNodeResolvers<ContextType>,
  IndividualNodeConnection?: IndividualNodeConnectionResolvers<ContextType>,
  IndividualNodeEdge?: IndividualNodeEdgeResolvers<ContextType>,
  JSONLazyString?: GraphQLScalarType,
  JSONString?: GraphQLScalarType,
  LabelNode?: LabelNodeResolvers<ContextType>,
  LogEntryObject?: LogEntryObjectResolvers<ContextType>,
  LogEntryObjectConnection?: LogEntryObjectConnectionResolvers<ContextType>,
  LogEntryObjectEdge?: LogEntryObjectEdgeResolvers<ContextType>,
  MergeRegistrationDataImportMutation?: MergeRegistrationDataImportMutationResolvers<ContextType>,
  Mutations?: MutationsResolvers<ContextType>,
  Node?: NodeResolvers,
  PageInfo?: PageInfoResolvers<ContextType>,
  PaymentEntitlementNode?: PaymentEntitlementNodeResolvers<ContextType>,
  PaymentRecordNode?: PaymentRecordNodeResolvers<ContextType>,
  PaymentRecordNodeConnection?: PaymentRecordNodeConnectionResolvers<ContextType>,
  PaymentRecordNodeEdge?: PaymentRecordNodeEdgeResolvers<ContextType>,
  ProgramNode?: ProgramNodeResolvers<ContextType>,
  ProgramNodeConnection?: ProgramNodeConnectionResolvers<ContextType>,
  ProgramNodeEdge?: ProgramNodeEdgeResolvers<ContextType>,
  Query?: QueryResolvers<ContextType>,
  RegistrationDataImportDatahubNode?: RegistrationDataImportDatahubNodeResolvers<ContextType>,
  RegistrationDataImportDatahubNodeConnection?: RegistrationDataImportDatahubNodeConnectionResolvers<ContextType>,
  RegistrationDataImportDatahubNodeEdge?: RegistrationDataImportDatahubNodeEdgeResolvers<ContextType>,
  RegistrationDataImportNode?: RegistrationDataImportNodeResolvers<ContextType>,
  RegistrationDataImportNodeConnection?: RegistrationDataImportNodeConnectionResolvers<ContextType>,
  RegistrationDataImportNodeEdge?: RegistrationDataImportNodeEdgeResolvers<ContextType>,
  TargetingCriteriaNode?: TargetingCriteriaNodeResolvers<ContextType>,
  TargetingCriteriaRuleFilterNode?: TargetingCriteriaRuleFilterNodeResolvers<ContextType>,
  TargetingCriteriaRuleNode?: TargetingCriteriaRuleNodeResolvers<ContextType>,
  TargetPopulationNode?: TargetPopulationNodeResolvers<ContextType>,
  TargetPopulationNodeConnection?: TargetPopulationNodeConnectionResolvers<ContextType>,
  TargetPopulationNodeEdge?: TargetPopulationNodeEdgeResolvers<ContextType>,
  UnapproveRegistrationDataImportMutation?: UnapproveRegistrationDataImportMutationResolvers<ContextType>,
  UnapproveTargetPopulationMutation?: UnapproveTargetPopulationMutationResolvers<ContextType>,
  UpdateProgram?: UpdateProgramResolvers<ContextType>,
  UpdateTargetPopulationMutation?: UpdateTargetPopulationMutationResolvers<ContextType>,
  Upload?: GraphQLScalarType,
  UploadImportDataXLSXFile?: UploadImportDataXlsxFileResolvers<ContextType>,
  UserNode?: UserNodeResolvers<ContextType>,
  UserNodeConnection?: UserNodeConnectionResolvers<ContextType>,
  UserNodeEdge?: UserNodeEdgeResolvers<ContextType>,
  UserObjectType?: UserObjectTypeResolvers<ContextType>,
  UUID?: GraphQLScalarType,
  XlsxRowErrorNode?: XlsxRowErrorNodeResolvers<ContextType>,
};


/**
 * @deprecated
 * Use "Resolvers" root object instead. If you wish to get "IResolvers", add "typesPrefix: I" to your config.
*/
export type IResolvers<ContextType = any> = Resolvers<ContextType>;

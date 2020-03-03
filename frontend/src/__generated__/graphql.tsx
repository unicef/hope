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
  JSONString: any,
  Decimal: any,
  JSONLazyString: any,
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
  locations: LocationNodeConnection,
  programSet: ProgramNodeConnection,
};


export type BusinessAreaNodeUserSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type BusinessAreaNodeLocationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
};


export type BusinessAreaNodeProgramSetArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
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

export type CreateCashPlan = {
   __typename?: 'CreateCashPlan',
  cashPlan?: Maybe<CashPlanNode>,
};

export type CreateCashPlanInput = {
  programId?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['DateTime']>,
  endDate?: Maybe<Scalars['DateTime']>,
  disbursementDate?: Maybe<Scalars['DateTime']>,
  numberOfHouseholds?: Maybe<Scalars['Int']>,
  coverageDuration?: Maybe<Scalars['Int']>,
  coverageUnits?: Maybe<Scalars['String']>,
  targetPopulationId?: Maybe<Scalars['String']>,
  cashAssistId?: Maybe<Scalars['String']>,
  distributionModality?: Maybe<Scalars['String']>,
  fsp?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>,
  currency?: Maybe<Scalars['String']>,
  totalEntitledQuantity?: Maybe<Scalars['Decimal']>,
  totalDeliveredQuantity?: Maybe<Scalars['Decimal']>,
  totalUndeliveredQuantity?: Maybe<Scalars['Decimal']>,
  dispersionDate?: Maybe<Scalars['Date']>,
};

export type CreateHousehold = {
   __typename?: 'CreateHousehold',
  household?: Maybe<HouseholdNode>,
};

export type CreateHouseholdInput = {
  householdCaId: Scalars['String'],
  residenceStatus: Scalars['String'],
  nationality: Scalars['String'],
  familySize?: Maybe<Scalars['Int']>,
  address?: Maybe<Scalars['String']>,
  locationId: Scalars['String'],
  registrationDataImportId: Scalars['String'],
};

export type CreateLocation = {
   __typename?: 'CreateLocation',
  location?: Maybe<LocationNode>,
};

export type CreateLocationInput = {
  name?: Maybe<Scalars['String']>,
  country?: Maybe<Scalars['String']>,
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




export type DeleteCashPlan = {
   __typename?: 'DeleteCashPlan',
  ok?: Maybe<Scalars['Boolean']>,
};

export type DeleteHousehold = {
   __typename?: 'DeleteHousehold',
  ok?: Maybe<Scalars['Boolean']>,
};

export type DeleteLocation = {
   __typename?: 'DeleteLocation',
  ok?: Maybe<Scalars['Boolean']>,
};

export type DeleteProgram = {
   __typename?: 'DeleteProgram',
  ok?: Maybe<Scalars['Boolean']>,
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

export enum HouseholdNationality {
  Af = 'AF',
  Al = 'AL',
  Dz = 'DZ',
  Ad = 'AD',
  Ao = 'AO',
  Ar = 'AR',
  Am = 'AM',
  A = 'A',
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
  Bt = 'BT',
  Bo = 'BO',
  Ba = 'BA',
  Bw = 'BW',
  Br = 'BR',
  Gb = 'GB',
  Bn = 'BN',
  Bg = 'BG',
  Bf = 'BF',
  Mm = 'MM',
  Bf_28 = 'BF_28',
  Bi = 'BI',
  Cm = 'CM',
  Ca = 'CA',
  Cv = 'CV',
  Td = 'TD',
  Cl = 'CL',
  Cn = 'CN',
  Co = 'CO',
  Cg = 'CG',
  Cr = 'CR',
  Hr = 'HR',
  C = 'C',
  Cy = 'CY',
  Cz = 'CZ',
  Dk = 'DK',
  Dj = 'DJ',
  Dm = 'DM',
  Do = 'DO',
  Ec = 'EC',
  Eg = 'EG',
  Sv = 'SV',
  Gb_50 = 'GB_50',
  Er = 'ER',
  Ee = 'EE',
  Et = 'ET',
  Fj = 'FJ',
  Fi = 'FI',
  Fr = 'FR',
  Ga = 'GA',
  Gm = 'GM',
  Ge = 'GE',
  De = 'DE',
  Gh = 'GH',
  Gr = 'GR',
  Gd = 'GD',
  Gt = 'GT',
  Gq = 'GQ',
  Gy = 'GY',
  Ht = 'HT',
  Nl = 'NL',
  Hn = 'HN',
  H = 'H',
  Is = 'IS',
  Io = 'IO',
  Id = 'ID',
  Ir = 'IR',
  Iq = 'IQ',
  Ie = 'IE',
  Il = 'IL',
  It = 'IT',
  Jm = 'JM',
  Jp = 'JP',
  Jo = 'JO',
  Kz = 'KZ',
  Ke = 'KE',
  Kw = 'KW',
  La = 'LA',
  Lv = 'LV',
  Lb = 'LB',
  Lr = 'LR',
  Ly = 'LY',
  Lt = 'LT',
  Mk = 'MK',
  Mg = 'MG',
  Mw = 'MW',
  My = 'MY',
  Mv = 'MV',
  Ml = 'ML',
  Mt = 'MT',
  Mr = 'MR',
  M = 'M',
  Mx = 'MX',
  Md = 'MD',
  Mc = 'MC',
  Mn = 'MN',
  Me = 'ME',
  Ma = 'MA',
  Mz = 'MZ',
  Na = 'NA',
  Np = 'NP',
  Ni = 'NI',
  Ne = 'NE',
  Ng = 'NG',
  Kp = 'KP',
  No = 'NO',
  Om = 'OM',
  Pk = 'PK',
  Pa = 'PA',
  Pg = 'PG',
  Py = 'PY',
  Pe = 'PE',
  Ph = 'PH',
  Pl = 'PL',
  Pt = 'PT',
  Qa = 'QA',
  Ro = 'RO',
  R = 'R',
  Rw = 'RW',
  Sa = 'SA',
  Ae = 'AE',
  Sn = 'SN',
  Rs = 'RS',
  Sc = 'SC',
  Sl = 'SL',
  Sg = 'SG',
  Sk = 'SK',
  Si = 'SI',
  So = 'SO',
  Za = 'ZA',
  Kr = 'KR',
  Es = 'ES',
  Lk = 'LK',
  Sd = 'SD',
  Sr = 'SR',
  Sz = 'SZ',
  Se = 'SE',
  Ch = 'CH',
  Sy = 'SY',
  Tw = 'TW',
  Tj = 'TJ',
  Tz = 'TZ',
  Th = 'TH',
  Tg = 'TG',
  Tt = 'TT',
  Tn = 'TN',
  Tr = 'TR',
  Tm = 'TM',
  Tv = 'TV',
  Ug = 'UG',
  Ua = 'UA',
  Uy = 'UY',
  Uz = 'UZ',
  V = 'V',
  Ve = 'VE',
  Vn = 'VN',
  Gb_164 = 'GB_164',
  Ye = 'YE',
  Zm = 'ZM',
  Zw = 'ZW'
}

export type HouseholdNode = Node & {
   __typename?: 'HouseholdNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  householdCaId: Scalars['String'],
  consent: Scalars['String'],
  residenceStatus: HouseholdResidenceStatus,
  nationality: HouseholdNationality,
  familySize: Scalars['Int'],
  address?: Maybe<Scalars['String']>,
  location: LocationNode,
  representative?: Maybe<IndividualNode>,
  registrationDataImportId: RegistrationDataImportNode,
  headOfHousehold?: Maybe<IndividualNode>,
  individuals: IndividualNodeConnection,
  paymentRecords: PaymentRecordNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
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
  last?: Maybe<Scalars['Int']>
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

export enum ImportedHouseholdNationality {
  Af = 'AF',
  Al = 'AL',
  Dz = 'DZ',
  Ad = 'AD',
  Ao = 'AO',
  Ar = 'AR',
  Am = 'AM',
  A = 'A',
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
  Bt = 'BT',
  Bo = 'BO',
  Ba = 'BA',
  Bw = 'BW',
  Br = 'BR',
  Gb = 'GB',
  Bn = 'BN',
  Bg = 'BG',
  Bf = 'BF',
  Mm = 'MM',
  Bf_28 = 'BF_28',
  Bi = 'BI',
  Cm = 'CM',
  Ca = 'CA',
  Cv = 'CV',
  Td = 'TD',
  Cl = 'CL',
  Cn = 'CN',
  Co = 'CO',
  Cg = 'CG',
  Cr = 'CR',
  Hr = 'HR',
  C = 'C',
  Cy = 'CY',
  Cz = 'CZ',
  Dk = 'DK',
  Dj = 'DJ',
  Dm = 'DM',
  Do = 'DO',
  Ec = 'EC',
  Eg = 'EG',
  Sv = 'SV',
  Gb_50 = 'GB_50',
  Er = 'ER',
  Ee = 'EE',
  Et = 'ET',
  Fj = 'FJ',
  Fi = 'FI',
  Fr = 'FR',
  Ga = 'GA',
  Gm = 'GM',
  Ge = 'GE',
  De = 'DE',
  Gh = 'GH',
  Gr = 'GR',
  Gd = 'GD',
  Gt = 'GT',
  Gq = 'GQ',
  Gy = 'GY',
  Ht = 'HT',
  Nl = 'NL',
  Hn = 'HN',
  H = 'H',
  Is = 'IS',
  Io = 'IO',
  Id = 'ID',
  Ir = 'IR',
  Iq = 'IQ',
  Ie = 'IE',
  Il = 'IL',
  It = 'IT',
  Jm = 'JM',
  Jp = 'JP',
  Jo = 'JO',
  Kz = 'KZ',
  Ke = 'KE',
  Kw = 'KW',
  La = 'LA',
  Lv = 'LV',
  Lb = 'LB',
  Lr = 'LR',
  Ly = 'LY',
  Lt = 'LT',
  Mk = 'MK',
  Mg = 'MG',
  Mw = 'MW',
  My = 'MY',
  Mv = 'MV',
  Ml = 'ML',
  Mt = 'MT',
  Mr = 'MR',
  M = 'M',
  Mx = 'MX',
  Md = 'MD',
  Mc = 'MC',
  Mn = 'MN',
  Me = 'ME',
  Ma = 'MA',
  Mz = 'MZ',
  Na = 'NA',
  Np = 'NP',
  Ni = 'NI',
  Ne = 'NE',
  Ng = 'NG',
  Kp = 'KP',
  No = 'NO',
  Om = 'OM',
  Pk = 'PK',
  Pa = 'PA',
  Pg = 'PG',
  Py = 'PY',
  Pe = 'PE',
  Ph = 'PH',
  Pl = 'PL',
  Pt = 'PT',
  Qa = 'QA',
  Ro = 'RO',
  R = 'R',
  Rw = 'RW',
  Sa = 'SA',
  Ae = 'AE',
  Sn = 'SN',
  Rs = 'RS',
  Sc = 'SC',
  Sl = 'SL',
  Sg = 'SG',
  Sk = 'SK',
  Si = 'SI',
  So = 'SO',
  Za = 'ZA',
  Kr = 'KR',
  Es = 'ES',
  Lk = 'LK',
  Sd = 'SD',
  Sr = 'SR',
  Sz = 'SZ',
  Se = 'SE',
  Ch = 'CH',
  Sy = 'SY',
  Tw = 'TW',
  Tj = 'TJ',
  Tz = 'TZ',
  Th = 'TH',
  Tg = 'TG',
  Tt = 'TT',
  Tn = 'TN',
  Tr = 'TR',
  Tm = 'TM',
  Tv = 'TV',
  Ug = 'UG',
  Ua = 'UA',
  Uy = 'UY',
  Uz = 'UZ',
  V = 'V',
  Ve = 'VE',
  Vn = 'VN',
  Gb_164 = 'GB_164',
  Ye = 'YE',
  Zm = 'ZM',
  Zw = 'ZW'
}

export type ImportedHouseholdNode = Node & {
   __typename?: 'ImportedHouseholdNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  householdCaId: Scalars['String'],
  consent: Scalars['String'],
  residenceStatus: ImportedHouseholdResidenceStatus,
  nationality: ImportedHouseholdNationality,
  familySize: Scalars['Int'],
  address: Scalars['String'],
  location: Scalars['String'],
  representative?: Maybe<ImportedIndividualNode>,
  registrationDataImportId: RegistrationDataImportDatahubNode,
  headOfHousehold?: Maybe<ImportedIndividualNode>,
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

export enum ImportedIndividualDisability {
  No = 'NO',
  Seeing = 'SEEING',
  Hearing = 'HEARING',
  Walking = 'WALKING',
  Memory = 'MEMORY',
  SelfCare = 'SELF_CARE',
  Communicating = 'COMMUNICATING'
}

export enum ImportedIndividualEstimatedDob {
  Yes = 'YES',
  No = 'NO'
}

export enum ImportedIndividualIdentificationType {
  Na = 'NA',
  BirthCertificate = 'BIRTH_CERTIFICATE',
  DrivingLicense = 'DRIVING_LICENSE',
  UnhcrIdCard = 'UNHCR_ID_CARD',
  NationalId = 'NATIONAL_ID',
  NationalPassport = 'NATIONAL_PASSPORT'
}

export enum ImportedIndividualMartialStatus {
  Single = 'SINGLE',
  Married = 'MARRIED',
  Widow = 'WIDOW',
  Divorced = 'DIVORCED',
  Separated = 'SEPARATED'
}

export enum ImportedIndividualNationality {
  Af = 'AF',
  Al = 'AL',
  Dz = 'DZ',
  Ad = 'AD',
  Ao = 'AO',
  Ar = 'AR',
  Am = 'AM',
  A = 'A',
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
  Bt = 'BT',
  Bo = 'BO',
  Ba = 'BA',
  Bw = 'BW',
  Br = 'BR',
  Gb = 'GB',
  Bn = 'BN',
  Bg = 'BG',
  Bf = 'BF',
  Mm = 'MM',
  Bf_28 = 'BF_28',
  Bi = 'BI',
  Cm = 'CM',
  Ca = 'CA',
  Cv = 'CV',
  Td = 'TD',
  Cl = 'CL',
  Cn = 'CN',
  Co = 'CO',
  Cg = 'CG',
  Cr = 'CR',
  Hr = 'HR',
  C = 'C',
  Cy = 'CY',
  Cz = 'CZ',
  Dk = 'DK',
  Dj = 'DJ',
  Dm = 'DM',
  Do = 'DO',
  Ec = 'EC',
  Eg = 'EG',
  Sv = 'SV',
  Gb_50 = 'GB_50',
  Er = 'ER',
  Ee = 'EE',
  Et = 'ET',
  Fj = 'FJ',
  Fi = 'FI',
  Fr = 'FR',
  Ga = 'GA',
  Gm = 'GM',
  Ge = 'GE',
  De = 'DE',
  Gh = 'GH',
  Gr = 'GR',
  Gd = 'GD',
  Gt = 'GT',
  Gq = 'GQ',
  Gy = 'GY',
  Ht = 'HT',
  Nl = 'NL',
  Hn = 'HN',
  H = 'H',
  Is = 'IS',
  Io = 'IO',
  Id = 'ID',
  Ir = 'IR',
  Iq = 'IQ',
  Ie = 'IE',
  Il = 'IL',
  It = 'IT',
  Jm = 'JM',
  Jp = 'JP',
  Jo = 'JO',
  Kz = 'KZ',
  Ke = 'KE',
  Kw = 'KW',
  La = 'LA',
  Lv = 'LV',
  Lb = 'LB',
  Lr = 'LR',
  Ly = 'LY',
  Lt = 'LT',
  Mk = 'MK',
  Mg = 'MG',
  Mw = 'MW',
  My = 'MY',
  Mv = 'MV',
  Ml = 'ML',
  Mt = 'MT',
  Mr = 'MR',
  M = 'M',
  Mx = 'MX',
  Md = 'MD',
  Mc = 'MC',
  Mn = 'MN',
  Me = 'ME',
  Ma = 'MA',
  Mz = 'MZ',
  Na = 'NA',
  Np = 'NP',
  Ni = 'NI',
  Ne = 'NE',
  Ng = 'NG',
  Kp = 'KP',
  No = 'NO',
  Om = 'OM',
  Pk = 'PK',
  Pa = 'PA',
  Pg = 'PG',
  Py = 'PY',
  Pe = 'PE',
  Ph = 'PH',
  Pl = 'PL',
  Pt = 'PT',
  Qa = 'QA',
  Ro = 'RO',
  R = 'R',
  Rw = 'RW',
  Sa = 'SA',
  Ae = 'AE',
  Sn = 'SN',
  Rs = 'RS',
  Sc = 'SC',
  Sl = 'SL',
  Sg = 'SG',
  Sk = 'SK',
  Si = 'SI',
  So = 'SO',
  Za = 'ZA',
  Kr = 'KR',
  Es = 'ES',
  Lk = 'LK',
  Sd = 'SD',
  Sr = 'SR',
  Sz = 'SZ',
  Se = 'SE',
  Ch = 'CH',
  Sy = 'SY',
  Tw = 'TW',
  Tj = 'TJ',
  Tz = 'TZ',
  Th = 'TH',
  Tg = 'TG',
  Tt = 'TT',
  Tn = 'TN',
  Tr = 'TR',
  Tm = 'TM',
  Tv = 'TV',
  Ug = 'UG',
  Ua = 'UA',
  Uy = 'UY',
  Uz = 'UZ',
  V = 'V',
  Ve = 'VE',
  Vn = 'VN',
  Gb_164 = 'GB_164',
  Ye = 'YE',
  Zm = 'ZM',
  Zw = 'ZW'
}

export type ImportedIndividualNode = Node & {
   __typename?: 'ImportedIndividualNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  individualCaId: Scalars['String'],
  fullName: Scalars['String'],
  firstName: Scalars['String'],
  middleName: Scalars['String'],
  lastName: Scalars['String'],
  sex: ImportedIndividualSex,
  dob: Scalars['Date'],
  estimatedDob: ImportedIndividualEstimatedDob,
  nationality: ImportedIndividualNationality,
  martialStatus: ImportedIndividualMartialStatus,
  phoneNumber: Scalars['String'],
  phoneNumberAlternative: Scalars['String'],
  identificationType: ImportedIndividualIdentificationType,
  identificationNumber: Scalars['String'],
  household: ImportedHouseholdNode,
  registrationDataImportId: RegistrationDataImportDatahubNode,
  workStatus: ImportedIndividualWorkStatus,
  disability: ImportedIndividualDisability,
  representedHouseholds: ImportedHouseholdNodeConnection,
  headingHousehold?: Maybe<ImportedHouseholdNode>,
};


export type ImportedIndividualNodeRepresentedHouseholdsArgs = {
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

export enum ImportedIndividualSex {
  Male = 'MALE',
  Female = 'FEMALE'
}

export enum ImportedIndividualWorkStatus {
  Yes = 'YES',
  No = 'NO'
}

export enum IndividualAdministrationOfRutf {
  Yes = 'YES',
  No = 'NO'
}

export enum IndividualDisability {
  No = 'NO',
  Seeing = 'SEEING',
  Hearing = 'HEARING',
  Walking = 'WALKING',
  Memory = 'MEMORY',
  SelfCare = 'SELF_CARE',
  Communicating = 'COMMUNICATING'
}

export enum IndividualEnrolledInNutritionProgramme {
  Yes = 'YES',
  No = 'NO'
}

export enum IndividualEnrolledInSchool {
  Yes = 'YES',
  No = 'NO'
}

export enum IndividualIdentificationType {
  Na = 'NA',
  BirthCertificate = 'BIRTH_CERTIFICATE',
  DrivingLicense = 'DRIVING_LICENSE',
  UnhcrIdCard = 'UNHCR_ID_CARD',
  NationalId = 'NATIONAL_ID',
  NationalPassport = 'NATIONAL_PASSPORT'
}

export enum IndividualMartialStatus {
  Single = 'SINGLE',
  Married = 'MARRIED',
  Widow = 'WIDOW',
  Divorced = 'DIVORCED',
  Separated = 'SEPARATED'
}

export enum IndividualNationality {
  Af = 'AF',
  Al = 'AL',
  Dz = 'DZ',
  Ad = 'AD',
  Ao = 'AO',
  Ar = 'AR',
  Am = 'AM',
  A = 'A',
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
  Bt = 'BT',
  Bo = 'BO',
  Ba = 'BA',
  Bw = 'BW',
  Br = 'BR',
  Gb = 'GB',
  Bn = 'BN',
  Bg = 'BG',
  Bf = 'BF',
  Mm = 'MM',
  Bf_28 = 'BF_28',
  Bi = 'BI',
  Cm = 'CM',
  Ca = 'CA',
  Cv = 'CV',
  Td = 'TD',
  Cl = 'CL',
  Cn = 'CN',
  Co = 'CO',
  Cg = 'CG',
  Cr = 'CR',
  Hr = 'HR',
  C = 'C',
  Cy = 'CY',
  Cz = 'CZ',
  Dk = 'DK',
  Dj = 'DJ',
  Dm = 'DM',
  Do = 'DO',
  Ec = 'EC',
  Eg = 'EG',
  Sv = 'SV',
  Gb_50 = 'GB_50',
  Er = 'ER',
  Ee = 'EE',
  Et = 'ET',
  Fj = 'FJ',
  Fi = 'FI',
  Fr = 'FR',
  Ga = 'GA',
  Gm = 'GM',
  Ge = 'GE',
  De = 'DE',
  Gh = 'GH',
  Gr = 'GR',
  Gd = 'GD',
  Gt = 'GT',
  Gq = 'GQ',
  Gy = 'GY',
  Ht = 'HT',
  Nl = 'NL',
  Hn = 'HN',
  H = 'H',
  Is = 'IS',
  Io = 'IO',
  Id = 'ID',
  Ir = 'IR',
  Iq = 'IQ',
  Ie = 'IE',
  Il = 'IL',
  It = 'IT',
  Jm = 'JM',
  Jp = 'JP',
  Jo = 'JO',
  Kz = 'KZ',
  Ke = 'KE',
  Kw = 'KW',
  La = 'LA',
  Lv = 'LV',
  Lb = 'LB',
  Lr = 'LR',
  Ly = 'LY',
  Lt = 'LT',
  Mk = 'MK',
  Mg = 'MG',
  Mw = 'MW',
  My = 'MY',
  Mv = 'MV',
  Ml = 'ML',
  Mt = 'MT',
  Mr = 'MR',
  M = 'M',
  Mx = 'MX',
  Md = 'MD',
  Mc = 'MC',
  Mn = 'MN',
  Me = 'ME',
  Ma = 'MA',
  Mz = 'MZ',
  Na = 'NA',
  Np = 'NP',
  Ni = 'NI',
  Ne = 'NE',
  Ng = 'NG',
  Kp = 'KP',
  No = 'NO',
  Om = 'OM',
  Pk = 'PK',
  Pa = 'PA',
  Pg = 'PG',
  Py = 'PY',
  Pe = 'PE',
  Ph = 'PH',
  Pl = 'PL',
  Pt = 'PT',
  Qa = 'QA',
  Ro = 'RO',
  R = 'R',
  Rw = 'RW',
  Sa = 'SA',
  Ae = 'AE',
  Sn = 'SN',
  Rs = 'RS',
  Sc = 'SC',
  Sl = 'SL',
  Sg = 'SG',
  Sk = 'SK',
  Si = 'SI',
  So = 'SO',
  Za = 'ZA',
  Kr = 'KR',
  Es = 'ES',
  Lk = 'LK',
  Sd = 'SD',
  Sr = 'SR',
  Sz = 'SZ',
  Se = 'SE',
  Ch = 'CH',
  Sy = 'SY',
  Tw = 'TW',
  Tj = 'TJ',
  Tz = 'TZ',
  Th = 'TH',
  Tg = 'TG',
  Tt = 'TT',
  Tn = 'TN',
  Tr = 'TR',
  Tm = 'TM',
  Tv = 'TV',
  Ug = 'UG',
  Ua = 'UA',
  Uy = 'UY',
  Uz = 'UZ',
  V = 'V',
  Ve = 'VE',
  Vn = 'VN',
  Gb_164 = 'GB_164',
  Ye = 'YE',
  Zm = 'ZM',
  Zw = 'ZW'
}

export type IndividualNode = Node & {
   __typename?: 'IndividualNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  individualCaId: Scalars['String'],
  fullName: Scalars['String'],
  firstName: Scalars['String'],
  middleName: Scalars['String'],
  lastName: Scalars['String'],
  sex: IndividualSex,
  dob?: Maybe<Scalars['Date']>,
  estimatedDob?: Maybe<Scalars['Date']>,
  nationality: IndividualNationality,
  martialStatus: IndividualMartialStatus,
  phoneNumber: Scalars['String'],
  phoneNumberAlternative: Scalars['String'],
  identificationType: IndividualIdentificationType,
  identificationNumber: Scalars['String'],
  household: HouseholdNode,
  registrationDataImportId: RegistrationDataImportNode,
  workStatus: IndividualWorkStatus,
  disability: IndividualDisability,
  seriousIllness: IndividualSeriousIllness,
  ageFirstMarried?: Maybe<Scalars['Int']>,
  enrolledInSchool: IndividualEnrolledInSchool,
  schoolAttendance: Scalars['String'],
  schoolType: Scalars['String'],
  yearsInSchool?: Maybe<Scalars['Int']>,
  minutesToSchool?: Maybe<Scalars['Int']>,
  enrolledInNutritionProgramme?: Maybe<IndividualEnrolledInNutritionProgramme>,
  administrationOfRutf?: Maybe<IndividualAdministrationOfRutf>,
  representedHouseholds: HouseholdNodeConnection,
  headingHousehold?: Maybe<HouseholdNode>,
};


export type IndividualNodeRepresentedHouseholdsArgs = {
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

export enum IndividualSeriousIllness {
  Yes = 'YES',
  No = 'NO'
}

export enum IndividualSex {
  Male = 'MALE',
  Female = 'FEMALE'
}

export enum IndividualWorkStatus {
  Yes = 'YES',
  No = 'NO'
}



export type LocationNode = Node & {
   __typename?: 'LocationNode',
  id: Scalars['ID'],
  title: Scalars['String'],
  businessArea?: Maybe<BusinessAreaNode>,
  latitude?: Maybe<Scalars['Float']>,
  longitude?: Maybe<Scalars['Float']>,
  pCode?: Maybe<Scalars['String']>,
  parent?: Maybe<LocationNode>,
  lft: Scalars['Int'],
  rght: Scalars['Int'],
  treeId: Scalars['Int'],
  level: Scalars['Int'],
  children: LocationNodeConnection,
  households: HouseholdNodeConnection,
  programs: ProgramNodeConnection,
};


export type LocationNodeChildrenArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
};


export type LocationNodeHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type LocationNodeProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  name?: Maybe<Scalars['String']>
};

export type LocationNodeConnection = {
   __typename?: 'LocationNodeConnection',
  pageInfo: PageInfo,
  edges: Array<Maybe<LocationNodeEdge>>,
  totalCount?: Maybe<Scalars['Int']>,
  edgeCount?: Maybe<Scalars['Int']>,
};

export type LocationNodeEdge = {
   __typename?: 'LocationNodeEdge',
  node?: Maybe<LocationNode>,
  cursor: Scalars['String'],
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

export type Mutations = {
   __typename?: 'Mutations',
  createProgram?: Maybe<CreateProgram>,
  updateProgram?: Maybe<UpdateProgram>,
  deleteProgram?: Maybe<DeleteProgram>,
  createCashPlan?: Maybe<CreateCashPlan>,
  updateCashPlan?: Maybe<UpdateCashPlan>,
  deleteCashPlan?: Maybe<DeleteCashPlan>,
  createHousehold?: Maybe<CreateHousehold>,
  updateHousehold?: Maybe<UpdateHousehold>,
  deleteHousehold?: Maybe<DeleteHousehold>,
  createLocation?: Maybe<CreateLocation>,
  updateLocation?: Maybe<UpdateLocation>,
  deleteLocation?: Maybe<DeleteLocation>,
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


export type MutationsCreateCashPlanArgs = {
  cashPlanData: CreateCashPlanInput
};


export type MutationsUpdateCashPlanArgs = {
  cashPlanData?: Maybe<UpdateCashPlanInput>
};


export type MutationsDeleteCashPlanArgs = {
  cashPlanId: Scalars['String']
};


export type MutationsCreateHouseholdArgs = {
  householdData?: Maybe<CreateHouseholdInput>
};


export type MutationsUpdateHouseholdArgs = {
  householdData?: Maybe<UpdateHouseholdInput>
};


export type MutationsDeleteHouseholdArgs = {
  householdId: Scalars['String']
};


export type MutationsCreateLocationArgs = {
  locationData: CreateLocationInput
};


export type MutationsUpdateLocationArgs = {
  locationData?: Maybe<UpdateLocationInput>
};


export type MutationsDeleteLocationArgs = {
  locationId: Scalars['String']
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
  locations: LocationNodeConnection,
  businessArea: BusinessAreaNode,
  budget?: Maybe<Scalars['Decimal']>,
  frequencyOfPayments: ProgramFrequencyOfPayments,
  sector: ProgramSector,
  scope: ProgramScope,
  cashPlus: Scalars['Boolean'],
  populationGoal: Scalars['Int'],
  administrativeAreasOfImplementation: Scalars['String'],
  cashPlans: CashPlanNodeConnection,
  totalEntitledQuantity?: Maybe<Scalars['Decimal']>,
  totalDeliveredQuantity?: Maybe<Scalars['Decimal']>,
  totalUndeliveredQuantity?: Maybe<Scalars['Decimal']>,
  totalNumberOfHouseholds?: Maybe<Scalars['Int']>,
  history?: Maybe<LogEntryObjectConnection>,
};


export type ProgramNodeLocationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
};


export type ProgramNodeCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
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
  location?: Maybe<LocationNode>,
  allLocations?: Maybe<LocationNodeConnection>,
  allBusinessAreas?: Maybe<BusinessAreaNodeConnection>,
  allLogEntries?: Maybe<LogEntryObjectConnection>,
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
  household?: Maybe<HouseholdNode>,
  allHouseholds?: Maybe<HouseholdNodeConnection>,
  individual?: Maybe<IndividualNode>,
  allIndividuals?: Maybe<IndividualNodeConnection>,
  me?: Maybe<UserObjectType>,
  allUsers?: Maybe<UserNodeConnection>,
  importedHousehold?: Maybe<ImportedHouseholdNode>,
  allImportedHouseholds?: Maybe<ImportedHouseholdNodeConnection>,
  registrationDataImportDatahub?: Maybe<RegistrationDataImportDatahubNode>,
  allRegistrationDataImportsDatahub?: Maybe<RegistrationDataImportDatahubNodeConnection>,
  importedIndividual?: Maybe<ImportedIndividualNode>,
  allImportedIndividuals?: Maybe<ImportedIndividualNodeConnection>,
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


export type QueryLocationArgs = {
  id: Scalars['ID']
};


export type QueryAllLocationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  title?: Maybe<Scalars['String']>
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
  nationality?: Maybe<Scalars['String']>,
  nationality_Icontains?: Maybe<Scalars['String']>,
  address?: Maybe<Scalars['String']>,
  address_Icontains?: Maybe<Scalars['String']>,
  representative_FullName?: Maybe<Scalars['String']>,
  representative_FullName_Icontains?: Maybe<Scalars['String']>,
  headOfHousehold_FullName?: Maybe<Scalars['String']>,
  headOfHousehold_FullName_Icontains?: Maybe<Scalars['String']>,
  householdCaId?: Maybe<Scalars['String']>,
  familySize_Range?: Maybe<Scalars['Int']>,
  familySize_Lte?: Maybe<Scalars['Int']>,
  familySize_Gte?: Maybe<Scalars['Int']>,
  familySize?: Maybe<Scalars['String']>,
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
  businessArea?: Maybe<Scalars['String']>,
  fullName?: Maybe<Scalars['String']>,
  fullName_Icontains?: Maybe<Scalars['String']>,
  sex?: Maybe<Array<Maybe<Scalars['ID']>>>,
  age?: Maybe<Scalars['String']>,
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
  nationality?: Maybe<Scalars['String']>,
  nationality_Icontains?: Maybe<Scalars['String']>,
  address?: Maybe<Scalars['String']>,
  address_Icontains?: Maybe<Scalars['String']>,
  representative_FullName?: Maybe<Scalars['String']>,
  representative_FullName_Icontains?: Maybe<Scalars['String']>,
  headOfHousehold_FullName?: Maybe<Scalars['String']>,
  headOfHousehold_FullName_Icontains?: Maybe<Scalars['String']>,
  householdCaId?: Maybe<Scalars['String']>,
  familySize_Range?: Maybe<Scalars['Int']>,
  familySize_Lte?: Maybe<Scalars['Int']>,
  familySize_Gte?: Maybe<Scalars['Int']>,
  familySize?: Maybe<Scalars['String']>,
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
  fullName?: Maybe<Scalars['String']>,
  fullName_Icontains?: Maybe<Scalars['String']>,
  sex?: Maybe<Array<Maybe<Scalars['ID']>>>,
  age?: Maybe<Scalars['String']>,
  orderBy?: Maybe<Scalars['String']>
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

export type TargetPopulationNode = Node & {
   __typename?: 'TargetPopulationNode',
  id: Scalars['ID'],
  name: Scalars['String'],
  createdAt: Scalars['DateTime'],
  createdBy?: Maybe<UserNode>,
  rules: Scalars['JSONString'],
  households: HouseholdNodeConnection,
  paymentRecords: PaymentRecordNodeConnection,
  cashPlans: CashPlanNodeConnection,
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

export type UpdateCashPlan = {
   __typename?: 'UpdateCashPlan',
  cashPlan?: Maybe<CashPlanNode>,
};

export type UpdateCashPlanInput = {
  id: Scalars['String'],
  programId?: Maybe<Scalars['String']>,
  name?: Maybe<Scalars['String']>,
  startDate?: Maybe<Scalars['DateTime']>,
  endDate?: Maybe<Scalars['DateTime']>,
  disbursementDate?: Maybe<Scalars['DateTime']>,
  numberOfHouseholds?: Maybe<Scalars['Int']>,
  coverageDuration?: Maybe<Scalars['Int']>,
  coverageUnits?: Maybe<Scalars['String']>,
  targetPopulationId?: Maybe<Scalars['String']>,
  cashAssistId?: Maybe<Scalars['String']>,
  distributionModality?: Maybe<Scalars['String']>,
  fsp?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>,
  currency?: Maybe<Scalars['String']>,
  totalEntitledQuantity?: Maybe<Scalars['Decimal']>,
  totalDeliveredQuantity?: Maybe<Scalars['Decimal']>,
  totalUndeliveredQuantity?: Maybe<Scalars['Decimal']>,
  dispersionDate?: Maybe<Scalars['Date']>,
};

export type UpdateHousehold = {
   __typename?: 'UpdateHousehold',
  household?: Maybe<HouseholdNode>,
};

export type UpdateHouseholdInput = {
  id: Scalars['String'],
  householdCaId?: Maybe<Scalars['String']>,
  consent?: Maybe<Scalars['String']>,
  residenceStatus?: Maybe<Scalars['String']>,
  nationality?: Maybe<Scalars['String']>,
  familySize?: Maybe<Scalars['Int']>,
  address?: Maybe<Scalars['String']>,
  locationId?: Maybe<Scalars['String']>,
  registrationDataImportId?: Maybe<Scalars['String']>,
};

export type UpdateLocation = {
   __typename?: 'UpdateLocation',
  location?: Maybe<LocationNode>,
};

export type UpdateLocationInput = {
  id: Scalars['String'],
  name?: Maybe<Scalars['String']>,
  country?: Maybe<Scalars['String']>,
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
  last?: Maybe<Scalars['Int']>
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
  last?: Maybe<Scalars['Int']>
};


export type UserObjectTypeRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


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
  headOfHouseholdFullNameIcontains?: Maybe<Scalars['String']>
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
        & Pick<HouseholdNode, 'id' | 'createdAt' | 'householdCaId' | 'residenceStatus' | 'familySize'>
        & { location: (
          { __typename?: 'LocationNode' }
          & Pick<LocationNode, 'id' | 'title'>
        ), individuals: (
          { __typename?: 'IndividualNodeConnection' }
          & Pick<IndividualNodeConnection, 'totalCount'>
        ), paymentRecords: (
          { __typename?: 'PaymentRecordNodeConnection' }
          & { edges: Array<Maybe<(
            { __typename?: 'PaymentRecordNodeEdge' }
            & { node: Maybe<(
              { __typename?: 'PaymentRecordNode' }
              & Pick<PaymentRecordNode, 'id' | 'headOfHousehold'>
              & { cashPlan: (
                { __typename?: 'CashPlanNode' }
                & Pick<CashPlanNode, 'id' | 'totalDeliveredQuantity'>
                & { program: (
                  { __typename?: 'ProgramNode' }
                  & Pick<ProgramNode, 'id' | 'name'>
                ) }
              ) }
            )> }
          )>> }
        ) }
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
  age?: Maybe<Scalars['String']>
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
      & { node: Maybe<(
        { __typename?: 'IndividualNode' }
        & Pick<IndividualNode, 'id' | 'createdAt' | 'updatedAt' | 'individualCaId' | 'fullName' | 'sex' | 'dob' | 'nationality' | 'martialStatus' | 'phoneNumber' | 'identificationType' | 'identificationNumber'>
        & { household: (
          { __typename?: 'HouseholdNode' }
          & Pick<HouseholdNode, 'id' | 'householdCaId'>
          & { location: (
            { __typename?: 'LocationNode' }
            & Pick<LocationNode, 'id' | 'title'>
          ) }
        ) }
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
          & Pick<HouseholdNode, 'id' | 'householdCaId' | 'familySize'>
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
        & Pick<RegistrationDataImportNode, 'id' | 'createdAt' | 'name' | 'status' | 'importDate' | 'dataSource' | 'numberOfHouseholds'>
        & { importedBy: (
          { __typename?: 'UserNode' }
          & Pick<UserNode, 'id' | 'firstName' | 'lastName'>
        ) }
      )> }
    )>> }
  )> }
);

export type AllUsersQueryVariables = {};


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
    & Pick<HouseholdNode, 'id' | 'createdAt' | 'familySize' | 'nationality' | 'residenceStatus'>
    & { individuals: (
      { __typename?: 'IndividualNodeConnection' }
      & Pick<IndividualNodeConnection, 'totalCount'>
      & { edges: Array<Maybe<(
        { __typename?: 'IndividualNodeEdge' }
        & { node: Maybe<(
          { __typename?: 'IndividualNode' }
          & Pick<IndividualNode, 'id' | 'individualCaId' | 'fullName' | 'sex' | 'dob' | 'nationality' | 'identificationType' | 'workStatus'>
          & { representedHouseholds: (
            { __typename?: 'HouseholdNodeConnection' }
            & { edges: Array<Maybe<(
              { __typename?: 'HouseholdNodeEdge' }
              & { node: Maybe<(
                { __typename?: 'HouseholdNode' }
                & Pick<HouseholdNode, 'id'>
                & { representative: Maybe<(
                  { __typename?: 'IndividualNode' }
                  & Pick<IndividualNode, 'fullName'>
                )> }
              )> }
            )>> }
          ) }
        )> }
      )>> }
    ), location: (
      { __typename?: 'LocationNode' }
      & Pick<LocationNode, 'id' | 'title'>
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
  )> }
);

export type IndividualQueryVariables = {
  id: Scalars['ID']
};


export type IndividualQuery = (
  { __typename?: 'Query' }
  & { individual: Maybe<(
    { __typename?: 'IndividualNode' }
    & Pick<IndividualNode, 'id' | 'createdAt' | 'individualCaId' | 'fullName' | 'firstName' | 'lastName' | 'sex' | 'dob' | 'estimatedDob' | 'nationality' | 'martialStatus' | 'phoneNumber' | 'identificationType' | 'identificationNumber'>
    & { household: (
      { __typename?: 'HouseholdNode' }
      & Pick<HouseholdNode, 'id' | 'address'>
      & { location: (
        { __typename?: 'LocationNode' }
        & Pick<LocationNode, 'id' | 'title' | 'level'>
      ) }
    ), headingHousehold: Maybe<(
      { __typename?: 'HouseholdNode' }
      & Pick<HouseholdNode, 'id'>
      & { headOfHousehold: Maybe<(
        { __typename?: 'IndividualNode' }
        & Pick<IndividualNode, 'id'>
      )> }
    )> }
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
      & Pick<HouseholdNode, 'id' | 'householdCaId' | 'familySize'>
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

export type RegistrationChoicesQueryVariables = {};


export type RegistrationChoicesQuery = (
  { __typename?: 'Query' }
  & { registrationDataStatusChoices: Maybe<Array<Maybe<(
    { __typename?: 'ChoiceObject' }
    & Pick<ChoiceObject, 'name' | 'value'>
  )>>> }
);


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
    query AllHouseholds($after: String, $before: String, $first: Int, $last: Int, $businessArea: String, $orderBy: String, $familySize: String, $headOfHouseholdFullNameIcontains: String) {
  allHouseholds(after: $after, before: $before, first: $first, last: $last, businessArea: $businessArea, familySize: $familySize, orderBy: $orderBy, headOfHousehold_FullName_Icontains: $headOfHouseholdFullNameIcontains) {
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
        createdAt
        householdCaId
        residenceStatus
        familySize
        location {
          id
          title
        }
        individuals {
          totalCount
        }
        paymentRecords {
          edges {
            node {
              id
              headOfHousehold
              cashPlan {
                id
                program {
                  id
                  name
                }
                totalDeliveredQuantity
              }
            }
          }
        }
      }
    }
  }
}
    `;
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
 *      headOfHouseholdFullNameIcontains: // value for 'headOfHouseholdFullNameIcontains'
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
    query AllIndividuals($before: String, $after: String, $first: Int, $last: Int, $fullNameContains: String, $sex: [ID], $age: String) {
  allIndividuals(before: $before, after: $after, first: $first, last: $last, fullName_Icontains: $fullNameContains, sex: $sex, age: $age) {
    totalCount
    pageInfo {
      startCursor
      endCursor
    }
    edges {
      node {
        id
        createdAt
        updatedAt
        individualCaId
        fullName
        sex
        dob
        nationality
        martialStatus
        phoneNumber
        identificationType
        identificationNumber
        household {
          id
          householdCaId
          location {
            id
            title
          }
        }
      }
    }
  }
}
    `;
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
          householdCaId
          familySize
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
        numberOfHouseholds
      }
    }
  }
}
    `;
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
export const AllUsersDocument = gql`
    query AllUsers {
  allUsers {
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
    id
    createdAt
    familySize
    nationality
    individuals {
      totalCount
      edges {
        node {
          id
          individualCaId
          fullName
          sex
          dob
          nationality
          identificationType
          workStatus
          representedHouseholds {
            edges {
              node {
                id
                representative {
                  fullName
                }
              }
            }
          }
        }
      }
    }
    location {
      id
      title
    }
    residenceStatus
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
}
    `;
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
export const IndividualDocument = gql`
    query Individual($id: ID!) {
  individual(id: $id) {
    id
    createdAt
    individualCaId
    fullName
    firstName
    lastName
    sex
    dob
    estimatedDob
    nationality
    martialStatus
    phoneNumber
    identificationType
    identificationNumber
    household {
      id
      address
      location {
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
}
    `;
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
      householdCaId
      familySize
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
  LocationNodeConnection: ResolverTypeWrapper<LocationNodeConnection>,
  PageInfo: ResolverTypeWrapper<PageInfo>,
  Boolean: ResolverTypeWrapper<Scalars['Boolean']>,
  LocationNodeEdge: ResolverTypeWrapper<LocationNodeEdge>,
  LocationNode: ResolverTypeWrapper<LocationNode>,
  BusinessAreaNode: ResolverTypeWrapper<BusinessAreaNode>,
  UserNodeConnection: ResolverTypeWrapper<UserNodeConnection>,
  UserNodeEdge: ResolverTypeWrapper<UserNodeEdge>,
  UserNode: ResolverTypeWrapper<UserNode>,
  UUID: ResolverTypeWrapper<Scalars['UUID']>,
  BusinessAreaNodeConnection: ResolverTypeWrapper<BusinessAreaNodeConnection>,
  BusinessAreaNodeEdge: ResolverTypeWrapper<BusinessAreaNodeEdge>,
  CashPlanNodeConnection: ResolverTypeWrapper<CashPlanNodeConnection>,
  CashPlanNodeEdge: ResolverTypeWrapper<CashPlanNodeEdge>,
  TargetPopulationNodeConnection: ResolverTypeWrapper<TargetPopulationNodeConnection>,
  TargetPopulationNodeEdge: ResolverTypeWrapper<TargetPopulationNodeEdge>,
  TargetPopulationNode: ResolverTypeWrapper<TargetPopulationNode>,
  JSONString: ResolverTypeWrapper<Scalars['JSONString']>,
  HouseholdNodeConnection: ResolverTypeWrapper<HouseholdNodeConnection>,
  HouseholdNodeEdge: ResolverTypeWrapper<HouseholdNodeEdge>,
  HouseholdNode: ResolverTypeWrapper<HouseholdNode>,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  HouseholdNationality: HouseholdNationality,
  IndividualNode: ResolverTypeWrapper<IndividualNode>,
  IndividualSex: IndividualSex,
  IndividualNationality: IndividualNationality,
  IndividualMartialStatus: IndividualMartialStatus,
  IndividualIdentificationType: IndividualIdentificationType,
  RegistrationDataImportNode: ResolverTypeWrapper<RegistrationDataImportNode>,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  IndividualNodeConnection: ResolverTypeWrapper<IndividualNodeConnection>,
  IndividualNodeEdge: ResolverTypeWrapper<IndividualNodeEdge>,
  IndividualWorkStatus: IndividualWorkStatus,
  IndividualDisability: IndividualDisability,
  IndividualSeriousIllness: IndividualSeriousIllness,
  IndividualEnrolledInSchool: IndividualEnrolledInSchool,
  IndividualEnrolledInNutritionProgramme: IndividualEnrolledInNutritionProgramme,
  IndividualAdministrationOfRutf: IndividualAdministrationOfRutf,
  PaymentRecordNodeConnection: ResolverTypeWrapper<PaymentRecordNodeConnection>,
  PaymentRecordNodeEdge: ResolverTypeWrapper<PaymentRecordNodeEdge>,
  RegistrationDataImportNodeConnection: ResolverTypeWrapper<RegistrationDataImportNodeConnection>,
  RegistrationDataImportNodeEdge: ResolverTypeWrapper<RegistrationDataImportNodeEdge>,
  ProgramNodeConnection: ResolverTypeWrapper<ProgramNodeConnection>,
  ProgramNodeEdge: ResolverTypeWrapper<ProgramNodeEdge>,
  Float: ResolverTypeWrapper<Scalars['Float']>,
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
  PaymentEntitlementNode: ResolverTypeWrapper<PaymentEntitlementNode>,
  PaymentEntitlementDeliveryType: PaymentEntitlementDeliveryType,
  ChoiceObject: ResolverTypeWrapper<ChoiceObject>,
  UserObjectType: ResolverTypeWrapper<UserObjectType>,
  ImportedHouseholdNode: ResolverTypeWrapper<ImportedHouseholdNode>,
  ImportedHouseholdResidenceStatus: ImportedHouseholdResidenceStatus,
  ImportedHouseholdNationality: ImportedHouseholdNationality,
  ImportedIndividualNode: ResolverTypeWrapper<ImportedIndividualNode>,
  ImportedIndividualSex: ImportedIndividualSex,
  ImportedIndividualEstimatedDob: ImportedIndividualEstimatedDob,
  ImportedIndividualNationality: ImportedIndividualNationality,
  ImportedIndividualMartialStatus: ImportedIndividualMartialStatus,
  ImportedIndividualIdentificationType: ImportedIndividualIdentificationType,
  RegistrationDataImportDatahubNode: ResolverTypeWrapper<RegistrationDataImportDatahubNode>,
  ImportedHouseholdNodeConnection: ResolverTypeWrapper<ImportedHouseholdNodeConnection>,
  ImportedHouseholdNodeEdge: ResolverTypeWrapper<ImportedHouseholdNodeEdge>,
  ImportedIndividualNodeConnection: ResolverTypeWrapper<ImportedIndividualNodeConnection>,
  ImportedIndividualNodeEdge: ResolverTypeWrapper<ImportedIndividualNodeEdge>,
  ImportedIndividualWorkStatus: ImportedIndividualWorkStatus,
  ImportedIndividualDisability: ImportedIndividualDisability,
  RegistrationDataImportDatahubNodeConnection: ResolverTypeWrapper<RegistrationDataImportDatahubNodeConnection>,
  RegistrationDataImportDatahubNodeEdge: ResolverTypeWrapper<RegistrationDataImportDatahubNodeEdge>,
  DjangoDebug: ResolverTypeWrapper<DjangoDebug>,
  DjangoDebugSQL: ResolverTypeWrapper<DjangoDebugSql>,
  Mutations: ResolverTypeWrapper<{}>,
  CreateProgramInput: CreateProgramInput,
  CreateProgram: ResolverTypeWrapper<CreateProgram>,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: ResolverTypeWrapper<UpdateProgram>,
  DeleteProgram: ResolverTypeWrapper<DeleteProgram>,
  CreateCashPlanInput: CreateCashPlanInput,
  CreateCashPlan: ResolverTypeWrapper<CreateCashPlan>,
  UpdateCashPlanInput: UpdateCashPlanInput,
  UpdateCashPlan: ResolverTypeWrapper<UpdateCashPlan>,
  DeleteCashPlan: ResolverTypeWrapper<DeleteCashPlan>,
  CreateHouseholdInput: CreateHouseholdInput,
  CreateHousehold: ResolverTypeWrapper<CreateHousehold>,
  UpdateHouseholdInput: UpdateHouseholdInput,
  UpdateHousehold: ResolverTypeWrapper<UpdateHousehold>,
  DeleteHousehold: ResolverTypeWrapper<DeleteHousehold>,
  CreateLocationInput: CreateLocationInput,
  CreateLocation: ResolverTypeWrapper<CreateLocation>,
  UpdateLocationInput: UpdateLocationInput,
  UpdateLocation: ResolverTypeWrapper<UpdateLocation>,
  DeleteLocation: ResolverTypeWrapper<DeleteLocation>,
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
  LocationNodeConnection: LocationNodeConnection,
  PageInfo: PageInfo,
  Boolean: Scalars['Boolean'],
  LocationNodeEdge: LocationNodeEdge,
  LocationNode: LocationNode,
  BusinessAreaNode: BusinessAreaNode,
  UserNodeConnection: UserNodeConnection,
  UserNodeEdge: UserNodeEdge,
  UserNode: UserNode,
  UUID: Scalars['UUID'],
  BusinessAreaNodeConnection: BusinessAreaNodeConnection,
  BusinessAreaNodeEdge: BusinessAreaNodeEdge,
  CashPlanNodeConnection: CashPlanNodeConnection,
  CashPlanNodeEdge: CashPlanNodeEdge,
  TargetPopulationNodeConnection: TargetPopulationNodeConnection,
  TargetPopulationNodeEdge: TargetPopulationNodeEdge,
  TargetPopulationNode: TargetPopulationNode,
  JSONString: Scalars['JSONString'],
  HouseholdNodeConnection: HouseholdNodeConnection,
  HouseholdNodeEdge: HouseholdNodeEdge,
  HouseholdNode: HouseholdNode,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  HouseholdNationality: HouseholdNationality,
  IndividualNode: IndividualNode,
  IndividualSex: IndividualSex,
  IndividualNationality: IndividualNationality,
  IndividualMartialStatus: IndividualMartialStatus,
  IndividualIdentificationType: IndividualIdentificationType,
  RegistrationDataImportNode: RegistrationDataImportNode,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  IndividualNodeConnection: IndividualNodeConnection,
  IndividualNodeEdge: IndividualNodeEdge,
  IndividualWorkStatus: IndividualWorkStatus,
  IndividualDisability: IndividualDisability,
  IndividualSeriousIllness: IndividualSeriousIllness,
  IndividualEnrolledInSchool: IndividualEnrolledInSchool,
  IndividualEnrolledInNutritionProgramme: IndividualEnrolledInNutritionProgramme,
  IndividualAdministrationOfRutf: IndividualAdministrationOfRutf,
  PaymentRecordNodeConnection: PaymentRecordNodeConnection,
  PaymentRecordNodeEdge: PaymentRecordNodeEdge,
  RegistrationDataImportNodeConnection: RegistrationDataImportNodeConnection,
  RegistrationDataImportNodeEdge: RegistrationDataImportNodeEdge,
  ProgramNodeConnection: ProgramNodeConnection,
  ProgramNodeEdge: ProgramNodeEdge,
  Float: Scalars['Float'],
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
  PaymentEntitlementNode: PaymentEntitlementNode,
  PaymentEntitlementDeliveryType: PaymentEntitlementDeliveryType,
  ChoiceObject: ChoiceObject,
  UserObjectType: UserObjectType,
  ImportedHouseholdNode: ImportedHouseholdNode,
  ImportedHouseholdResidenceStatus: ImportedHouseholdResidenceStatus,
  ImportedHouseholdNationality: ImportedHouseholdNationality,
  ImportedIndividualNode: ImportedIndividualNode,
  ImportedIndividualSex: ImportedIndividualSex,
  ImportedIndividualEstimatedDob: ImportedIndividualEstimatedDob,
  ImportedIndividualNationality: ImportedIndividualNationality,
  ImportedIndividualMartialStatus: ImportedIndividualMartialStatus,
  ImportedIndividualIdentificationType: ImportedIndividualIdentificationType,
  RegistrationDataImportDatahubNode: RegistrationDataImportDatahubNode,
  ImportedHouseholdNodeConnection: ImportedHouseholdNodeConnection,
  ImportedHouseholdNodeEdge: ImportedHouseholdNodeEdge,
  ImportedIndividualNodeConnection: ImportedIndividualNodeConnection,
  ImportedIndividualNodeEdge: ImportedIndividualNodeEdge,
  ImportedIndividualWorkStatus: ImportedIndividualWorkStatus,
  ImportedIndividualDisability: ImportedIndividualDisability,
  RegistrationDataImportDatahubNodeConnection: RegistrationDataImportDatahubNodeConnection,
  RegistrationDataImportDatahubNodeEdge: RegistrationDataImportDatahubNodeEdge,
  DjangoDebug: DjangoDebug,
  DjangoDebugSQL: DjangoDebugSql,
  Mutations: {},
  CreateProgramInput: CreateProgramInput,
  CreateProgram: CreateProgram,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: UpdateProgram,
  DeleteProgram: DeleteProgram,
  CreateCashPlanInput: CreateCashPlanInput,
  CreateCashPlan: CreateCashPlan,
  UpdateCashPlanInput: UpdateCashPlanInput,
  UpdateCashPlan: UpdateCashPlan,
  DeleteCashPlan: DeleteCashPlan,
  CreateHouseholdInput: CreateHouseholdInput,
  CreateHousehold: CreateHousehold,
  UpdateHouseholdInput: UpdateHouseholdInput,
  UpdateHousehold: UpdateHousehold,
  DeleteHousehold: DeleteHousehold,
  CreateLocationInput: CreateLocationInput,
  CreateLocation: CreateLocation,
  UpdateLocationInput: UpdateLocationInput,
  UpdateLocation: UpdateLocation,
  DeleteLocation: DeleteLocation,
};

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
  locations?: Resolver<ResolversTypes['LocationNodeConnection'], ParentType, ContextType, BusinessAreaNodeLocationsArgs>,
  programSet?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, BusinessAreaNodeProgramSetArgs>,
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

export type CreateCashPlanResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateCashPlan'] = ResolversParentTypes['CreateCashPlan']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export type CreateHouseholdResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateHousehold'] = ResolversParentTypes['CreateHousehold']> = {
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
};

export type CreateLocationResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateLocation'] = ResolversParentTypes['CreateLocation']> = {
  location?: Resolver<Maybe<ResolversTypes['LocationNode']>, ParentType, ContextType>,
};

export type CreateProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateProgram'] = ResolversParentTypes['CreateProgram']> = {
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
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

export type DeleteCashPlanResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteCashPlan'] = ResolversParentTypes['DeleteCashPlan']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type DeleteHouseholdResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteHousehold'] = ResolversParentTypes['DeleteHousehold']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type DeleteLocationResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteLocation'] = ResolversParentTypes['DeleteLocation']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
};

export type DeleteProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteProgram'] = ResolversParentTypes['DeleteProgram']> = {
  ok?: Resolver<Maybe<ResolversTypes['Boolean']>, ParentType, ContextType>,
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

export type HouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['HouseholdNode'] = ResolversParentTypes['HouseholdNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  householdCaId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  residenceStatus?: Resolver<ResolversTypes['HouseholdResidenceStatus'], ParentType, ContextType>,
  nationality?: Resolver<ResolversTypes['HouseholdNationality'], ParentType, ContextType>,
  familySize?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  address?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  location?: Resolver<ResolversTypes['LocationNode'], ParentType, ContextType>,
  representative?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
  registrationDataImportId?: Resolver<ResolversTypes['RegistrationDataImportNode'], ParentType, ContextType>,
  headOfHousehold?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType>,
  individuals?: Resolver<ResolversTypes['IndividualNodeConnection'], ParentType, ContextType, HouseholdNodeIndividualsArgs>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, HouseholdNodePaymentRecordsArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, HouseholdNodeTargetPopulationsArgs>,
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

export type ImportedHouseholdNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['ImportedHouseholdNode'] = ResolversParentTypes['ImportedHouseholdNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  householdCaId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  consent?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  residenceStatus?: Resolver<ResolversTypes['ImportedHouseholdResidenceStatus'], ParentType, ContextType>,
  nationality?: Resolver<ResolversTypes['ImportedHouseholdNationality'], ParentType, ContextType>,
  familySize?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  address?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  location?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  representative?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType>,
  registrationDataImportId?: Resolver<ResolversTypes['RegistrationDataImportDatahubNode'], ParentType, ContextType>,
  headOfHousehold?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType>,
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
  individualCaId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  firstName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  middleName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  lastName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  sex?: Resolver<ResolversTypes['ImportedIndividualSex'], ParentType, ContextType>,
  dob?: Resolver<ResolversTypes['Date'], ParentType, ContextType>,
  estimatedDob?: Resolver<ResolversTypes['ImportedIndividualEstimatedDob'], ParentType, ContextType>,
  nationality?: Resolver<ResolversTypes['ImportedIndividualNationality'], ParentType, ContextType>,
  martialStatus?: Resolver<ResolversTypes['ImportedIndividualMartialStatus'], ParentType, ContextType>,
  phoneNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  phoneNumberAlternative?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  identificationType?: Resolver<ResolversTypes['ImportedIndividualIdentificationType'], ParentType, ContextType>,
  identificationNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['ImportedHouseholdNode'], ParentType, ContextType>,
  registrationDataImportId?: Resolver<ResolversTypes['RegistrationDataImportDatahubNode'], ParentType, ContextType>,
  workStatus?: Resolver<ResolversTypes['ImportedIndividualWorkStatus'], ParentType, ContextType>,
  disability?: Resolver<ResolversTypes['ImportedIndividualDisability'], ParentType, ContextType>,
  representedHouseholds?: Resolver<ResolversTypes['ImportedHouseholdNodeConnection'], ParentType, ContextType, ImportedIndividualNodeRepresentedHouseholdsArgs>,
  headingHousehold?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType>,
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
  individualCaId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  fullName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  firstName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  middleName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  lastName?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  sex?: Resolver<ResolversTypes['IndividualSex'], ParentType, ContextType>,
  dob?: Resolver<Maybe<ResolversTypes['Date']>, ParentType, ContextType>,
  estimatedDob?: Resolver<Maybe<ResolversTypes['Date']>, ParentType, ContextType>,
  nationality?: Resolver<ResolversTypes['IndividualNationality'], ParentType, ContextType>,
  martialStatus?: Resolver<ResolversTypes['IndividualMartialStatus'], ParentType, ContextType>,
  phoneNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  phoneNumberAlternative?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  identificationType?: Resolver<ResolversTypes['IndividualIdentificationType'], ParentType, ContextType>,
  identificationNumber?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
  registrationDataImportId?: Resolver<ResolversTypes['RegistrationDataImportNode'], ParentType, ContextType>,
  workStatus?: Resolver<ResolversTypes['IndividualWorkStatus'], ParentType, ContextType>,
  disability?: Resolver<ResolversTypes['IndividualDisability'], ParentType, ContextType>,
  seriousIllness?: Resolver<ResolversTypes['IndividualSeriousIllness'], ParentType, ContextType>,
  ageFirstMarried?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  enrolledInSchool?: Resolver<ResolversTypes['IndividualEnrolledInSchool'], ParentType, ContextType>,
  schoolAttendance?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  schoolType?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  yearsInSchool?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  minutesToSchool?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  enrolledInNutritionProgramme?: Resolver<Maybe<ResolversTypes['IndividualEnrolledInNutritionProgramme']>, ParentType, ContextType>,
  administrationOfRutf?: Resolver<Maybe<ResolversTypes['IndividualAdministrationOfRutf']>, ParentType, ContextType>,
  representedHouseholds?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, IndividualNodeRepresentedHouseholdsArgs>,
  headingHousehold?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
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

export type LocationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['LocationNode'] = ResolversParentTypes['LocationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  title?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  businessArea?: Resolver<Maybe<ResolversTypes['BusinessAreaNode']>, ParentType, ContextType>,
  latitude?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  longitude?: Resolver<Maybe<ResolversTypes['Float']>, ParentType, ContextType>,
  pCode?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  parent?: Resolver<Maybe<ResolversTypes['LocationNode']>, ParentType, ContextType>,
  lft?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  rght?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  treeId?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  level?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  children?: Resolver<ResolversTypes['LocationNodeConnection'], ParentType, ContextType, LocationNodeChildrenArgs>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, LocationNodeHouseholdsArgs>,
  programs?: Resolver<ResolversTypes['ProgramNodeConnection'], ParentType, ContextType, LocationNodeProgramsArgs>,
};

export type LocationNodeConnectionResolvers<ContextType = any, ParentType extends ResolversParentTypes['LocationNodeConnection'] = ResolversParentTypes['LocationNodeConnection']> = {
  pageInfo?: Resolver<ResolversTypes['PageInfo'], ParentType, ContextType>,
  edges?: Resolver<Array<Maybe<ResolversTypes['LocationNodeEdge']>>, ParentType, ContextType>,
  totalCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  edgeCount?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
};

export type LocationNodeEdgeResolvers<ContextType = any, ParentType extends ResolversParentTypes['LocationNodeEdge'] = ResolversParentTypes['LocationNodeEdge']> = {
  node?: Resolver<Maybe<ResolversTypes['LocationNode']>, ParentType, ContextType>,
  cursor?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
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

export type MutationsResolvers<ContextType = any, ParentType extends ResolversParentTypes['Mutations'] = ResolversParentTypes['Mutations']> = {
  createProgram?: Resolver<Maybe<ResolversTypes['CreateProgram']>, ParentType, ContextType, RequireFields<MutationsCreateProgramArgs, 'programData'>>,
  updateProgram?: Resolver<Maybe<ResolversTypes['UpdateProgram']>, ParentType, ContextType, MutationsUpdateProgramArgs>,
  deleteProgram?: Resolver<Maybe<ResolversTypes['DeleteProgram']>, ParentType, ContextType, RequireFields<MutationsDeleteProgramArgs, 'programId'>>,
  createCashPlan?: Resolver<Maybe<ResolversTypes['CreateCashPlan']>, ParentType, ContextType, RequireFields<MutationsCreateCashPlanArgs, 'cashPlanData'>>,
  updateCashPlan?: Resolver<Maybe<ResolversTypes['UpdateCashPlan']>, ParentType, ContextType, MutationsUpdateCashPlanArgs>,
  deleteCashPlan?: Resolver<Maybe<ResolversTypes['DeleteCashPlan']>, ParentType, ContextType, RequireFields<MutationsDeleteCashPlanArgs, 'cashPlanId'>>,
  createHousehold?: Resolver<Maybe<ResolversTypes['CreateHousehold']>, ParentType, ContextType, MutationsCreateHouseholdArgs>,
  updateHousehold?: Resolver<Maybe<ResolversTypes['UpdateHousehold']>, ParentType, ContextType, MutationsUpdateHouseholdArgs>,
  deleteHousehold?: Resolver<Maybe<ResolversTypes['DeleteHousehold']>, ParentType, ContextType, RequireFields<MutationsDeleteHouseholdArgs, 'householdId'>>,
  createLocation?: Resolver<Maybe<ResolversTypes['CreateLocation']>, ParentType, ContextType, RequireFields<MutationsCreateLocationArgs, 'locationData'>>,
  updateLocation?: Resolver<Maybe<ResolversTypes['UpdateLocation']>, ParentType, ContextType, MutationsUpdateLocationArgs>,
  deleteLocation?: Resolver<Maybe<ResolversTypes['DeleteLocation']>, ParentType, ContextType, RequireFields<MutationsDeleteLocationArgs, 'locationId'>>,
};

export type NodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['Node'] = ResolversParentTypes['Node']> = {
  __resolveType: TypeResolveFn<'PaymentRecordNode' | 'CashPlanNode' | 'ProgramNode' | 'LocationNode' | 'BusinessAreaNode' | 'UserNode' | 'TargetPopulationNode' | 'HouseholdNode' | 'IndividualNode' | 'RegistrationDataImportNode' | 'ImportedHouseholdNode' | 'ImportedIndividualNode' | 'RegistrationDataImportDatahubNode', ParentType, ContextType>,
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
  locations?: Resolver<ResolversTypes['LocationNodeConnection'], ParentType, ContextType, ProgramNodeLocationsArgs>,
  businessArea?: Resolver<ResolversTypes['BusinessAreaNode'], ParentType, ContextType>,
  budget?: Resolver<Maybe<ResolversTypes['Decimal']>, ParentType, ContextType>,
  frequencyOfPayments?: Resolver<ResolversTypes['ProgramFrequencyOfPayments'], ParentType, ContextType>,
  sector?: Resolver<ResolversTypes['ProgramSector'], ParentType, ContextType>,
  scope?: Resolver<ResolversTypes['ProgramScope'], ParentType, ContextType>,
  cashPlus?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  populationGoal?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  administrativeAreasOfImplementation?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, ProgramNodeCashPlansArgs>,
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
  location?: Resolver<Maybe<ResolversTypes['LocationNode']>, ParentType, ContextType, RequireFields<QueryLocationArgs, 'id'>>,
  allLocations?: Resolver<Maybe<ResolversTypes['LocationNodeConnection']>, ParentType, ContextType, QueryAllLocationsArgs>,
  allBusinessAreas?: Resolver<Maybe<ResolversTypes['BusinessAreaNodeConnection']>, ParentType, ContextType, QueryAllBusinessAreasArgs>,
  allLogEntries?: Resolver<Maybe<ResolversTypes['LogEntryObjectConnection']>, ParentType, ContextType, RequireFields<QueryAllLogEntriesArgs, 'objectId'>>,
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
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType, RequireFields<QueryHouseholdArgs, 'id'>>,
  allHouseholds?: Resolver<Maybe<ResolversTypes['HouseholdNodeConnection']>, ParentType, ContextType, QueryAllHouseholdsArgs>,
  individual?: Resolver<Maybe<ResolversTypes['IndividualNode']>, ParentType, ContextType, RequireFields<QueryIndividualArgs, 'id'>>,
  allIndividuals?: Resolver<Maybe<ResolversTypes['IndividualNodeConnection']>, ParentType, ContextType, QueryAllIndividualsArgs>,
  me?: Resolver<Maybe<ResolversTypes['UserObjectType']>, ParentType, ContextType>,
  allUsers?: Resolver<Maybe<ResolversTypes['UserNodeConnection']>, ParentType, ContextType, QueryAllUsersArgs>,
  importedHousehold?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNode']>, ParentType, ContextType, RequireFields<QueryImportedHouseholdArgs, 'id'>>,
  allImportedHouseholds?: Resolver<Maybe<ResolversTypes['ImportedHouseholdNodeConnection']>, ParentType, ContextType, QueryAllImportedHouseholdsArgs>,
  registrationDataImportDatahub?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNode']>, ParentType, ContextType, RequireFields<QueryRegistrationDataImportDatahubArgs, 'id'>>,
  allRegistrationDataImportsDatahub?: Resolver<Maybe<ResolversTypes['RegistrationDataImportDatahubNodeConnection']>, ParentType, ContextType, QueryAllRegistrationDataImportsDatahubArgs>,
  importedIndividual?: Resolver<Maybe<ResolversTypes['ImportedIndividualNode']>, ParentType, ContextType, RequireFields<QueryImportedIndividualArgs, 'id'>>,
  allImportedIndividuals?: Resolver<Maybe<ResolversTypes['ImportedIndividualNodeConnection']>, ParentType, ContextType, QueryAllImportedIndividualsArgs>,
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

export type TargetPopulationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['TargetPopulationNode'] = ResolversParentTypes['TargetPopulationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  createdBy?: Resolver<Maybe<ResolversTypes['UserNode']>, ParentType, ContextType>,
  rules?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, TargetPopulationNodeHouseholdsArgs>,
  paymentRecords?: Resolver<ResolversTypes['PaymentRecordNodeConnection'], ParentType, ContextType, TargetPopulationNodePaymentRecordsArgs>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, TargetPopulationNodeCashPlansArgs>,
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

export type UpdateCashPlanResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateCashPlan'] = ResolversParentTypes['UpdateCashPlan']> = {
  cashPlan?: Resolver<Maybe<ResolversTypes['CashPlanNode']>, ParentType, ContextType>,
};

export type UpdateHouseholdResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateHousehold'] = ResolversParentTypes['UpdateHousehold']> = {
  household?: Resolver<Maybe<ResolversTypes['HouseholdNode']>, ParentType, ContextType>,
};

export type UpdateLocationResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateLocation'] = ResolversParentTypes['UpdateLocation']> = {
  location?: Resolver<Maybe<ResolversTypes['LocationNode']>, ParentType, ContextType>,
};

export type UpdateProgramResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateProgram'] = ResolversParentTypes['UpdateProgram']> = {
  program?: Resolver<Maybe<ResolversTypes['ProgramNode']>, ParentType, ContextType>,
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

export type Resolvers<ContextType = any> = {
  BusinessAreaNode?: BusinessAreaNodeResolvers<ContextType>,
  BusinessAreaNodeConnection?: BusinessAreaNodeConnectionResolvers<ContextType>,
  BusinessAreaNodeEdge?: BusinessAreaNodeEdgeResolvers<ContextType>,
  CashPlanNode?: CashPlanNodeResolvers<ContextType>,
  CashPlanNodeConnection?: CashPlanNodeConnectionResolvers<ContextType>,
  CashPlanNodeEdge?: CashPlanNodeEdgeResolvers<ContextType>,
  ChoiceObject?: ChoiceObjectResolvers<ContextType>,
  CreateCashPlan?: CreateCashPlanResolvers<ContextType>,
  CreateHousehold?: CreateHouseholdResolvers<ContextType>,
  CreateLocation?: CreateLocationResolvers<ContextType>,
  CreateProgram?: CreateProgramResolvers<ContextType>,
  Date?: GraphQLScalarType,
  DateTime?: GraphQLScalarType,
  Decimal?: GraphQLScalarType,
  DeleteCashPlan?: DeleteCashPlanResolvers<ContextType>,
  DeleteHousehold?: DeleteHouseholdResolvers<ContextType>,
  DeleteLocation?: DeleteLocationResolvers<ContextType>,
  DeleteProgram?: DeleteProgramResolvers<ContextType>,
  DjangoDebug?: DjangoDebugResolvers<ContextType>,
  DjangoDebugSQL?: DjangoDebugSqlResolvers<ContextType>,
  HouseholdNode?: HouseholdNodeResolvers<ContextType>,
  HouseholdNodeConnection?: HouseholdNodeConnectionResolvers<ContextType>,
  HouseholdNodeEdge?: HouseholdNodeEdgeResolvers<ContextType>,
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
  LocationNode?: LocationNodeResolvers<ContextType>,
  LocationNodeConnection?: LocationNodeConnectionResolvers<ContextType>,
  LocationNodeEdge?: LocationNodeEdgeResolvers<ContextType>,
  LogEntryObject?: LogEntryObjectResolvers<ContextType>,
  LogEntryObjectConnection?: LogEntryObjectConnectionResolvers<ContextType>,
  LogEntryObjectEdge?: LogEntryObjectEdgeResolvers<ContextType>,
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
  TargetPopulationNode?: TargetPopulationNodeResolvers<ContextType>,
  TargetPopulationNodeConnection?: TargetPopulationNodeConnectionResolvers<ContextType>,
  TargetPopulationNodeEdge?: TargetPopulationNodeEdgeResolvers<ContextType>,
  UpdateCashPlan?: UpdateCashPlanResolvers<ContextType>,
  UpdateHousehold?: UpdateHouseholdResolvers<ContextType>,
  UpdateLocation?: UpdateLocationResolvers<ContextType>,
  UpdateProgram?: UpdateProgramResolvers<ContextType>,
  UserNode?: UserNodeResolvers<ContextType>,
  UserNodeConnection?: UserNodeConnectionResolvers<ContextType>,
  UserNodeEdge?: UserNodeEdgeResolvers<ContextType>,
  UserObjectType?: UserObjectTypeResolvers<ContextType>,
  UUID?: GraphQLScalarType,
};


/**
 * @deprecated
 * Use "Resolvers" root object instead. If you wish to get "IResolvers", add "typesPrefix: I" to your config.
*/
export type IResolvers<ContextType = any> = Resolvers<ContextType>;

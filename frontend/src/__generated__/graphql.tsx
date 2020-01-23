import { GraphQLResolveInfo, GraphQLScalarType, GraphQLScalarTypeConfig } from 'graphql';
import gql from 'graphql-tag';
import * as React from 'react';
import * as ApolloReactCommon from '@apollo/react-common';
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
  UUID: any,
  JSONString: any,
  Date: any,
  Decimal: any,
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
  createdBy?: Maybe<UserObjectType>,
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
  startDate?: Maybe<Scalars['DateTime']>,
  endDate?: Maybe<Scalars['DateTime']>,
  description?: Maybe<Scalars['String']>,
  programCaId?: Maybe<Scalars['String']>,
  locationId?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['Float']>,
  frequencyOfPayments?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  scope?: Maybe<Scalars['String']>,
  cashPlus?: Maybe<Scalars['Boolean']>,
  populationGoal?: Maybe<Scalars['Int']>,
};

export type CreateRegistrationDataImport = {
   __typename?: 'CreateRegistrationDataImport',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type CreateRegistrationDataImportInput = {
  name?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>,
  importDate?: Maybe<Scalars['DateTime']>,
  importedById?: Maybe<Scalars['String']>,
  dataSource?: Maybe<Scalars['String']>,
  numberOfIndividuals?: Maybe<Scalars['Int']>,
  numberOfHouseholds?: Maybe<Scalars['Int']>,
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

export type DeleteRegistrationDataImport = {
   __typename?: 'DeleteRegistrationDataImport',
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
  familySize?: Maybe<Scalars['Int']>,
  address?: Maybe<Scalars['String']>,
  location: LocationNode,
  registrationDataImportId: RegistrationDataImportNode,
  paymentRecords: PaymentRecordNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
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


export enum LocationCountry {
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

export type LocationNode = Node & {
   __typename?: 'LocationNode',
  id: Scalars['ID'],
  name: Scalars['String'],
  country: LocationCountry,
  households: HouseholdNodeConnection,
  programs: ProgramNodeConnection,
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
  last?: Maybe<Scalars['Int']>
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
  createRegistrationDataImport?: Maybe<CreateRegistrationDataImport>,
  updateRegistrationDataImport?: Maybe<UpdateRegistrationDataImport>,
  deleteRegistrationDataImport?: Maybe<DeleteRegistrationDataImport>,
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


export type MutationsCreateRegistrationDataImportArgs = {
  registrationDataImportData: CreateRegistrationDataImportInput
};


export type MutationsUpdateRegistrationDataImportArgs = {
  registrationDataImportData?: Maybe<UpdateRegistrationDataImportInput>
};


export type MutationsDeleteRegistrationDataImportArgs = {
  registrationDataImportId: Scalars['String']
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

export enum PaymentRecordDeliveryType {
  Delivered = 'DELIVERED',
  InProgress = 'IN_PROGRESS'
}

export type PaymentRecordNode = Node & {
   __typename?: 'PaymentRecordNode',
  id: Scalars['ID'],
  createdAt: Scalars['DateTime'],
  updatedAt: Scalars['DateTime'],
  name: Scalars['String'],
  startDate: Scalars['DateTime'],
  endDate: Scalars['DateTime'],
  cashAssistId: Scalars['String'],
  deliveryType: PaymentRecordDeliveryType,
  cashPlan: CashPlanNode,
  household: HouseholdNode,
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
  startDate: Scalars['DateTime'],
  endDate: Scalars['DateTime'],
  description: Scalars['String'],
  programCaId: Scalars['String'],
  location: LocationNode,
  budget: Scalars['Float'],
  frequencyOfPayments: ProgramFrequencyOfPayments,
  sector: ProgramSector,
  scope: ProgramScope,
  cashPlus: Scalars['Boolean'],
  populationGoal: Scalars['Int'],
  cashPlans: CashPlanNodeConnection,
  totalNumberOfHouseholds?: Maybe<Scalars['Int']>,
};


export type ProgramNodeCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  program?: Maybe<Scalars['ID']>
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
  Child = 'CHILD',
  Protection = 'PROTECTION',
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
  paymentDeliveryTypeChoices?: Maybe<Array<Maybe<ChoiceObject>>>,
  location?: Maybe<LocationNode>,
  allLocations?: Maybe<LocationNodeConnection>,
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
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
  allRegistrationDataImports?: Maybe<RegistrationDataImportNodeConnection>,
  me?: Maybe<UserObjectType>,
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
  household?: Maybe<Scalars['ID']>
};


export type QueryLocationArgs = {
  id: Scalars['ID']
};


export type QueryAllLocationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  country?: Maybe<Scalars['String']>
};


export type QueryProgramArgs = {
  id: Scalars['ID']
};


export type QueryAllProgramsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type QueryCashPlanArgs = {
  id: Scalars['ID']
};


export type QueryAllCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  program?: Maybe<Scalars['ID']>
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
  last?: Maybe<Scalars['Int']>
};


export type QueryRegistrationDataImportArgs = {
  id: Scalars['ID']
};


export type QueryAllRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
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
  importedBy: UserObjectType,
  dataSource: RegistrationDataImportDataSource,
  numberOfIndividuals: Scalars['Int'],
  numberOfHouseholds: Scalars['Int'],
  households: HouseholdNodeConnection,
};


export type RegistrationDataImportNodeHouseholdsArgs = {
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
  InProgress = 'IN_PROGRESS',
  Done = 'DONE'
}

export type TargetPopulationNode = Node & {
   __typename?: 'TargetPopulationNode',
  id: Scalars['ID'],
  name: Scalars['String'],
  createdAt: Scalars['DateTime'],
  createdBy?: Maybe<UserObjectType>,
  rules: Scalars['JSONString'],
  households: HouseholdNodeConnection,
  cashPlans: CashPlanNodeConnection,
};


export type TargetPopulationNodeHouseholdsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type TargetPopulationNodeCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  program?: Maybe<Scalars['ID']>
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
  startDate?: Maybe<Scalars['DateTime']>,
  endDate?: Maybe<Scalars['DateTime']>,
  description?: Maybe<Scalars['String']>,
  programCaId?: Maybe<Scalars['String']>,
  locationId?: Maybe<Scalars['String']>,
  budget?: Maybe<Scalars['Float']>,
  frequencyOfPayments?: Maybe<Scalars['String']>,
  sector?: Maybe<Scalars['String']>,
  scope?: Maybe<Scalars['String']>,
  cashPlus?: Maybe<Scalars['Boolean']>,
  populationGoal?: Maybe<Scalars['Int']>,
};

export type UpdateRegistrationDataImport = {
   __typename?: 'UpdateRegistrationDataImport',
  registrationDataImport?: Maybe<RegistrationDataImportNode>,
};

export type UpdateRegistrationDataImportInput = {
  id: Scalars['String'],
  name?: Maybe<Scalars['String']>,
  status?: Maybe<Scalars['String']>,
  importDate?: Maybe<Scalars['DateTime']>,
  importedById?: Maybe<Scalars['String']>,
  dataSource?: Maybe<Scalars['String']>,
  numberOfIndividuals?: Maybe<Scalars['Int']>,
  numberOfHouseholds?: Maybe<Scalars['Int']>,
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
  registrationDataImports: RegistrationDataImportNodeConnection,
  cashPlans: CashPlanNodeConnection,
  targetPopulations: TargetPopulationNodeConnection,
};


export type UserObjectTypeRegistrationDataImportsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type UserObjectTypeCashPlansArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>,
  program?: Maybe<Scalars['ID']>
};


export type UserObjectTypeTargetPopulationsArgs = {
  before?: Maybe<Scalars['String']>,
  after?: Maybe<Scalars['String']>,
  first?: Maybe<Scalars['Int']>,
  last?: Maybe<Scalars['Int']>
};


export type AllCashPlansQueryVariables = {
  program: Scalars['ID'],
  after?: Maybe<Scalars['String']>,
  count?: Maybe<Scalars['Int']>
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

export type AllProgramsQueryVariables = {};


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

export type MeQueryVariables = {};


export type MeQuery = (
  { __typename?: 'Query' }
  & { me: Maybe<(
    { __typename?: 'UserObjectType' }
    & Pick<UserObjectType, 'id' | 'username' | 'email' | 'firstName' | 'lastName'>
  )> }
);

export type ProgramQueryVariables = {
  id: Scalars['ID']
};


export type ProgramQuery = (
  { __typename?: 'Query' }
  & { program: Maybe<(
    { __typename?: 'ProgramNode' }
    & Pick<ProgramNode, 'id' | 'name' | 'startDate' | 'endDate' | 'status' | 'programCaId' | 'description' | 'budget' | 'frequencyOfPayments' | 'cashPlus' | 'populationGoal' | 'scope' | 'sector' | 'totalNumberOfHouseholds'>
    & { location: (
      { __typename?: 'LocationNode' }
      & Pick<LocationNode, 'country' | 'id' | 'name'>
    ) }
  )> }
);


export const AllCashPlansDocument = gql`
    query AllCashPlans($program: ID!, $after: String, $count: Int) {
  allCashPlans(program: $program, after: $after, first: $count) {
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
 *      count: // value for 'count'
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
export const AllProgramsDocument = gql`
    query AllPrograms {
  allPrograms {
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
export const MeDocument = gql`
    query Me {
  me {
    id
    username
    email
    firstName
    lastName
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
    location {
      country
      id
      name
    }
    populationGoal
    scope
    sector
    totalNumberOfHouseholds
    location {
      name
    }
    cashPlus
    frequencyOfPayments
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
  String: ResolverTypeWrapper<Scalars['String']>,
  PaymentRecordDeliveryType: PaymentRecordDeliveryType,
  CashPlanNode: ResolverTypeWrapper<CashPlanNode>,
  ProgramNode: ResolverTypeWrapper<ProgramNode>,
  ProgramStatus: ProgramStatus,
  LocationNode: ResolverTypeWrapper<LocationNode>,
  LocationCountry: LocationCountry,
  Int: ResolverTypeWrapper<Scalars['Int']>,
  HouseholdNodeConnection: ResolverTypeWrapper<HouseholdNodeConnection>,
  PageInfo: ResolverTypeWrapper<PageInfo>,
  Boolean: ResolverTypeWrapper<Scalars['Boolean']>,
  HouseholdNodeEdge: ResolverTypeWrapper<HouseholdNodeEdge>,
  HouseholdNode: ResolverTypeWrapper<HouseholdNode>,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  HouseholdNationality: HouseholdNationality,
  RegistrationDataImportNode: ResolverTypeWrapper<RegistrationDataImportNode>,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  UserObjectType: ResolverTypeWrapper<UserObjectType>,
  UUID: ResolverTypeWrapper<Scalars['UUID']>,
  RegistrationDataImportNodeConnection: ResolverTypeWrapper<RegistrationDataImportNodeConnection>,
  RegistrationDataImportNodeEdge: ResolverTypeWrapper<RegistrationDataImportNodeEdge>,
  CashPlanNodeConnection: ResolverTypeWrapper<CashPlanNodeConnection>,
  CashPlanNodeEdge: ResolverTypeWrapper<CashPlanNodeEdge>,
  TargetPopulationNodeConnection: ResolverTypeWrapper<TargetPopulationNodeConnection>,
  TargetPopulationNodeEdge: ResolverTypeWrapper<TargetPopulationNodeEdge>,
  TargetPopulationNode: ResolverTypeWrapper<TargetPopulationNode>,
  JSONString: ResolverTypeWrapper<Scalars['JSONString']>,
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  PaymentRecordNodeConnection: ResolverTypeWrapper<PaymentRecordNodeConnection>,
  PaymentRecordNodeEdge: ResolverTypeWrapper<PaymentRecordNodeEdge>,
  ProgramNodeConnection: ResolverTypeWrapper<ProgramNodeConnection>,
  ProgramNodeEdge: ResolverTypeWrapper<ProgramNodeEdge>,
  Float: ResolverTypeWrapper<Scalars['Float']>,
  ProgramFrequencyOfPayments: ProgramFrequencyOfPayments,
  ProgramSector: ProgramSector,
  ProgramScope: ProgramScope,
  CashPlanStatus: CashPlanStatus,
  Date: ResolverTypeWrapper<Scalars['Date']>,
  ChoiceObject: ResolverTypeWrapper<ChoiceObject>,
  LocationNodeConnection: ResolverTypeWrapper<LocationNodeConnection>,
  LocationNodeEdge: ResolverTypeWrapper<LocationNodeEdge>,
  DjangoDebug: ResolverTypeWrapper<DjangoDebug>,
  DjangoDebugSQL: ResolverTypeWrapper<DjangoDebugSql>,
  Mutations: ResolverTypeWrapper<{}>,
  CreateProgramInput: CreateProgramInput,
  CreateProgram: ResolverTypeWrapper<CreateProgram>,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: ResolverTypeWrapper<UpdateProgram>,
  DeleteProgram: ResolverTypeWrapper<DeleteProgram>,
  CreateCashPlanInput: CreateCashPlanInput,
  Decimal: ResolverTypeWrapper<Scalars['Decimal']>,
  CreateCashPlan: ResolverTypeWrapper<CreateCashPlan>,
  UpdateCashPlanInput: UpdateCashPlanInput,
  UpdateCashPlan: ResolverTypeWrapper<UpdateCashPlan>,
  DeleteCashPlan: ResolverTypeWrapper<DeleteCashPlan>,
  CreateHouseholdInput: CreateHouseholdInput,
  CreateHousehold: ResolverTypeWrapper<CreateHousehold>,
  UpdateHouseholdInput: UpdateHouseholdInput,
  UpdateHousehold: ResolverTypeWrapper<UpdateHousehold>,
  DeleteHousehold: ResolverTypeWrapper<DeleteHousehold>,
  CreateRegistrationDataImportInput: CreateRegistrationDataImportInput,
  CreateRegistrationDataImport: ResolverTypeWrapper<CreateRegistrationDataImport>,
  UpdateRegistrationDataImportInput: UpdateRegistrationDataImportInput,
  UpdateRegistrationDataImport: ResolverTypeWrapper<UpdateRegistrationDataImport>,
  DeleteRegistrationDataImport: ResolverTypeWrapper<DeleteRegistrationDataImport>,
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
  String: Scalars['String'],
  PaymentRecordDeliveryType: PaymentRecordDeliveryType,
  CashPlanNode: CashPlanNode,
  ProgramNode: ProgramNode,
  ProgramStatus: ProgramStatus,
  LocationNode: LocationNode,
  LocationCountry: LocationCountry,
  Int: Scalars['Int'],
  HouseholdNodeConnection: HouseholdNodeConnection,
  PageInfo: PageInfo,
  Boolean: Scalars['Boolean'],
  HouseholdNodeEdge: HouseholdNodeEdge,
  HouseholdNode: HouseholdNode,
  HouseholdResidenceStatus: HouseholdResidenceStatus,
  HouseholdNationality: HouseholdNationality,
  RegistrationDataImportNode: RegistrationDataImportNode,
  RegistrationDataImportStatus: RegistrationDataImportStatus,
  UserObjectType: UserObjectType,
  UUID: Scalars['UUID'],
  RegistrationDataImportNodeConnection: RegistrationDataImportNodeConnection,
  RegistrationDataImportNodeEdge: RegistrationDataImportNodeEdge,
  CashPlanNodeConnection: CashPlanNodeConnection,
  CashPlanNodeEdge: CashPlanNodeEdge,
  TargetPopulationNodeConnection: TargetPopulationNodeConnection,
  TargetPopulationNodeEdge: TargetPopulationNodeEdge,
  TargetPopulationNode: TargetPopulationNode,
  JSONString: Scalars['JSONString'],
  RegistrationDataImportDataSource: RegistrationDataImportDataSource,
  PaymentRecordNodeConnection: PaymentRecordNodeConnection,
  PaymentRecordNodeEdge: PaymentRecordNodeEdge,
  ProgramNodeConnection: ProgramNodeConnection,
  ProgramNodeEdge: ProgramNodeEdge,
  Float: Scalars['Float'],
  ProgramFrequencyOfPayments: ProgramFrequencyOfPayments,
  ProgramSector: ProgramSector,
  ProgramScope: ProgramScope,
  CashPlanStatus: CashPlanStatus,
  Date: Scalars['Date'],
  ChoiceObject: ChoiceObject,
  LocationNodeConnection: LocationNodeConnection,
  LocationNodeEdge: LocationNodeEdge,
  DjangoDebug: DjangoDebug,
  DjangoDebugSQL: DjangoDebugSql,
  Mutations: {},
  CreateProgramInput: CreateProgramInput,
  CreateProgram: CreateProgram,
  UpdateProgramInput: UpdateProgramInput,
  UpdateProgram: UpdateProgram,
  DeleteProgram: DeleteProgram,
  CreateCashPlanInput: CreateCashPlanInput,
  Decimal: Scalars['Decimal'],
  CreateCashPlan: CreateCashPlan,
  UpdateCashPlanInput: UpdateCashPlanInput,
  UpdateCashPlan: UpdateCashPlan,
  DeleteCashPlan: DeleteCashPlan,
  CreateHouseholdInput: CreateHouseholdInput,
  CreateHousehold: CreateHousehold,
  UpdateHouseholdInput: UpdateHouseholdInput,
  UpdateHousehold: UpdateHousehold,
  DeleteHousehold: DeleteHousehold,
  CreateRegistrationDataImportInput: CreateRegistrationDataImportInput,
  CreateRegistrationDataImport: CreateRegistrationDataImport,
  UpdateRegistrationDataImportInput: UpdateRegistrationDataImportInput,
  UpdateRegistrationDataImport: UpdateRegistrationDataImport,
  DeleteRegistrationDataImport: DeleteRegistrationDataImport,
  CreateLocationInput: CreateLocationInput,
  CreateLocation: CreateLocation,
  UpdateLocationInput: UpdateLocationInput,
  UpdateLocation: UpdateLocation,
  DeleteLocation: DeleteLocation,
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
  createdBy?: Resolver<Maybe<ResolversTypes['UserObjectType']>, ParentType, ContextType>,
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

export type CreateRegistrationDataImportResolvers<ContextType = any, ParentType extends ResolversParentTypes['CreateRegistrationDataImport'] = ResolversParentTypes['CreateRegistrationDataImport']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
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

export type DeleteRegistrationDataImportResolvers<ContextType = any, ParentType extends ResolversParentTypes['DeleteRegistrationDataImport'] = ResolversParentTypes['DeleteRegistrationDataImport']> = {
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
  familySize?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
  address?: Resolver<Maybe<ResolversTypes['String']>, ParentType, ContextType>,
  location?: Resolver<ResolversTypes['LocationNode'], ParentType, ContextType>,
  registrationDataImportId?: Resolver<ResolversTypes['RegistrationDataImportNode'], ParentType, ContextType>,
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

export interface JsonStringScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['JSONString'], any> {
  name: 'JSONString'
}

export type LocationNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['LocationNode'] = ResolversParentTypes['LocationNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  country?: Resolver<ResolversTypes['LocationCountry'], ParentType, ContextType>,
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
  createRegistrationDataImport?: Resolver<Maybe<ResolversTypes['CreateRegistrationDataImport']>, ParentType, ContextType, RequireFields<MutationsCreateRegistrationDataImportArgs, 'registrationDataImportData'>>,
  updateRegistrationDataImport?: Resolver<Maybe<ResolversTypes['UpdateRegistrationDataImport']>, ParentType, ContextType, MutationsUpdateRegistrationDataImportArgs>,
  deleteRegistrationDataImport?: Resolver<Maybe<ResolversTypes['DeleteRegistrationDataImport']>, ParentType, ContextType, RequireFields<MutationsDeleteRegistrationDataImportArgs, 'registrationDataImportId'>>,
  createLocation?: Resolver<Maybe<ResolversTypes['CreateLocation']>, ParentType, ContextType, RequireFields<MutationsCreateLocationArgs, 'locationData'>>,
  updateLocation?: Resolver<Maybe<ResolversTypes['UpdateLocation']>, ParentType, ContextType, MutationsUpdateLocationArgs>,
  deleteLocation?: Resolver<Maybe<ResolversTypes['DeleteLocation']>, ParentType, ContextType, RequireFields<MutationsDeleteLocationArgs, 'locationId'>>,
};

export type NodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['Node'] = ResolversParentTypes['Node']> = {
  __resolveType: TypeResolveFn<'PaymentRecordNode' | 'CashPlanNode' | 'ProgramNode' | 'LocationNode' | 'HouseholdNode' | 'RegistrationDataImportNode' | 'TargetPopulationNode', ParentType, ContextType>,
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
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  startDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  endDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  cashAssistId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  deliveryType?: Resolver<ResolversTypes['PaymentRecordDeliveryType'], ParentType, ContextType>,
  cashPlan?: Resolver<ResolversTypes['CashPlanNode'], ParentType, ContextType>,
  household?: Resolver<ResolversTypes['HouseholdNode'], ParentType, ContextType>,
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
  startDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  endDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  description?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  programCaId?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  location?: Resolver<ResolversTypes['LocationNode'], ParentType, ContextType>,
  budget?: Resolver<ResolversTypes['Float'], ParentType, ContextType>,
  frequencyOfPayments?: Resolver<ResolversTypes['ProgramFrequencyOfPayments'], ParentType, ContextType>,
  sector?: Resolver<ResolversTypes['ProgramSector'], ParentType, ContextType>,
  scope?: Resolver<ResolversTypes['ProgramScope'], ParentType, ContextType>,
  cashPlus?: Resolver<ResolversTypes['Boolean'], ParentType, ContextType>,
  populationGoal?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, ProgramNodeCashPlansArgs>,
  totalNumberOfHouseholds?: Resolver<Maybe<ResolversTypes['Int']>, ParentType, ContextType>,
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
  paymentDeliveryTypeChoices?: Resolver<Maybe<Array<Maybe<ResolversTypes['ChoiceObject']>>>, ParentType, ContextType>,
  location?: Resolver<Maybe<ResolversTypes['LocationNode']>, ParentType, ContextType, RequireFields<QueryLocationArgs, 'id'>>,
  allLocations?: Resolver<Maybe<ResolversTypes['LocationNodeConnection']>, ParentType, ContextType, QueryAllLocationsArgs>,
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
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType, RequireFields<QueryRegistrationDataImportArgs, 'id'>>,
  allRegistrationDataImports?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNodeConnection']>, ParentType, ContextType, QueryAllRegistrationDataImportsArgs>,
  me?: Resolver<Maybe<ResolversTypes['UserObjectType']>, ParentType, ContextType>,
  _debug?: Resolver<Maybe<ResolversTypes['DjangoDebug']>, ParentType, ContextType>,
};

export type RegistrationDataImportNodeResolvers<ContextType = any, ParentType extends ResolversParentTypes['RegistrationDataImportNode'] = ResolversParentTypes['RegistrationDataImportNode']> = {
  id?: Resolver<ResolversTypes['ID'], ParentType, ContextType>,
  createdAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  updatedAt?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  name?: Resolver<ResolversTypes['String'], ParentType, ContextType>,
  status?: Resolver<ResolversTypes['RegistrationDataImportStatus'], ParentType, ContextType>,
  importDate?: Resolver<ResolversTypes['DateTime'], ParentType, ContextType>,
  importedBy?: Resolver<ResolversTypes['UserObjectType'], ParentType, ContextType>,
  dataSource?: Resolver<ResolversTypes['RegistrationDataImportDataSource'], ParentType, ContextType>,
  numberOfIndividuals?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  numberOfHouseholds?: Resolver<ResolversTypes['Int'], ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, RegistrationDataImportNodeHouseholdsArgs>,
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
  createdBy?: Resolver<Maybe<ResolversTypes['UserObjectType']>, ParentType, ContextType>,
  rules?: Resolver<ResolversTypes['JSONString'], ParentType, ContextType>,
  households?: Resolver<ResolversTypes['HouseholdNodeConnection'], ParentType, ContextType, TargetPopulationNodeHouseholdsArgs>,
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

export type UpdateRegistrationDataImportResolvers<ContextType = any, ParentType extends ResolversParentTypes['UpdateRegistrationDataImport'] = ResolversParentTypes['UpdateRegistrationDataImport']> = {
  registrationDataImport?: Resolver<Maybe<ResolversTypes['RegistrationDataImportNode']>, ParentType, ContextType>,
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
  registrationDataImports?: Resolver<ResolversTypes['RegistrationDataImportNodeConnection'], ParentType, ContextType, UserObjectTypeRegistrationDataImportsArgs>,
  cashPlans?: Resolver<ResolversTypes['CashPlanNodeConnection'], ParentType, ContextType, UserObjectTypeCashPlansArgs>,
  targetPopulations?: Resolver<ResolversTypes['TargetPopulationNodeConnection'], ParentType, ContextType, UserObjectTypeTargetPopulationsArgs>,
};

export interface UuidScalarConfig extends GraphQLScalarTypeConfig<ResolversTypes['UUID'], any> {
  name: 'UUID'
}

export type Resolvers<ContextType = any> = {
  CashPlanNode?: CashPlanNodeResolvers<ContextType>,
  CashPlanNodeConnection?: CashPlanNodeConnectionResolvers<ContextType>,
  CashPlanNodeEdge?: CashPlanNodeEdgeResolvers<ContextType>,
  ChoiceObject?: ChoiceObjectResolvers<ContextType>,
  CreateCashPlan?: CreateCashPlanResolvers<ContextType>,
  CreateHousehold?: CreateHouseholdResolvers<ContextType>,
  CreateLocation?: CreateLocationResolvers<ContextType>,
  CreateProgram?: CreateProgramResolvers<ContextType>,
  CreateRegistrationDataImport?: CreateRegistrationDataImportResolvers<ContextType>,
  Date?: GraphQLScalarType,
  DateTime?: GraphQLScalarType,
  Decimal?: GraphQLScalarType,
  DeleteCashPlan?: DeleteCashPlanResolvers<ContextType>,
  DeleteHousehold?: DeleteHouseholdResolvers<ContextType>,
  DeleteLocation?: DeleteLocationResolvers<ContextType>,
  DeleteProgram?: DeleteProgramResolvers<ContextType>,
  DeleteRegistrationDataImport?: DeleteRegistrationDataImportResolvers<ContextType>,
  DjangoDebug?: DjangoDebugResolvers<ContextType>,
  DjangoDebugSQL?: DjangoDebugSqlResolvers<ContextType>,
  HouseholdNode?: HouseholdNodeResolvers<ContextType>,
  HouseholdNodeConnection?: HouseholdNodeConnectionResolvers<ContextType>,
  HouseholdNodeEdge?: HouseholdNodeEdgeResolvers<ContextType>,
  JSONString?: GraphQLScalarType,
  LocationNode?: LocationNodeResolvers<ContextType>,
  LocationNodeConnection?: LocationNodeConnectionResolvers<ContextType>,
  LocationNodeEdge?: LocationNodeEdgeResolvers<ContextType>,
  Mutations?: MutationsResolvers<ContextType>,
  Node?: NodeResolvers,
  PageInfo?: PageInfoResolvers<ContextType>,
  PaymentRecordNode?: PaymentRecordNodeResolvers<ContextType>,
  PaymentRecordNodeConnection?: PaymentRecordNodeConnectionResolvers<ContextType>,
  PaymentRecordNodeEdge?: PaymentRecordNodeEdgeResolvers<ContextType>,
  ProgramNode?: ProgramNodeResolvers<ContextType>,
  ProgramNodeConnection?: ProgramNodeConnectionResolvers<ContextType>,
  ProgramNodeEdge?: ProgramNodeEdgeResolvers<ContextType>,
  Query?: QueryResolvers<ContextType>,
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
  UpdateRegistrationDataImport?: UpdateRegistrationDataImportResolvers<ContextType>,
  UserObjectType?: UserObjectTypeResolvers<ContextType>,
  UUID?: GraphQLScalarType,
};


/**
 * @deprecated
 * Use "Resolvers" root object instead. If you wish to get "IResolvers", add "typesPrefix: I" to your config.
*/
export type IResolvers<ContextType = any> = Resolvers<ContextType>;

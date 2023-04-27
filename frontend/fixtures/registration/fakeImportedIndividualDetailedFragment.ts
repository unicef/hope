import { ImportedIndividualDetailedFragment } from '../../src/__generated__/graphql';

export const fakeImportedIndividualDetailedFragment = {
  id:
    'SW1wb3J0ZWRJbmRpdmlkdWFsTm9kZTphODQ0OTY3OS0wNzcxLTQwODAtYjlhMy05ZTUxNDVjNGRiZmE=',
  age: 80,
  fullName: 'Alicja Kowalska',
  birthDate: '1941-08-26',
  sex: 'FEMALE',
  role: 'ALTERNATE',
  relationship: 'NON_BENEFICIARY',
  deduplicationBatchStatus: 'UNIQUE_IN_BATCH',
  deduplicationGoldenRecordStatus: 'UNIQUE',
  deduplicationGoldenRecordResults: [],
  deduplicationBatchResults: [],
  registrationDataImport: {
    id:
      'UmVnaXN0cmF0aW9uRGF0YUltcG9ydERhdGFodWJOb2RlOmE1YzAyNWU0LTAwMTAtNDA0Yy04YTIyLTUxNWUwNjA5ZDQ2OQ==',
    hctId: '8cc865bb-c993-489d-a6b5-5ceb21c6a0c3',
    __typename: 'RegistrationDataImportDatahubNode',
    name: 'romaniaks',
  },
  __typename: 'ImportedIndividualNode',
  photo: '',
  givenName: 'Alicja',
  familyName: 'Kowalska',
  middleName: '',
  estimatedBirthDate: false,
  maritalStatus: 'MARRIED',
  workStatus: 'NOT_PROVIDED',
  pregnant: true,
  flexFields: {
    muac_i_f: 12,
    school_enrolled_i_f: '0',
    school_enrolled_before_i_f: '1',
  },
  observedDisability: [],
  seeingDisability: '',
  hearingDisability: '',
  physicalDisability: '',
  memoryDisability: '',
  selfcareDisability: '',
  commsDisability: '',
  disability: 'NOT_DISABLED',
  documents: {
    edges: [
      {
        node: {
          id:
            'RG9jdW1lbnROb2RlOjBlYjYwZmY5LWRhMDYtNGYwMC1iMzQwLTFhOTU5Y2NjMjQyMw==',
          country: 'Poland',
          documentNumber: 'WSH221365',
          photo: null,
          type: {
            label: 'National ID',
            key: 'NATIONAL_ID',
            __typename: 'ImportedDocumentTypeNode',
          },
          __typename: 'ImportedDocumentNode',
        },
        __typename: 'ImportedDocumentNodeEdge',
      },
    ],
    __typename: 'ImportedDocumentNodeConnection',
  },
  identities: {
    edges: [],
    __typename: 'ImportedIndividualIdentityNodeConnection',
  },
  household: null,
  phoneNo: '+48503123555',
  phoneNoAlternative: '',
} as ImportedIndividualDetailedFragment;

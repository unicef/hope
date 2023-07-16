import { AllIndividualsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllIndividuals = [
  {
    request: {
      query: AllIndividualsDocument,
      variables: {
        age: '{"min":"","max":""}',
        businessArea: 'afghanistan',
        sex: [''],
        search: '',
        admin2: [''],
        flags: [],
        status: '',
        lastRegistrationDate: '{}',
        first: 10,
        orderBy: 'unicef_id',
      },
    },
    result: {
      data: {
        allIndividuals: {
          totalCount: 138,
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjk=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6Y2MwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAx',
                unicefId: 'IND-22-0000.0007',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Jan Kowalski',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTphYTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDE=',
                  unicefId: 'HH-22-0000.0003',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: null,
                age: 29,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6Y2MwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAy',
                unicefId: 'IND-22-0000.0008',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Adam Nowak',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTphYTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDI=',
                  unicefId: 'HH-22-0000.0004',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: null,
                age: 29,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZWRkNzRmNjQtZmQ1NS00MGNmLWE0OTMtZjU3ZDJjMjY5OWNi',
                unicefId: 'IND-23-0000.0009',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Wendy Kelly Byrd',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'HEAD',
                age: 66,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6OTgxZDM4NDItZjA5YS00OWQ3LTk3ZWUtMGFmYTM3NmFhOTFh',
                unicefId: 'IND-23-0000.0010',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Cory Anthony Hamilton',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'FREE_UNION',
                age: 21,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6NGYyZDkwZDItYTg4OC00MDAwLTllOWMtNWJiYWU2Yjg3YjZh',
                unicefId: 'IND-23-0000.0011',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Edward Ashley Costa',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'NEPHEW_NIECE',
                age: 54,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjU=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZjliYTFmNjItMjlmMC00ZjBmLThiMTAtODIyZDJhZGE2MGJm',
                unicefId: 'IND-23-0000.0012',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Phillip Patrick Gomez',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'MOTHERINLAW_FATHERINLAW',
                age: 86,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjY=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6NmJhMWQyMWYtNzU5Ni00MzI3LWJhMmYtNmIxZTg5NTNiZDgz',
                unicefId: 'IND-23-0000.0013',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Kenneth Jacob Gibson',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'OTHER',
                age: 59,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjc=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6NjI2N2NjYTQtMTA1OS00NWNjLWI5NjItMDk1Y2VkNGY0MjRk',
                unicefId: 'IND-23-0000.0014',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Valerie David Williams',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'WIFE_HUSBAND',
                age: 39,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjg=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZGI3ZjBkYjMtM2U1Ni00ZWMxLTllNjktZWYzNjQ3NjdhYTQx',
                unicefId: 'IND-23-0000.0015',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Logan Sarah Morrison',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'GRANDDAUGHER_GRANDSON',
                age: 35,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjk=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6Nzc3MDUwYTItNGI1OS00ZTlkLWE4YTItZGY3NzA3MTNjMWFm',
                unicefId: 'IND-23-0000.0016',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-13T04:00:35.700739+00:00',
                fullName: 'Jake Levi Cox',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo3MGI1MGZiOC01YmFhLTQ3MmYtYWEwMS0yMzFjNmUxN2FiM2M=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'BROTHER_SISTER',
                age: 60,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
          ],
          __typename: 'IndividualNodeConnection',
        },
      },
    },
  },
];

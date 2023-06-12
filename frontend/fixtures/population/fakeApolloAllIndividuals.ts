import { AllIndividualsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllIndividuals = [
  {
    request: {
      query: AllIndividualsDocument,
      variables: {
        businessArea: 'afghanistan',
        sex: [null],
        first: 10,
        orderBy: '-unicef_id',
      },
    },
    result: {
      data: {
        allIndividuals: {
          totalCount: 54,
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
                  'SW5kaXZpZHVhbE5vZGU6ZTRmZGVlNjUtMDIzYy00NTA4LTg5NGYtNGMwODM4OWY1MTM2',
                unicefId: 'IND-23-0000.0009',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Susan Dean Dixon',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'HEAD',
                age: 28,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZjI1YzkyYzEtY2M5OC00Nzk4LTlkYzEtNzg5OTRkY2Y3NmY1',
                unicefId: 'IND-23-0000.0010',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Ricky Juan George',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'FREE_UNION',
                age: 57,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6NTNiNzZkNGYtN2ZjMi00MzhmLTk1NTAtZGIwNGY2YjNlMDI3',
                unicefId: 'IND-23-0000.0011',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Tanya Devin Mccann',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'AUNT_UNCLE',
                age: 50,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZjhmNWQ5OWQtZGUwNy00M2UwLTk4Y2UtMjMwMTk2NDUxYWQ4',
                unicefId: 'IND-23-0000.0012',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Lisa Jeffrey King',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'MOTHERINLAW_FATHERINLAW',
                age: 24,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6OWFhODUwZTQtYTNkOC00NzY2LWFiNmItNjNiYWM3ODYyYWQ5',
                unicefId: 'IND-23-0000.0013',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Gregory Jennifer Gray',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'AUNT_UNCLE',
                age: 42,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjU=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6OGY4MzBkM2ItMjdjZC00Njg0LWEyNTEtNDA5NTMyNDVkMWNj',
                unicefId: 'IND-23-0000.0014',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Shane Ashley Guerra',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'SISTERINLAW_BROTHERINLAW',
                age: 41,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjY=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6NjBjNjEyZmQtNGQ2My00M2JlLWE5NDMtNjJmYmRiM2Y0ZmM3',
                unicefId: 'IND-23-0000.0015',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Seth Elizabeth Vega',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpiMWNmN2RjMC00OTY4LTRhZTUtOTUzNC05NDAxNDhhY2NlMGE=',
                  unicefId: 'HH-23-0000.0005',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'NON_BENEFICIARY',
                age: 86,
                sex: 'MALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjc=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ODgzZGJiZWEtMzczNy00Yjg2LWI3MzAtMWQ3NTczZjBjODkz',
                unicefId: 'IND-23-0000.0016',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Tyrone Richard Hunter',
                household: null,
                relationship: 'NON_BENEFICIARY',
                age: 74,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjg=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6NmJhMjE3MjctYjMzMi00MTY5LTk1YjMtNTJkNjZkNDUyNWU1',
                unicefId: 'IND-23-0000.0017',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Paula Steven Oneill',
                household: null,
                relationship: 'NON_BENEFICIARY',
                age: 43,
                sex: 'FEMALE',
                __typename: 'IndividualNode',
              },
              __typename: 'IndividualNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjk=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZDJlOGQ0NzAtODYyNy00MWIyLWFjY2QtZWVmMjFkZmI3MDQ5',
                unicefId: 'IND-23-0000.0018',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: '2023-06-10T00:00:42.759664+00:00',
                fullName: 'Monica John Miranda',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTpjNTY0YzFjZi03Njg2LTRjMGUtOTExYy0xZDIyZjU5NTM4Zjk=',
                  unicefId: 'HH-23-0000.0006',
                  admin2: null,
                  __typename: 'HouseholdNode',
                },
                relationship: 'HEAD',
                age: 88,
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

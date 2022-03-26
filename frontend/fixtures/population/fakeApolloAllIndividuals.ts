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
          totalCount: 6,
          pageInfo: {
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjU=',
            __typename: 'PageInfo',
          },
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjU=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6ZmU5MTQzZDUtYzJjMC00ODQ2LTlmZWMtMDU0Y2I4N2Q5MDc0',
                unicefId: 'IND-42-0000.0001',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'UNIQUE',
                sanctionListLastCheck: null,
                fullName: 'Alicja Kowalska',
                household: null,
                relationship: 'NON_BENEFICIARY',
                age: 80,
                sex: 'FEMALE',
                lastRegistrationDate: '1942-12-12',
                documents: {
                  edges: [
                    {
                      node: {
                        id:
                          'RG9jdW1lbnROb2RlOjAxMDk5MGJhLTEzZmQtNDUwMC04ODJlLTczZTU5MjZhMmFkYw==',
                        country: 'Poland',
                        documentNumber: 'BSH221315',
                        photo: null,
                        type: {
                          country: 'Poland',
                          label: 'National ID',
                          type: 'NATIONAL_ID',
                          countryIso3: 'POL',
                          __typename: 'DocumentTypeNode',
                        },
                        __typename: 'DocumentNode',
                      },
                      __typename: 'DocumentNodeEdge',
                    },
                  ],
                  __typename: 'DocumentNodeConnection',
                },
                identities: {
                  edges: [],
                  __typename: 'IndividualIdentityNodeConnection',
                },
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

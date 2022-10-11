import { AllImportedHouseholdsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllImportedHouseholds = [
  {
    request: {
      query: AllImportedHouseholdsDocument,
      variables: {
        businessArea: 'afghanistan',
        first: 10,
        orderBy: null,
        rdiId:
          'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl',
      },
    },
    result: {
      data: {
        allImportedHouseholds: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjk=',
            __typename: 'PageInfo',
          },
          totalCount: 159,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'SW1wb3J0ZWRIb3VzZWhvbGROb2RlOjNlYjE5Y2RiLTBjZTYtNDgwZS1iZTI5LTczYjY0ZWI1ZjI3Mg==',
                importId: null,
                headOfHousehold: {
                  id:
                    'SW1wb3J0ZWRJbmRpdmlkdWFsTm9kZTo0NTM0MzY3MS1hOTFiLTQyYTUtOTNmZC00MmUwMGQxZmE2NDg=',
                  fullName: 'Noel Wyatt',
                  __typename: 'ImportedIndividualNode',
                },
                size: 2,
                admin1: '',
                admin1Title: '',
                admin2: '',
                admin2Title: '',
                flexFields: { RCSI_h_f: 14 },
                deviceid: '',
                start: null,
                koboAssetId: '',
                rowId: null,
                firstRegistrationDate: '2021-01-11T00:00:00',
                lastRegistrationDate: '2021-01-11T00:00:00',
                hasDuplicates: false,
                fchildHoh: false,
                childHoh: false,
                collectIndividualData: "A_1",
                __typename: 'ImportedHouseholdNode',
              },
              __typename: 'ImportedHouseholdNodeEdge',
            },
          ],
          __typename: 'ImportedHouseholdNodeConnection',
        },
      },
    },
  },
];

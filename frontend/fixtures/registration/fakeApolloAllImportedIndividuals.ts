import { AllImportedIndividualsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllImportedIndividuals = [
  {
    request: {
      query: AllImportedIndividualsDocument,
      variables: {
        businessArea: 'afghanistan',
        duplicatesOnly: false,
        first: 10,
        orderBy: null,
        rdiId:
          'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YzY1NzRkODQtMzEzYS00MTNlLTgzMDUtMDY5ZmU4NWMyOGRl',
      },
    },
    result: {
      data: {
        allImportedIndividuals: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjk=',
            __typename: 'PageInfo',
          },
          totalCount: 477,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjk=',
              node: {
                id:
                  'SW1wb3J0ZWRJbmRpdmlkdWFsTm9kZTozYjcwYzY4MC0xZWI2LTQ0ODAtOWExNS0yMDMwNDFhZTI4NzY=',
                age: 30,
                importId: null,
                fullName: 'Selena Hart',
                birthDate: '1991-03-31',
                sex: 'MALE',
                role: 'NO_ROLE',
                relationship: 'NEPHEW_NIECE',
                deduplicationBatchStatus: 'UNIQUE_IN_BATCH',
                deduplicationGoldenRecordStatus: 'UNIQUE',
                deduplicationGoldenRecordResults: [],
                deduplicationBatchResults: [],
                registrationDataImport: {
                  id:
                    'UmVnaXN0cmF0aW9uRGF0YUltcG9ydERhdGFodWJOb2RlOmQxZTFjYWQyLWIwNGYtNDllMy04NzBiLTcwNDViM2I4ZjA4OQ==',
                  hctId: 'c6574d84-313a-413e-8305-069fe85c28de',
                  __typename: 'RegistrationDataImportDatahubNode',
                },
                __typename: 'ImportedIndividualNode',
              },
              __typename: 'ImportedIndividualNodeEdge',
            },
          ],
          __typename: 'ImportedIndividualNodeConnection',
        },
      },
    },
  },
];

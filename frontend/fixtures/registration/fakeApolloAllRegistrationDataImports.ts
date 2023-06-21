import { AllRegistrationDataImportsDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllRegistrationDataImports = [
  {
    request: {
      query: AllRegistrationDataImportsDocument,
      variables: {
        first: 10,
        importDate: null,
        orderBy: '-import_date',
        businessArea: 'afghanistan',
      },
    },
    result: {
      data: {
        allRegistrationDataImports: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjk=',
            __typename: 'PageInfo',
          },
          totalCount: 87,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6OWJlMjUwNGMtZGQ3YS00ZDZkLWE4OGEtOTU5YWZkZGY3MTgy',
                createdAt: '2022-01-19T09:53:19.418282',
                name: 'Adam Row ID Test 2',
                status: 'MERGED',
                importDate: '2022-01-19T09:53:19.418319',
                importedBy: {
                  id:
                    'VXNlck5vZGU6OGYyMDVhZWUtODVjOS00YmQwLTgwMzItYjEzOTcxNjUwMjVj',
                  firstName: 'Adam',
                  lastName: 'Fifield',
                  email: 'afifield@unicef.org',
                  __typename: 'UserNode',
                },
                dataSource: 'XLS',
                numberOfHouseholds: 3,
                numberOfIndividuals: 6,
                programId: "939ff91b-7f89-4e3c-9519-26ed62f51718",
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
          ],
          __typename: 'RegistrationDataImportNodeConnection',
        },
      },
    },
  },
];

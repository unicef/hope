import { AllRegistrationDataImportsDocument } from '../../src/__generated__/graphql';
import { fakeProgram } from '../programs/fakeProgram';

export const fakeApolloAllRegistrationDataImports = [
  {
    request: {
      query: AllRegistrationDataImportsDocument,
      variables: {
        search: '',
        businessArea: 'afghanistan',
        program:
          'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
        importDateRange: '{"min":null,"max":null}',
        size: '{"min":"","max":""}',
        first: 10,
        orderBy: '-import_date',
      },
    },
    result: {
      data: {
        allRegistrationDataImports: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            __typename: 'PageInfo',
          },
          totalCount: 1,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6NGQxMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAw',
                createdAt: '2023-09-29T10:52:29.562586+00:00',
                name: 'Test Import',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-29T10:52:29.562609+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6NTE1MTQ4MzMtM2U1Yy00NGRiLTljN2UtNWYxNzdmNDkxYmZk',
                  firstName: 'Tiffany',
                  lastName: 'Glenn',
                  email: 'tiffany.glenn_1695984749500934169@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'API',
                numberOfHouseholds: 1,
                numberOfIndividuals: 3,
                program: {
                  id:
                    'UHJvZ3JhbU5vZGU6MDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtZmFjZWIwMGMwMDAw',
                  name: 'Test Program',
                  startDate: '2023-09-29',
                  endDate: '2024-09-28',
                  status: 'ACTIVE',
                  __typename: 'ProgramNode',
                },
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
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

import { AllSteficonRulesDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllSteficonRules = [
  {
    request: {
      query: AllSteficonRulesDocument,
      variables: {
        enabled: true,
        deprecated: false,
        type: 'PAYMENT_PLAN',
        first: 5,
      },
    },
    result: {
      data: {
        allStepiconRules: {
          pageInfo: {
            hasNextPage: true,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          totalCount: 2,
          edges: [
            {
              node: {
                id: "U3RlZmljb25SdWxlTm9kZTo1",
                name: "Test Formula for Payment Plan 033"
              },
            },
            {
              node: {
                id: "U3RlZmljb25SdWxlTm9kZTo3",
                name: "Test Formula for Payment Plan 044"
              },
            },
          ],
        },
      },
    },
  }
];

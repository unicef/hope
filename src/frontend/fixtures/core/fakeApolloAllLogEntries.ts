import { AllLogEntriesDocument } from '../../src/__generated__/graphql';

export const fakeApolloAllLogEntries = [
  {
    request: {
      query: AllLogEntriesDocument,
      variables: {},
    },
    result: {
      data: {
        allLogEntries: {
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: 'YXJyYXljb25uZWN0aW9uOjA=',
            endCursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
            __typename: 'PageInfo',
          },
          totalCount: 5,
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id: 'TG9nRW50cnlOb2RlOjU=',
                action: 'UPDATE',
                changes: { status: { to: 'MERGED', from: 'MERGING' } },
                objectRepr: 'roamaniaks',
                objectId: '30bb58c2-11ad-4208-8d5e-d435f0796e76',
                timestamp: '2022-02-22T15:12:47.536737',
                contentType: {
                  id: '96',
                  appLabel: 'registration_data',
                  model: 'registrationdataimport',
                  name: 'Registration data import',
                  __typename: 'ContentTypeObjectType',
                },
                user: null,
                __typename: 'LogEntryNode',
              },
              __typename: 'LogEntryNodeEdge',
            },
          ],
          __typename: 'LogEntryNodeConnection',
        },
        logEntryActionChoices: [
          { name: 'Create', value: 'CREATE', __typename: 'ChoiceObject' },
          { name: 'Update', value: 'UPDATE', __typename: 'ChoiceObject' },
          { name: 'Delete', value: 'DELETE', __typename: 'ChoiceObject' },
          {
            name: 'Soft Delete',
            value: 'SOFT_DELETE',
            __typename: 'ChoiceObject',
          },
        ],
      },
    },
  },
];

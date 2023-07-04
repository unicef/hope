import { AllIndividualsForPopulationTableDocument } from '../../src/__generated__/graphql';
import { fakeProgram } from '../programs/fakeProgram';

export const fakeApolloAllIndividualsForPopulationTable = [
  {
    request: {
      query: AllIndividualsForPopulationTableDocument,
      variables: {
        age: '{"min":"","max":""}',
        businessArea: 'afghanistan',
        sex: [''],
        search: '',
        admin2: [''],
        flags: [],
        status: '',
        lastRegistrationDate: '{"min":"","max":""}',
        first: 10,
        orderBy: 'unicef_id',
        programs: [fakeProgram.id],
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
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
                  'SW5kaXZpZHVhbE5vZGU6Y2VkZDRiNDktNTRlMC00NDA4LThmZDItMTAzMGYwNWE3YTZh',
                unicefId: 'IND-74-0000.0006',
                sanctionListPossibleMatch: false,
                sanctionListConfirmedMatch: false,
                deduplicationGoldenRecordStatus: 'DUPLICATE',
                sanctionListLastCheck: '2022-06-06T06:11:41.336055',
                fullName: 'Jan Romaniak',
                household: {
                  id:
                    'SG91c2Vob2xkTm9kZTo5NjBmN2VlZS1kNDVhLTQ3OGEtYjRiNC04MmQwZThlODBhZGQ=',
                  unicefId: 'HH-20-0000.0002',
                  admin2: {
                    id:
                      'QXJlYU5vZGU6NWYwNmViMzEtM2I1ZC00YmQ1LWIyOTMtYTg5YmE3OTgxYmZj',
                    name: 'Abband',
                    __typename: 'AreaNode',
                  },
                  __typename: 'HouseholdNode',
                },
                relationship: 'HEAD',
                age: 30,
                sex: 'MALE',
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

import { AllRegistrationDataImportsDocument } from '../../src/__generated__/graphql';
import { fakeProgram } from '../programs/fakeProgram';

export const fakeApolloAllRegistrationDataImports = [
  {
    request: {
      query: AllRegistrationDataImportsDocument,
      variables: {
        search: '',
        businessArea: 'afghanistan',
<<<<<<< HEAD
        program: fakeProgram.id,
        importDateRange: '{}',
        size: '{}',
=======
        importDateRange: '{"min":null,"max":null}',
        size: '{"min":"","max":""}',
>>>>>>> develop
        first: 10,
        orderBy: '-import_date',
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
<<<<<<< HEAD
          totalCount: 27,
=======
          totalCount: 13,
>>>>>>> develop
          edges: [
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjA=',
              node: {
                id:
<<<<<<< HEAD
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ZjRmMGY4NjktNTllNS00YWI2LWJkYjEtYWJiMGVkMTU5YTRl',
                createdAt: '2023-06-12T11:14:35.582648+00:00',
                name: 'Lol123',
                status: 'IMPORT_ERROR',
                importDate: '2023-06-12T11:14:35.582685+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                dataSource: 'XLS',
                numberOfHouseholds: 2,
                numberOfIndividuals: 6,
=======
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ZTNhMTFiMmEtOWExZS00MzExLWJiODctNmZmNDA2ZWY5OTZi',
                createdAt: '2023-09-26T10:58:23.422311+00:00',
                name: 'Some white tell. - 1695725903375430680',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:23.422324+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6MTA4ODI2OWUtY2Q2NS00ODhkLTljOWQtYmRlYjc1YTFkZDE2',
                  firstName: 'Christina',
                  lastName: 'Wilson',
                  email: 'christina.wilson_1695725903376303347@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'XLS',
                numberOfHouseholds: 20,
                numberOfIndividuals: 1732,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjE=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ODczZTAwYzUtZDQyZS00YTM4LTgzYWYtNmU0M2Q4M2MyZGQ4',
                createdAt: '2023-09-26T10:58:23.370452+00:00',
                name: 'Strategy century under. - 1695725903319024055',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:23.370468+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6ZjhhYzU5ZTEtYjRlYS00ZjYwLWIyY2ItMzZhNTljZmRlMTI3',
                  firstName: 'Michelle',
                  lastName: 'Powell',
                  email: 'michelle.powell_1695725903320501263@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'API',
                numberOfHouseholds: 34,
                numberOfIndividuals: 8831,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjI=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YmRlOWI1OTAtOGNiMS00YjY5LThjYzAtMzFjYTM3YTJlMWYw',
                createdAt: '2023-09-26T10:58:23.109293+00:00',
                name: 'Happy military during. - 1695725903060029722',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:23.109310+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6ZjRlYTFiMzctYTVhYi00MWUyLTgzNTktN2ZkNjYwZTkyMGE1',
                  firstName: 'Ronald',
                  lastName: 'Jackson',
                  email: 'ronald.jackson_1695725903061224722@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'FLEX_REGISTRATION',
                numberOfHouseholds: 12,
                numberOfIndividuals: 9517,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjM=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6OTg1NjE1NDctZDkxYS00NjAxLWFmNDktYWQyM2FlOTE1YmJj',
                createdAt: '2023-09-26T10:58:23.054392+00:00',
                name: 'Knowledge claim event. - 1695725903002218138',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:23.054410+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6N2U2ZjMzNGItOWFmOC00YTc0LWFiZGEtZDEwNmJkZTczZGNh',
                  firstName: 'Angela',
                  lastName: 'Tapia',
                  email: 'angela.tapia_1695725903003836930@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'XLS',
                numberOfHouseholds: 9,
                numberOfIndividuals: 7925,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjQ=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ODI0NjdlYzgtZmIyYy00OWFiLTlmZDYtZWRiZDc3MTUzMWFk',
                createdAt: '2023-09-26T10:58:22.794110+00:00',
                name: 'Between husband skill. - 1695725902743894221',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:22.794128+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6MmZkNTk5ZjQtODllMi00OTQwLWI1NWItN2I1ODM4MzFmMTVh',
                  firstName: 'Brianna',
                  lastName: 'Schultz',
                  email: 'brianna.schultz_1695725902745131221@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'EDOPOMOGA',
                numberOfHouseholds: 50,
                numberOfIndividuals: 6720,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjU=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6YjEzYWIxZTEtMzA5My00YzMzLWFiMTctYjVkMDU0MTk2MjQw',
                createdAt: '2023-09-26T10:58:22.737922+00:00',
                name: 'Even activity it. - 1695725902685812513',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:22.737943+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6MTRiNWQ5OGYtOTM3NS00NjJkLTgwMmItNDhkNWM1YTA3Y2Fm',
                  firstName: 'Daniel',
                  lastName: 'Walton',
                  email: 'daniel.walton_1695725902687290055@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'FLEX_REGISTRATION',
                numberOfHouseholds: 10,
                numberOfIndividuals: 8864,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjY=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6NWQ3NTI1MWQtOGNlNy00NjRiLThkMTctZTlkZmZlMjk5Y2Q1',
                createdAt: '2023-09-26T10:58:22.485764+00:00',
                name: 'Feeling already. - 1695725902434868763',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:22.485787+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6YTFiYTAzNzgtYjYzNC00NGVlLTgxYjAtOTU4M2U3ZTRhOTIw',
                  firstName: 'John',
                  lastName: 'Yoder',
                  email: 'john.yoder_1695725902435974096@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'DIIA',
                numberOfHouseholds: 49,
                numberOfIndividuals: 4923,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjc=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6NGFlODQ3YzMtZTFmYi00MmQ0LTk1MzMtOGU5MWIyYTNjNDk5',
                createdAt: '2023-09-26T10:58:22.427929+00:00',
                name: 'Response reason positive talk. - 1695725902374813305',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:22.427950+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6ZTYzMWE3OTItM2Y2YS00MWI5LWI5YWItM2M5ZTI5NDA2YjQ5',
                  firstName: 'Kelly',
                  lastName: 'Swanson',
                  email: 'kelly.swanson_1695725902376114013@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'FLEX_REGISTRATION',
                numberOfHouseholds: 23,
                numberOfIndividuals: 6748,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjg=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ZWQxNDg2OWItYjg1Ni00NWQwLWI0MmMtOTI5ZGRlYWYxNzFl',
                createdAt: '2023-09-26T10:58:22.139754+00:00',
                name: 'Finally teach public. - 1695725902089511388',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:22.139777+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6MTI4NzA2MmEtNTk2Yy00M2FlLWFlYjktZjMzZTliYmU1OTRi',
                  firstName: 'David',
                  lastName: 'Thompson',
                  email: 'david.thompson_1695725902090292721@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'KOBO',
                numberOfHouseholds: 12,
                numberOfIndividuals: 3713,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
                __typename: 'RegistrationDataImportNode',
              },
              __typename: 'RegistrationDataImportNodeEdge',
            },
            {
              cursor: 'YXJyYXljb25uZWN0aW9uOjk=',
              node: {
                id:
                  'UmVnaXN0cmF0aW9uRGF0YUltcG9ydE5vZGU6ZDZjMTIyZTUtODlmMy00MmM2LWIzNjUtNzdhMmM5Mzg5MDFk',
                createdAt: '2023-09-26T10:58:22.084687+00:00',
                name: 'Hear someone. - 1695725902026326763',
                status: 'IN_REVIEW',
                erased: false,
                importDate: '2023-09-26T10:58:22.084701+00:00',
                importedBy: {
                  id:
                    'VXNlck5vZGU6ZWRkZjVlZmItYTYxNy00YTMyLTk4YjYtZDE3NzUzNjE3ZjEz',
                  firstName: 'Sandra',
                  lastName: 'Bryan',
                  email: 'sandra.bryan_1695725902028008304@unicef.com',
                  __typename: 'UserNode',
                },
                dataSource: 'XLS',
                numberOfHouseholds: 31,
                numberOfIndividuals: 411,
                refuseReason: null,
                totalHouseholdsCountWithValidPhoneNo: 0,
>>>>>>> develop
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

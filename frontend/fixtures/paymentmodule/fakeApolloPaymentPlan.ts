import {
  PaymentPlanQuery,
  PaymentPlanStatus,
  PaymentPlanCurrency,
} from '../../src/__generated__/graphql';

export const fakeApolloPaymentPlan: PaymentPlanQuery['paymentPlan'] = {
  id:
    'UGF5bWVudFBsYW5Ob2RlOmE5YzJjMmM4LWJmYWUtNDBhMy05YmYwLWIxYWE1ZmRlMDE0YQ==',
  unicefId: 'PP-0060-22-00000001',
  status: PaymentPlanStatus.Locked,
  backgroundActionStatus: null,
  createdBy: {
    id: 'VXNlck5vZGU6ZjRlMTYwZDEtOTgyNy00NmEwLTg4MzAtZmU1MjljZDVhNDBj',
    firstName: 'Matthew',
    lastName: 'Sosa',
    email: 'matthew.sosa_1661510712238266406@unicef.com',
    __typename: 'UserNode',
  },
  program: {
    id: 'UHJvZ3JhbU5vZGU6NWJhMjEzY2UtNmNlOS00NTc4LThhNDgtYjFmMDgyM2Q2MDAy',
    name: 'Already attention fear well hit instead person.',
    __typename: 'ProgramNode',
  },
  targetPopulation: {
    id:
      'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MzlmMjQ0YzEtZGRiMC00ZGZmLWE0MzEtN2JiMDFhMTdiMThm',
    name: 'Report should property early adult.',
    __typename: 'TargetPopulationNode',
  },
  currency: PaymentPlanCurrency.Pln,
  currencyName: 'Polish złoty',
  startDate: '2020-10-27',
  endDate: '2021-09-08',
  dispersionStartDate: '2028-05-19',
  dispersionEndDate: '2029-08-07',
  femaleChildrenCount: 0,
  femaleAdultsCount: 1,
  maleChildrenCount: 0,
  maleAdultsCount: 2,
  totalHouseholdsCount: 1,
  totalIndividualsCount: 3,
  totalEntitledQuantity: 2691.69,
  totalDeliveredQuantity: 1769,
  totalUndeliveredQuantity: 922.69,
  approvalProcess: {
    totalCount: 1,
    edgeCount: 1,
    edges: [
      {
        node: {
          id:
            'QXBwcm92YWxQcm9jZXNzTm9kZTo2OTBkYTdmNy03M2QxLTQ4MWEtODc3Mi1hODVhMWIzZDFlYzI=',
          sentForApprovalBy: {
            id: 'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
            firstName: 'Root',
            lastName: 'Rootkowski',
            email: 'root@root.com',
            __typename: 'UserNode',
          },
          sentForApprovalDate: '2022-08-30T07:15:31.428788+00:00',
          sentForAuthorizationBy: {
            id: 'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
            firstName: 'Root',
            lastName: 'Rootkowski',
            email: 'root@root.com',
            __typename: 'UserNode',
          },
          sentForAuthorizationDate: '2022-08-30T07:15:41.790444+00:00',
          sentForFinanceReviewBy: null,
          sentForFinanceReviewDate: null,
          actions: {
            approval: [
              {
                createdAt: '2022-08-30T07:15:41.787449+00:00',
                comment: '',
                info: 'Approved by Root Rootkowski',
                createdBy: {
                  id:
                    'VXNlck5vZGU6NDE5NmMyYzUtYzJkZC00OGQyLTg4N2YtM2E5ZDM5ZTc4OTE2',
                  firstName: 'Root',
                  lastName: 'Rootkowski',
                  email: 'root@root.com',
                  __typename: 'UserNode',
                },
                __typename: 'ApprovalNode',
              },
            ],
            authorization: [],
            financeReview: [],
            reject: [],
            __typename: 'FilteredActionsListNode',
          },
          rejectedOn: null,
          __typename: 'ApprovalProcessNode',
        },
        __typename: 'ApprovalProcessNodeEdge',
      },
    ],
    __typename: 'ApprovalProcessNodeConnection',
  },
  approvalNumberRequired: 1,
  authorizationNumberRequired: 1,
  financeReviewNumberRequired: 1,
  steficonRule: null,
  hasPaymentListExportFile: false,
  importedFileDate: null,
  importedFileName: '',
  totalEntitledQuantityUsd: 376,
  paymentsConflictsCount: 0,
  deliveryMechanisms: [
    {
      id:
        'RGVsaXZlcnlNZWNoYW5pc21Ob2RlOjkyNGM5NTBhLTE5YzQtNGJiNC04ZDExLTI3Yzg5OTczNzlhYQ==',
      name: 'Cash',
      fsp: {
        id:
          'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZToyMzA5MzQ2YS01NTA3LTRjY2UtOTkxMS05MDYwNjBkYWNkMDM=',
        name: 'Miranda Ltd',
        __typename: 'FinancialServiceProviderNode',
      },
      __typename: 'DeliveryMechanismNode',
    },
    {
      id:
        'RGVsaXZlcnlNZWNoYW5pc21Ob2RlOjFjMjQwMmFhLWY5N2QtNDNhNC1iYThkLTcwM2Q0YjUxYTQ5OQ==',
      name: 'In Kind',
      fsp: {
        id:
          'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTplNjlkZTM1Yi1kMzRjLTQyNzYtOTJhMi1lNTYyOWQwNmEzMzY=',
        name: 'Frazier-Watson',
        __typename: 'FinancialServiceProviderNode',
      },
      __typename: 'DeliveryMechanismNode',
    },
    {
      id:
        'RGVsaXZlcnlNZWNoYW5pc21Ob2RlOjAwYjlhNTA5LTE4MDEtNGQ1MS04ODk1LTJkYzMyOGNjNjI3MA==',
      name: 'Transfer',
      fsp: {
        id:
          'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTpkODU3MmFjNy04MjMyLTQwYjItOWFjNS0zMDBiZWQ2YjcwNDU=',
        name: 'Bray Group',
        __typename: 'FinancialServiceProviderNode',
      },
      __typename: 'DeliveryMechanismNode',
    },
  ],
  volumeByDeliveryMechanism: [
    {
      deliveryMechanism: {
        id:
          'RGVsaXZlcnlNZWNoYW5pc21Ob2RlOjkyNGM5NTBhLTE5YzQtNGJiNC04ZDExLTI3Yzg5OTczNzlhYQ==',
        name: 'Cash',
        order: 1,
        fsp: {
          id:
            'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZToyMzA5MzQ2YS01NTA3LTRjY2UtOTkxMS05MDYwNjBkYWNkMDM=',
          name: 'Miranda Ltd',
          __typename: 'FinancialServiceProviderNode',
        },
        __typename: 'DeliveryMechanismNode',
      },
      volume: 0,
      volumeUsd: 0,
      __typename: 'VolumeByDeliveryMechanismNode',
    },
    {
      deliveryMechanism: {
        id:
          'RGVsaXZlcnlNZWNoYW5pc21Ob2RlOjFjMjQwMmFhLWY5N2QtNDNhNC1iYThkLTcwM2Q0YjUxYTQ5OQ==',
        name: 'In Kind',
        order: 2,
        fsp: {
          id:
            'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTplNjlkZTM1Yi1kMzRjLTQyNzYtOTJhMi1lNTYyOWQwNmEzMzY=',
          name: 'Frazier-Watson',
          __typename: 'FinancialServiceProviderNode',
        },
        __typename: 'DeliveryMechanismNode',
      },
      volume: 0,
      volumeUsd: 0,
      __typename: 'VolumeByDeliveryMechanismNode',
    },
    {
      deliveryMechanism: {
        id:
          'RGVsaXZlcnlNZWNoYW5pc21Ob2RlOjAwYjlhNTA5LTE4MDEtNGQ1MS04ODk1LTJkYzMyOGNjNjI3MA==',
        name: 'Transfer',
        order: 3,
        fsp: {
          id:
            'RmluYW5jaWFsU2VydmljZVByb3ZpZGVyTm9kZTpkODU3MmFjNy04MjMyLTQwYjItOWFjNS0zMDBiZWQ2YjcwNDU=',
          name: 'Bray Group',
          __typename: 'FinancialServiceProviderNode',
        },
        __typename: 'DeliveryMechanismNode',
      },
      volume: 0,
      volumeUsd: 0,
      __typename: 'VolumeByDeliveryMechanismNode',
    },
  ],
  __typename: 'PaymentPlanNode',
};

import { CashPlanNode } from '../../src/__generated__/graphql';

export const fakeCashPlan = {
  id: 'Q2FzaFBsYW5Ob2RlOjI1ZTNkODA0LTAzMzEtNDhkOC1iYTk2LWVmZjEzYmU3ZDdiYQ==',
  canCreatePaymentVerificationPlan: false,
  name: 'Military citizen until amount.',
  startDate: '2020-07-14T05:04:13',
  endDate: '2023-03-17T05:04:13',
  updatedAt: '2022-02-16T10:53:05.636703',
  status: 'DISTRIBUTION_COMPLETED',
  deliveryType: 'Voucher',
  fundsCommitment: '62947144',
  downPayment: '27371694',
  dispersionDate: '2021-12-14T05:04:13',
  assistanceThrough: '123-21-SRV-00002',
  serviceProvider: null,
  caId: '123-21-CSH-00003',
  caHashId: 'bf0e9242-5748-4557-8bc1-3d1f8c9eacfa',
  bankReconciliationSuccess: 1,
  bankReconciliationError: 3,
  totalNumberOfHouseholds: 5,
  verificationPlans: {
    totalCount: 3,
    edges: [
      {
        node: {
          id:
            'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTpkYTAwZGJiMy0xMTMzLTQxNzctYTVhNC0xOTUxOGIyNjBmNjU=',
          unicefId: 'PVP-1',
          status: 'ACTIVE',
          sampleSize: 1,
          receivedCount: null,
          notReceivedCount: null,
          respondedCount: null,
          verificationChannel: 'MANUAL',
          sampling: 'FULL_LIST',
          receivedWithProblemsCount: null,
          rapidProFlowId: '',
          confidenceInterval: null,
          marginOfError: null,
          activationDate: '2022-02-07T16:02:51.287552',
          completionDate: null,
          ageFilter: null,
          excludedAdminAreasFilter: [],
          sexFilter: null,
          __typename: 'CashPlanPaymentVerificationNode',
        },
        __typename: 'CashPlanPaymentVerificationNodeEdge',
      },
      {
        node: {
          id:
            'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTpkODA1NTgzYy0xMWMxLTQxNGYtYTdmZC1hYmU1YjBhNTY4NTQ=',
          unicefId: 'PVP-2',
          status: 'ACTIVE',
          sampleSize: 1,
          receivedCount: null,
          notReceivedCount: null,
          respondedCount: null,
          verificationChannel: 'XLSX',
          sampling: 'FULL_LIST',
          receivedWithProblemsCount: null,
          rapidProFlowId: '',
          confidenceInterval: null,
          marginOfError: null,
          activationDate: '2022-02-08T10:03:34.755575',
          completionDate: null,
          ageFilter: null,
          excludedAdminAreasFilter: [],
          sexFilter: null,
          __typename: 'CashPlanPaymentVerificationNode',
        },
        __typename: 'CashPlanPaymentVerificationNodeEdge',
      },
      {
        node: {
          id:
            'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uTm9kZTozNTg0MTk4Ni00ZTNjLTQyNjAtODIzYi1mYmUwZTg3ZGUyMDU=',
          unicefId: 'PVP-3',
          status: 'PENDING',
          sampleSize: 1,
          receivedCount: null,
          notReceivedCount: null,
          respondedCount: null,
          verificationChannel: 'MANUAL',
          sampling: 'FULL_LIST',
          receivedWithProblemsCount: null,
          rapidProFlowId: '',
          confidenceInterval: null,
          marginOfError: null,
          activationDate: null,
          completionDate: null,
          ageFilter: null,
          excludedAdminAreasFilter: [],
          sexFilter: null,
          __typename: 'CashPlanPaymentVerificationNode',
        },
        __typename: 'CashPlanPaymentVerificationNodeEdge',
      },
    ],
    __typename: 'CashPlanPaymentVerificationNodeConnection',
  },
  paymentVerificationSummary: {
    id:
      'Q2FzaFBsYW5QYXltZW50VmVyaWZpY2F0aW9uU3VtbWFyeU5vZGU6MTNjY2MxNzMtNzEwZS00N2NkLTg1ZmQtODM4YTFlMjZiNDUy',
    createdAt: '2022-02-17T14:23:02.018701',
    updatedAt: '2022-02-17T14:23:02.018730',
    status: 'PENDING',
    activationDate: null,
    completionDate: null,
    __typename: 'CashPlanPaymentVerificationSummaryNode',
  },
  program: {
    id: 'UHJvZ3JhbU5vZGU6YzRkNTY1N2QtMWEyOS00NmUxLTgxOTAtZGY3Zjg1YTBkMmVm',
    name: 'Surface campaign practice actually about about will what.',
    caId: '123-21-PRG-00001',
    __typename: 'ProgramNode',
  },
  paymentItems: {
    totalCount: 5,
    edgeCount: 5,
    edges: [
      {
        node: {
          targetPopulation: {
            id:
              'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZGRlODE4MDUtMWQ0Ny00YzY0LTgzYTMtMzQ3NWEzMGVmZTJk',
            name: 'Floor anyone remain play most.',
            __typename: 'TargetPopulationNode',
          },
          __typename: 'PaymentRecordNode',
        },
        __typename: 'PaymentRecordNodeEdge',
      },
      {
        node: {
          targetPopulation: {
            id:
              'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MTdlM2VmMjAtNjczMy00ZDNhLWFiMDUtZjVkOTgzZjViMjI1',
            name: 'Former center score fire role.',
            __typename: 'TargetPopulationNode',
          },
          __typename: 'PaymentRecordNode',
        },
        __typename: 'PaymentRecordNodeEdge',
      },
      {
        node: {
          targetPopulation: {
            id:
              'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6MjRkMTdhODktMjg4OC00NDI0LTgxMDAtYmU3MTZjOWFkNDk3',
            name: 'Stock before maybe campaign blue history recently.',
            __typename: 'TargetPopulationNode',
          },
          __typename: 'PaymentRecordNode',
        },
        __typename: 'PaymentRecordNodeEdge',
      },
      {
        node: {
          targetPopulation: {
            id:
              'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6NzNiNTFhNjctZmRmNy00ODkwLWIyOWItMjhhYzk4NTc4OGRk',
            name: 'Eight affect late place.',
            __typename: 'TargetPopulationNode',
          },
          __typename: 'PaymentRecordNode',
        },
        __typename: 'PaymentRecordNodeEdge',
      },
      {
        node: {
          targetPopulation: {
            id:
              'VGFyZ2V0UG9wdWxhdGlvbk5vZGU6ZjZkZjc2MDctMzMyZi00NDYwLWJiMzgtMTZiZGM4MGVkNTkz',
            name: 'Seek development woman once worker.',
            __typename: 'TargetPopulationNode',
          },
          __typename: 'PaymentRecordNode',
        },
        __typename: 'PaymentRecordNodeEdge',
      },
    ],
    __typename: 'PaymentRecordNodeConnection',
  },
  __typename: 'CashPlanNode',
} as CashPlanNode;

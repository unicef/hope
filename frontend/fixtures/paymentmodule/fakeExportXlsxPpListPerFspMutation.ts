import { ExportXlsxPpListPerFspDocument } from '../../src/__generated__/graphql';

export const fakeExportXlsxPpListPerFspMutation = [
  {
    request: {
      query: ExportXlsxPpListPerFspDocument,
      variables: {
        paymentPlanId: 'fakePaymentPlanId',
      },
    },
    result: {
      data: {
        exportXlsxPaymentPlanPaymentListPerFsp: {
          paymentPlan: {
            id: 'fakePaymentPlanId',
            status: 'fakeStatus',
          },
        },
      },
    },
  },
];

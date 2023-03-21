import { ImportXlsxPpListPerFspDocument } from '../../src/__generated__/graphql';

export const fakeImportXlsxPpListPerFspMutation = [
  {
    request: {
      query: ImportXlsxPpListPerFspDocument,
      variables: {
        file: 'fakeFile',
        paymentPlanId: 'fakePaymentPlanId',
      },
    },
    result: {
      data: {
        importXlsxPaymentPlanPaymentListPerFsp: {
          paymentPlan: {
            id: 'fakePaymentPlanId',
            status: 'fakeStatus',
          },
          errors: {
            sheet: 'fakeSheet',
            coordinates: 'fakeCoordinates',
            message: 'fakeMessage',
          },
        },
      },
    },
  },
];

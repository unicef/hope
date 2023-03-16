import { ImportXlsxPpListDocument } from '../../src/__generated__/graphql';

export const fakeImportXlsxPpListMutation = [
  {
    request: {
      query: ImportXlsxPpListDocument,
      variables: {
        file: 'fakeFile',
        paymentPlanId: 'fakePaymentPlanId',
      },
    },
    result: {
      data: {
        importXlsxPaymentPlanPaymentList: {
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
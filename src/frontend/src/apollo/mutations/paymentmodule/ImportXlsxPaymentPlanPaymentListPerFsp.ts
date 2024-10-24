import { gql } from '@apollo/client';

export const ImportXlsxPPListPerFsp = gql`
  mutation importXlsxPPListPerFsp($paymentPlanId: ID!, $file: Upload!) {
    importXlsxPaymentPlanPaymentListPerFsp(
      paymentPlanId: $paymentPlanId
      file: $file
    ) {
      paymentPlan {
        id
        status
      }
      errors {
        sheet
        coordinates
        message
      }
    }
  }
`;

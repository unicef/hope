import { gql } from '@apollo/client';

export const ImportXlsxPPList = gql`
  mutation importXlsxPPList($paymentPlanId: ID!, $file: Upload!) {
    importXlsxPaymentPlanPaymentList(
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

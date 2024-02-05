import { gql } from '@apollo/client';

export const ImportXlsxPaymentVerificationPlanFile = gql`
  mutation ImportXlsxPaymentVerificationPlanFile(
    $paymentVerificationPlanId: ID!
    $file: Upload!
  ) {
    importXlsxPaymentVerificationPlanFile(
      paymentVerificationPlanId: $paymentVerificationPlanId
      file: $file
    ) {
      paymentPlan {
        id
      }
      errors {
        sheet
        coordinates
        message
      }
    }
  }
`;

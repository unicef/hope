import { gql } from 'apollo-boost';

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

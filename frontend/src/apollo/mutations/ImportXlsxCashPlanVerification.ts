import { gql } from 'apollo-boost';

export const ImportXlsxCashPlanVerification = gql`
  mutation importXlsxCashPlanVerification(
    $cashPlanVerificationId: ID!
    $file: Upload!
  ) {
    importXlsxCashPlanVerification(
      cashPlanVerificationId: $cashPlanVerificationId
      file: $file
    ) {
      cashPlan {
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

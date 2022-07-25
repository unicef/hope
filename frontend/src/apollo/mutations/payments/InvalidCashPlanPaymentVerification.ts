import { gql } from 'apollo-boost';
export const InvalidCashPlanPaymentVerification = gql`
  mutation InvalidCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
    invalidCashPlanPaymentVerification(
      cashPlanVerificationId: $cashPlanVerificationId
    ) {
      cashPlan {
        id
        verifications {
          edges {
            node {
              id
              xlsxFileExporting
              hasXlsxFile
              xlsxFileWasDownloaded
              xlsxFileImported
            }
          }
        }
      }
    }
  }
`;

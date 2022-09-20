import { gql } from 'apollo-boost';
export const InvalidCashPlanPaymentVerification = gql`
  mutation InvalidCashPlanPaymentVerification($cashPlanVerificationId: ID!) {
    invalidCashPlanPaymentVerification(
      cashPlanVerificationId: $cashPlanVerificationId
    ) {
      cashPlan {
        id
        verificationPlans {
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

import { gql } from 'apollo-boost';
export const ExportXlsxCashPlanVerification = gql`
  mutation ExportXlsxCashPlanVerification($cashPlanVerificationId: ID!) {
    exportXlsxCashPlanVerification(
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

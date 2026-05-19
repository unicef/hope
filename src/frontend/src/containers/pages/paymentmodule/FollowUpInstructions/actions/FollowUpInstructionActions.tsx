import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { RestService } from '@restgenerated/services/RestService';
import { ReactElement } from 'react';
import { ConfirmWorkflowButton } from './ConfirmWorkflowButton';
import { SimpleWorkflowButton } from './SimpleWorkflowButton';
import { ReconciliationImportButton } from './ReconciliationImportButton';

interface FollowUpInstructionActionsProps {
  instruction: FollowUpInstructionDetail;
  permissions: string[];
}

export function FollowUpInstructionActions({
  instruction,
}: FollowUpInstructionActionsProps): ReactElement {
  const { businessArea, programId } = useBaseUrl();
  const { status } = instruction;

  const commonArgs = {
    businessAreaSlug: businessArea,
    id: instruction.id,
    programCode: programId,
  };

  return (
    <Box display="flex" gap={1} flexWrap="wrap">
      {status === 'OPEN' && (
        <SimpleWorkflowButton
          label="Lock"
          instruction={instruction}
          mutationFn={() =>
            RestService.restBusinessAreasProgramsFollowUpInstructionsLockRetrieve(
              commonArgs,
            )
          }
          successMessage="Follow-up Instruction locked"
          dataCy="button-lock"
        />
      )}

      {status === 'LOCKED' && (
        <>
          <SimpleWorkflowButton
            label="Unlock"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsUnlockRetrieve(
                commonArgs,
              )
            }
            successMessage="Follow-up Instruction unlocked"
            variant="outlined"
            dataCy="button-unlock"
          />
          <SimpleWorkflowButton
            label="Lock FSP"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsLockFspRetrieve(
                commonArgs,
              )
            }
            successMessage="FSP locked"
            dataCy="button-lock-fsp"
          />
        </>
      )}

      {status === 'LOCKED_FSP' && (
        <>
          <SimpleWorkflowButton
            label="Unlock FSP"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsUnlockFspRetrieve(
                commonArgs,
              )
            }
            successMessage="FSP unlocked"
            variant="outlined"
            dataCy="button-unlock-fsp"
          />
          <SimpleWorkflowButton
            label="Send for Approval"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsSendForApprovalRetrieve(
                commonArgs,
              )
            }
            successMessage="Sent for approval"
            dataCy="button-send-for-approval"
          />
        </>
      )}

      {status === 'IN_APPROVAL' && (
        <>
          <ConfirmWorkflowButton
            label="Approve"
            instruction={instruction}
            mutationFn={(comment) =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsApproveCreate(
                { ...commonArgs, requestBody: comment ? { comment } : undefined },
              )
            }
            successMessage="Approved"
            withComment
            dataCy="button-approve"
          />
          <ConfirmWorkflowButton
            label="Reject"
            instruction={instruction}
            mutationFn={(comment) =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsRejectCreate(
                { ...commonArgs, requestBody: comment ? { comment } : undefined },
              )
            }
            successMessage="Rejected"
            withComment
            color="error"
            variant="outlined"
            dataCy="button-reject"
          />
        </>
      )}

      {status === 'IN_AUTHORIZATION' && (
        <>
          <ConfirmWorkflowButton
            label="Authorize"
            instruction={instruction}
            mutationFn={(comment) =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsAuthorizeCreate(
                { ...commonArgs, requestBody: comment ? { comment } : undefined },
              )
            }
            successMessage="Authorized"
            withComment
            dataCy="button-authorize"
          />
          <ConfirmWorkflowButton
            label="Reject"
            instruction={instruction}
            mutationFn={(comment) =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsRejectCreate(
                { ...commonArgs, requestBody: comment ? { comment } : undefined },
              )
            }
            successMessage="Rejected"
            withComment
            color="error"
            variant="outlined"
            dataCy="button-reject"
          />
        </>
      )}

      {status === 'IN_REVIEW' && (
        <>
          <ConfirmWorkflowButton
            label="Mark as Released"
            instruction={instruction}
            mutationFn={(comment) =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsMarkAsReleasedCreate(
                { ...commonArgs, requestBody: comment ? { comment } : undefined },
              )
            }
            successMessage="Marked as released"
            withComment
            dataCy="button-mark-as-released"
          />
          <ConfirmWorkflowButton
            label="Reject"
            instruction={instruction}
            mutationFn={(comment) =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsRejectCreate(
                { ...commonArgs, requestBody: comment ? { comment } : undefined },
              )
            }
            successMessage="Rejected"
            withComment
            color="error"
            variant="outlined"
            dataCy="button-reject"
          />
        </>
      )}

      {(status === 'ACCEPTED' || status === 'FINISHED') && (
        <>
          <SimpleWorkflowButton
            label="Export XLSX"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsExportXlsxRetrieve(
                commonArgs,
              )
            }
            successMessage="Export started"
            dataCy="button-export-xlsx"
          />
          <SimpleWorkflowButton
            label="Reconciliation Export"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsReconciliationExportXlsxRetrieve(
                commonArgs,
              )
            }
            successMessage="Reconciliation export started"
            variant="outlined"
            dataCy="button-reconciliation-export"
          />
          <ReconciliationImportButton instruction={instruction} />
        </>
      )}

      {(status === 'ACCEPTED' || status === 'FINISHED') && (
        <SimpleWorkflowButton
          label="Close"
          instruction={instruction}
          mutationFn={() =>
            RestService.restBusinessAreasProgramsFollowUpInstructionsCloseRetrieve(
              commonArgs,
            )
          }
          successMessage="Follow-up Instruction closed"
          variant="outlined"
          dataCy="button-close"
        />
      )}

      {status !== 'ABORTED' &&
        status !== 'CLOSED' &&
        status !== 'FINISHED' && (
          <ConfirmWorkflowButton
            label="Abort"
            instruction={instruction}
            mutationFn={() =>
              RestService.restBusinessAreasProgramsFollowUpInstructionsAbortCreate(
                commonArgs,
              )
            }
            successMessage="Follow-up Instruction aborted"
            confirmMessage="Are you sure you want to abort this Follow-up Instruction?"
            color="error"
            variant="outlined"
            dataCy="button-abort"
          />
        )}

      {status === 'ABORTED' && (
        <SimpleWorkflowButton
          label="Reactivate"
          instruction={instruction}
          mutationFn={() =>
            RestService.restBusinessAreasProgramsFollowUpInstructionsReactivateAbortRetrieve(
              commonArgs,
            )
          }
          successMessage="Follow-up Instruction reactivated"
          dataCy="button-reactivate"
        />
      )}
    </Box>
  );
}

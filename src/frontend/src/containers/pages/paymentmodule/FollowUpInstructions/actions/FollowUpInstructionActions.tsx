import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box } from '@mui/material';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { RestService } from '@restgenerated/services/RestService';
import type { ReactElement } from 'react';
import { ConfirmWorkflowButton } from './ConfirmWorkflowButton';
import { SimpleWorkflowButton } from './SimpleWorkflowButton';
import { ReconciliationImportButton } from './ReconciliationImportButton';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';

interface FollowUpInstructionActionsProps {
  instruction: FollowUpInstructionDetail;
  permissions: string[];
}

const REJECT_PERMISSION_BY_STATUS: Partial<Record<string, string>> = {
  IN_APPROVAL: PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE,
  IN_AUTHORIZATION: PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
  IN_REVIEW: PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
};

export function FollowUpInstructionActions({
  instruction,
  permissions,
}: FollowUpInstructionActionsProps): ReactElement {
  const { businessArea, programId } = useBaseUrl();
  const { status } = instruction;

  const commonArgs = {
    businessAreaSlug: businessArea,
    id: instruction.id,
    programCode: programId,
  };
  const can = (permission: string): boolean =>
    hasPermissions(permission, permissions);
  const rejectPermission = REJECT_PERMISSION_BY_STATUS[status];

  const abortButton = can(PERMISSIONS.PM_ABORT) && (
    <ConfirmWorkflowButton
      label="Abort"
      instruction={instruction}
      mutationFn={(comment) =>
        RestService.restBusinessAreasProgramsFollowUpInstructionsAbortCreate({
          ...commonArgs,
          requestBody: { abortComment: comment },
        })
      }
      successMessage="Follow-up Instruction aborted"
      withComment
      color="error"
      variant="outlined"
      dataCy="button-abort"
    />
  );
  const rejectButton = rejectPermission && can(rejectPermission) && (
    <ConfirmWorkflowButton
      label="Reject"
      instruction={instruction}
      mutationFn={(comment) =>
        RestService.restBusinessAreasProgramsFollowUpInstructionsRejectCreate({
          ...commonArgs,
          requestBody: comment ? { comment } : undefined,
        })
      }
      successMessage="Rejected"
      withComment
      color="error"
      variant="outlined"
      dataCy="button-reject"
    />
  );

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1,
        flexWrap: 'wrap',
      }}
    >
      {status === 'OPEN' && can(PERMISSIONS.PM_LOCK_AND_UNLOCK) && (
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
          {can(PERMISSIONS.PM_LOCK_AND_UNLOCK) && (
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
          )}
          {can(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP) && (
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
          )}
          {abortButton}
        </>
      )}
      {status === 'LOCKED_FSP' && (
        <>
          {can(PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP) && (
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
          )}
          {can(PERMISSIONS.PM_SEND_FOR_APPROVAL) && (
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
          )}
          {abortButton}
        </>
      )}
      {status === 'IN_APPROVAL' && (
        <>
          {can(PERMISSIONS.PM_ACCEPTANCE_PROCESS_APPROVE) && (
            <ConfirmWorkflowButton
              label="Approve"
              instruction={instruction}
              mutationFn={(comment) =>
                RestService.restBusinessAreasProgramsFollowUpInstructionsApproveCreate(
                  {
                    ...commonArgs,
                    requestBody: comment ? { comment } : undefined,
                  },
                )
              }
              successMessage="Approved"
              withComment
              dataCy="button-approve"
            />
          )}
          {rejectButton}
          {abortButton}
        </>
      )}
      {status === 'IN_AUTHORIZATION' && (
        <>
          {can(PERMISSIONS.PM_ACCEPTANCE_PROCESS_AUTHORIZE) && (
            <ConfirmWorkflowButton
              label="Authorize"
              instruction={instruction}
              mutationFn={(comment) =>
                RestService.restBusinessAreasProgramsFollowUpInstructionsAuthorizeCreate(
                  {
                    ...commonArgs,
                    requestBody: comment ? { comment } : undefined,
                  },
                )
              }
              successMessage="Authorized"
              withComment
              dataCy="button-authorize"
            />
          )}
          {rejectButton}
          {abortButton}
        </>
      )}
      {status === 'IN_REVIEW' && (
        <>
          {can(PERMISSIONS.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW) && (
            <ConfirmWorkflowButton
              label="Mark as Released"
              instruction={instruction}
              mutationFn={(comment) =>
                RestService.restBusinessAreasProgramsFollowUpInstructionsMarkAsReleasedCreate(
                  {
                    ...commonArgs,
                    requestBody: comment ? { comment } : undefined,
                  },
                )
              }
              successMessage="Marked as released"
              withComment
              dataCy="button-mark-as-released"
            />
          )}
          {rejectButton}
          {abortButton}
        </>
      )}
      {(status === 'ACCEPTED' || status === 'FINISHED') && (
        <>
          {can(PERMISSIONS.PM_VIEW_LIST) && (
            <SimpleWorkflowButton
              label="Export XLSX"
              instruction={instruction}
              mutationFn={() =>
                RestService.restBusinessAreasProgramsFollowUpInstructionsDeliveryExportXlsxRetrieve(
                  commonArgs,
                )
              }
              successMessage="Exporting XLSX started"
              variant="outlined"
              dataCy="button-reconciliation-export"
            />
          )}
          {can(PERMISSIONS.PM_IMPORT_XLSX_WITH_RECONCILIATION) && (
            <ReconciliationImportButton instruction={instruction} />
          )}
        </>
      )}
      {status === 'FINISHED' && can(PERMISSIONS.PM_CLOSE_FINISHED) && (
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
      {status === 'ABORTED' && can(PERMISSIONS.PM_REACTIVATE_ABORT) && (
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

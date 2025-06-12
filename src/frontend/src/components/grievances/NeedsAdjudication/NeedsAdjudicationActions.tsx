import React, { FC } from 'react';
import { Box, Button } from '@mui/material';
import RemoveIcon from '@mui/icons-material/Remove';
import { useConfirmation } from '@components/core/ConfirmationDialog';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useSnackbar } from '@hooks/useSnackBar';
import { BiometricsResults } from './BiometricsResults';
import { useMutation } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

interface NeedsAdjudicationActionsProps {
  ticket: GrievanceTicketDetail;
  isEditable: boolean;
  canApprove: boolean;
  isTicketForApproval: boolean;
  selectedIndividualIds: string[];
  setIsEditMode: (editMode: boolean) => void;
  setSelectedIndividualIds: (individualIds: string[]) => void;
}

export const NeedsAdjudicationActions: FC<NeedsAdjudicationActionsProps> = ({
  ticket,
  isEditable,
  canApprove,
  isTicketForApproval,
  selectedIndividualIds,
  setIsEditMode,
  setSelectedIndividualIds,
}) => {
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const { baseUrl, businessArea } = useBaseUrl();
  const navigate = useNavigate();
  const confirm = useConfirmation();
  const { isActiveProgram } = useProgramContext();
  const actionsDisabled =
    !isTicketForApproval || !isActiveProgram || !selectedIndividualIds.length;
  const { dedupEngineSimilarityPair } = ticket.ticketDetails.extraData;

  const { mutateAsync: approve, isPending: isApproving } = useMutation({
    mutationFn: async (body: Record<string, any>) => {
      return RestService.restBusinessAreasGrievanceTicketsApproveNeedsAdjudicationCreate(
        {
          businessAreaSlug: businessArea,
          id: ticket.id,
          requestBody: body,
        },
      );
    },
    onSuccess: () => {
      showMessage(t('Action successful'));
      setSelectedIndividualIds([]);
    },
    onError: (error: any) => {
      showMessage(error?.body?.errors || error?.message || 'An error occurred');
    },
  });

  return (
    <Box
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      mt={2}
    >
      <Box display="flex" gap={2}>
        <Button
          onClick={() =>
            navigate(`/${baseUrl}/grievance/new-ticket`, {
              state: { linkedTicketId: ticket.id },
            })
          }
          variant="outlined"
          color="primary"
          data-cy="button-create-linked-ticket"
          disabled={!isActiveProgram}
        >
          {t('Create Linked Ticket')}
        </Button>
        {!isEditable && (
          <Button
            variant="outlined"
            color="primary"
            data-cy="button-edit"
            disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
            onClick={() => setIsEditMode(true)}
          >
            {t('Edit')}
          </Button>
        )}
        {dedupEngineSimilarityPair && (
          <BiometricsResults
            ticketId={ticket.id}
            similarityScore={dedupEngineSimilarityPair.similarityScore}
            individual1={dedupEngineSimilarityPair.individual1}
            individual2={dedupEngineSimilarityPair.individual2}
            statusCode={dedupEngineSimilarityPair.statusCode}
          />
        )}
        {isEditable && canApprove && (
          <>
            <Button
              disabled={actionsDisabled || isApproving}
              data-cy="button-mark-distinct"
              onClick={() =>
                confirm({
                  content:
                    'Are you sure you want to mark this record as distinct?',
                }).then(async () => {
                  try {
                    await approve({
                      distinctIndividualIds: selectedIndividualIds,
                    });
                  } catch (e: any) {
                    showMessage(
                      e?.body?.errors || e?.message || 'An error occurred',
                    );
                  }
                  setIsEditMode(false);
                })
              }
              variant="contained"
              color="primary"
            >
              {t('Mark as Distinct')}
            </Button>
            <Button
              disabled={actionsDisabled || isApproving}
              data-cy="button-mark-duplicate"
              onClick={() =>
                confirm({
                  content: t(
                    'Are you sure you want to mark this record as a duplicate?',
                  ),
                }).then(async () => {
                  try {
                    await approve({
                      duplicateIndividualIds: selectedIndividualIds,
                    });
                  } catch (e: any) {
                    showMessage(
                      e?.body?.errors || e?.message || 'An error occurred',
                    );
                  }
                  setIsEditMode(false);
                })
              }
              variant="contained"
              color="primary"
            >
              {t('Mark as Duplicate')}
            </Button>
          </>
        )}
      </Box>
      <Button
        variant="outlined"
        color="error"
        data-cy="button-clear"
        disabled={actionsDisabled || isApproving}
        onClick={() =>
          confirm({
            content: t(
              "Are you sure you want to clear the selected ids? They won't be marked as a duplicate or distinct anymore.",
            ),
          }).then(async () => {
            try {
              await approve({ clearIndividualIds: selectedIndividualIds });
            } catch (e: any) {
              showMessage(e?.body?.errors || e?.message || 'An error occurred');
            }
            setIsEditMode(false);
          })
        }
        endIcon={<RemoveIcon />}
      >
        {t('Clear')}
      </Button>
    </Box>
  );
};

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
import {
  GrievanceTicketQuery,
  useApproveNeedsAdjudicationMutation,
  GrievanceTicketDocument,
} from '@generated/graphql';

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
  const [approve] = useApproveNeedsAdjudicationMutation({
    refetchQueries: () => [
      {
        query: GrievanceTicketDocument,
        variables: { id: ticket.id },
      },
    ],
  });
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const navigate = useNavigate();
  const confirm = useConfirmation();
  const { isActiveProgram } = useProgramContext();
  const actionsDisabled =
    !isTicketForApproval || !isActiveProgram || !selectedIndividualIds.length;
  const { dedupEngineSimilarityPair } =
    ticket.needsAdjudicationTicketDetails.extraData;

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
              disabled={actionsDisabled}
              data-cy="button-mark-distinct"
              onClick={() =>
                confirm({
                  content:
                    'Are you sure you want to mark this record as distinct?',
                }).then(async () => {
                  try {
                    await approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        distinctIndividualIds: selectedIndividualIds,
                      },
                    });
                    setSelectedIndividualIds([]);
                  } catch (e) {
                    e.graphQLErrors.map((x) => showMessage(x.message));
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
              disabled={actionsDisabled}
              data-cy="button-mark-duplicate"
              onClick={() =>
                confirm({
                  content: t(
                    'Are you sure you want to mark this record as a duplicate?',
                  ),
                }).then(async () => {
                  try {
                    await approve({
                      variables: {
                        grievanceTicketId: ticket.id,
                        duplicateIndividualIds: selectedIndividualIds,
                      },
                    });
                    setSelectedIndividualIds([]);
                  } catch (e) {
                    e.graphQLErrors.map((x) => showMessage(x.message));
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
        disabled={actionsDisabled}
        onClick={() =>
          confirm({
            content: t(
              "Are you sure you want to clear the selected ids? They won't be marked as a duplicate or distinct anymore.",
            ),
          }).then(async () => {
            try {
              await approve({
                variables: {
                  grievanceTicketId: ticket.id,
                  clearIndividualIds: selectedIndividualIds,
                },
              });
              setSelectedIndividualIds([]);
            } catch (e) {
              e.graphQLErrors.map((x) => showMessage(x.message));
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

import React from 'react';
import { Box, Button } from '@mui/material';
import { PageHeader } from '@core/PageHeader';
import {
  finishProgramCycle,
  ProgramCycle,
  reactivateProgramCycle,
} from '@api/programCycleApi';
import { useTranslation } from 'react-i18next';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';

interface ProgramCycleDetailsHeaderProps {
  programCycle: ProgramCycle;
}

export const ProgramCycleDetailsHeader = ({
  programCycle,
}: ProgramCycleDetailsHeaderProps): React.ReactElement => {
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: finishMutation, isPending: isPendingFinishing } =
    useMutation({
      mutationFn: async () => {
        return finishProgramCycle(businessArea, programId, programCycle.id);
      },
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: [
            'programCyclesDetails',
            businessArea,
            programId,
            programCycle.id,
          ],
        });
      },
    });

  const { mutateAsync: reactivateMutation, isPending: isPendingReactivation } =
    useMutation({
      mutationFn: async () => {
        return reactivateProgramCycle(businessArea, programId, programCycle.id);
      },
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: [
            'programCyclesDetails',
            businessArea,
            programId,
            programCycle.id,
          ],
        });
      },
    });

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: '..',
    },
  ];

  const finishAction = async () => {
    try {
      await finishMutation();
      showMessage(t('Programme Cycle Finished'));
    } catch (e) {
      showMessage(e.message);
    }
  };

  const reactivateAction = async () => {
    try {
      await reactivateMutation();
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      showMessage(e.message);
    }
  };

  const buttons = (
    <>
      <Box display="flex" mt={2} mb={2}>
        {programCycle.status !== 'Finished' && (
          <Box>
            <Button
              variant="outlined"
              color="primary"
              component={Link}
              startIcon={<AddIcon />}
              to="payment-plans/new-plan"
              data-cy="button-create-payment-plan"
            >
              {t('Create Payment Plan')}
            </Button>
          </Box>
        )}
        {programCycle.status === 'Active' && (
          <Box ml={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={finishAction}
              disabled={isPendingFinishing}
              data-cy="button-finish-programme-cycle"
            >
              {t('Finish Cycle')}
            </Button>
          </Box>
        )}
        {programCycle.status === 'Finished' && (
          <Box ml={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={reactivateAction}
              disabled={isPendingReactivation}
              data-cy="button-reactivate-programme-cycle"
            >
              {t('Reactivate Cycle')}
            </Button>
          </Box>
        )}
      </Box>
    </>
  );

  return (
    <PageHeader
      title={
        <Box display="flex" alignItems={'center'}>
          <Box display="flex" flexDirection="column">
            <Box>
              {programCycle.title} (ID: {programCycle.unicef_id})
            </Box>
          </Box>
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
    >
      {buttons}
    </PageHeader>
  );
};

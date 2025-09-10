import { AdminButton } from '@core/AdminButton';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import AddIcon from '@mui/icons-material/Add';
import { Box, Button } from '@mui/material';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';
import { RestService } from '@restgenerated/index';
import { showApiErrorMessages } from '@utils/utils';

interface ProgramCycleDetailsHeaderProps {
  programCycle: ProgramCycleList;
}

export const ProgramCycleDetailsHeader = ({
  programCycle,
}: ProgramCycleDetailsHeaderProps): ReactElement => {
  const permissions = usePermissions();
  const { showMessage } = useSnackbar();
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: finishMutation, isPending: isPendingFinishing } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programSlug,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesFinishCreate({
          businessAreaSlug,
          id,
          programSlug,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: [
            'programCyclesDetails',
            businessArea,
            programCycle.id,
            programId,
          ],
        });
        showMessage(t('Programme Cycle Finished'));
      },
      onError: (error) => {
        showMessage(t('Failed to finish the programme cycle.'));
        console.error(error);
      },
    });

  const { mutateAsync: reactivateMutation, isPending: isPendingReactivation } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programSlug,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesReactivateCreate({
          businessAreaSlug,
          id,
          programSlug,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: [
            'programCyclesDetails',
            businessArea,
            programCycle.id,
            programId,
          ],
        });
      },
    });

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: '..',
    },
    {
      title: t('Programme Cycle'),
      to: '..',
    },
  ];

  const finishAction = async () => {
    try {
      await finishMutation({
        businessAreaSlug: businessArea,
        id: programCycle.id,
        programSlug: programId,
      });
      showMessage(t('Programme Cycle Finished'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const reactivateAction = async () => {
    try {
      await reactivateMutation({
        businessAreaSlug: businessArea,
        id: programCycle.id,
        programSlug: programId,
      });
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const buttons = (
    <>
      <Box display="flex" mt={2} mb={2}>
        {programCycle.status !== 'Finished' &&
          hasPermissions(PERMISSIONS.PM_CREATE, permissions) && (
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
            <Box>{programCycle.title}</Box>
          </Box>
        </Box>
      }
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={programCycle.adminUrl} />}
    >
      {buttons}
    </PageHeader>
  );
};

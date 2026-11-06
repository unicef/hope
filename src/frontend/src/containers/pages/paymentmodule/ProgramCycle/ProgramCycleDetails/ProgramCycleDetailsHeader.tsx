import { HeaderActions } from '@components/core/HeaderActions';
import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import AddIcon from '@mui/icons-material/Add';
import { Box, Button } from '@mui/material';
import { CreatePaymentPlanModal } from '@components/paymentmodule/CreatePaymentPlanModal';
import type { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/index';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../../config/permissions';

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
  const [createPaymentPlanOpen, setCreatePaymentPlanOpen] = useState(false);

  const { mutateAsync: finishMutation, isPending: isPendingFinishing } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programCode,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesFinishCreate({
          businessAreaSlug,
          id,
          programCode,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsCyclesRetrieve,
          ),
        });
        showMessage(t('Programme Cycle Finished'));
      },
      onError: (error) => {
        showApiErrorMessages(error, showMessage);
      },
    });

  const { mutateAsync: reactivateMutation, isPending: isPendingReactivation } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programCode,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
      }) =>
        RestService.restBusinessAreasProgramsCyclesReactivateCreate({
          businessAreaSlug,
          id,
          programCode,
        }),
      onSuccess: async () => {
        await queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsCyclesRetrieve,
          ),
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
        programCode: programId,
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
        programCode: programId,
      });
      showMessage(t('Programme Cycle Reactivated'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const buttons = (
    <>
      <HeaderActions spacing="between">
        {programCycle.status !== 'Finished' &&
          hasPermissions(PERMISSIONS.PM_CREATE, permissions) && (
            <Box>
              <Button
                variant="outlined"
                color="primary"
                component={Link}
                startIcon={<AddIcon />}
                to="payment-lists/new-plan"
                data-cy="button-create-payment-list"
                data-perm={PERMISSIONS.PM_CREATE}
              >
                {t('Create Payment List')}
              </Button>
            </Box>
          )}

        {hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_CREATE, permissions) && (
          <Box>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setCreatePaymentPlanOpen(true)}
              data-cy="button-create-payment-plan"
              data-perm={PERMISSIONS.PM_PAYMENT_PLAN_CREATE}
            >
              {t('Create Payment Plan')}
            </Button>
          </Box>
        )}

        {programCycle.status === 'Active' &&
          hasPermissions(
            PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE,
            permissions,
          ) && (
            <Box>
              <Button
                variant="contained"
                color="primary"
                onClick={finishAction}
                disabled={isPendingFinishing}
                data-cy="button-finish-programme-cycle"
                data-perm={PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE}
              >
                {t('Finish Cycle')}
              </Button>
            </Box>
          )}
        {programCycle.status === 'Finished' &&
          hasPermissions(
            PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE,
            permissions,
          ) && (
            <Box>
              <Button
                variant="contained"
                color="primary"
                onClick={reactivateAction}
                disabled={isPendingReactivation}
                data-cy="button-reactivate-programme-cycle"
                data-perm={PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE}
              >
                {t('Reactivate Cycle')}
              </Button>
            </Box>
          )}
      </HeaderActions>

      <CreatePaymentPlanModal
        open={createPaymentPlanOpen}
        onClose={() => setCreatePaymentPlanOpen(false)}
        cycleId={programCycle.id}
        cycleTitle={programCycle.title}
        onSuccess={() => setCreatePaymentPlanOpen(false)}
      />
    </>
  );

  return (
    <PageHeader
      title={
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
            }}
          >
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

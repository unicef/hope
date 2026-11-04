import { HeaderActions } from '@components/core/HeaderActions';
import { AdminButton } from '@core/AdminButton';
import type { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import AddIcon from '@mui/icons-material/Add';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import type { PaymentPlanCreate } from '@restgenerated/models/PaymentPlanCreate';
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
  const [newPaymentPlanName, setNewPaymentPlanName] = useState('');

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

  const { mutateAsync: createPaymentPlan, isPending: creatingPaymentPlan } =
    useMutation({
      mutationFn: (name: string) =>
        RestService.restBusinessAreasProgramsPaymentPlansCreate({
          businessAreaSlug: businessArea,
          programCode: programId,
          // Generated PaymentPlanCreate marks readonly id/unicefId as
          // required; only name + cycle are accepted on create.
          // The generated PaymentPlanCreate model doesn't match the actual
          // create payload ({ name, cycle }); cast until codegen is corrected.
          requestBody: {
            name,
            cycle: programCycle.id,
          } as unknown as PaymentPlanCreate,
        }),
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentPlansList,
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

  const handleCreatePaymentPlan = async (): Promise<void> => {
    try {
      await createPaymentPlan(newPaymentPlanName.trim());
      showMessage(t('Payment Plan created'));
      setCreatePaymentPlanOpen(false);
      setNewPaymentPlanName('');
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

      <Dialog
        open={createPaymentPlanOpen}
        onClose={() => setCreatePaymentPlanOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>{t('Create Payment Plan')}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label={t('Payment Plan Name')}
            name="groupName"
            fullWidth
            value={newPaymentPlanName}
            onChange={(e) => setNewPaymentPlanName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatePaymentPlanOpen(false)}>
            {t('Cancel')}
          </Button>
          <Button
            onClick={handleCreatePaymentPlan}
            variant="contained"
            disabled={!newPaymentPlanName.trim() || creatingPaymentPlan}
            data-cy="button-create-group-submit"
          >
            {t('Create')}
          </Button>
        </DialogActions>
      </Dialog>
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

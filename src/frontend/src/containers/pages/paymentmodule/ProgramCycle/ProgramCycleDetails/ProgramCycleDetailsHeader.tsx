import { AdminButton } from '@core/AdminButton';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
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
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';
import { RestService } from '@restgenerated/index';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
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
  const [createGroupOpen, setCreateGroupOpen] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');

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
          queryKey: [
            'programCyclesDetails',
            businessArea,
            programCycle.id,
            programId,
          ],
        });
      },
    });

  const { mutateAsync: createGroup, isPending: creatingGroup } = useMutation({
    mutationFn: (name: string) =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        requestBody: { name, cycle: programCycle.id } as any,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroupsList', businessArea, programId],
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

  const handleCreateGroup = async (): Promise<void> => {
    try {
      await createGroup(newGroupName.trim());
      showMessage(t('Payment Plan Group created'));
      setCreateGroupOpen(false);
      setNewGroupName('');
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
                data-perm={PERMISSIONS.PM_CREATE}
              >
                {t('Create Payment Plan')}
              </Button>
            </Box>
          )}

        {hasPermissions(PERMISSIONS.PM_PAYMENT_PLAN_GROUP_CREATE, permissions) && (
          <Box ml={2}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setCreateGroupOpen(true)}
              data-cy="button-create-payment-plan-group"
              data-perm={PERMISSIONS.PM_PAYMENT_PLAN_GROUP_CREATE}
            >
              {t('Create Payment Plan Group')}
            </Button>
          </Box>
        )}

        {programCycle.status === 'Active' &&
          hasPermissions(
            PERMISSIONS.PM_PROGRAMME_CYCLE_UPDATE,
            permissions,
          ) && (
            <Box ml={2}>
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
            <Box ml={2}>
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
      </Box>

      <Dialog
        open={createGroupOpen}
        onClose={() => setCreateGroupOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>{t('Create Payment Plan Group')}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label={t('Group Name')}
            name="groupName"
            fullWidth
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateGroupOpen(false)}>{t('Cancel')}</Button>
          <Button
            onClick={handleCreateGroup}
            variant="contained"
            disabled={!newGroupName.trim() || creatingGroup}
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

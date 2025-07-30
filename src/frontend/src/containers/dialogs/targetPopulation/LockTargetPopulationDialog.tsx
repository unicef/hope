import { LoadingButton } from '@components/core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { Button, DialogContent, DialogTitle } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

export interface LockTargetPopulationDialogProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  targetPopulationId: string;
}

export const LockTargetPopulationDialog = ({
  open,
  setOpen,
  targetPopulationId,
}: LockTargetPopulationDialogProps): ReactElement => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync: lock, isPending: loadingLock } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      programSlug,
      id,
    }: {
      businessAreaSlug: string;
      programSlug: string;
      id: string;
    }) =>
      RestService.restBusinessAreasProgramsTargetPopulationsLockRetrieve({
        businessAreaSlug,
        programSlug,
        id,
      }),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          'targetPopulation',
          businessArea,
          targetPopulationId,
          programId,
        ],
      });
      showMessage(t('Payment Plan has been locked.'));
    },
    onError: (e) => showMessage(e.message),
  });

  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <>
        <DialogTitleWrapper>
          <DialogTitle>{t('Lock Target Population')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t(
              'After you lock this Target Population, the selected criteria will no longer accept new households that may get merged to Population in the future.',
            )}
          </DialogDescription>
          <DialogDescription>
            {t(
              'Note: You may duplicate the Programme Population target criteria at any time.',
            )}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              color="primary"
              variant="contained"
              loading={loadingLock}
              onClick={() => {
                lock({
                  businessAreaSlug: businessArea,
                  programSlug: programId,
                  id: targetPopulationId,
                })
                  .then(() => {
                    setOpen(false);
                    showMessage(t('Target Population Locked'));
                    navigate(
                      `/${baseUrl}/target-population/${targetPopulationId}`,
                    );
                  })
                  .catch((e) => showMessage(e.message));
              }}
              data-cy="button-target-population-modal-lock"
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
};

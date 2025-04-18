import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';
import { useBaseUrl } from '@hooks/useBaseUrl';

export interface LockFspPaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
}

export function LockFspPaymentPlan({
  paymentPlan,
  permissions,
}: LockFspPaymentPlanProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const [lockDialogOpen, setLockDialogOpen] = useState(false);
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: lock, isPending: loadingLock } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansLockFspRetrieve({
        businessAreaSlug,
        id,
        programSlug,
      }),
    onSuccess: () => {
      showMessage(t('Payment Plan FSPs are locked.'));
      setLockDialogOpen(false);
    },
  });

  const canLockFsp = hasPermissions(
    PERMISSIONS.PM_LOCK_AND_UNLOCK_FSP,
    permissions,
  );

  return (
    <>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setLockDialogOpen(true)}
          data-cy="button-lock-plan"
          disabled={!canLockFsp || !isActiveProgram}
        >
          {t('Lock FSP')}
        </Button>
      </Box>
      <Dialog
        open={lockDialogOpen}
        onClose={() => setLockDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Lock FSP')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'After you lock the FSP in this Payment Plan, you will be able to send the Payment Plan for approval.',
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLockDialogOpen(false)}>CANCEL</Button>
            <LoadingButton
              loading={loadingLock}
              type="submit"
              color="primary"
              variant="contained"
              onClick={() =>
                lock({
                  businessAreaSlug: businessArea,
                  id: paymentPlan.id,
                  programSlug: programId,
                })
              }
              data-cy="button-submit"
            >
              {t('Lock FSP')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

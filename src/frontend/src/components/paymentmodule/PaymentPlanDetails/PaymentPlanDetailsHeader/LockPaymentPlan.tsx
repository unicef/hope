import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { GreyText } from '@core/GreyText';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

export interface LockPaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
}

export function LockPaymentPlan({
  paymentPlan,
}: LockPaymentPlanProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { selectedProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const [lockDialogOpen, setLockDialogOpen] = useState(false);
  const { mutateAsync: lock, isPending: loadingLock } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programCode,
    }: {
      businessAreaSlug: string;
      id: string;
      programCode: string;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansLockRetrieve({
        businessAreaSlug,
        id,
        programCode,
      }),
    onSuccess: async () => {
      showMessage(t('Payment Plan has been locked.'));
      setLockDialogOpen(false);
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
        ),
        exact: false,
      });
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  return (
    <>
      <Box
        sx={{
          p: 2,
        }}
      >
        <Button
          color="primary"
          variant="contained"
          onClick={() => setLockDialogOpen(true)}
          data-cy="button-lock-plan"
          data-perm={PERMISSIONS.PM_LOCK_AND_UNLOCK}
        >
          {t('Lock')}
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
          <DialogTitle>{t('Lock Payment Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box
              sx={{
                p: 5,
              }}
            >
              {t(
                'After you lock this Payment Plan, you will be able to run entitlement formula for selected target population.',
              )}
            </Box>
            {paymentPlan.paymentsConflictsCount > 0 && (
              <Box
                sx={{
                  p: 5,
                }}
              >
                <GreyText>
                  {t('Note:')}{' '}
                  {paymentPlan.paymentsConflictsCount === 1
                    ? t('There is')
                    : t('There are')}{' '}
                  {paymentPlan.paymentsConflictsCount}{' '}
                  {paymentPlan.paymentsConflictsCount === 1
                    ? t(beneficiaryGroup?.groupLabel)
                    : t(beneficiaryGroup?.groupLabelPlural)}{' '}
                  {t('that will be ignored in this Payment Plan.')}
                </GreyText>
              </Box>
            )}
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
                  programCode: programId,
                })
              }
              data-cy="button-submit"
            >
              {t('Lock')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

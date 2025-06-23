import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { ErrorButton } from '@core/ErrorButton';
import { ErrorButtonContained } from '@core/ErrorButtonContained';
import { useProgramContext } from '../../programContext';

export interface DiscardVerificationPlanProps {
  paymentVerificationPlanId: string;
  cashOrPaymentPlanId: string;
}

export function DiscardVerificationPlan({
  paymentVerificationPlanId,
  cashOrPaymentPlanId,
}: DiscardVerificationPlanProps): ReactElement {
  const { t } = useTranslation();
  const [discardDialogOpen, setDiscardDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId: programSlug } = useBaseUrl();

  const discardVerificationPlanMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsDiscardVerificationPlanCreate(
        {
          businessAreaSlug: businessArea,
          id: cashOrPaymentPlanId,
          programSlug: programSlug,
          verificationPlanId: paymentVerificationPlanId,
        },
      ),
  });

  const discard = async (): Promise<void> => {
    try {
      await discardVerificationPlanMutation.mutateAsync();
      setDiscardDialogOpen(false);
      showMessage(t('Verification plan has been discarded.'));
    } catch (error) {
      showMessage(error?.message || t('Error while submitting'));
    }
  };
  return (
    <>
      <Box p={2}>
        <ErrorButton
          startIcon={<ClearIcon />}
          onClick={() => setDiscardDialogOpen(true)}
          data-cy="button-discard-plan"
          disabled={!isActiveProgram}
        >
          DISCARD
        </ErrorButton>
      </Box>
      <Dialog
        open={discardDialogOpen}
        onClose={() => setDiscardDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Discard Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                {t(
                  'Are you sure you would like to remove payment verification records',
                )}
                <br /> {t('and restart the verification process?')}
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDiscardDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
            <ErrorButtonContained
              type="submit"
              onClick={() => discard()}
              data-cy="button-submit"
            >
              {t('DISCARD')}
            </ErrorButtonContained>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

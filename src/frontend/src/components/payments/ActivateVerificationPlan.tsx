import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation } from '@tanstack/react-query';
import { useProgramContext } from '../../programContext';

export interface ActivateVerificationPlanProps {
  paymentVerificationPlanId: string;
  cashOrPaymentPlanId: string;
}

export function ActivateVerificationPlan({
  paymentVerificationPlanId,
  cashOrPaymentPlanId,
}: ActivateVerificationPlanProps): ReactElement {
  const { t } = useTranslation();
  const [activateDialogOpen, setActivateDialogOpen] = useState(false);
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId: programSlug } = useBaseUrl();
  const { showMessage } = useSnackbar();

  const activateVerificationPlanMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsActivateVerificationPlanCreate(
        {
          businessAreaSlug: businessArea,
          id: cashOrPaymentPlanId,
          programSlug: programSlug,
          verificationPlanId: paymentVerificationPlanId,
        },
      ),
  });

  const activate = async (): Promise<void> => {
    try {
      await activateVerificationPlanMutation.mutateAsync();
      setActivateDialogOpen(false);
      showMessage(t('Verification plan has been activated.'));

      // TODO: Implement proper React Query cache invalidation if needed
    } catch (error) {
      showMessage(error?.message || t('Error while submitting'));
    }
  };
  return (
    <>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setActivateDialogOpen(true)}
          data-cy="button-activate-plan"
          disabled={!isActiveProgram}
        >
          {t('ACTIVATE')}
        </Button>
      </Box>
      <Dialog
        open={activateDialogOpen}
        onClose={() => setActivateDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Activate Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'Are you sure you want to activate the Verification Plan for this Payment Plan?',
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setActivateDialogOpen(false)}>CANCEL</Button>
            <Button
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => activate()}
              data-cy="button-submit"
            >
              {t('ACTIVATE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

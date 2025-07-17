import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import ClearIcon from '@mui/icons-material/Clear';
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
import { ErrorButton } from '@core/ErrorButton';
import { ErrorButtonContained } from '@core/ErrorButtonContained';
import { useProgramContext } from '../../programContext';
import { showApiErrorMessages } from '@utils/utils';

export interface DeleteVerificationPlanProps {
  paymentVerificationPlanId: string;
  cashOrPaymentPlanId: string;
}

export function DeleteVerificationPlan({
  paymentVerificationPlanId,
  cashOrPaymentPlanId,
}: DeleteVerificationPlanProps): ReactElement {
  const { t } = useTranslation();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId: programSlug } = useBaseUrl();

  const deleteVerificationPlanMutation = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentVerificationsDeleteVerificationPlanCreate(
        {
          businessAreaSlug: businessArea,
          id: cashOrPaymentPlanId,
          programSlug: programSlug,
          verificationPlanId: paymentVerificationPlanId,
        },
      ),
  });

  const handleDeleteVerificationPlan = async (): Promise<void> => {
    try {
      await deleteVerificationPlanMutation.mutateAsync();

      setDeleteDialogOpen(false);
      showMessage(t('Verification plan has been deleted.'));
    } catch (error) {
      showApiErrorMessages(error, showMessage);
    }
  };
  return (
    <>
      <Box p={2}>
        <ErrorButton
          startIcon={<ClearIcon />}
          onClick={() => setDeleteDialogOpen(true)}
          data-cy="button-delete-plan"
          disabled={!isActiveProgram}
        >
          DELETE
        </ErrorButton>
      </Box>
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Delete Verification Plan')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                {t(
                  'Are you sure you would like to remove this verification plan?',
                )}
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>
              {t('CANCEL')}
            </Button>
            <ErrorButtonContained
              type="submit"
              onClick={() => handleDeleteVerificationPlan()}
              data-cy="button-submit"
            >
              {t('DELETE')}
            </ErrorButtonContained>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '@hooks/useSnackBar';
import { useMarkPayAsFailedMutation } from '@generated/graphql';

export interface ForceFailedButtonProps {
  paymentId: string;
  disabled?: boolean;
}
export function ForceFailedButton({
  paymentId,
  disabled = false,
}: ForceFailedButtonProps): React.ReactElement {
  const { t } = useTranslation();
  const [isOpenModal, setOpenModal] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useMarkPayAsFailedMutation();

  const submit = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentId,
        },
      });
      setOpenModal(false);
      showMessage(t('Payment has been marked as failed.'));
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Box>
      <Box p={2}>
        <Button
          color="primary"
          variant="contained"
          onClick={() => setOpenModal(true)}
          data-cy="button-mark-as-failed"
          disabled={disabled}
        >
          {t('Mark as failed')}
        </Button>
      </Box>
      <Dialog
        open={isOpenModal}
        onClose={() => setOpenModal(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
        maxWidth="md"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Mark as failed')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t('Are you sure you would like to mark payment as failed?')}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpenModal(false)}>{t('CANCEL')}</Button>
            <Button
              type="submit"
              color="primary"
              variant="contained"
              onClick={() => submit()}
              data-cy="button-submit"
              disabled={loading}
            >
              {t('Mark as failed')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </Box>
  );
}

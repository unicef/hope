import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../hooks/useSnackBar';
import { useRevertMarkPrAsFailedMutation } from '../../__generated__/graphql';

export interface RevertForceFailedButtonProps {
  paymentRecordId: string;
  disabled?: boolean;
}
export function RevertForceFailedButton({
  paymentRecordId,
  disabled = false,
}: RevertForceFailedButtonProps): React.ReactElement {
  const { t } = useTranslation();
  const [isOpenModal, setOpenModal] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useRevertMarkPrAsFailedMutation();

  const submit = async (): Promise<void> => {
    try {
      await mutate({
        variables: {
          paymentRecordId,
        },
      });
      setOpenModal(false);
      showMessage(t('Force failed has been reverted.'));
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Box>
      <Box p={2}>
        <Button
          color='primary'
          variant='contained'
          onClick={() => setOpenModal(true)}
          data-cy='button-revert-mark-as-failed'
          disabled={disabled}
        >
          {t('Revert mark as failed')}
        </Button>
      </Box>
      <Dialog
        open={isOpenModal}
        onClose={() => setOpenModal(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Revert mark as failed')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              {t(
                'Are you sure you would like to revert mark payment record as failed?',
              )}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpenModal(false)}>{t('CANCEL')}</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => submit()}
              data-cy='button-submit'
              disabled={loading}
            >
              {t('Revert mark as failed')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </Box>
  );
}

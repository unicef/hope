import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogDescription } from '../../../containers/dialogs/DialogDescription';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  RegistrationDetailedFragment,
  useRerunDedupeMutation,
} from '../../../__generated__/graphql';
import { LoadingButton } from '../../core/LoadingButton';

interface RerunDedupeProps {
  registration: RegistrationDetailedFragment;
}

export function RerunDedupe({
  registration,
}: RerunDedupeProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useRerunDedupeMutation({
    variables: { registrationDataImportDatahubId: registration.datahubId },
  });
  const rerunDedupe = async (): Promise<void> => {
    try {
      await mutate();
      showMessage('Rerunning Deduplication started');
      setOpen(false);
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };
  return (
    <span>
      <Button color='primary' variant='contained' onClick={() => setOpen(true)}>
        {t('Rerun Deduplication')}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Rerun Deduplication')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>{t('Are your sure you want to rerun deduplication?')}</div>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={loading}
              type='submit'
              color='primary'
              variant='contained'
              onClick={rerunDedupe}
            >
              {t('Rerun')}
            </LoadingButton>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}

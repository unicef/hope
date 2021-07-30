import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  RegistrationDetailedFragment,
  useRerunDedupeMutation,
} from '../../../__generated__/graphql';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

interface RerunDedupeProps {
  registration: RegistrationDetailedFragment;
}

export function RerunDedupe({
  registration,
}: RerunDedupeProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useRerunDedupeMutation({
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
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={rerunDedupe}
            >
              {t('Rerun')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}

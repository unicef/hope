import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import MergeTypeRoundedIcon from '@material-ui/icons/MergeTypeRounded';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '../../../hooks/useSnackBar';
import {
  RegistrationDetailedFragment,
  useMergeRdiMutation,
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

interface MergeRegistrationDataImportDialogProps {
  registration: RegistrationDetailedFragment;
}

export function MergeRegistrationDataImportDialog({
  registration,
}: MergeRegistrationDataImportDialogProps): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const [mutate] = useMergeRdiMutation({
    variables: { id: registration.id },
  });
  const merge = async (): Promise<void> => {
    const { errors } = await mutate();
    if (errors) {
      showMessage(t('Error while merging Registration Data Import'));
      return;
    }
    showMessage(t('Registration Data Import Merging started'));
  };
  return (
    <span>
      <Button
        startIcon={<MergeTypeRoundedIcon />}
        color='primary'
        variant='contained'
        onClick={() => setOpen(true)}
      >
        {t('Merge')}
      </Button>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>{t('Merge Import')}</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>{t('Are your sure you want to merge this data import?')}</div>
            <div>
              <strong>
                {registration.numberOfHouseholds} {t('households and')}{' '}
                {registration.numberOfIndividuals}{' '}
                {t('individuals will be merged.')}{' '}
              </strong>
              {t('Do you want to proceed?')}
            </div>
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={merge}
            >
              {t('MERGE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </span>
  );
}

import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useApproveTpMutation } from '../../../__generated__/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';

export interface ApproveCandidateListPropTypes {
  open: boolean;
  setOpen: Function;
}

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

export function ApproveCandidateList({
  open,
  setOpen,
  targetPopulationId,
}): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();

  const { showMessage } = useSnackbar();
  const [mutate] = useApproveTpMutation();
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <>
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <Typography variant='h6'>{t('Lock Target Population')}</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            {t(
              'After you lock this Target Population, the selected criteria will no longer accept new households that may get merged to Population in the future.',
            )}
          </DialogDescription>
          <DialogDescription>
            {t(
              'Note: You may duplicate the Programme Population target criteria at any time.',
            )}
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
            <Button
              color='primary'
              variant='contained'
              onClick={() => {
                mutate({
                  variables: { id: targetPopulationId },
                }).then(() => {
                  setOpen(false);
                  showMessage(t('Target Population Locked'), {
                    pathname: `/${businessArea}/target-population/${targetPopulationId}`,
                  });
                });
              }}
              data-cy='button-target-population-close'
            >
              {t('Lock')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
}

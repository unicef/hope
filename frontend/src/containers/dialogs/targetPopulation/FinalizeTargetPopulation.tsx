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
import { useFinalizeTpMutation } from '../../../__generated__/graphql';
import { Dialog } from '../Dialog';
import { DialogActions } from '../DialogActions';

export interface FinalizeTargetPopulationPropTypes {
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

export function FinalizeTargetPopulation({
  open,
  setOpen,
  totalHouseholds,
  targetPopulationId,
}): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, loading] = useFinalizeTpMutation();
  const onSubmit = (id: string): void => {
    mutate({
      variables: {
        id,
      },
    }).then(() => {
      setOpen(false);
      showMessage(t('Target Population Finalized'), {
        pathname: `/${businessArea}/target-population/${id}`,
      });
    });
  };
  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <DialogTitleWrapper>
        <DialogTitle id='scroll-dialog-title'>
          <Typography variant='h6'>{t('Send to Cash Assist')}</Typography>
        </DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          {t('Are you sure you want to push')} {totalHouseholds}{' '}
          {t(
            'households to CashAssist? Target population will not be editable further.',
          )}
        </DialogDescription>
        {/* {!totalHouseholds && <ErrorMessage>There are not any households selected in this criteria.</ErrorMessage>} */}
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
          <Button
            onClick={() => onSubmit(targetPopulationId)}
            color='primary'
            variant='contained'
            disabled={!loading || !totalHouseholds}
            data-cy='button-target-population-send-to-cash-assist'
          >
            {t('Send to cash assist')}
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
}

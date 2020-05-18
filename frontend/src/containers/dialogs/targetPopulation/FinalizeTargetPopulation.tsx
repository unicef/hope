import React from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { useFinalizeTpMutation } from '../../../__generated__/graphql';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useSnackbar } from '../../../hooks/useSnackBar';
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
}) {
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const [mutate, loading] = useFinalizeTpMutation();
  const onSubmit = (id) => {
    mutate({
      variables: {
        id,
      },
    }).then((res) => {
      setOpen(false);
      showMessage('Target Population Finalized', {
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
          <Typography variant='h6'>Send to Cash Assist</Typography>
        </DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          Are you sure you want to push {totalHouseholds} households to
          CashAssist? Target population will not be eeditable further.
        </DialogDescription>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>CANCEL</Button>
          <Button
            onClick={() => onSubmit(targetPopulationId)}
            color='primary'
            variant='contained'
            disabled={!loading}
            data-cy='button-target-population-send-to-cash-assist'
          >
            Send to cash assist
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
}

import React from 'react';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import styled from 'styled-components';
import { useApproveTpMutation } from '../../../__generated__/graphql';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { DialogActions } from '../DialogActions';
import { Dialog } from '../Dialog';

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
            <Typography variant='h6'>Lock Target Population</Typography>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            After you lock this Target Population, the selected criteria will no
            longer accept new households that may get merged to Population in
            the future.
          </DialogDescription>
          <DialogDescription>
            Note: You may duplicate the Programme Population target criteria at
            any time.
          </DialogDescription>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>CANCEL</Button>
            <Button
              color='primary'
              variant='contained'
              onClick={() => {
                mutate({
                  variables: { id: targetPopulationId },
                }).then(() => {
                  setOpen(false);
                  showMessage('Target Population Locked', {
                    pathname: `/${businessArea}/target-population/${targetPopulationId}`,
                  });
                });
              }}
              data-cy='button-target-population-close'
            >
              Lock
            </Button>
          </DialogActions>
        </DialogFooter>
      </>
    </Dialog>
  );
}
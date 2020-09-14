import React, { useState } from 'react';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useSnackbar } from '../../hooks/useSnackBar';

export interface Props {
  disabled: boolean;
  grievanceTicketsNumber: number;
}
export function CreateGrievanceTickets({
  disabled,
  grievanceTicketsNumber,
}: Props): React.ReactElement {
  const [DialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const DialogTitleWrapper = styled.div`
    border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  `;

  const DialogFooter = styled.div`
    padding: 12px 16px;
    margin: 0;
    border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
    text-align: right;
  `;

  const DialogContainer = styled.div`
    width: 700px;
  `;

  const createGrievanceTickets = () => {
    console.log('create');
    setDialogOpen(false);
  };

  return (
    <>
      <Button
        color='primary'
        disabled={disabled}
        onClick={() => setDialogOpen(true)}
        data-cy='button-ed-plan'
      >
        CREATE GRIEVANCE TICKETS
      </Button>
      <Dialog
        open={DialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Create Grievance Tickets
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                You will generate {grievanceTicketsNumber} grievance ticket
                {grievanceTicketsNumber === 1 ? null : 's'}. Are you sure you
                want to continue?
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => createGrievanceTickets()}
              data-cy='button-submit'
            >
              Continue
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

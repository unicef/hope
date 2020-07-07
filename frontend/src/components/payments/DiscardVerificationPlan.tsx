import React, { useState } from 'react';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import CheckRoundedIcon from '@material-ui/icons/CheckRounded';
import styled from 'styled-components';
import ClearIcon from '@material-ui/icons/Clear';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';

export function DiscardVerificationPlan(): React.ReactElement {
  const [finishDialogOpen, setFinishDialogOpen] = useState(false);

  // const submit = async (): Promise<void> => {
  //   // const { errors } = await mutate();
  //   const errors = [];
  //   if (errors) {
  //     showMessage('Error while submitting');
  //     return;
  //   }
  //   showMessage('New verification plan created.');
  // };
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

  return (
    <>
      <Box p={2}>
        <Button
          color='secondary'
          startIcon={<ClearIcon />}
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-discard-plan'
        >
          DISCARD
        </Button>
      </Box>
      <Dialog
        open={finishDialogOpen}
        onClose={() => setFinishDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Discard Verification Plan
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                Payment verification for households who have responded will not
                be visible
              </div>
              <div>or valid anymore. Are you sure?</div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='secondary'
              variant='contained'
              onClick={() => console.log('discard')}
              data-cy='button-submit'
            >
              DISCARD
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

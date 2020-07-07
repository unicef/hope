import React, { useState } from 'react';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import CheckRoundedIcon from '@material-ui/icons/CheckRounded';
import styled from 'styled-components';

import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';

export function FinishVerificationPlan(): React.ReactElement {
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
          color='primary'
          variant='contained'
          onClick={() => setFinishDialogOpen(true)}
          data-cy='button-ed-plan'
        >
          Finish
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
            Finish Verification Plan
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box p={5}>
              <div>
                Only 43% of the beneficiaries have responded to this payment
                verification.
              </div>
              <div>Are you sure that you want to finish?</div>
              <div>
                Closing this verification will generate 43 grievance tickets.
              </div>
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setFinishDialogOpen(false)}>CANCEL</Button>
            <Button
              startIcon={<CheckRoundedIcon />}
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => console.log('activate')}
              data-cy='button-submit'
            >
              FINISH
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

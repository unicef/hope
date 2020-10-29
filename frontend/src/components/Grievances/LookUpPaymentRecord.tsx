import React, { useState } from 'react';
import SearchIcon from '@material-ui/icons/Search';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
import { LookUpPaymentRecordTable } from './LookUpPaymentRecordTable/LookUpPaymentRecordTable';

const LookUp = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  border: 1.5px solid #043e91;
  border-radius: 5px;
  color: #033f91;
  font-size: 16px;
  text-align: center;
  padding: 25px;
  font-weight: 500;
  cursor: pointer;
`;
const MarginRightSpan = styled.span`
  margin-right: 5px;
`;
const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;
const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const LookUpPaymentRecord = (): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      <LookUp onClick={() => setLookUpDialogOpen(true)}>
        <MarginRightSpan>
          <SearchIcon />
        </MarginRightSpan>
        <span>Look up Payment Record</span>
      </LookUp>
      <Dialog
        maxWidth='lg'
        fullWidth
        open={lookUpDialogOpen}
        onClose={() => setLookUpDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Look up Payment Record
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <LookUpPaymentRecordTable cashPlanId='Q2FzaFBsYW5Ob2RlOmUwNzUzNWE1LWEzZGMtNDVjZi05MzVhLWQzNWJmZmY0YTFlZQ==' />
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLookUpDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => null}
              data-cy='button-submit'
            >
              SAVE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};

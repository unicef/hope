import React, { useState } from 'react';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@material-ui/core';
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

interface GoldenRecordResultsProps {
  registration: RegistrationDetailedFragment;
}

export function GoldenRecordResults({
  registration,
}: GoldenRecordResultsProps): React.ReactElement {
  const [open, setOpen] = useState(false);

  return (
    <Dialog
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <DialogTitleWrapper>
        <DialogTitle id='scroll-dialog-title'>GoldenRecordResults</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          <div>GoldenRecordResults</div>
        </DialogDescription>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>CLOSE</Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
}

import { Button } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import { DialogActions } from '../../containers/dialogs/DialogActions';

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

export const PhotoModalFooter = ({
  setTurnAngle,
  setDialogOpen,
}: {
  setTurnAngle: React.Dispatch<React.SetStateAction<number>>;
  setDialogOpen: React.Dispatch<React.SetStateAction<boolean>>;
}): React.ReactElement => {
  return (
    <DialogFooter>
      <DialogActions>
        <Button
          onClick={() => {
            setDialogOpen(false);
            setTurnAngle(90);
          }}
        >
          CANCEL
        </Button>
      </DialogActions>
    </DialogFooter>
  );
};

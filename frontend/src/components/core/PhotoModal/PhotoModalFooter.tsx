import { Button } from '@material-ui/core';
import React from 'react';
import { DialogActions } from '../../../containers/dialogs/DialogActions';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';

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
          data-cy='button-cancel'
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

import { Button } from '@mui/material';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { Dispatch, SetStateAction, ReactElement } from 'react';

export function PhotoModalFooter({
  setTurnAngle,
  setDialogOpen,
}: {
  setTurnAngle: Dispatch<SetStateAction<number>>;
  setDialogOpen: Dispatch<SetStateAction<boolean>>;
}): ReactElement {
  return (
    <DialogFooter>
      <DialogActions>
        <Button
          data-cy="button-cancel"
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
}

import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

export function ButtonDialog({
  message,
  buttonText,
  closeButtonText = 'dismiss',
  title = 'Error',
}: {
  message: string;
  title?: string;
  buttonText: string;
  closeButtonText?: string;
}): React.ReactElement {
  const [open, setOpen] = React.useState(false);

  const handleClose = (): void => {
    setOpen(false);
  };

  return (
    <>
      <Button color="primary" variant="contained" onClick={() => setOpen(true)}>
        {buttonText}
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{title}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary" autoFocus>
            {closeButtonText}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

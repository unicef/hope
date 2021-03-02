import React from 'react';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';

export function ButtonDialog({
  message,
  buttonText,
  closeButtonText = 'dismiss',
  title= "Error"
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
      <Button color='primary' variant='contained' onClick={() => setOpen(true)}>
        {buttonText}
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby='alert-dialog-title'
        aria-describedby='alert-dialog-description'
      >
        <DialogTitle id='alert-dialog-title'>{title}</DialogTitle>
        <DialogContent>
          <DialogContentText id='alert-dialog-description'>
            {message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color='primary' autoFocus>
            {closeButtonText}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

export function AlertDialog({
  message,
  show,
}: {
  message: string;
  show: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = React.useState(false);
  const [oldShow, setOldShow] = React.useState(false);
  useEffect(() => {
    if (!oldShow && show) {
      setOpen(true);
    }
    setOldShow(show);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [show]);

  const handleClose = (): void => {
    setOpen(false);
  };

  return (
    <div>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby='alert-dialog-title'
        aria-describedby='alert-dialog-description'
      >
        <DialogTitle id='alert-dialog-title'>{t('Error')}</DialogTitle>
        <DialogContent>
          <DialogContentText id='alert-dialog-description'>
            {message}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color='primary' autoFocus>
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@material-ui/core';
import React, { FC } from 'react';
import { useTranslation } from 'react-i18next';
import { DialogFooter } from '../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../containers/dialogs/DialogTitleWrapper';

export interface ConfirmationDialogOptions {
  catchOnCancel?: boolean;
  title?: string;
  content?: string | React.ReactElement;
  continueText?: string;
  extraContent?: string;
  disabled?: boolean;
}

export interface ConfirmationDialogProps extends ConfirmationDialogOptions {
  open: boolean;
  onSubmit: () => void;
  onClose: () => void;
}

export const ConfirmationDialog: FC<ConfirmationDialogProps> = ({
  open,
  title,
  content,
  continueText,
  extraContent,
  onSubmit,
  onClose,
  disabled = false,
}) => {
  const { t } = useTranslation();

  return (
    <Dialog fullWidth scroll='paper' open={open}>
      <DialogTitleWrapper>
        <DialogTitle id='scroll-dialog-title'>
          {title || t('Confirmation')}
        </DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        {extraContent ? (
          <Typography variant='body2' style={{ paddingBottom: '16px' }}>
            {extraContent}
          </Typography>
        ) : null}
        <Typography variant='body2'>{content}</Typography>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button color='primary' onClick={onClose} autoFocus>
            {t('Cancel')}
          </Button>
          <Button
            variant='contained'
            color='primary'
            disabled={disabled}
            onClick={onSubmit}
          >
            {continueText || t('Continue')}
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};

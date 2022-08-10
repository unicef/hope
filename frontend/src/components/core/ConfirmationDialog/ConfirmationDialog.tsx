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
  content?: string;
  continueText?: string;
  extraContent?: string;
  warningContent?: string | null;
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
  warningContent,
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
        <Typography variant='body2' gutterBottom={!!warningContent}>{content}</Typography>
        {warningContent ? (
          <Typography color='primary' variant='body2' style={{ paddingBottom: '16px', fontWeight: 'bold' }}>
            {warningContent}
          </Typography>
        ) : null}
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

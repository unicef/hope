import React, { FC, ReactElement } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';

export interface ConfirmationDialogOptions {
  catchOnCancel?: boolean;
  title?: string;
  content?: string | ReactElement;
  continueText?: string;
  extraContent?: React.ReactNode;
  warningContent?: string | null;
  disabled?: boolean;
  type?: 'error' | 'primary';
}

export interface ConfirmationDialogProps extends ConfirmationDialogOptions {
  open: boolean;
  onSubmit: () => void;
  onClose: () => void;
  type?: 'error' | 'primary';
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
  type = 'primary',
}) => {
  const { t } = useTranslation();

  return (
    <Dialog fullWidth scroll="paper" open={open}>
      <DialogTitleWrapper>
        <DialogTitle>{title || t('Confirmation')}</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        {extraContent ? (
          <Typography variant="body2" style={{ marginBottom: '16px' }}>
            {extraContent}
          </Typography>
        ) : null}
        <Typography
          variant="body2"
          style={{ marginBottom: warningContent ? '16px' : 'inherit' }}
        >
          {content}
        </Typography>
        {warningContent ? (
          <Typography
            color="primary"
            variant="body2"
            style={{ fontWeight: 'bold' }}
          >
            {warningContent}
          </Typography>
        ) : null}
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button
            data-cy="button-cancel"
            color="primary"
            onClick={onClose}
            autoFocus
          >
            {t('Cancel')}
          </Button>
          <Button
            variant="contained"
            color={type}
            disabled={disabled}
            onClick={onSubmit}
            data-cy="button-confirm"
          >
            {continueText || t('Continue')}
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};

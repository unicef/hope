import React, { FC } from 'react';
import styled from 'styled-components';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from '@material-ui/core';
import { useTranslation } from 'react-i18next';

export const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

export const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

export interface ConfirmationDialogOptions {
  catchOnCancel?: boolean;
  title?: string;
  content?: string;
  continueText?: string;
  extraContent?: string;
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
          <Button variant='contained' color='primary' onClick={onSubmit}>
            {continueText || t('Continue')}
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};

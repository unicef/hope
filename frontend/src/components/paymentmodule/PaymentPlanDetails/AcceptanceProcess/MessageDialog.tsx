import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import MessageIcon from '@material-ui/icons/Message';
import styled from 'styled-components';
import { Dialog } from '../../../../containers/dialogs/Dialog';
import { DialogActions } from '../../../../containers/dialogs/DialogActions';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const GreyText = styled.div`
  color: #9e9e9e;
`;

const MessageIconContainer = styled(Box)`
  position: relative;
  top: 4px;
  font-size: 16px;
  color: #043f91;
`;

export interface MessageDialogProps {
  message: string;
  author: string;
  date: string;
}
export function MessageDialog({
  message,
  author,
  date,
}: MessageDialogProps): React.ReactElement {
  const { t } = useTranslation();
  const [MessageDialogOpen, setMessageDialogOpen] = useState(false);
  return (
    <>
      <Box p={2}>
        <IconButton size='small' onClick={() => setMessageDialogOpen(true)}>
          <MessageIconContainer>
            <MessageIcon fontSize='inherit' />
          </MessageIconContainer>
        </IconButton>
      </Box>
      <Dialog
        open={MessageDialogOpen}
        onClose={() => setMessageDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>{t('Comment')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box display='flex' flexDirection='column'>
            <Box display='flex'>
              {author}{' '}
              <GreyText>
                <Box ml={1}>on {date}</Box>
              </GreyText>
            </Box>
            {message}
          </Box>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => setMessageDialogOpen(false)}
            >
              {t('Close')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}

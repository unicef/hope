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
import { UserNode } from '../../__generated__/graphql';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { renderUserName } from '../../utils/utils';
import { UniversalMoment } from '../../components/core/UniversalMoment';
import { DividerLine } from '../../components/core/DividerLine';
import { DialogActions } from '../../containers/dialogs/DialogActions';

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
  comment: string;
  author: Pick<UserNode, 'id' | 'email' | 'firstName' | 'lastName'>;
  date: string;
}
export const MessageDialog = ({
  comment,
  author,
  date,
}: MessageDialogProps): React.ReactElement => {
  const { t } = useTranslation();
  const [MessageDialogOpen, setMessageDialogOpen] = useState(false);
  return (
    <>
      <IconButton size='small' onClick={() => setMessageDialogOpen(true)}>
        <MessageIconContainer>
          <MessageIcon fontSize='inherit' />
        </MessageIconContainer>
      </IconButton>
      <Dialog
        open={MessageDialogOpen}
        onClose={() => setMessageDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Comment')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogContainer>
            <Box display='flex' flexDirection='column'>
              <Box mt={2} display='flex'>
                {renderUserName(author)}{' '}
                <GreyText>
                  <Box ml={1}>
                    on <UniversalMoment>{date}</UniversalMoment>
                  </Box>
                </GreyText>
              </Box>
              <DividerLine />
              {comment}
            </Box>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
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
};

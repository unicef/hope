import React, { useState } from 'react';
import styled from 'styled-components';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { BlackLink } from '../BlackLink';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const StyledImage = styled.img`
  max-width: 100%;
  max-height: 100%;
`;

interface DocumentPhotoModalProps {
  photo: string;
  documentId: string;
}

export const DocumentPhotoModal = ({
  photo,
  documentId,
}: DocumentPhotoModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <BlackLink
        onClick={() => {
          setDialogOpen(true);
        }}
      >
        {documentId}
      </BlackLink>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            Document&apos;s Photo
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box p={3}>
            <StyledImage alt='document' src={photo} />
          </Box>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};

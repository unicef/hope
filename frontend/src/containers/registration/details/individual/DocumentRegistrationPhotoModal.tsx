import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { Button, DialogContent, DialogTitle, Box } from '@material-ui/core';
import {
  ImportedIndividualDetailedFragment,
  useImportedIndividualPhotosLazyQuery,
} from '../../../../__generated__/graphql';
import { Dialog } from '../../../dialogs/Dialog';
import { DialogActions } from '../../../dialogs/DialogActions';

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

export const StyledLink = styled(Link)`
  color: #000;
`;

interface DocumentRegistrationPhotoModalProps {
  individual: ImportedIndividualDetailedFragment;
  documentNumber: string;
  documentId: string;
}

export const DocumentRegistrationPhotoModal = ({
  individual,
  documentNumber,
  documentId,
}: DocumentRegistrationPhotoModalProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [getPhotos, { data }] = useImportedIndividualPhotosLazyQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });
  const documentWithPhoto = data?.importedIndividual?.documents?.edges?.find(
    (el) => el.node.id === documentId,
  );

  return (
    <>
      <StyledLink
        onClick={() => {
          setDialogOpen(true);
          getPhotos();
        }}
      >
        {documentNumber}
      </StyledLink>
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
            <StyledImage alt='document' src={documentWithPhoto?.node?.photo} />
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

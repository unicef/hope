import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import {
  DialogFooter,
  DialogTitleWrapper,
  StyledImage,
  StyledLink,
} from '../../../../components/population/IndividualFlexFieldPhotoModal';
import {
  ImportedIndividualDetailedFragment,
  useImportedIndividualPhotosLazyQuery,
} from '../../../../__generated__/graphql';
import { Dialog } from '../../../dialogs/Dialog';
import { DialogActions } from '../../../dialogs/DialogActions';

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

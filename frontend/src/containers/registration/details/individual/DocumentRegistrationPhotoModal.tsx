import { Box, Button, DialogContent } from '@material-ui/core';
import React, { useState } from 'react';
import { PhotoModalHeader } from '../../../../components/PhotoModal/PhotoModalHeader';
import {
  DialogFooter,
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
  const [turnAngle, setTurnAngle] = useState(90);
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
        <PhotoModalHeader
          turnAngle={turnAngle}
          setTurnAngle={setTurnAngle}
          title="Document's Photo"
        />
        <DialogContent>
          <Box p={3}>
            <StyledImage
              id='modalImg'
              alt='document'
              src={documentWithPhoto?.node?.photo}
            />
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

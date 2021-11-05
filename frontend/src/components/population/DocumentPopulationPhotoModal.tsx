import { Box, Button, DialogContent } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  IndividualNode,
  useIndividualPhotosLazyQuery,
} from '../../__generated__/graphql';
import { PhotoModalHeader } from '../PhotoModal/PhotoModalHeader';
import {
  DialogFooter,
  StyledImage,
  StyledLink,
} from './IndividualFlexFieldPhotoModal';

interface DocumentPopulationPhotoModalProps {
  individual: IndividualNode;
  documentNumber: string;
  documentId: string;
}

export const DocumentPopulationPhotoModal = ({
  individual,
  documentNumber,
  documentId,
}: DocumentPopulationPhotoModalProps): React.ReactElement => {
  const [turnAngle, setTurnAngle] = useState(90);
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [getPhotos, { data }] = useIndividualPhotosLazyQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });
  const documentWithPhoto = data?.individual?.documents?.edges?.find(
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
            <Button onClick={() => setDialogOpen(false)}>{t('CANCEL')}</Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};

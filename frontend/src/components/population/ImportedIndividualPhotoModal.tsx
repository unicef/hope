import { Box, Button, DialogContent } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  ImportedIndividualNode,
  useImportedIndividualPhotosLazyQuery,
} from '../../__generated__/graphql';
import { PhotoModalHeader } from '../PhotoModal/PhotoModalHeader';
import { DialogFooter, StyledImage } from './IndividualFlexFieldPhotoModal';

interface ImportedIndividualPhotoModalProps {
  individual: ImportedIndividualNode;
}

export const ImportedIndividualPhotoModal = ({
  individual,
}: ImportedIndividualPhotoModalProps): React.ReactElement => {
  const { t } = useTranslation();
  const [turnAngle, setTurnAngle] = useState(90);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [getPhotos, { data }] = useImportedIndividualPhotosLazyQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });

  return (
    <>
      <Button
        color='primary'
        variant='outlined'
        onClick={() => {
          setDialogOpen(true);
          getPhotos();
        }}
      >
        {t('Show Photo')}
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        aria-labelledby='form-dialog-title'
      >
        <PhotoModalHeader turnAngle={turnAngle} setTurnAngle={setTurnAngle} />
        <DialogContent>
          <Box p={3}>
            <StyledImage
              id='modalImg'
              alt={t('Individual')}
              src={data?.importedIndividual?.photo}
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

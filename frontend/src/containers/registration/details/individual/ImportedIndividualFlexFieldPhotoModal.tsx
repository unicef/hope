import { Box, Button, DialogContent } from '@material-ui/core';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { PhotoModalHeader } from '../../../../components/PhotoModal/PhotoModalHeader';
import {
  DialogFooter,
  MiniImage,
  StyledImage,
} from '../../../../components/population/IndividualFlexFieldPhotoModal';
import { useImportedIndividualFlexFieldsQuery } from '../../../../__generated__/graphql';
import { Dialog } from '../../../dialogs/Dialog';
import { DialogActions } from '../../../dialogs/DialogActions';

export const ImportedIndividualFlexFieldPhotoModal = ({
  field,
}): React.ReactElement => {
  const { id } = useParams();
  const [turnAngle, setTurnAngle] = useState(90);
  const { data } = useImportedIndividualFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const [dialogOpen, setDialogOpen] = useState(false);

  if (!data) {
    return null;
  }

  const { flexFields } = data.importedIndividual;
  const picUrl = flexFields[field.name];

  return (
    <>
      <MiniImage alt='photo' src={picUrl} onClick={() => setDialogOpen(true)} />
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        aria-labelledby='form-dialog-title'
      >
        <PhotoModalHeader turnAngle={turnAngle} setTurnAngle={setTurnAngle} />
        <DialogContent>
          <Box p={3}>
            <StyledImage id='modalImg' alt='photo' src={picUrl} />
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

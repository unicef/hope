import { Box, Button, DialogContent } from '@material-ui/core';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useHouseholdFlexFieldsQuery } from '../../__generated__/graphql';
import { PhotoModalHeader } from '../PhotoModal/PhotoModalHeader';
import {
  DialogFooter,
  MiniImage,
  StyledImage,
} from './IndividualFlexFieldPhotoModal';

export const HouseholdFlexFieldPhotoModal = ({ field }): React.ReactElement => {
  const { id } = useParams();
  const [turnAngle, setTurnAngle] = useState(90);
  const { data } = useHouseholdFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const [dialogOpen, setDialogOpen] = useState(false);

  if (!data) {
    return null;
  }

  const { flexFields } = data.household;
  const picUrl = flexFields[field.name];

  return picUrl ? (
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
  ) : (
    <Box display='flex' alignItems='center'>
      -
    </Box>
  );
};

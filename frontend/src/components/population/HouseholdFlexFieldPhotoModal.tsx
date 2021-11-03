import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useHouseholdFlexFieldsQuery } from '../../__generated__/graphql';
import {
  DialogFooter,
  DialogTitleWrapper,
  MiniImage,
  StyledImage,
} from './IndividualFlexFieldPhotoModal';

export const HouseholdFlexFieldPhotoModal = ({ field }): React.ReactElement => {
  const { id } = useParams();
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
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>Photo</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box p={3}>
            <StyledImage alt='photo' src={picUrl} />
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

import { Box, Button, DialogContent } from '@material-ui/core';
import React, { useState } from 'react';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  AllEditHouseholdFieldsQuery,
  useHouseholdFlexFieldsQuery,
} from '../../__generated__/graphql';
import { PhotoModalHeader } from '../PhotoModal/PhotoModalHeader';
import {
  DialogFooter,
  MiniImage,
  StyledImage,
} from '../population/IndividualFlexFieldPhotoModal';

export interface GrievanceFlexFieldPhotoModalNewHouseholdProps {
  flexField: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  householdId: string;
}

export const GrievanceFlexFieldPhotoModalNewHousehold = ({
  flexField,
  householdId,
}: GrievanceFlexFieldPhotoModalNewHouseholdProps): React.ReactElement => {
  const [turnAngle, setTurnAngle] = useState(90);
  const { data } = useHouseholdFlexFieldsQuery({
    variables: { id: householdId },
    fetchPolicy: 'network-only',
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  if (!data) {
    return null;
  }

  const { flexFields } = data.household;

  const picUrl: string = flexFields[flexField.name];

  return (
    <Box style={{ height: '100%' }} display='flex' alignItems='center'>
      {picUrl ? (
        <>
          <MiniImage
            alt='photo'
            src={picUrl}
            onClick={() => setDialogOpen(true)}
          />
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            aria-labelledby='form-dialog-title'
          >
            <PhotoModalHeader
              turnAngle={turnAngle}
              setTurnAngle={setTurnAngle}
            />
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
        <Box style={{ height: '100%' }} display='flex' alignItems='center'>
          -
        </Box>
      )}
    </Box>
  );
};

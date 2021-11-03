import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  AllAddIndividualFieldsQuery,
  useIndividualFlexFieldsQuery,
} from '../../__generated__/graphql';
import {
  DialogFooter,
  DialogTitleWrapper,
  MiniImage,
  StyledImage,
} from '../population/IndividualFlexFieldPhotoModal';

export interface GrievanceFlexFieldPhotoModalNewIndividualProps {
  flexField: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  individualId: string;
}

export const GrievanceFlexFieldPhotoModalNewIndividual = ({
  flexField,
  individualId,
}: GrievanceFlexFieldPhotoModalNewIndividualProps): React.ReactElement => {
  const { data } = useIndividualFlexFieldsQuery({
    variables: { id: individualId },
    fetchPolicy: 'network-only',
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  if (!data) {
    return null;
  }

  const { flexFields } = data.individual;

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
        <Box style={{ height: '100%' }} display='flex' alignItems='center'>
          -
        </Box>
      )}
    </Box>
  );
};

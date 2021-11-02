import { Box, Button, DialogContent, DialogTitle } from '@material-ui/core';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import {
  AllAddIndividualFieldsQuery,
  useGrievanceTicketFlexFieldsQuery,
} from '../../__generated__/graphql';
import {
  DialogFooter,
  DialogTitleWrapper,
  MiniImage,
  StyledImage,
} from '../population/IndividualFlexFieldPhotoModal';

export interface GrievanceFlexFieldPhotoModalProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  isCurrent?: boolean;
  isIndividual?: boolean;
}

export const GrievanceFlexFieldPhotoModal = ({
  field,
  isCurrent,
  isIndividual,
}: GrievanceFlexFieldPhotoModalProps): React.ReactElement => {
  const { id } = useParams();
  const { data } = useGrievanceTicketFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  if (!data) {
    return null;
  }

  const flexFields = isIndividual
    ? data.grievanceTicket?.individualDataUpdateTicketDetails?.individualData
        ?.flex_fields
    : data.grievanceTicket?.householdDataUpdateTicketDetails?.householdData
        ?.flex_fields;

  const picUrl: string = isCurrent
    ? flexFields[field.name]?.previous_value
    : flexFields[field.name]?.value;
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
    <Box style={{ height: '100%' }} display='flex' alignItems='center'>
      -
    </Box>
  );
};

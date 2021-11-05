import { Box, Button, DialogContent, IconButton } from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { FormikFileField } from '../../shared/Formik/FormikFileField';
import {
  AllAddIndividualFieldsQuery,
  useGrievanceTicketFlexFieldsQuery,
} from '../../__generated__/graphql';
import { PhotoModalHeader } from '../PhotoModal/PhotoModalHeader';
import {
  DialogFooter,
  MiniImage,
  StyledImage,
} from '../population/IndividualFlexFieldPhotoModal';

export interface GrievanceFlexFieldPhotoModalEditableProps {
  flexField: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  isCurrent?: boolean;
  isIndividual?: boolean;
  field;
  form;
}

export const GrievanceFlexFieldPhotoModalEditable = ({
  isCurrent,
  isIndividual,
  field,
  form,
  flexField,
}: GrievanceFlexFieldPhotoModalEditableProps): React.ReactElement => {
  const [isEdited, setEdit] = useState(false);
  const [turnAngle, setTurnAngle] = useState(90);
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
    ? flexFields[flexField.name]?.previous_value
    : flexFields[flexField.name]?.value;

  return (
    <Box style={{ height: '100%' }} display='flex' alignItems='center'>
      {isEdited || !picUrl ? (
        <Box style={{ height: '100%' }} display='flex' alignItems='center'>
          <FormikFileField field={field} form={form} />
        </Box>
      ) : (
        <>
          <Box display='flex' alignItems='center'>
            <MiniImage
              alt='photo'
              src={picUrl}
              onClick={() => setDialogOpen(true)}
            />
            <IconButton onClick={() => setEdit(true)}>
              <CloseIcon />
            </IconButton>
          </Box>
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
      )}
    </Box>
  );
};

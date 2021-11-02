import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@material-ui/core';
import CloseIcon from '@material-ui/icons/Close';
import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { FormikFileField } from '../../shared/Formik/FormikFileField';
import {
  AllAddIndividualFieldsQuery,
  useGrievanceTicketFlexFieldsQuery,
} from '../../__generated__/graphql';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const StyledImage = styled.img`
  max-width: 100%;
  max-height: 100%;
`;

const MiniImage = styled.img`
  height: 45px;
  width: 45px;
  cursor: pointer;
`;

export const StyledLink = styled(Link)`
  color: #000;
`;

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
      )}
    </Box>
  );
};

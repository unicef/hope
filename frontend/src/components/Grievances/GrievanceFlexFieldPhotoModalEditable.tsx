import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { FormikFileField } from '../../shared/Formik/FormikFileField';
import {
  AllAddIndividualFieldsQuery,
  useGrievanceTicketFlexFieldsQuery,
} from '../../__generated__/graphql';
import { PhotoModal } from '../PhotoModal/PhotoModal';

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
        <PhotoModal
          src={picUrl}
          variant='pictureClose'
          closeHandler={() => setEdit(true)}
        />
      )}
    </Box>
  );
};

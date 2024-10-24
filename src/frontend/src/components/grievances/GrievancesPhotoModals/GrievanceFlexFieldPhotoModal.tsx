import { Box } from '@mui/material';
import * as React from 'react';
import { useParams } from 'react-router-dom';
import {
  AllAddIndividualFieldsQuery,
  useGrievanceTicketFlexFieldsQuery,
} from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';

export interface GrievanceFlexFieldPhotoModalProps {
  field: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  isCurrent?: boolean;
  isIndividual?: boolean;
}

export function GrievanceFlexFieldPhotoModal({
  field,
  isCurrent,
  isIndividual,
}: GrievanceFlexFieldPhotoModalProps): React.ReactElement {
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
    ? flexFields[field.name]?.previous_value
    : flexFields[field.name]?.value;
  return picUrl ? (
    <PhotoModal src={picUrl} />
  ) : (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      -
    </Box>
  );
}

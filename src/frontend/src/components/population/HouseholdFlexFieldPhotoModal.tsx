import { Box } from '@mui/material';
import * as React from 'react';
import { useParams } from 'react-router-dom';
import { useHouseholdFlexFieldsQuery } from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';

export function HouseholdFlexFieldPhotoModal({ field }): React.ReactElement {
  const { id } = useParams();
  const { data } = useHouseholdFlexFieldsQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  if (!data) {
    return null;
  }

  const { flexFields } = data.household;
  const picUrl = flexFields[field.name];

  return picUrl ? (
    <PhotoModal src={picUrl} />
  ) : (
    <Box display="flex" alignItems="center">
      -
    </Box>
  );
}

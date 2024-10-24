import { Box } from '@mui/material';
import * as React from 'react';
import {
  AllAddIndividualFieldsQuery,
  useIndividualFlexFieldsQuery,
} from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';

export interface GrievanceFlexFieldPhotoModalNewIndividualProps {
  flexField: AllAddIndividualFieldsQuery['allAddIndividualsFieldsAttributes'][number];
  individualId: string;
}

export function GrievanceFlexFieldPhotoModalNewIndividual({
  flexField,
  individualId,
}: GrievanceFlexFieldPhotoModalNewIndividualProps): React.ReactElement {
  const { data } = useIndividualFlexFieldsQuery({
    variables: { id: individualId },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }

  const { flexFields } = data.individual;

  const picUrl: string = flexFields[flexField.name];

  return (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      {picUrl ? (
        <PhotoModal src={picUrl} />
      ) : (
        <Box style={{ height: '100%' }} display="flex" alignItems="center">
          -
        </Box>
      )}
    </Box>
  );
}

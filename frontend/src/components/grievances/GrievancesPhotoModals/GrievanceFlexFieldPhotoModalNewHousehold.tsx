import { Box } from '@mui/material';
import React from 'react';
import {
  AllEditHouseholdFieldsQuery,
  useHouseholdFlexFieldsQuery,
} from '../../../__generated__/graphql';
import { PhotoModal } from '../../core/PhotoModal/PhotoModal';

export interface GrievanceFlexFieldPhotoModalNewHouseholdProps {
  flexField: AllEditHouseholdFieldsQuery['allEditHouseholdFieldsAttributes'][number];
  householdId: string;
}

export const GrievanceFlexFieldPhotoModalNewHousehold = ({
  flexField,
  householdId,
}: GrievanceFlexFieldPhotoModalNewHouseholdProps): React.ReactElement => {
  const { data } = useHouseholdFlexFieldsQuery({
    variables: { id: householdId },
    fetchPolicy: 'network-only',
  });
  if (!data) {
    return null;
  }

  const { flexFields } = data.household;

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
};

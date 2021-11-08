import { Box } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import { useHouseholdFlexFieldsQuery } from '../../__generated__/graphql';
import { PhotoModal } from '../PhotoModal/PhotoModal';

export const HouseholdFlexFieldPhotoModal = ({ field }): React.ReactElement => {
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
    <Box display='flex' alignItems='center'>
      -
    </Box>
  );
};

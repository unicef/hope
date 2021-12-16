import React from 'react';
import {
  IndividualNode,
  useIndividualPhotosQuery,
} from '../../__generated__/graphql';
import { PhotoModal } from '../PhotoModal/PhotoModal';

interface IndividualPhotoModalProps {
  individual: IndividualNode;
}

export const IndividualPhotoModal = ({
  individual,
}: IndividualPhotoModalProps): React.ReactElement => {
  const { data } = useIndividualPhotosQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });

  return (
    <PhotoModal
      src={data?.individual?.photo}
      variant='button'
      title="Individuals's Photo"
    />
  );
};

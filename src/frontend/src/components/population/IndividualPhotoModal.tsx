import * as React from 'react';
import { IndividualNode, useIndividualPhotosQuery } from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';

interface IndividualPhotoModalProps {
  individual: IndividualNode;
}

export function IndividualPhotoModal({
  individual,
}: IndividualPhotoModalProps): React.ReactElement {
  const { data } = useIndividualPhotosQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });

  return (
    <PhotoModal
      src={data?.individual?.photo}
      variant="button"
      title="Individuals's Photo"
    />
  );
}

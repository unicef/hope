import { IndividualNode, useIndividualPhotosQuery } from '@generated/graphql';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';

interface IndividualPhotoModalProps {
  individual: IndividualNode;
}

export function IndividualPhotoModal({
  individual,
}: IndividualPhotoModalProps): ReactElement {
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

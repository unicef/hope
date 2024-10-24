import * as React from 'react';
import { IndividualNode, useIndividualPhotosQuery } from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';

interface DocumentPopulationPhotoModalProps {
  individual: IndividualNode;
  documentNumber: string;
  documentId: string;
}

export function DocumentPopulationPhotoModal({
  individual,
  documentNumber,
  documentId,
}: DocumentPopulationPhotoModalProps): React.ReactElement {
  const { data } = useIndividualPhotosQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });
  const documentWithPhoto = data?.individual?.documents?.edges?.find(
    (el) => el.node.id === documentId,
  );

  return (
    <PhotoModal
      src={documentWithPhoto?.node?.photo}
      linkText={documentNumber}
      variant="link"
      title="Document's Photo"
    />
  );
}

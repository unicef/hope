import { useIndividualPhotosQuery } from '@generated/graphql';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

interface DocumentPopulationPhotoModalProps {
  individual: IndividualDetail;
  documentNumber: string;
  documentId: string;
}

export function DocumentPopulationPhotoModal({
  individual,
  documentNumber,
  documentId,
}: DocumentPopulationPhotoModalProps): ReactElement {
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

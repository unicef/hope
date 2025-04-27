import PhotoModal from '@core/PhotoModal/PhotoModal';
import { useIndividualPhotosQuery } from '@generated/graphql';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { ReactElement } from 'react';

interface DocumentRegistrationPhotoModalProps {
  individual: IndividualDetail;
  documentNumber: string;
  documentId: string;
}

export function DocumentRegistrationPhotoModal({
  individual,
  documentNumber,
  documentId,
}: DocumentRegistrationPhotoModalProps): ReactElement {
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

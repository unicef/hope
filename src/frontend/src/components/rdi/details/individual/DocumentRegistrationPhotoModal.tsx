import PhotoModal from '@core/PhotoModal/PhotoModal';
import {
  IndividualDetailedFragment,
  useIndividualPhotosQuery,
} from '@generated/graphql';
import { ReactElement } from 'react';

interface DocumentRegistrationPhotoModalProps {
  individual: IndividualDetailedFragment;
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

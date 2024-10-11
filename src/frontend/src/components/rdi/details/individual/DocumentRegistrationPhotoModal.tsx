import * as React from 'react';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';
import {
  ImportedIndividualDetailedFragment,
  useImportedIndividualPhotosQuery,
} from '@generated/graphql';

interface DocumentRegistrationPhotoModalProps {
  individual: ImportedIndividualDetailedFragment;
  documentNumber: string;
  documentId: string;
}

export function DocumentRegistrationPhotoModal({
  individual,
  documentNumber,
  documentId,
}: DocumentRegistrationPhotoModalProps): React.ReactElement {
  const { data } = useImportedIndividualPhotosQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });
  const documentWithPhoto = data?.importedIndividual?.documents?.edges?.find(
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

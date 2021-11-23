import React from 'react';
import { PhotoModal } from '../../../../components/PhotoModal/PhotoModal';
import {
  ImportedIndividualDetailedFragment,
  useImportedIndividualPhotosQuery,
} from '../../../../__generated__/graphql';

interface DocumentRegistrationPhotoModalProps {
  individual: ImportedIndividualDetailedFragment;
  documentNumber: string;
  documentId: string;
}

export const DocumentRegistrationPhotoModal = ({
  individual,
  documentNumber,
  documentId,
}: DocumentRegistrationPhotoModalProps): React.ReactElement => {
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
      variant='link'
      title="Document's Photo"
    />
  );
};

import React from 'react';
import {
  ImportedIndividualNode,
  useImportedIndividualPhotosQuery,
} from '../../__generated__/graphql';
import { PhotoModal } from '../core/PhotoModal/PhotoModal';

interface ImportedIndividualPhotoModalProps {
  individual: ImportedIndividualNode;
}

export function ImportedIndividualPhotoModal({
  individual,
}: ImportedIndividualPhotoModalProps): React.ReactElement {
  const { data } = useImportedIndividualPhotosQuery({
    variables: { id: individual?.id },
    fetchPolicy: 'network-only',
  });

  return (
    <PhotoModal
      src={data?.importedIndividual?.photo}
      variant="button"
      title="Individuals's Photo"
    />
  );
}

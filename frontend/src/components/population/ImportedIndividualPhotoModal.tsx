import * as React from 'react';
import {
  ImportedIndividualNode,
  useImportedIndividualPhotosQuery,
} from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';

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

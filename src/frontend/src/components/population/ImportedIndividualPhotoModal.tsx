import {
  ImportedIndividualNode,
  useImportedIndividualPhotosQuery,
} from '@generated/graphql';
import { PhotoModal } from '@core/PhotoModal/PhotoModal';
import { ReactElement } from 'react';

interface ImportedIndividualPhotoModalProps {
  individual: ImportedIndividualNode;
}

export function ImportedIndividualPhotoModal({
  individual,
}: ImportedIndividualPhotoModalProps): ReactElement {
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

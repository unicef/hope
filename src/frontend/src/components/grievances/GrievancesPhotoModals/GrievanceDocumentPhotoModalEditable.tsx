import { Box } from '@mui/material';
import { ReactElement, useState } from 'react';
import PhotoModal from '@core/PhotoModal/PhotoModal';

interface GrievanceDocumentPhotoModalProps {
  photoSrc: string;
  setFieldValue;
  fieldName;
}

export function GrievanceDocumentPhotoModalEditable({
  photoSrc,
  setFieldValue,
  fieldName,
}: GrievanceDocumentPhotoModalProps): ReactElement {
  const [isEdited, setEdit] = useState(false);
  const picUrl = photoSrc;

  return (
    <Box style={{ height: '100%' }} display="flex" alignItems="center">
      {isEdited || !picUrl ? (
        <Box style={{ height: '100%' }} display="flex" alignItems="center">
          <input
            type="file"
            accept="image/*"
            onChange={(event) => {
              setFieldValue(fieldName, event.currentTarget.files[0]);
            }}
          />
        </Box>
      ) : (
        <PhotoModal
          src={picUrl}
          variant="pictureClose"
          closeHandler={() => {
            setEdit(true);
            setFieldValue(fieldName, null);
          }}
          showRotate={false}
        />
      )}
    </Box>
  );
}

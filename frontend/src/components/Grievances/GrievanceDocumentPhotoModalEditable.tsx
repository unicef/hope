import { Box } from '@material-ui/core';
import React, { useState } from 'react';
import { PhotoModal } from '../PhotoModal/PhotoModal';

interface GrievanceDocumentPhotoModalProps {
  photoSrc: string;
  setFieldValue;
  fieldName;
}

export const GrievanceDocumentPhotoModalEditable = ({
  photoSrc,
  setFieldValue,
  fieldName,
}: GrievanceDocumentPhotoModalProps): React.ReactElement => {
  const [isEdited, setEdit] = useState(false);
  const picUrl = photoSrc;

  return (
    <Box style={{ height: '100%' }} display='flex' alignItems='center'>
      {isEdited || !picUrl ? (
        <Box style={{ height: '100%' }} display='flex' alignItems='center'>
          <input
            type='file'
            accept='image/*'
            onChange={(event) => {
              setFieldValue(fieldName, event.currentTarget.files[0]);
            }}
          />
        </Box>
      ) : (
        <PhotoModal
          src={picUrl}
          variant='pictureClose'
          closeHandler={() => setEdit(true)}
        />
      )}
    </Box>
  );
};

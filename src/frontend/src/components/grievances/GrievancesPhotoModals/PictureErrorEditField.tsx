import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Grid, IconButton, Typography } from '@mui/material';
import PhotoModal from '@core/PhotoModal/PhotoModal';
import { useFormikContext } from 'formik';
import { ReactElement, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const PhotoPreview = styled.img`
  width: 220px;
  height: 220px;
  object-fit: cover;
  border: 1px solid ${({ theme }) => theme.palette.grey[300]};
  border-radius: 4px;
`;

const PlaceholderBox = styled(Box)`
  width: 220px;
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed ${({ theme }) => theme.palette.grey[400]};
  border-radius: 4px;
  color: ${({ theme }) => theme.palette.grey[600]};
`;

interface PictureErrorEditFieldProps {
  currentPhotoSrc?: string;
  fieldName: string;
}

export function PictureErrorEditField({
  currentPhotoSrc,
  fieldName,
}: PictureErrorEditFieldProps): ReactElement {
  const { t } = useTranslation();
  const { values, setFieldValue } = useFormikContext<{
    [key: string]: File | null;
  }>();
  const inputRef = useRef<HTMLInputElement>(null);
  const selectedFile = values[fieldName];

  const clearSelection = (): void => {
    setFieldValue(fieldName, null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <Grid container spacing={4}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Typography variant="caption" color="textSecondary">
          {t('Current photo')}
        </Typography>
        <Box mt={2}>
          {currentPhotoSrc ? (
            <PhotoModal
              src={currentPhotoSrc}
              title={t('Current photo')}
              alt={t('Current photo')}
            >
              <PhotoPreview
                src={currentPhotoSrc}
                alt={t('Current photo')}
                data-cy="current-picture"
              />
            </PhotoModal>
          ) : (
            <PlaceholderBox data-cy="no-current-picture">
              {t('No photo on file')}
            </PlaceholderBox>
          )}
        </Box>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <Typography variant="caption" color="textSecondary">
          {t('Upload replacement')}
        </Typography>
        <Box mt={2} display="flex" alignItems="center">
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            data-cy="file-input"
            onChange={(event) =>
              setFieldValue(fieldName, event.currentTarget.files?.[0] ?? null)
            }
          />
          {selectedFile && (
            <IconButton
              size="small"
              onClick={clearSelection}
              data-cy="button-remove-new-photo"
              aria-label={t('Remove')}
            >
              <DeleteIcon />
            </IconButton>
          )}
        </Box>
      </Grid>
    </Grid>
  );
}

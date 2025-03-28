import { Box, Grid2 as Grid, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { ReactElement } from 'react';

export interface DocumentationFieldProps {
  index: number;
  baseName: string;
  onDelete: () => void;
  isEdited?: boolean;
  setFieldValue;
}

export function DocumentationField({
  index,
  baseName,
  onDelete,
  isEdited,
  setFieldValue,
}: DocumentationFieldProps): ReactElement {
  const { t } = useTranslation();

  return (
    <Grid container spacing={3} alignItems="center">
      <Grid size={{ xs: 3 }}>
        <Field
          name={`${baseName}[${index}].name`}
          fullWidth
          variant="outlined"
          label={t('Document Name')}
          component={FormikTextField}
          required
          maxLength={100}
        />
      </Grid>
      <Grid size={{ xs: 3 }}>
        <Box style={{ height: '100%' }} display="flex" alignItems="center">
          <input
            type="file"
            accept=".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,.pdf,image/*"
            onChange={(event) => {
              setFieldValue(
                `${baseName}[${index}].file`,
                event.currentTarget.files[0],
              );
            }}
          />
        </Box>
      </Grid>
      {!isEdited ? (
        <Grid size={{ xs:6 }}>
          <IconButton onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
    </Grid>
  );
}

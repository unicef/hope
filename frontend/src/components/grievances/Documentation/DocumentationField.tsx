import { Box, Grid, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';

export interface DocumentationFieldProps {
  index: number;
  baseName: string;
  onDelete: () => {};
  isEdited?: boolean;
  setFieldValue;
  photoSrc?: string;
}

export const DocumentationField = ({
  index,
  baseName,
  onDelete,
  isEdited,
  setFieldValue,
  photoSrc,
}: DocumentationFieldProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <>
      <Grid item xs={3}>
        <Field
          name={`${baseName}[${index}].name`}
          fullWidth
          variant='outlined'
          label={t('Document Name')}
          component={FormikTextField}
          required
        />
      </Grid>
      <Grid item xs={3}>
        <Box style={{ height: '100%' }} display='flex' alignItems='center'>
          <input
            type='file'
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
        <Grid item xs={6}>
          <IconButton onClick={onDelete}>
            <Delete />
          </IconButton>
        </Grid>
      ) : null}
    </>
  );
};

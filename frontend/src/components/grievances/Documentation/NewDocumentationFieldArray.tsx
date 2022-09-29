import { Button, FormHelperText, Grid } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { DocumentationField } from './DocumentationField';

export interface NewDocumentationFieldArrayProps {
  values;
  setFieldValue;
  errors;
}

export const NewDocumentationFieldArray = ({
  values,
  setFieldValue,
  errors,
}: NewDocumentationFieldArrayProps): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name='documentation'
        render={(arrayHelpers) => {
          return (
            <>
              {values.documentation?.map((_item, index) => (
                <DocumentationField
                  index={index}
                  key={`${index}-documentation-file`}
                  onDelete={() => arrayHelpers.remove(index)}
                  baseName='documentation'
                  setFieldValue={setFieldValue}
                />
              ))}
              <Grid item xs={12}>
                <Button
                  color='primary'
                  onClick={() => {
                    arrayHelpers.push({
                      name: '',
                      file: null,
                    });
                  }}
                  startIcon={<AddCircleOutline />}
                >
                  {t(
                    values.documentation?.length > 0
                      ? 'Add another document'
                      : 'Add document',
                  )}
                </Button>
              </Grid>
              {errors?.documentation && (
                <FormHelperText error>{errors?.documentation}</FormHelperText>
              )}
            </>
          );
        }}
      />
    </Grid>
  );
};

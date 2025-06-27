import { Button, FormHelperText, Grid2 as Grid } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { FieldArray } from 'formik';
import { useTranslation } from 'react-i18next';
import { DocumentationField } from './DocumentationField';
import { ReactElement } from 'react';

export interface NewDocumentationFieldArrayProps {
  values;
  setFieldValue;
  errors;
}

export function NewDocumentationFieldArray({
  values,
  setFieldValue,
  errors,
}: NewDocumentationFieldArrayProps): ReactElement {
  const { t } = useTranslation();
  return (
    <Grid container spacing={3}>
      <FieldArray
        name="documentation"
        render={(arrayHelpers) => (
          <>
            {values.documentation?.map((_item, index) => (
              <Grid size={{ xs: 12 }} key={`${index}-documentation-file`}>
                <DocumentationField
                  index={index}
                  onDelete={() => arrayHelpers.remove(index)}
                  baseName="documentation"
                  setFieldValue={setFieldValue}
                />
              </Grid>
            ))}
            <Grid size={{ xs: 12 }}>
              <Button
                data-cy="add-documentation"
                color="primary"
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
                    ? 'Add more grievance supporting documents'
                    : 'Add grievance supporting documents',
                )}
              </Button>
            </Grid>
            {errors?.documentation && (
              <FormHelperText error>{errors?.documentation}</FormHelperText>
            )}
          </>
        )}
      />
    </Grid>
  );
}

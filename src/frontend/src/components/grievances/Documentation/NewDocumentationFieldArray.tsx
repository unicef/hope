import { Button, FormHelperText, Grid } from '@mui/material';
import { AddCircleOutlined } from '@mui/icons-material';
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
    <Grid container size={12} spacing={3}>
      <FieldArray
        name="documentation"
        render={(arrayHelpers) => (
          <>
            {values.documentation?.map((_item, index) => (
              <Grid
                container
                size={12}
                direction="row"
                spacing={3}
                key={`${index}-documentation-file`}
                sx={{
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <DocumentationField
                  index={index}
                  onDelete={() => arrayHelpers.remove(index)}
                  baseName="documentation"
                  setFieldValue={setFieldValue}
                />
              </Grid>
            ))}
            <Grid size={12}>
              <Button
                data-cy="add-documentation"
                color="primary"
                onClick={() => {
                  arrayHelpers.push({
                    name: '',
                    file: null,
                  });
                }}
                startIcon={<AddCircleOutlined />}
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

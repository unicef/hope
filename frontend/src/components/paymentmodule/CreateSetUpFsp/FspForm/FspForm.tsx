import { Box, Grid } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';

interface FspFormProps {
  index: number;
  baseName: string;
}

export function FspForm({ index, baseName }: FspFormProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box flexDirection='column'>
      <Grid container>
        <Grid item xs={3}>
          <Grid item xs={6}>
            <Field
              name={`${baseName}[${index}].fsp`}
              variant='outlined'
              label={t('FSP')}
              component={FormikSelectField}
              choices={[
                { name: 'USD', value: 'USD' },
                { name: 'PLN', value: 'PLN' },
              ]}
              required
            />
          </Grid>
        </Grid>
        <Grid item xs={3}>
          <Grid item xs={6}>
            <Field
              name={`${baseName}[${index}].maximumAmount`}
              label={t('Maximum Amount (USD)')}
              type='number'
              color='primary'
              variant='outlined'
              fullWidth
              component={FormikTextField}
            />
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
}

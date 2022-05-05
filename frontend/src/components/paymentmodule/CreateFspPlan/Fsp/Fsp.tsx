import { Box, Button, Grid, Typography } from '@material-ui/core';
import { Field } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';
import { Title } from '../../../core/Title';

const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

interface FspProps {
  permissions: string[];
}

export function Fsp({ permissions }: FspProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box flexDirection='column'>
      <Title>
        <Typography variant='h6'>{t('Mobile Money')}</Typography>
      </Title>
      <Grid container>
        <Grid item xs={3}>
          <LabelizedField label={t('To be delivered USD')}>
            <Missing />
          </LabelizedField>
        </Grid>
        <Grid item xs={3}>
          <LabelizedField label={t('Total Maximum Amount')}>
            <Missing />
          </LabelizedField>
        </Grid>
      </Grid>
      <GreyText>{t('Set up order')}</GreyText>
      <Grid container>
        <Grid item xs={3}>
          <Grid item xs={6}>
            <Field
              name='fsp'
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
              name='maxAmount'
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

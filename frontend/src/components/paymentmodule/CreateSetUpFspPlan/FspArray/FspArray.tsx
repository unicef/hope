import { Box, Button, Grid, Typography } from '@material-ui/core';
import { FieldArray } from 'formik';
import styled from 'styled-components';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';
import { Title } from '../../../core/Title';
import { FspForm } from '../FspForm/FspForm';

const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

interface FspArrayProps {
  baseName: string;
  label: string;
  values;
  permissions;
}

export function FspArray({
  baseName,
  label,
  values,
  permissions,
}: FspArrayProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <>
      <Box mt={4}>
        <Title>
          <Typography variant='h6'>{label}</Typography>
        </Title>
      </Box>
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
      <FieldArray
        name={baseName}
        render={(arrayHelpers) => {
          return (
            <>
              {values[baseName].map((item, index) => (
                <FspForm key={label} index={index} baseName={baseName} />
              ))}
              <Grid container>
                <Grid item xs={12}>
                  <Box mt={4} mb={6}>
                    <Button
                      color='primary'
                      onClick={() => {
                        arrayHelpers.push({
                          fsp: null,
                          maximumAmount: null,
                        });
                      }}
                    >
                      {t('Select Another Fsp')}
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </>
          );
        }}
      />
    </>
  );
}

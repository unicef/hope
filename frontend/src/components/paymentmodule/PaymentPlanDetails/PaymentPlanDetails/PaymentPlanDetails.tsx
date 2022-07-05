import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { Missing } from '../../../core/Missing';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { Title } from '../../../core/Title';

interface PaymentPlanDetailsProps {
  businessArea: string;
  permissions: string[];
}

export function PaymentPlanDetails({
  businessArea,
  permissions,
}: PaymentPlanDetailsProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid item xs={3}>
              <LabelizedField label={t('Created By')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Target Population')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Currency')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Start Date')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('End Date')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Dispersion Start Date')}>
                <Missing />
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Dispersion End Date')}>
                <Missing />
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
}

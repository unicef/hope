import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { PaymentPlanQuery } from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { BlackLink } from '../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../core/LabelizedField';
import { OverviewContainer } from '../../core/OverviewContainer';
import { UniversalMoment } from '../../core/UniversalMoment';
import { Title } from '../../core/Title';

interface ExampleDetailsProps {
  paymentPlan?: PaymentPlanQuery['paymentPlan'];
}

export const ExampleDetails = ({}: ExampleDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  return (
    <Grid item xs={12}>
      <ContainerColumnWithBorder>
        <Title>
          <Typography variant='h6'>{t('Details')}</Typography>
        </Title>
        <OverviewContainer>
          <Grid container spacing={6}>
            <Grid item xs={3}>
              <LabelizedField label={t('Created By')}>something</LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Something')}>
                <BlackLink to={`/${baseUrl}/details/someID`}>
                  something
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Example')}>
                <BlackLink to={`/${baseUrl}/target-population/example`}>
                  example
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Currency')}>example</LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{new Date().toISOString()}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{new Date().toISOString()}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Dispersion Start Date')}>
                <UniversalMoment>{new Date().toISOString()}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Dispersion End Date')}>
                <UniversalMoment>{new Date().toISOString()}</UniversalMoment>
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};

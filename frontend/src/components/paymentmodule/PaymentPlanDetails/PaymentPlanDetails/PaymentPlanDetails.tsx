import { Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { renderUserName } from '../../../../utils/utils';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { LabelizedField } from '../../../core/LabelizedField';
import { OverviewContainer } from '../../../core/OverviewContainer';
import { Title } from '../../../core/Title';
import { UniversalMoment } from '../../../core/UniversalMoment';

interface PaymentPlanDetailsProps {
  businessArea: string;
  permissions: string[];
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const PaymentPlanDetails = ({
  businessArea,
  permissions,
  paymentPlan,
}: PaymentPlanDetailsProps): React.ReactElement => {
  const { t } = useTranslation();
  const {
    createdBy,
    program,
    targetPopulation,
    currency,
    startDate,
    endDate,
    dispersionStartDate,
    dispersionEndDate,
  } = paymentPlan;

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
                {renderUserName(createdBy)}
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Programme')}>
                <BlackLink to={`/${businessArea}/programs/${program.id}`}>
                  {program.name}
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Target Population')}>
                <BlackLink
                  to={`/${businessArea}/target-populations/${targetPopulation.id}`}
                >
                  {targetPopulation.name}
                </BlackLink>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Currency')}>{currency}</LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{endDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Dispersion Start Date')}>
                <UniversalMoment>{dispersionStartDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={3}>
              <LabelizedField label={t('Dispersion End Date')}>
                <UniversalMoment>{dispersionEndDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
          </Grid>
        </OverviewContainer>
      </ContainerColumnWithBorder>
    </Grid>
  );
};

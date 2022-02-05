import { Grid } from '@material-ui/core';
import PeopleIcon from '@material-ui/icons/People';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { formatNumber } from '../../../utils/utils';
import { AllChartsQuery } from '../../../__generated__/graphql';
import {
  CardAmountSmaller,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../DashboardCard';

interface TotalNumberOfHouseholdsReachedSectionProps {
  data: AllChartsQuery['sectionHouseholdsReached'];
}

export const TotalNumberOfHouseholdsReachedSection = ({
  data,
}: TotalNumberOfHouseholdsReachedSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  if (!data) return null;
  return (
    <DashboardCard color='#00A9FB'>
      <CardTitle>{t('TOTAL NUMBER OF HOUSEHOLDS REACHED')}</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>{formatNumber(data?.total)}</CardAmountSmaller>
        </Grid>
        <Grid item>
          <IconContainer bg='#DAF1FF' color='#00A9FB'>
            <PeopleIcon fontSize='inherit' />
          </IconContainer>
        </Grid>
      </Grid>
    </DashboardCard>
  );
};

import { Grid } from '@material-ui/core';
import ChildCareIcon from '@material-ui/icons/ChildCare';
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

interface TotalNumberOfChildrenReachedSectionProps {
  data: AllChartsQuery['sectionChildReached'];
}

export const TotalNumberOfChildrenReachedSection = ({
  data,
}: TotalNumberOfChildrenReachedSectionProps): React.ReactElement => {
  const { t } = useTranslation();
  if (!data) return null;
  return (
    <DashboardCard color='#4CD0E0'>
      <CardTitle>{t('TOTAL NUMBER OF CHILDREN REACHED')}</CardTitle>
      <Grid container justify='space-between' alignItems='center'>
        <Grid item>
          <CardAmountSmaller>{formatNumber(data?.total)}</CardAmountSmaller>
        </Grid>
        <Grid item>
          <IconContainer bg='#E4F7FA' color='#4CD0E0'>
            <ChildCareIcon fontSize='inherit' />
          </IconContainer>
        </Grid>
      </Grid>
    </DashboardCard>
  );
};

import { Grid } from '@mui/material';
import ChildCareIcon from '@mui/icons-material/ChildCare';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { formatNumber } from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';
import {
  CardAmountSmaller,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../../DashboardCard';

interface TotalNumberOfChildrenReachedSectionProps {
  data: AllChartsQuery['sectionChildReached'];
}

export function TotalNumberOfChildrenReachedSection({
  data,
}: TotalNumberOfChildrenReachedSectionProps): React.ReactElement {
  const { t } = useTranslation();
  return (
    <DashboardCard color="#4CD0E0">
      <CardTitle>{t('TOTAL NUMBER OF CHILDREN REACHED')}</CardTitle>
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid item data-cy="total-number-of-children-reached">
          <CardAmountSmaller>{formatNumber(data?.total)}</CardAmountSmaller>
        </Grid>
        <Grid item>
          <IconContainer bg="#E4F7FA" color="#4CD0E0">
            <ChildCareIcon fontSize="inherit" />
          </IconContainer>
        </Grid>
      </Grid>
    </DashboardCard>
  );
}

import { Grid } from '@mui/material';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { formatCurrencyWithSymbol } from '@utils/utils';
import { AllChartsQuery } from '@generated/graphql';
import {
  CardAmount,
  CardTextLight,
  CardTitle,
  DashboardCard,
  IconContainer,
} from '../../DashboardCard';

interface TotalAmountTransferredSectionProps {
  data: AllChartsQuery['sectionTotalTransferred'];
}
export function TotalAmountTransferredSection({
  data,
}: TotalAmountTransferredSectionProps): React.ReactElement {
  const { t } = useTranslation();
  if (!data) return null;
  return (
    <DashboardCard color="#1E877D">
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid item>
          <CardTitle>{t('TOTAL AMOUNT TRANSFERRED')}</CardTitle>
          <CardTextLight>{t('IN USD')}</CardTextLight>
        </Grid>
        <Grid item>
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <CardAmount>{formatCurrencyWithSymbol(data?.total)}</CardAmount>
            </Grid>
            <Grid item>
              <IconContainer bg="#d9eceb" color="#03867b">
                <AccountBalanceWalletIcon fontSize="inherit" />
              </IconContainer>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </DashboardCard>
  );
}

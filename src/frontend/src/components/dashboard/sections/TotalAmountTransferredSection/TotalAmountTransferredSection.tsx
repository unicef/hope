import { Grid2 as Grid } from '@mui/material';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
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
import { ReactElement } from 'react';

interface TotalAmountTransferredSectionProps {
  data: AllChartsQuery['sectionTotalTransferred'];
}
export function TotalAmountTransferredSection({
  data,
}: TotalAmountTransferredSectionProps): ReactElement {
  const { t } = useTranslation();
  if (!data) return null;
  return (
    <DashboardCard color="#1E877D">
      <Grid container justifyContent="space-between" alignItems="center">
        <Grid>
          <CardTitle>{t('TOTAL AMOUNT TRANSFERRED')}</CardTitle>
          <CardTextLight>{t('IN USD')}</CardTextLight>
        </Grid>
        <Grid data-cy="total-amount-transferred">
          <Grid container spacing={3} alignItems="center">
            <Grid>
              <CardAmount>{formatCurrencyWithSymbol(data?.total)}</CardAmount>
            </Grid>
            <Grid>
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

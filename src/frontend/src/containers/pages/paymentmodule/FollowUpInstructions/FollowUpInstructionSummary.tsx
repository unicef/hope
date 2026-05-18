import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { formatCurrencyWithSymbol } from '@utils/utils';
import { Grid, Typography } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface FollowUpInstructionSummaryProps {
  instruction: FollowUpInstructionDetail;
}

export function FollowUpInstructionSummary({
  instruction,
}: FollowUpInstructionSummaryProps): ReactElement {
  const { t } = useTranslation();

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Summary')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid container spacing={6}>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Payment Plans')}>
              {instruction.childPaymentPlansCount}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Households')}>
              {instruction.householdsCount}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Total Entitled')}>
              {formatCurrencyWithSymbol(instruction.totalEntitledQuantity, 'USD')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Total Delivered')}>
              {formatCurrencyWithSymbol(instruction.totalDeliveredQuantity, 'USD')}
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 3 }}>
            <LabelizedField label={t('Total Undelivered')}>
              {formatCurrencyWithSymbol(
                instruction.totalUndeliveredQuantity,
                'USD',
              )}
            </LabelizedField>
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

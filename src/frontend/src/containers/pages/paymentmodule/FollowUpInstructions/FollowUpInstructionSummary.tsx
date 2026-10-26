import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { formatCurrencyWithSymbol } from '@utils/utils';
import { Typography } from '@mui/material';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

interface FollowUpInstructionSummaryProps {
  instruction: FollowUpInstructionDetail;
}

function formatInstructionAmount(
  amount: number,
  amountUsd: number,
  currency?: string | null,
  visionCode?: string | null,
): string {
  if (!currency) {
    return formatCurrencyWithSymbol(amountUsd, 'USD');
  }
  return `${formatCurrencyWithSymbol(amount, currency, visionCode)} (${formatCurrencyWithSymbol(amountUsd, 'USD')})`;
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
        <ResponsiveGridContainer spacing={6}>
          <ResponsiveGrid size="quarter" data-cy="summary-child-plans-count">
            <LabelizedField label={t('Payment Plans')}>
              {instruction.childPaymentPlansCount}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" data-cy="summary-households-count">
            <LabelizedField label={t('Households')}>
              {instruction.householdsCount}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" data-cy="summary-total-entitled">
            <LabelizedField label={t('Total Entitled')}>
              {formatInstructionAmount(
                instruction.totalEntitledQuantity,
                instruction.totalEntitledQuantityUsd,
                instruction.currency,
                instruction.currencyVisionCode,
              )}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" data-cy="summary-total-delivered">
            <LabelizedField label={t('Total Delivered')}>
              {formatInstructionAmount(
                instruction.totalDeliveredQuantity,
                instruction.totalDeliveredQuantityUsd,
                instruction.currency,
                instruction.currencyVisionCode,
              )}
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="quarter" data-cy="summary-total-undelivered">
            <LabelizedField label={t('Total Undelivered')}>
              {formatInstructionAmount(
                instruction.totalUndeliveredQuantity,
                instruction.totalUndeliveredQuantityUsd,
                instruction.currency,
                instruction.currencyVisionCode,
              )}
            </LabelizedField>
          </ResponsiveGrid>
        </ResponsiveGridContainer>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

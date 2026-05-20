import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { FollowUpInstructionChildPaymentPlanSummary } from '@restgenerated/models/FollowUpInstructionChildPaymentPlanSummary';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface ChildPaymentPlansTableProps {
  paymentPlans: FollowUpInstructionChildPaymentPlanSummary[];
}

function formatInstructionAmount(
  amount: number,
  amountUsd: number,
  currency?: string | null,
): string {
  if (!currency) {
    return formatCurrencyWithSymbol(amountUsd, 'USD');
  }
  return `${formatCurrencyWithSymbol(amount, currency)} (${formatCurrencyWithSymbol(amountUsd, 'USD')})`;
}

export function ChildPaymentPlansTable({
  paymentPlans,
}: ChildPaymentPlansTableProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Payment Plans')}</Typography>
      </Title>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Status')}</TableCell>
            <TableCell align="right">{t('Households')}</TableCell>
            <TableCell align="right">{t('Total Entitled')}</TableCell>
            <TableCell align="right">{t('Total Delivered')}</TableCell>
            <TableCell align="right">{t('Total Undelivered')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {paymentPlans.map((pp) => (
            <TableRow key={pp.id}>
              <TableCell>
                <BlackLink
                  to={`/${baseUrl}/payment-module/followup-payment-plans/${pp.id}`}
                >
                  {pp.unicefId ?? pp.id}
                </BlackLink>
              </TableCell>
              <TableCell>
                {pp.status ? (
                  <StatusBox
                    status={pp.status}
                    statusToColor={paymentPlanStatusToColor}
                  />
                ) : (
                  '-'
                )}
              </TableCell>
              <TableCell align="right">{pp.householdsCount}</TableCell>
              <TableCell align="right">
                {formatInstructionAmount(
                  pp.totalEntitledQuantity,
                  pp.totalEntitledQuantityUsd,
                  pp.currency,
                )}
              </TableCell>
              <TableCell align="right">
                {formatInstructionAmount(
                  pp.totalDeliveredQuantity,
                  pp.totalDeliveredQuantityUsd,
                  pp.currency,
                )}
              </TableCell>
              <TableCell align="right">
                {formatInstructionAmount(
                  pp.totalUndeliveredQuantity,
                  pp.totalUndeliveredQuantityUsd,
                  pp.currency,
                )}
              </TableCell>
            </TableRow>
          ))}
          {paymentPlans.length === 0 && (
            <TableRow>
              <TableCell colSpan={8} align="center">
                {t('No Payment Plans')}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </ContainerColumnWithBorder>
  );
}

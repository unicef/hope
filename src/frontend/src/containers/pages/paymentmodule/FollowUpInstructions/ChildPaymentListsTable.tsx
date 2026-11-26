import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { Title } from '@core/Title';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import type { FollowUpInstructionChildPaymentListSummary } from '@restgenerated/models/FollowUpInstructionChildPaymentListSummary';
import {
  formatCurrencyWithSymbol,
  paymentListStatusToColor,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

interface ChildPaymentListsTableProps {
  paymentLists: FollowUpInstructionChildPaymentListSummary[];
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

export function ChildPaymentListsTable({
  paymentLists,
}: ChildPaymentListsTableProps): ReactElement {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();

  return (
    <ContainerColumnWithBorder>
      <Title>
        <Typography variant="h6">{t('Payment Lists')}</Typography>
      </Title>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('Payment List ID')}</TableCell>
              <TableCell>{t('Status')}</TableCell>
              <TableCell align="right">{t('Households')}</TableCell>
              <TableCell align="right">{t('Total Entitled')}</TableCell>
              <TableCell align="right">{t('Total Delivered')}</TableCell>
              <TableCell align="right">{t('Total Undelivered')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paymentLists.map((pp, index) => (
              <TableRow key={pp.id} data-cy={`plan-row-${index}`}>
                <TableCell>
                  <BlackLink
                    to={`/${baseUrl}/payment-module/followup-payment-lists/${pp.id}`}
                  >
                    {pp.unicefId ?? pp.id}
                  </BlackLink>
                </TableCell>
                <TableCell data-cy={`plan-status-${index}`}>
                  {pp.status ? (
                    <StatusBox
                      status={pp.status}
                      statusToColor={paymentListStatusToColor}
                    />
                  ) : (
                    '-'
                  )}
                </TableCell>
                <TableCell align="right" data-cy={`plan-households-${index}`}>
                  {pp.householdsCount}
                </TableCell>
                <TableCell align="right" data-cy={`plan-entitled-${index}`}>
                  {formatInstructionAmount(
                    pp.totalEntitledQuantity,
                    pp.totalEntitledQuantityUsd,
                    pp.currency,
                    pp.currencyVisionCode,
                  )}
                </TableCell>
                <TableCell align="right" data-cy={`plan-delivered-${index}`}>
                  {formatInstructionAmount(
                    pp.totalDeliveredQuantity,
                    pp.totalDeliveredQuantityUsd,
                    pp.currency,
                    pp.currencyVisionCode,
                  )}
                </TableCell>
                <TableCell align="right" data-cy={`plan-undelivered-${index}`}>
                  {formatInstructionAmount(
                    pp.totalUndeliveredQuantity,
                    pp.totalUndeliveredQuantityUsd,
                    pp.currency,
                    pp.currencyVisionCode,
                  )}
                </TableCell>
              </TableRow>
            ))}
            {paymentLists.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  {t('No Payment Lists')}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </ContainerColumnWithBorder>
  );
}

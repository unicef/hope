import React from 'react';
import {
  TableContainer,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
} from '@mui/material';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useTranslation } from 'react-i18next';
import type { PaginatedPaymentListList } from '@restgenerated/models/PaginatedPaymentListList';

interface PaymentsDataTableProps {
  paymentsData: PaginatedPaymentListList;
}

const PaymentsDataTable: React.FC<PaymentsDataTableProps> = ({
  paymentsData,
}) => {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Payment ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Household ID')}</TableCell>
            <TableCell>{t('Individual ID')}</TableCell>
            <TableCell>{t('Individual Full Name')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {paymentsData.results && paymentsData.results.length > 0 ? (
            paymentsData.results.map((payment) => {
              const paymentDetailsPath = `/${baseUrl}/payment/payments/${payment.id}`;
              const programDetailsPath = `/${baseUrl}/programs/all/details/${payment.programName || ''}`;
              const paymentPlanDetailsPath = `/${baseUrl}/payment/payment-plans/${payment.parentId}`;
              const householdDetailsPath = `/${baseUrl}/population/households/${payment.householdId}`;
              const individualId = payment.peopleIndividual?.id;
              const individualDetailsPath = individualId
                ? `/${baseUrl}/population/individuals/${individualId}`
                : '#';
              return (
                <TableRow key={payment.id} hover>
                  <TableCell>
                    <BlackLink to={paymentDetailsPath}>
                      {payment.unicefId || payment.id}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={programDetailsPath}>
                      {payment.programName}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={paymentPlanDetailsPath}>
                      {payment.parentId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={householdDetailsPath}>
                      {payment.householdUnicefId || payment.householdId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    {individualId ? (
                      <BlackLink to={individualDetailsPath}>
                        {individualId}
                      </BlackLink>
                    ) : null}
                  </TableCell>
                  <TableCell>{payment.individual?.fullName}</TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell colSpan={6}>{t('No results found')}</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default PaymentsDataTable;

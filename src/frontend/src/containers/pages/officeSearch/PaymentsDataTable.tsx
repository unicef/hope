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
  const { baseUrl, businessArea } = useBaseUrl();
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
              const paymentDetailsPath = `/${businessArea}/programs/${payment.programSlug}/payment-module/payments/${payment.id}`;
              const programDetailsPath = `/${baseUrl}/details/${payment.programSlug}`;
              const paymentPlanDetailsPath = `/${businessArea}/programs/${payment.programSlug}/payment-module/payment-plans/${payment.parentId}`;
              const householdDetailsPath = `/${businessArea}/programs/${payment.programSlug}/population/household/${payment.householdId}`;
              const individualDetailsPath = `/${businessArea}/programs/${payment.programSlug}/population/individuals/${payment.hohId}`;

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
                      {payment.parentUnicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={householdDetailsPath}>
                      {payment.householdUnicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    {payment.hohId ? (
                      <BlackLink to={individualDetailsPath}>
                        {payment.hohUnicefId}
                      </BlackLink>
                    ) : null}
                  </TableCell>
                  <TableCell>{payment.hohFullName}</TableCell>
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

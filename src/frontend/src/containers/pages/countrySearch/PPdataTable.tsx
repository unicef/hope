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
import type { PaginatedPaymentListListList } from '@restgenerated/models/PaginatedPaymentListListList';
import type { PaymentListList } from '@restgenerated/models/PaymentListList';

interface PPDataTableProps {
  ppData: PaginatedPaymentListListList;
}

const PPDataTable: React.FC<PPDataTableProps> = ({ ppData }) => {
  const { baseUrl, businessArea } = useBaseUrl();
  const { t } = useTranslation();
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Payment List ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {ppData.results && ppData.results.length > 0 ? (
            ppData.results.map((plan: PaymentListList) => {
              const paymentListDetailsPath = `/${businessArea}/programs/${plan.program.code}/payment-module/payment-lists/${plan.id}`;
              const programDetailsPath = `/${baseUrl}/details/${plan.program.code}`;

              return (
                <TableRow key={plan.id} hover>
                  <TableCell>
                    <BlackLink to={paymentListDetailsPath}>
                      {plan.unicefId}
                    </BlackLink>
                  </TableCell>
                  <TableCell>
                    <BlackLink to={programDetailsPath}>
                      {plan.program.name}
                    </BlackLink>
                  </TableCell>
                </TableRow>
              );
            })
          ) : (
            <TableRow>
              <TableCell colSpan={7}>{t('No results found')}</TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default PPDataTable;

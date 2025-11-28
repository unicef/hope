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
import { PaginatedPaymentPlanListList } from '@restgenerated/models/PaginatedPaymentPlanListList';
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';

interface PPDataTableProps {
  ppData: PaginatedPaymentPlanListList;
}

const PPDataTable: React.FC<PPDataTableProps> = ({ ppData }) => {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {ppData.results && ppData.results.length > 0 ? (
            ppData.results.map((plan: PaymentPlanList) => {
              const paymentPlanDetailsPath = `/${baseUrl}/payment-module/payment-plans/${plan.id}`;
              const programDetailsPath = `/${baseUrl}/programs/all/details/${plan.program.slug}`;

              return (
                <TableRow key={plan.id} hover>
                  <TableCell>
                    <BlackLink to={paymentPlanDetailsPath}>
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

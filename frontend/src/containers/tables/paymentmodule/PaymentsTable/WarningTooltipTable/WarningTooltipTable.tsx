import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BlackLink } from '../../../../../components/core/BlackLink';
import { LabelizedField } from '../../../../../components/core/LabelizedField';
import { StatusBox } from '../../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../../components/core/UniversalMoment';
import { paymentPlanStatusToColor } from '../../../../../utils/utils';
import {
  AllPaymentsForTableQuery,
  PaymentConflictDataNode,
  PaymentPlanQuery,
} from '../../../../../__generated__/graphql';
import { DialogFooter } from '../../../../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../dialogs/DialogTitleWrapper';

const StyledTable = styled(Table)`
  min-width: 100px;
`;
const Bold = styled.div`
  font-weight: bold;
  padding: 0 5px;
`;

const GreyBox = styled(Box)`
  background-color: #f3f3f3;
`;

interface WarningTooltipTableProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'];
  setDialogOpen: (dialogOpen: boolean) => void;
  businessArea: string;
  canViewDetails: boolean;
}

export const WarningTooltipTable = ({
  paymentPlan,
  payment,
  setDialogOpen,
  businessArea,
  canViewDetails = false,
}: WarningTooltipTableProps): React.ReactElement => {
  const { t } = useTranslation();
  if (!payment) return null;
  const mappedPaymentPlanRows = (): React.ReactElement[] => {
    const {
      paymentPlanSoftConflicted,
      paymentPlanHardConflicted,
      paymentPlanHardConflictedData,
      paymentPlanSoftConflictedData,
    } = payment;

    const renderRow = (row: PaymentConflictDataNode): React.ReactElement => (
      <ClickableTableRow hover>
        <TableCell align='left'>
          {canViewDetails ? (
            <BlackLink to={`/${businessArea}/payment-module/payment-plans/${row.paymentPlanEncodedId}`}>
              {row.paymentPlanUnicefId}
            </BlackLink>
          ) : (
            row.paymentPlanUnicefId
          )}
        </TableCell>
        <TableCell align='left'>
          <UniversalMoment>{row.paymentPlanStartDate}</UniversalMoment>
        </TableCell>
        <TableCell align='left'>
          <UniversalMoment>{row.paymentPlanEndDate}</UniversalMoment>
        </TableCell>
        <TableCell align='left'>
          <StatusBox
            status={row.paymentPlanStatus}
            statusToColor={paymentPlanStatusToColor}
          />
        </TableCell>
        <TableCell align='left'>{row.paymentUnicefId}</TableCell>
      </ClickableTableRow>
    );

    if (paymentPlanHardConflicted) {
      return paymentPlanHardConflictedData.map((el) => renderRow(el));
    }
    if (paymentPlanSoftConflicted) {
      return paymentPlanSoftConflictedData.map((el) => renderRow(el));
    }
    return [];
  };

  return (
    <Dialog
      open={!!payment}
      onClose={() => setDialogOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
      maxWidth='md'
    >
      <DialogTitleWrapper>
        <DialogTitle id='scroll-dialog-title'>{t('Warning')}</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <Box mt={4} mb={2} display='flex'>
          {t('Payment Plan ID')} <Bold>{paymentPlan.unicefId}</Bold>{' '}
          {t('details')}:
        </Box>
        <GreyBox p={3}>
          <Grid container>
            <Grid item xs={6}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{paymentPlan.startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{paymentPlan.endDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
          </Grid>
        </GreyBox>
        <Box mt={10} mb={10} display='flex'>
          {t('Household ID')} <Bold>{payment.household?.unicefId}</Bold>{' '}
          {t('is also included in the following Payment Plans')}:
        </Box>
        <StyledTable>
          <TableHead>
            <TableRow>
              <TableCell align='left'>{t('Payment Plan ID')}</TableCell>
              <TableCell align='left'>{t('Start Date')}</TableCell>
              <TableCell align='left'>{t('End Date')}</TableCell>
              <TableCell align='left'>{t('Status')}</TableCell>
              <TableCell align='left'>{t('Payment ID')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>{mappedPaymentPlanRows()}</TableBody>
        </StyledTable>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button
            onClick={(e) => {
              e.stopPropagation();
              setDialogOpen(false);
            }}
          >
            {t('CLOSE')}
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};

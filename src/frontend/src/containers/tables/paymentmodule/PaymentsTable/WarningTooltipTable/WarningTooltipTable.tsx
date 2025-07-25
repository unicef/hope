import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BlackLink } from '@components/core/BlackLink';
import { LabelizedField } from '@components/core/LabelizedField';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { paymentPlanStatusToColor } from '@utils/utils';
import { DialogFooter } from '../../../../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../dialogs/DialogTitleWrapper';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentList } from '@restgenerated/models/PaymentList';

// Interface to replace PaymentConflictDataNode
interface PaymentConflictData {
  paymentPlanId?: string;
  paymentPlanUnicefId?: string;
  paymentPlanStartDate?: string;
  paymentPlanEndDate?: string;
  paymentPlanStatus?: string;
  paymentId?: string;
  paymentUnicefId?: string;
}

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
  paymentPlan: PaymentPlanDetail;
  payment: PaymentList;
  setDialogOpen: (dialogOpen: boolean) => void;
  baseUrl: string;
  canViewDetails: boolean;
}

export function WarningTooltipTable({
  paymentPlan,
  payment,
  setDialogOpen,
  baseUrl,
  canViewDetails = false,
}: WarningTooltipTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  if (!payment) return null;
  const mappedPaymentPlanRows = (): ReactElement[] => {
    const {
      paymentPlanSoftConflicted,
      paymentPlanHardConflicted,
      paymentPlanHardConflictedData,
      paymentPlanSoftConflictedData,
    } = payment;

    const renderRow = (row: PaymentConflictData): ReactElement => (
      <ClickableTableRow hover>
        <TableCell align="left">
          {canViewDetails ? (
            <BlackLink
              to={`/${baseUrl}/payment-module/payment-plans/${row.paymentPlanId}`}
            >
              {row.paymentPlanUnicefId}
            </BlackLink>
          ) : (
            row.paymentPlanUnicefId
          )}
        </TableCell>
        <TableCell align="left">
          <UniversalMoment>{row.paymentPlanStartDate}</UniversalMoment>
        </TableCell>
        <TableCell align="left">
          <UniversalMoment>{row.paymentPlanEndDate}</UniversalMoment>
        </TableCell>
        <TableCell align="left">
          <StatusBox
            status={row.paymentPlanStatus}
            statusToColor={paymentPlanStatusToColor}
          />
        </TableCell>
        <TableCell align="left">{row.paymentUnicefId}</TableCell>
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
      scroll="paper"
      aria-labelledby="form-dialog-title"
      maxWidth="md"
    >
      <DialogTitleWrapper>
        <DialogTitle>{t('Warning')}</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <Box mt={4} mb={2} display="flex">
          {t('Payment Plan ID')} <Bold>{paymentPlan.unicefId}</Bold>{' '}
          {t('details')}:
        </Box>
        <GreyBox p={3}>
          <Grid container>
            <Grid size={{ xs: 6 }}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{paymentPlan.startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 6 }}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{paymentPlan.endDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
          </Grid>
        </GreyBox>
        <Box mt={10} mb={10} display="flex">
          {`${beneficiaryGroup?.groupLabel} ID`}{' '}
          <Bold>{payment.householdUnicefId}</Bold>{' '}
          {t('is also included in the following Payment Plans')}:
        </Box>
        <StyledTable>
          <TableHead>
            <TableRow>
              <TableCell align="left">{t('Payment Plan ID')}</TableCell>
              <TableCell align="left">{t('Start Date')}</TableCell>
              <TableCell align="left">{t('End Date')}</TableCell>
              <TableCell align="left">{t('Status')}</TableCell>
              <TableCell align="left">{t('Payment ID')}</TableCell>
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
}

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
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { BlackLink } from '@components/core/BlackLink';
import { LabelizedField } from '@components/core/LabelizedField';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { paymentListStatusToColor } from '@utils/utils';
import { DialogFooter } from '../../../../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../dialogs/DialogTitleWrapper';
import { useProgramContext } from 'src/programContext';
import type { ReactElement } from 'react';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import type { PaymentRow } from '@restgenerated/models/PaymentRow';

// Interface to replace PaymentConflictDataNode
interface PaymentConflictData {
  paymentListId?: string;
  paymentListUnicefId?: string;
  paymentListStartDate?: string;
  paymentListEndDate?: string;
  paymentListStatus?: string;
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
  paymentList: PaymentListDetail;
  payment: PaymentRow;
  setDialogOpen: (dialogOpen: boolean) => void;
  baseUrl: string;
  canViewDetails: boolean;
}

export function WarningTooltipTable({
  paymentList,
  payment,
  setDialogOpen,
  baseUrl,
  canViewDetails = false,
}: WarningTooltipTableProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  if (!payment) return null;
  const mappedPaymentListRows = (): ReactElement[] => {
    const {
      paymentListSoftConflicted,
      paymentListHardConflicted,
      paymentListHardConflictedData,
      paymentListSoftConflictedData,
    } = payment;

    const renderRow = (row: PaymentConflictData): ReactElement => (
      <ClickableTableRow hover>
        <TableCell align="left">
          {canViewDetails ? (
            <BlackLink
              to={`/${baseUrl}/payment-module/payment-lists/${row.paymentListId}`}
            >
              {row.paymentListUnicefId}
            </BlackLink>
          ) : (
            row.paymentListUnicefId
          )}
        </TableCell>
        <TableCell align="left">
          <UniversalMoment>{row.paymentListStartDate}</UniversalMoment>
        </TableCell>
        <TableCell align="left">
          <UniversalMoment>{row.paymentListEndDate}</UniversalMoment>
        </TableCell>
        <TableCell align="left">
          <StatusBox
            status={row.paymentListStatus}
            statusToColor={paymentListStatusToColor}
          />
        </TableCell>
        <TableCell align="left">{row.paymentUnicefId}</TableCell>
      </ClickableTableRow>
    );

    if (paymentListHardConflicted) {
      return paymentListHardConflictedData.map((el) => renderRow(el));
    }
    if (paymentListSoftConflicted) {
      return paymentListSoftConflictedData.map((el) => renderRow(el));
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
        <Box
          sx={{
            mt: 4,
            mb: 2,
            display: 'flex',
          }}
        >
          {t('Payment List ID')} <Bold>{paymentList.unicefId}</Bold>{' '}
          {t('details')}:
        </Box>
        <GreyBox
          sx={{
            p: 3,
          }}
        >
          <Grid container>
            <Grid size={6}>
              <LabelizedField label={t('Start Date')}>
                <UniversalMoment>{paymentList.startDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
            <Grid size={6}>
              <LabelizedField label={t('End Date')}>
                <UniversalMoment>{paymentList.endDate}</UniversalMoment>
              </LabelizedField>
            </Grid>
          </Grid>
        </GreyBox>
        <Box
          sx={{
            mt: 10,
            mb: 10,
            display: 'flex',
          }}
        >
          {`${beneficiaryGroup?.groupLabel} ID`}{' '}
          <Bold>{payment.householdUnicefId}</Bold>{' '}
          {t('is also included in the following Payment Lists')}:
        </Box>
        <StyledTable>
          <TableHead>
            <TableRow>
              <TableCell align="left">{t('Payment List ID')}</TableCell>
              <TableCell align="left">{t('Start Date')}</TableCell>
              <TableCell align="left">{t('End Date')}</TableCell>
              <TableCell align="left">{t('Status')}</TableCell>
              <TableCell align="left">{t('Payment ID')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>{mappedPaymentListRows()}</TableBody>
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

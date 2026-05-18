import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TableCell } from '@mui/material';
import { FollowUpInstructionList } from '@restgenerated/models/FollowUpInstructionList';
import {
  formatCurrencyWithSymbol,
  paymentPlanStatusToColor,
} from '@utils/utils';
import { ReactElement } from 'react';

interface FollowUpInstructionTableRowProps {
  instruction: FollowUpInstructionList;
}

export const FollowUpInstructionTableRow = ({
  instruction,
}: FollowUpInstructionTableRowProps): ReactElement => {
  const { baseUrl } = useBaseUrl();
  const path = `/${baseUrl}/payment-module/follow-up-instructions/${instruction.id}`;

  return (
    <ClickableTableRow key={instruction.id}>
      <TableCell align="left">
        <BlackLink to={path}>{instruction.unicefId ?? '-'}</BlackLink>
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={instruction.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="left">
        {instruction.backgroundActionStatusDisplay || '-'}
      </TableCell>
      <TableCell align="right">{instruction.childPaymentPlansCount}</TableCell>
      <TableCell align="right">{instruction.householdsCount}</TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(instruction.totalEntitledQuantity, 'USD')}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(instruction.totalDeliveredQuantity, 'USD')}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(instruction.totalUndeliveredQuantity, 'USD')}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{instruction.createdAt}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};

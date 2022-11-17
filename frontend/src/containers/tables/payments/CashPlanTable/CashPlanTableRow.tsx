import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanAndPaymentPlanNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { StatusBox } from '../../../../components/core/StatusBox';
import {
  cashPlanStatusToColor,
  renderSomethingOrDash,
} from '../../../../utils/utils';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';

interface CashPlanTableRowProps {
  cashAndPaymentPlan: CashPlanAndPaymentPlanNode;
}

export function CashPlanTableRow({
  cashAndPaymentPlan,
}: CashPlanTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const cashPlanPath = `/${businessArea}/cashplans/${cashAndPaymentPlan.id}`;
  const handleClick = (): void => {
    history.push(cashPlanPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={cashAndPaymentPlan.id}
      data-cy='cash-plan-table-row'
    >
      <TableCell align='left'>
        <BlackLink to={cashPlanPath}>
          <div
            style={{
              textOverflow: 'ellipsis',
            }}
          >
            {cashAndPaymentPlan.unicefId}
          </div>
        </BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={cashAndPaymentPlan.verificationStatus}
          statusToColor={cashPlanStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>{cashAndPaymentPlan.totalNumberOfHouseholds}</TableCell>
      <TableCell align='left'>{cashAndPaymentPlan.assistanceMeasurement}</TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashAndPaymentPlan?.totalEntitledQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashAndPaymentPlan?.totalDeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashAndPaymentPlan?.totalUndeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{cashAndPaymentPlan.dispersionDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanNode } from '../../../../__generated__/graphql';
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
  cashPlan: CashPlanNode;
}

export function CashPlanTableRow({
  cashPlan,
}: CashPlanTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const cashPlanPath = `/${businessArea}/cashplans/${cashPlan.id}`;
  const handleClick = (): void => {
    history.push(cashPlanPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={cashPlan.id}
      data-cy='cash-plan-table-row'
    >
      <TableCell align='left'>
        <BlackLink to={cashPlanPath}>
          <div
            style={{
              textOverflow: 'ellipsis',
            }}
          >
            {cashPlan.caId}
          </div>
        </BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={cashPlan.status}
          statusToColor={cashPlanStatusToColor}
        />
      </TableCell>
      <TableCell align='right'>{cashPlan.totalNumberOfHouseholds}</TableCell>
      <TableCell align='left'>{cashPlan.assistanceMeasurement}</TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashPlan?.totalEntitledQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashPlan?.totalDeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='right'>
        {renderSomethingOrDash(
          cashPlan?.totalUndeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align='left'>
        <UniversalMoment>{cashPlan.dispersionDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

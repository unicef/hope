import TableCell from '@mui/material/TableCell';
import React from 'react';
import { useHistory } from 'react-router-dom';
import { CashPlanAndPaymentPlanNode } from '../../../../__generated__/graphql';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import {
  paymentPlanStatusToColor,
  renderSomethingOrDash,
} from '../../../../utils/utils';

interface CashPlanTableRowProps {
  cashAndPaymentPlan: CashPlanAndPaymentPlanNode;
}

export const CashPlanTableRow = ({
  cashAndPaymentPlan,
}: CashPlanTableRowProps): React.ReactElement => {
  const history = useHistory();
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const objectPath =
    cashAndPaymentPlan.objType === 'PaymentPlan'
      ? `/${baseUrl}/payment-module/payment-plans/${cashAndPaymentPlan.id}`
      : `/${baseUrl}/cashplans/${cashAndPaymentPlan.id}`;

  const handleClick = (): void => {
    history.push(objectPath);
  };
  return (
    <ClickableTableRow
      hover={!isAllPrograms}
      onClick={!isAllPrograms ? handleClick : undefined}
      role="checkbox"
      key={cashAndPaymentPlan.id}
      data-cy="cash-plan-table-row"
    >
      <TableCell align="left">
        {!isAllPrograms ? (
          <BlackLink to={objectPath}>
            <div>{cashAndPaymentPlan.unicefId}</div>
          </BlackLink>
        ) : (
          <div>{cashAndPaymentPlan.unicefId}</div>
        )}
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={cashAndPaymentPlan.status}
          statusToColor={paymentPlanStatusToColor}
        />
      </TableCell>
      <TableCell align="right">
        {cashAndPaymentPlan.totalNumberOfHouseholds}
      </TableCell>
      <TableCell align="left">{cashAndPaymentPlan.currency}</TableCell>
      <TableCell align="right">
        {renderSomethingOrDash(
          cashAndPaymentPlan?.totalEntitledQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align="right">
        {renderSomethingOrDash(
          cashAndPaymentPlan?.totalDeliveredQuantity?.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          }),
        )}
      </TableCell>
      <TableCell align="right">
        {renderSomethingOrDash(
          cashAndPaymentPlan?.totalUndeliveredQuantity?.toLocaleString(
            'en-US',
            {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            },
          ),
        )}
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{cashAndPaymentPlan.dispersionDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
};

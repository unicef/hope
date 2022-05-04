import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import {
  AllCashPlansQuery,
  useCashPlanVerificationStatusChoicesQuery,
} from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  paymentVerificationStatusToColor,
} from '../../../../utils/utils';
import { StatusBox } from '../../../../components/core/StatusBox';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { BlackLink } from '../../../../components/core/BlackLink';
import { Missing } from '../../../../components/core/Missing';

const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;
interface FspTableRowProps {
  plan: AllCashPlansQuery['allCashPlans']['edges'][number]['node'];
  canViewDetails: boolean;
}

export const FspTableRow = ({
  plan,
  canViewDetails,
}: FspTableRowProps): React.ReactElement => {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const paymentVerificationPlanPath = `/${businessArea}/payment-verification/${plan.id}`;
  const handleClick = (): void => {
    history.push(paymentVerificationPlanPath);
  };
  const {
    data: statusChoicesData,
  } = useCashPlanVerificationStatusChoicesQuery();

  if (!statusChoicesData) return null;
  const deliveryTypeChoicesDict = choicesToDict(
    statusChoicesData.paymentRecordDeliveryTypeChoices,
  );

  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={plan.id}
    >
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
    </ClickableTableRow>
  );
};

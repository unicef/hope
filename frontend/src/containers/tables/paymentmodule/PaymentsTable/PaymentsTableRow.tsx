import TableCell from '@material-ui/core/TableCell';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { BlackLink } from '../../../../components/core/BlackLink';
import { Missing } from '../../../../components/core/Missing';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { AllGrievanceTicketQuery } from '../../../../__generated__/graphql';
import { SuggestNewAmount } from './SuggestNewAmount';
import { WarningTooltipTable } from './WarningTooltipTable';

const ErrorText = styled.div`
  display: flex;
  align-items: center;
  text-transform: uppercase;
  color: #ec2323;
`;

const CheckCircleOutline = styled(CheckCircleOutlineIcon)`
  color: #8ece32;
`;

const ErrorOutline = styled(ErrorOutlineIcon)`
  color: #e90202;
  margin-right: 5px;
`;

interface PaymentsTableRowProps {
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'];
  statusChoices: { [id: number]: string };
  categoryChoices: { [id: number]: string };
  canViewDetails: boolean;
}

export function PaymentsTableRow({
  ticket,
  statusChoices,
  categoryChoices,
  canViewDetails,
}: PaymentsTableRowProps): React.ReactElement {
  const history = useHistory();
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const detailsPath = `/${businessArea}/grievance-and-feedback/${ticket.id}`;

  const handleClick = (): void => {
    history.push(detailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={ticket.id}
    >
      <TableCell align='left'>
        <WarningTooltipTable businessArea={businessArea} />
      </TableCell>
      <TableCell align='left'>
        {canViewDetails ? (
          <BlackLink to={detailsPath}>{ticket.unicefId}</BlackLink>
        ) : (
          ticket.unicefId
        )}
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
      <TableCell align='left'>
        {false ? (
          <CheckCircleOutline />
        ) : (
          <ErrorText>
            <ErrorOutline />
            {t('Missing')}
          </ErrorText>
        )}
      </TableCell>
      <TableCell align='left'>
        <Missing />
      </TableCell>
      <TableCell align='left'>
        <Missing />
        <SuggestNewAmount businessArea={businessArea} />
      </TableCell>
    </ClickableTableRow>
  );
}

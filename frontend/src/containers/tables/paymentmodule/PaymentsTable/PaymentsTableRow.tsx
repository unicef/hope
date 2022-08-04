import TableCell from '@material-ui/core/TableCell';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { BlackLink } from '../../../../components/core/BlackLink';
import { Missing } from '../../../../components/core/Missing';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { WarningTooltip } from '../../../../components/core/WarningTooltip';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { decodeIdString, formatCurrency } from '../../../../utils/utils';
import { AllPaymentsForTableQuery } from '../../../../__generated__/graphql';
import { WarningTooltipTable } from './WarningTooltipTable';

const ErrorText = styled.div`
  display: flex;
  align-items: center;
  text-transform: uppercase;
  color: #ec2323;
`;

const ErrorOutline = styled(ErrorOutlineIcon)`
  color: #e90202;
  margin-right: 5px;
`;

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

interface PaymentsTableRowProps {
  payment: AllPaymentsForTableQuery['allPayments']['edges'][number]['node'];
  canViewDetails: boolean;
}

export function PaymentsTableRow({
  payment,
  canViewDetails,
}: PaymentsTableRowProps): React.ReactElement {
  const { t } = useTranslation();
  const history = useHistory();
  const businessArea = useBusinessArea();
  const [dialogWarningOpen, setDialogWarningOpen] = useState(false);
  const detailsPath = `/${businessArea}/payment/${payment.id}`;
  const householdDetailsPath = `/${businessArea}/population/household/${payment.household.id}`;

  const handleClick = (): void => {
    history.push(detailsPath);
  };

  const handleDialogWarningOpen = (e: React.SyntheticEvent<HTMLDivElement>): void => {
    e.stopPropagation();
    setDialogWarningOpen(true);
  };

  return (
    <>
      <ClickableTableRow
        hover
        onClick={canViewDetails ? handleClick : undefined}
        role='checkbox'
        key={payment.id}
      >
        <TableCell align='left'>
          <WarningTooltip
            handleClick={(e) => handleDialogWarningOpen(e)}
            message={t(
              'This household is also included in other Payment Plans. Click this icon to view details.',
            )}
          />
        </TableCell>
        <TableCell align='left'>
            {decodeIdString(payment.id)}
        </TableCell>
        <TableCell align='left'>
          {canViewDetails ? (
            <BlackLink to={householdDetailsPath}>{payment.household.unicefId}</BlackLink>
          ) : (
            payment.household.unicefId
          )}
        </TableCell>
        <TableCell align='left'>
          {payment.household.size}
        </TableCell>
        <TableCell align='left'>
          {payment.household.admin2.name}
        </TableCell>
        <TableCell align='left'>
          <Missing />
        </TableCell>
        <TableCell align='left'>
          <ErrorText>
            <ErrorOutline />
            {t('Missing')}
          </ErrorText>
        </TableCell>
        <TableCell align='left'>
          {formatCurrency(payment.entitlementQuantityUsd, true)}
        </TableCell>
      </ClickableTableRow>
      <WarningTooltipTable
        businessArea={businessArea}
        setDialogOpen={setDialogWarningOpen}
        dialogOpen={dialogWarningOpen}
      />
    </>
  );
}

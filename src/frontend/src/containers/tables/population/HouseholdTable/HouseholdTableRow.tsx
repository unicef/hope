import { Box } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { FlagTooltip } from '@components/core/FlagTooltip';
import { StatusBox } from '@components/core/StatusBox';
import { AnonTableCell } from '@components/core/Table/AnonTableCell';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { WarningTooltip } from '@components/core/WarningTooltip';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  householdStatusToColor,
} from '@utils/utils';
import { HouseholdChoiceDataQuery, HouseholdNode } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface HouseholdTableRowProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
  canViewDetails: boolean;
}

export function HouseholdTableRow({
  household,
  choicesData,
  canViewDetails,
}: HouseholdTableRowProps): React.ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const residenceStatusChoiceDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  const householdDetailsPath = `/${baseUrl}/population/household/${household.id}`;
  const handleClick = (): void => {
    navigate(householdDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role="checkbox"
      key={household.unicefId}
      data-cy="household-table-row"
    >
      <TableCell align="left">
        <>
          <Box mr={2}>
            {household.hasDuplicates && (
              <WarningTooltip
                confirmed
                message={t('Houesehold has Duplicates')}
              />
            )}
          </Box>
          <Box mr={2}>
            {household.sanctionListPossibleMatch && (
              <FlagTooltip message={t('Sanction List Possible Match')} />
            )}
          </Box>
          <Box mr={2}>
            {household.sanctionListConfirmedMatch && (
              <FlagTooltip
                message={t('Sanction List Confirmed Match')}
                confirmed
              />
            )}
          </Box>
        </>
      </TableCell>
      <TableCell align="left">
        <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
      </TableCell>
      <TableCell align="left">
        <StatusBox
          status={household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <AnonTableCell>{household.headOfHousehold.fullName}</AnonTableCell>
      <TableCell align="left">{household.size}</TableCell>
      <TableCell align="left">{household.admin2?.name || '-'}</TableCell>
      <TableCell align="left">
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align="right">
        {formatCurrencyWithSymbol(
          household.totalCashReceived,
          household.currency,
        )}
      </TableCell>
      <TableCell align="right">
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

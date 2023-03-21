import { Box } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../components/core/BlackLink';
import { FlagTooltip } from '../../../../components/core/FlagTooltip';
import { StatusBox } from '../../../../components/core/StatusBox';
import { AnonTableCell } from '../../../../components/core/Table/AnonTableCell';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import { WarningTooltip } from '../../../../components/core/WarningTooltip';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  choicesToDict,
  formatCurrencyWithSymbol,
  householdStatusToColor,
} from '../../../../utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../../../__generated__/graphql';

interface HouseHoldTableRowProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
  canViewDetails: boolean;
}

export function HouseHoldTableRow({
  household,
  choicesData,
  canViewDetails,
}: HouseHoldTableRowProps): React.ReactElement {
  const history = useHistory();
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const residenceStatusChoiceDict = choicesToDict(
    choicesData.residenceStatusChoices,
  );
  const householdDetailsPath = `/${businessArea}/population/household/${household.id}`;
  const handleClick = (): void => {
    history.push(householdDetailsPath);
  };
  return (
    <ClickableTableRow
      hover
      onClick={canViewDetails ? handleClick : undefined}
      role='checkbox'
      key={household.unicefId}
      data-cy='household-table-row'
    >
      <TableCell align='left'>
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
      <TableCell align='left'>
        <BlackLink to={householdDetailsPath}>{household.unicefId}</BlackLink>
      </TableCell>
      <TableCell align='left'>
        <StatusBox
          status={household.status}
          statusToColor={householdStatusToColor}
        />
      </TableCell>
      <AnonTableCell>{household.headOfHousehold.fullName}</AnonTableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household.admin2?.name || '-'}</TableCell>
      <TableCell align='left'>
        {residenceStatusChoiceDict[household.residenceStatus]}
      </TableCell>
      <TableCell align='right'>
        {formatCurrencyWithSymbol(
          household.totalCashReceived,
          household.currency,
        )}
      </TableCell>
      <TableCell align='right'>
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

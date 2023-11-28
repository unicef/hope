import { Checkbox, Radio } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import {
  AllHouseholdsForPopulationTableQuery,
  HouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { BlackLink } from '../../../core/BlackLink';
import { ClickableTableRow } from '../../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../core/UniversalMoment';

interface LookUpHouseholdTableRowProps {
  household: AllHouseholdsForPopulationTableQuery['allHouseholds']['edges'][number]['node'];
  radioChangeHandler: (
    household: AllHouseholdsForPopulationTableQuery['allHouseholds']['edges'][number]['node'],
  ) => void;
  selectedHousehold: AllHouseholdsForPopulationTableQuery['allHouseholds']['edges'][number]['node'];
  choicesData: HouseholdChoiceDataQuery;
  checkboxClickHandler?: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    number,
  ) => void;
  selected?: Array<string>;
  householdMultiSelect: boolean;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}

export const LookUpHouseholdTableRow = ({
  household,
  radioChangeHandler,
  selectedHousehold,
  checkboxClickHandler,
  selected,
  householdMultiSelect,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: LookUpHouseholdTableRowProps): React.ReactElement => {
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const isSelected = (id: string): boolean => selected.includes(id);
  const isItemSelected = isSelected(household.id);

  const handleClick = (event): void => {
    event.preventDefault();
    if (householdMultiSelect) {
      checkboxClickHandler(event, household.id);
    } else {
      radioChangeHandler(household);
    }
  };

  const isSelectionDisabled =
    redirectedFromRelatedTicket || isFeedbackWithHouseholdOnly || false;
  return (
    <ClickableTableRow
      onClick={(event) => {
        if (redirectedFromRelatedTicket || isFeedbackWithHouseholdOnly) return;
        handleClick(event);
      }}
      hover
      role='checkbox'
      key={household.id}
      data-cy='household-table-row'
    >
      <TableCell padding='checkbox'>
        {householdMultiSelect ? (
          <Checkbox
            color='primary'
            onClick={(event) => checkboxClickHandler(event, household.id)}
            checked={isItemSelected}
            data-cy='input-checkbox-household'
            inputProps={{ 'aria-labelledby': household.id }}
            disabled={isSelectionDisabled}
          />
        ) : (
          <Radio
            color='primary'
            checked={selectedHousehold?.id === household.id}
            onChange={() => {
              radioChangeHandler(household);
            }}
            value={household.id}
            name='radio-button-household'
            inputProps={{ 'aria-label': household.id }}
            data-cy='input-radio-household'
            disabled={isSelectionDisabled}
          />
        )}
      </TableCell>
      <TableCell align='left'>
        {!isAllPrograms ? (
          <BlackLink to={`/${baseUrl}/population/household/${household.id}`}>
            {household.unicefId}
          </BlackLink>
        ) : (
          <span>{household.unicefId}</span>
        )}
      </TableCell>
      <TableCell align='left'>{household.headOfHousehold.fullName}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household?.admin2?.name || '-'}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
      {isAllPrograms && (
        <TableCell align='left'>
          {household.program ? (
            <BlackLink to={`/${baseUrl}/details/${household.program.id}`}>
              {household.program.name}
            </BlackLink>
          ) : (
            '-'
          )}
        </TableCell>
      )}
    </ClickableTableRow>
  );
};

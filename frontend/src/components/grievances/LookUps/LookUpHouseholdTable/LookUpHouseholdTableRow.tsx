import { Checkbox, Radio } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import {
  AllHouseholdsQuery,
  HouseholdChoiceDataQuery,
} from '../../../../__generated__/graphql';
import { BlackLink } from '../../../core/BlackLink';
import { ClickableTableRow } from '../../../core/Table/ClickableTableRow';
import { UniversalMoment } from '../../../core/UniversalMoment';

interface LookUpHouseholdTableRowProps {
  household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'];
  radioChangeHandler: (
    household: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'],
  ) => void;
  selectedHousehold: AllHouseholdsQuery['allHouseholds']['edges'][number]['node'];
  choicesData: HouseholdChoiceDataQuery;
  checkboxClickHandler?: (
    event:
      | React.MouseEvent<HTMLButtonElement, MouseEvent>
      | React.MouseEvent<HTMLTableRowElement, MouseEvent>,
    number,
  ) => void;
  selected?: Array<string>;
  householdMultiSelect: boolean;
}

export function LookUpHouseholdTableRow({
  household,
  radioChangeHandler,
  selectedHousehold,
  checkboxClickHandler,
  selected,
  householdMultiSelect,
}: LookUpHouseholdTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
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
  const renderPrograms = (): string => {
    const programNames = household.programs?.edges?.map(
      (edge) => edge.node.name,
    );
    return programNames?.length ? programNames.join(', ') : '-';
  };
  return (
    <ClickableTableRow
      onClick={(event) => {
        handleClick(event);
      }}
      hover
      role='checkbox'
      key={household.id}
    >
      <TableCell padding='checkbox'>
        {householdMultiSelect ? (
          <Checkbox
            color='primary'
            onClick={(event) => checkboxClickHandler(event, household.id)}
            checked={isItemSelected}
            inputProps={{ 'aria-labelledby': household.id }}
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
          />
        )}
      </TableCell>
      <TableCell align='left'>
        <BlackLink to={`/${businessArea}/population/household/${household.id}`}>
          {household.unicefId}
        </BlackLink>
      </TableCell>
      <TableCell align='left'>{household.headOfHousehold.fullName}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{household?.admin2?.name || '-'}</TableCell>
      <TableCell align='left'>{renderPrograms()}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

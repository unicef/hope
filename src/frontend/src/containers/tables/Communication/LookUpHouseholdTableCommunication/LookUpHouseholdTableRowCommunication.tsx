import { Checkbox, Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { useBusinessArea } from '@hooks/useBusinessArea';
import { HouseholdChoiceDataQuery } from '@generated/graphql';
import { BlackLink } from '@components/core/BlackLink';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { MouseEvent, ReactElement } from 'react';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';

interface LookUpHouseholdTableRowCommunicationProps {
  household;
  // household: HouseholdDetail;
  radioChangeHandler: (household) => void;
  selectedHousehold: HouseholdDetail;
  choicesData: HouseholdChoiceDataQuery;
  checkboxClickHandler?: (
    event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
    number,
  ) => void;
  selected?: Array<string>;
  householdMultiSelect: boolean;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}

export function LookUpHouseholdTableRowCommunication({
  household,
  radioChangeHandler,
  selectedHousehold,
  checkboxClickHandler,
  selected,
  householdMultiSelect,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: LookUpHouseholdTableRowCommunicationProps): ReactElement {
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

  const isSelectionDisabled =
    redirectedFromRelatedTicket || isFeedbackWithHouseholdOnly || false;
  return (
    <ClickableTableRow
      onClick={(event) => {
        if (redirectedFromRelatedTicket || isFeedbackWithHouseholdOnly) return;
        handleClick(event);
      }}
      hover
      role="checkbox"
      key={household.id}
      data-cy="household-table-row"
    >
      <TableCell padding="checkbox">
        {householdMultiSelect ? (
          <Checkbox
            color="primary"
            onClick={(event) => checkboxClickHandler(event, household.id)}
            checked={isItemSelected}
            data-cy="input-checkbox-household"
            inputProps={{ 'aria-labelledby': household.id }}
            disabled={isSelectionDisabled}
          />
        ) : (
          <Radio
            color="primary"
            checked={selectedHousehold?.id === household.id}
            onChange={() => {
              radioChangeHandler(household);
            }}
            value={household.id}
            name="radio-button-household"
            inputProps={{ 'aria-label': household.id }}
            data-cy="input-radio-household"
            disabled={isSelectionDisabled}
          />
        )}
      </TableCell>
      <TableCell align="left">
        <BlackLink to={`/${businessArea}/population/household/${household.id}`}>
          {household.unicefId}
        </BlackLink>
      </TableCell>
      <TableCell align="left">{household.headOfHousehold.fullName}</TableCell>
      <TableCell align="left">{household.size}</TableCell>
      <TableCell align="left">{household?.admin2 || '-'}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

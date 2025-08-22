import { Checkbox, Radio } from '@mui/material';
import TableCell from '@mui/material/TableCell';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BlackLink } from '@core/BlackLink';
import { ClickableTableRow } from '@core/Table/ClickableTableRow';
import { UniversalMoment } from '@core/UniversalMoment';
import { MouseEvent, ReactElement } from 'react';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { HouseholdList } from '@restgenerated/models/HouseholdList';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';

interface LookUpHouseholdTableRowProps {
  household: HouseholdList;
  radioChangeHandler: (household) => void;
  selectedHousehold: HouseholdDetail;
  choicesData: HouseholdChoices;
  checkboxClickHandler?: (
    event: MouseEvent<HTMLTableRowElement> | MouseEvent<HTMLButtonElement>,
    number,
  ) => void;
  selected?: Array<string>;
  householdMultiSelect: boolean;
  redirectedFromRelatedTicket?: boolean;
  isFeedbackWithHouseholdOnly?: boolean;
}

export function LookUpHouseholdTableRow({
  household,
  radioChangeHandler,
  selectedHousehold,
  checkboxClickHandler,
  selected,
  householdMultiSelect,
  redirectedFromRelatedTicket,
  isFeedbackWithHouseholdOnly,
}: LookUpHouseholdTableRowProps): ReactElement {
  const { baseUrl, isAllPrograms } = useBaseUrl();
  const isSelected = (id: string): boolean => selected.includes(id);
  const isItemSelected = isSelected(household.id);
  const permissions = usePermissions();
  const canViewDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    permissions,
  );

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
            slotProps={{ input: { 'aria-labelledby': household.id } }}
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
            slotProps={{ input: { 'aria-label': household.id } }}
            data-cy="input-radio-household"
            disabled={isSelectionDisabled}
          />
        )}
      </TableCell>
      <TableCell align="left">
        {!isAllPrograms && canViewDetails ? (
          <BlackLink to={`/${baseUrl}/population/household/${household.id}`}>
            {household.unicefId}
          </BlackLink>
        ) : (
          <span>{household.unicefId}</span>
        )}
      </TableCell>
      <TableCell align="left">{household.headOfHousehold}</TableCell>
      <TableCell align="left">{household.size}</TableCell>
      <TableCell align="left">{household?.admin2?.name || '-'}</TableCell>
      <TableCell align="left">
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
      {isAllPrograms && (
        <TableCell align="left">
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
}

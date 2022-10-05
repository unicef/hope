import { Radio } from '@material-ui/core';
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
}

export function LookUpHouseholdTableRow({
  household,
  radioChangeHandler,
  selectedHousehold,
}: LookUpHouseholdTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();
  const renderPrograms = (): string => {
    const programNames = household.programs?.edges?.map(
      (edge) => edge.node.name,
    );
    return programNames?.length ? programNames.join(', ') : '-';
  };
  return (
    <ClickableTableRow
      onClick={() => {
        radioChangeHandler(household);
      }}
      hover
      role='checkbox'
      key={household.id}
      data-cy='household-table-row'
    >
      <TableCell padding='checkbox'>
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

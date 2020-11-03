import { Radio } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import React from 'react';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
} from '../../../__generated__/graphql';
import { Pointer } from '../../Pointer';
import { ClickableTableRow } from '../../table/ClickableTableRow';
import { UniversalMoment } from '../../UniversalMoment';

interface LookUpHouseholdTableRowProps {
  household: HouseholdNode;
  radioChangeHandler: (event: React.ChangeEvent<HTMLInputElement>) => void;
  selectedHousehold: string;
  choicesData: HouseholdChoiceDataQuery;
}

export function LookUpHouseholdTableRow({
  household,
  radioChangeHandler,
  selectedHousehold,
}: LookUpHouseholdTableRowProps): React.ReactElement {
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    const win = window.open(path, '_blank');
    if (win != null) {
      win.focus();
    }
  };
  const renderPrograms = (): string => {
    const programNames = household.programs?.edges?.map(
      (edge) => edge.node.name,
    );
    return programNames?.length ? programNames.join(', ') : '-';
  };
  const renderAdminLevel2 = (): string => {
    if (household?.adminArea?.adminAreaType?.adminLevel === 2) {
      return household?.adminArea?.title;
    }
    return '-';
  };
  return (
    <ClickableTableRow hover role='checkbox' key={household.unicefId}>
      <TableCell padding='checkbox'>
        <Radio
          color='primary'
          checked={selectedHousehold === household.unicefId}
          onChange={radioChangeHandler}
          value={household.unicefId}
          name='radio-button-household'
          inputProps={{ 'aria-label': household.unicefId }}
        />
      </TableCell>
      <TableCell onClick={handleClick} align='left'>
        <Pointer>{household.unicefId}</Pointer>
      </TableCell>
      <TableCell align='left'>{household.headOfHousehold.fullName}</TableCell>
      <TableCell align='left'>{household.size}</TableCell>
      <TableCell align='left'>{renderAdminLevel2()}</TableCell>
      <TableCell align='left'>{renderPrograms()}</TableCell>
      <TableCell align='left'>
        <UniversalMoment>{household.lastRegistrationDate}</UniversalMoment>
      </TableCell>
    </ClickableTableRow>
  );
}

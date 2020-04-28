import React from 'react';
import styled from 'styled-components';
import TableCell from '@material-ui/core/TableCell';
import { useHistory } from 'react-router-dom';
import { HouseholdNode } from '../../../../__generated__/graphql';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { ClickableTableRow } from '../../../../components/table/ClickableTableRow';
import { decodeIdString } from '../../../../utils/utils';

interface TargetPopulationHouseholdTableRowProps {
  household: HouseholdNode;
}

export function TargetPopulationHouseholdTableRow({ household }) {
  const history = useHistory();
  const businessArea = useBusinessArea();

  const handleClick = (): void => {
    const path = `/${businessArea}/population/household/${household.id}`;
    history.push(path);
  };
  return (
    <ClickableTableRow
      hover
      onClick={handleClick}
      role='checkbox'
      key={household.id}
    >
      <TableCell align='left'>{decodeIdString(household.id)}</TableCell>
      <TableCell align='left'>{`${household.headOfHousehold.firstName} ${household.headOfHousehold.lastName}`}</TableCell>
      <TableCell align='left'>{household.familySize}</TableCell>
      <TableCell align='left'>-</TableCell>
      <TableCell align='left'>{household.location.title}</TableCell>
    </ClickableTableRow>
  );
}

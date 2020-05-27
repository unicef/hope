import React, { ReactElement } from 'react';
import styled from 'styled-components';
import { Table, TableHead, TableRow, TableCell, TableBody } from '@material-ui/core';
import { useFlexFieldsQuery } from '../../../../__generated__/graphql';
import { headCells } from './HeadCells';
import { FlexFieldRow } from './TableRow';

const TableWrapper = styled.div`
  padding: 0;
`;

interface TargetPopulationHouseholdProps {
  id?: string;
  query?;
  queryObjectName?;
  variables?;
}

export const FlexFieldsTable = (): ReactElement => {
  const { data } = useFlexFieldsQuery();
  console.log(data);
  if (!data) {
    return null;
  }
  return (
    <TableWrapper>
      <Table aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.allFieldsAttributes.map((row) => (
            <TableRow key={row.name}>
              <TableCell component="th" scope="row">
                {row.name}
              </TableCell>
              <TableCell>{row.type}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableWrapper>
  );
};

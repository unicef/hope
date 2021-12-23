import React, { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { Table, TableBody, TableCell, TableRow } from '@material-ui/core';
import { EnhancedTableHead } from '../../../../components/Table/EnhancedTableHead';
import { getComparator, stableSort } from '../../../../utils/utils';
import { AllFieldsAttributesQuery } from '../../../../__generated__/graphql';
import { headCells } from './HeadCells';

const TableWrapper = styled.div`
  padding: 0;
`;

const StyledCell = styled(TableCell)`
  width: 70%;
`;

type Order = 'asc' | 'desc';

export const FlexFieldsTable = ({
  fields,
  selectedOption,
  searchValue,
  selectedFieldType,
}): ReactElement => {
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('');

  const handleRequestSort = (event, property): void => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const filterTable = (): AllFieldsAttributesQuery['allFieldsAttributes'] => {
    const filters = {
      labelEn: searchValue,
      associatedWith: selectedOption,
    };
    let filteredByFieldType = [];
    if (selectedFieldType === 'All') {
      filteredByFieldType = fields;
    } else if (selectedFieldType === 'Flex field') {
      filteredByFieldType = fields.filter((el) => el.isFlexField === true);
    } else if (selectedFieldType === 'Core field') {
      filteredByFieldType = fields.filter((el) => el.isFlexField === false);
    }
    return filteredByFieldType.filter((each) => {
      //eslint-disable-next-line
      for (const key in filters) {
        if (
          each[key] === undefined ||
          (each[key] !== filters[key] &&
            !each[key].toLowerCase().includes(filters[key].toLowerCase()))
        ) {
          return false;
        }
      }
      return true;
    });
  };
  type orderedType = () => AllFieldsAttributesQuery['allFieldsAttributes'];
  const orderResults: orderedType = () => {
    return stableSort(filterTable(), getComparator(order, orderBy));
  };

  return (
    <TableWrapper>
      <Table aria-label='simple table'>
        <EnhancedTableHead
          order={order as Order}
          headCells={headCells}
          orderBy={orderBy}
          onRequestSort={handleRequestSort}
          rowCount={fields.length - 1}
        />
        <TableBody>
          {orderResults().map((row) => (
            <TableRow key={row.id}>
              <StyledCell>{row.labelEn}</StyledCell>
              <TableCell>{row.associatedWith}</TableCell>
              <TableCell>
                {row.isFlexField ? 'Flex field' : 'Core field'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableWrapper>
  );
};

import TableCell from '@material-ui/core/TableCell';
import React, { ReactElement, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { BlackLink } from '../../../../components/core/BlackLink';
import { StatusBox } from '../../../../components/core/StatusBox';
import { ClickableTableRow } from '../../../../components/core/Table/ClickableTableRow';
import { HeadCell } from '../../../../components/core/Table/EnhancedTableHead';
import {
  Order,
  TableComponent,
} from '../../../../components/core/Table/TableComponent';
import { UniversalMoment } from '../../../../components/core/UniversalMoment';
import {
  choicesToDict,
  populationStatusToColor,
  sexToCapitalize,
} from '../../../../utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
  IndividualNode,
} from '../../../../__generated__/graphql';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';

const headCells: HeadCell<IndividualNode>[] = [
  {
    disablePadding: false,
    label: 'Individual ID',
    id: 'unicefId',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Individual',
    id: 'fullName',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Status',
    id: 'status',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Role',
    id: 'role',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Relationship to HoH',
    id: 'relationship',
    numeric: false,
  },
  {
    disablePadding: false,
    label: 'Date of Birth',
    id: 'birthDate',
    numeric: true,
  },
  {
    disablePadding: false,
    label: 'Gender',
    id: 'sex',
    numeric: false,
  },
];

interface HouseholdIndividualsTableProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}
export function HouseholdIndividualsTable({
  household,
  choicesData,
}: HouseholdIndividualsTableProps): ReactElement {
  const history = useHistory();
  const { baseUrl } = useBaseUrl();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const handleClick = (row): void => {
    history.push(`/${baseUrl}/population/individuals/${row.id}`);
  };

  const relationshipChoicesDict = choicesToDict(
    choicesData?.relationshipChoices,
  );
  const roleChoicesDict = choicesToDict(choicesData?.roleChoices);
  const allIndividuals = household?.individuals?.edges?.map(
    (edge) => edge.node,
  );
  if (orderBy) {
    if (orderDirection === 'asc') {
      allIndividuals.sort((a, b) => {
        return a[orderBy] < b[orderBy] ? 1 : -1;
      });
    } else {
      allIndividuals.sort((a, b) => {
        return a[orderBy] > b[orderBy] ? 1 : -1;
      });
    }
  }

  const totalCount = allIndividuals.length;
  return (
    <TableComponent<IndividualNode>
      title='Individuals in Household'
      data={allIndividuals.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      )}
      allowSort={false}
      renderRow={(row) => {
        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role='checkbox'
            key={row.id}
          >
            <TableCell align='left'>
              <BlackLink to={`/${baseUrl}/population/individuals/${row.id}`}>
                {row.unicefId}
              </BlackLink>
            </TableCell>
            <TableCell align='left'>{row.fullName}</TableCell>
            <TableCell align='left'>
              <StatusBox
                status={row.status}
                statusToColor={populationStatusToColor}
              />
            </TableCell>
            <TableCell align='left'>{roleChoicesDict[row.role]}</TableCell>
            <TableCell align='left'>
              {household?.id === row?.household?.id
                ? relationshipChoicesDict[row.relationship]
                : relationshipChoicesDict.NON_BENEFICIARY}
            </TableCell>
            <TableCell align='left'>
              <UniversalMoment>{row.birthDate}</UniversalMoment>
            </TableCell>
            <TableCell align='left'>{sexToCapitalize(row.sex)}</TableCell>
          </ClickableTableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={totalCount < 5 ? [totalCount] : [5, 10, 15]}
      rowsPerPage={totalCount > 5 ? rowsPerPage : totalCount}
      page={page}
      itemsCount={totalCount}
      handleChangePage={(event, newPage) => {
        setPage(newPage);
      }}
      handleChangeRowsPerPage={(event) => {
        setRowsPerPage(Number(event.target.value));
        setPage(0);
      }}
      handleRequestSort={(event, property) => {
        let direction = 'asc';
        if (property === orderBy) {
          direction = orderDirection === 'asc' ? 'desc' : 'asc';
        }
        setOrderBy(property);
        setOrderDirection(direction);
      }}
      orderBy={orderBy}
      order={orderDirection as Order}
    />
  );
}

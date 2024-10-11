import TableCell from '@mui/material/TableCell';
import React, { ReactElement, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { Order, TableComponent } from '@components/core/Table/TableComponent';
import { choicesToDict } from '@utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
  IndividualNode,
  IndividualRoleInHouseholdRole,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Bold } from '@components/core/Bold';
import { BlackLink } from '@components/core/BlackLink';

const headCells: HeadCell<IndividualNode>[] = [
  {
    disablePadding: false,
    label: 'Role',
    id: 'role',
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
    label: 'Relationship to Household',
    id: 'relationship',
    numeric: false,
  },
];

interface CollectorsTableProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}
export const CollectorsTable = ({
  household,
  choicesData,
}: CollectorsTableProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const handleClick = (row): void => {
    navigate(`/${baseUrl}/population/individuals/${row.id}`);
  };

  const roleChoicesDict = choicesToDict(choicesData?.roleChoices);
  const relationshipChoicesDict = choicesToDict(
    choicesData?.relationshipChoices,
  );

  const allCollectors =
    household?.individuals?.edges
      ?.map((edge) => edge.node)
      .filter(
        (el) =>
          el.role === IndividualRoleInHouseholdRole.Alternate ||
          el.role === IndividualRoleInHouseholdRole.Primary,
      ) || [];

  if (orderBy) {
    if (orderDirection === 'asc') {
      allCollectors.sort((a, b) => (a[orderBy] < b[orderBy] ? 1 : -1));
    } else {
      allCollectors.sort((a, b) => (a[orderBy] > b[orderBy] ? 1 : -1));
    }
  }

  const sortedCollectors = allCollectors.sort((a, b) => {
    if (a.role === IndividualRoleInHouseholdRole.Primary) {
      return -1;
    } else if (b.role === IndividualRoleInHouseholdRole.Primary) {
      return 1;
    } else if (a.role === IndividualRoleInHouseholdRole.Alternate) {
      return -1;
    } else if (b.role === IndividualRoleInHouseholdRole.Alternate) {
      return 1;
    } else {
      return 0;
    }
  });
  const totalCount = allCollectors.length;
  return (
    <TableComponent<IndividualNode>
      title="Collectors"
      data={sortedCollectors.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      )}
      allowSort={false}
      renderRow={(row) => {
        const isHead = row.relationship === 'HEAD';

        const renderTableCellContent = (content: React.ReactNode) => {
          return isHead ? <Bold>{content}</Bold> : content;
        };

        const renderRelationship = (): string | React.ReactElement => {
          if (!row.household) {
            return 'Not a beneficiary';
          }
          if (household?.id !== row?.household?.id) {
            return (
              <BlackLink
                to={`/${baseUrl}/population/household/${row.household.id}`}
              >
                Member of {row.household.unicefId}
              </BlackLink>
            );
          }
          if (household?.id === row?.household?.id) {
            return (
              <span>
                {renderTableCellContent(
                  relationshipChoicesDict[row.relationship],
                )}
              </span>
            );
          }
        };

        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role="checkbox"
            key={row.id}
          >
            <TableCell align="left">{roleChoicesDict[row.role]}</TableCell>
            <TableCell align="left">{row.fullName}</TableCell>
            <TableCell align="left">{renderRelationship()}</TableCell>
          </ClickableTableRow>
        );
      }}
      headCells={headCells}
      rowsPerPageOptions={totalCount < 5 ? [totalCount] : [5, 10, 15]}
      rowsPerPage={totalCount > 5 ? rowsPerPage : totalCount}
      page={page}
      itemsCount={totalCount}
      handleChangePage={(_event, newPage) => {
        setPage(newPage);
      }}
      handleChangeRowsPerPage={(event) => {
        setRowsPerPage(Number(event.target.value));
        setPage(0);
      }}
      handleRequestSort={(_event, property) => {
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
};

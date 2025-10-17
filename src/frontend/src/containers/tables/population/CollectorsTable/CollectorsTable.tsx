import { BlackLink } from '@components/core/BlackLink';
import { Bold } from '@components/core/Bold';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { Order, TableComponent } from '@components/core/Table/TableComponent';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableCell from '@mui/material/TableCell';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { IndividualSimple } from '@restgenerated/models/IndividualSimple';
import { PaginatedHouseholdMemberList } from '@restgenerated/models/PaginatedHouseholdMemberList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { adjustHeadCells, choicesToDict } from '@utils/utils';
import { ReactElement, ReactNode, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';

const headCells: HeadCell<IndividualSimple>[] = [
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
  household: HouseholdDetail;
  choicesData: IndividualChoices;
}
export const CollectorsTable = ({
  household,
  choicesData,
}: CollectorsTableProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const handleClick = (row): void => {
    navigate(`/${baseUrl}/population/individuals/${row.id}`);
  };
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const replacements = {
    fullName: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel}`,
    relationship: (_beneficiaryGroup) =>
      `Relationship to ${_beneficiaryGroup?.groupLabel}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  const roleChoicesDict = choicesToDict(choicesData?.roleChoices);
  const relationshipChoicesDict = choicesToDict(
    choicesData?.relationshipChoices,
  );

  const { data, isLoading, error } = useQuery<PaginatedHouseholdMemberList>({
    queryKey: [
      'businessAreasProgramsHouseholdsMembers',
      programId,
      businessArea,
      household.id,
    ],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsMembersList({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: household.id,
      }),
    enabled: !!businessArea && !!programId && !!household?.id,
  });

  if (isLoading) {
    return <LoadingComponent />;
  }

  if (error) {
    console.error('Error loading household members:', error);
    return <div>Error loading collectors. Please try again.</div>;
  }

  // Extract collectors from the response
  const allCollectors = (data?.results || []).filter(
    (collector) => collector.role !== 'NONE',
  );

  let sortedCollectors = [...allCollectors];

  if (orderBy) {
    if (orderDirection === 'asc') {
      sortedCollectors.sort((a, b) => (a[orderBy] < b[orderBy] ? 1 : -1));
    } else {
      sortedCollectors.sort((a, b) => (a[orderBy] > b[orderBy] ? 1 : -1));
    }
  }

  // Sort collectors by role (PRIMARY first, then ALTERNATE)
  sortedCollectors = sortedCollectors.sort((a, b) => {
    if (a.role === 'PRIMARY') {
      return -1;
    } else if (b.role === 'PRIMARY') {
      return 1;
    } else if (a.role === 'ALTERNATE') {
      return -1;
    } else if (b.role === 'ALTERNATE') {
      return 1;
    } else {
      return 0;
    }
  });

  const totalCount = allCollectors.length;

  return (
    <TableComponent
      title="Collectors"
      data={sortedCollectors.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      )}
      allowSort={false}
      renderRow={(row) => {
        const isHead = row.relationship === 'HEAD';

        const renderTableCellContent = (content: ReactNode) => {
          return isHead ? <Bold>{content}</Bold> : content;
        };

        const renderRelationship = (): string | ReactElement => {
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
      headCells={adjustedHeadCells}
      rowsPerPageOptions={totalCount < 5 ? [totalCount || 1] : [5, 10, 15]}
      rowsPerPage={totalCount > 5 ? rowsPerPage : totalCount || 1}
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

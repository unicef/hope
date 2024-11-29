import TableCell from '@mui/material/TableCell';
import { ReactElement, ReactNode, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BlackLink } from '@components/core/BlackLink';
import { StatusBox } from '@components/core/StatusBox';
import { ClickableTableRow } from '@components/core/Table/ClickableTableRow';
import { HeadCell } from '@components/core/Table/EnhancedTableHead';
import { Order, TableComponent } from '@components/core/Table/TableComponent';
import { UniversalMoment } from '@components/core/UniversalMoment';
import {
  adjustHeadCells,
  choicesToDict,
  populationStatusToColor,
  sexToCapitalize,
} from '@utils/utils';
import {
  HouseholdChoiceDataQuery,
  HouseholdNode,
  IndividualNode,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Bold } from '@components/core/Bold';
import { useProgramContext } from 'src/programContext';

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

interface HouseholdMembersTableProps {
  household: HouseholdNode;
  choicesData: HouseholdChoiceDataQuery;
}
export const HouseholdMembersTable = ({
  household,
  choicesData,
}: HouseholdMembersTableProps): ReactElement => {
  const navigate = useNavigate();
  const { baseUrl } = useBaseUrl();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [orderBy, setOrderBy] = useState(null);
  const [orderDirection, setOrderDirection] = useState('asc');
  const handleClick = (row): void => {
    navigate(`/${baseUrl}/population/individuals/${row.id}`);
  };

  const relationshipChoicesDict = choicesToDict(
    choicesData?.relationshipChoices,
  );
  const allIndividuals = household?.individuals?.edges?.map(
    (edge) => edge.node,
  );
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  if (orderBy) {
    if (orderDirection === 'asc') {
      allIndividuals.sort((a, b) => (a[orderBy] < b[orderBy] ? 1 : -1));
    } else {
      allIndividuals.sort((a, b) => (a[orderBy] > b[orderBy] ? 1 : -1));
    }
  }

  const totalCount = allIndividuals.length;

  const replacements = {
    unicefId: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel} ID`,
    fullName: (_beneficiaryGroup) => `${_beneficiaryGroup?.memberLabel}`,
    relationship: (_beneficiaryGroup) =>
      `Relationship to Head of ${_beneficiaryGroup?.groupLabel}`,
  };

  const adjustedHeadCells = adjustHeadCells(
    headCells,
    beneficiaryGroup,
    replacements,
  );

  return (
    <TableComponent<IndividualNode>
      title={`${beneficiaryGroup?.groupLabel} Members`}
      data={allIndividuals.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      )}
      allowSort={false}
      renderRow={(row) => {
        const isHead = row.relationship === 'HEAD';

        const renderTableCellContent = (content: ReactNode) => {
          return isHead ? <Bold>{content}</Bold> : content;
        };

        return (
          <ClickableTableRow
            hover
            onClick={() => handleClick(row)}
            role="checkbox"
            key={row.id}
          >
            <TableCell align="left">
              {renderTableCellContent(
                <BlackLink to={`/${baseUrl}/population/individuals/${row.id}`}>
                  {row.unicefId}
                </BlackLink>,
              )}
            </TableCell>
            <TableCell align="left">
              {renderTableCellContent(row.fullName)}
            </TableCell>
            <TableCell align="left">
              <StatusBox
                status={row.status}
                statusToColor={populationStatusToColor}
              />
            </TableCell>
            <TableCell align="left">
              {renderTableCellContent(
                household?.id === row?.household?.id
                  ? relationshipChoicesDict[row.relationship]
                  : relationshipChoicesDict.NON_BENEFICIARY,
              )}
            </TableCell>
            <TableCell align="right">
              {renderTableCellContent(
                <UniversalMoment>{row.birthDate}</UniversalMoment>,
              )}
            </TableCell>
            <TableCell align="left">
              {renderTableCellContent(sexToCapitalize(row.sex))}
            </TableCell>
          </ClickableTableRow>
        );
      }}
      headCells={adjustedHeadCells}
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

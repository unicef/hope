import type { Dispatch, FC, SetStateAction } from 'react';
import { useState } from 'react';
import { BaseSection } from '@components/core/BaseSection';
import type { PaginatedPaymentPlanManagerialList } from '@restgenerated/models/PaginatedPaymentPlanManagerialList';
import type {
  BulkActionMutation,
  SelectAllHandler,
  SelectHandler,
} from './types';
import {
  Table,
  TableContainer,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Box,
  TableSortLabel,
  TableBody,
  InputAdornment,
  TextField,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useTranslation } from 'react-i18next';
import { AuthorizePaymentPlansModal } from '@components/managerialConsole/AuthorizePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ProgramSelect, useSortAndFilter } from './useSortAndFilter';
import { getVisibleSelection } from './visibleSelection';
import { showApiErrorMessages } from '@utils/utils';
import { responsiveValue } from 'src/responsive';

interface AuthorizationSectionProps {
  selectedAuthorized: string[];
  setSelectedAuthorized: Dispatch<SetStateAction<string[]>>;
  handleSelect: SelectHandler;
  handleSelectAll: SelectAllHandler;
  inAuthorizationData: PaginatedPaymentPlanManagerialList;
  bulkAction: BulkActionMutation;
  enableSearch?: boolean;
}

export const AuthorizationSection: FC<AuthorizationSectionProps> = ({
  selectedAuthorized,
  setSelectedAuthorized,
  handleSelect,
  handleSelectAll,
  inAuthorizationData,
  bulkAction,
  enableSearch = false,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const [searchText, setSearchText] = useState('');

  const {
    sortField,
    sortDirection,
    selectedProgram,
    setSelectedProgram,
    handleSort,
    sortRows,
    filterRows,
  } = useSortAndFilter({ initialSortField: null, initialSortDirection: 'asc' });

  const programs = inAuthorizationData?.results?.reduce<string[]>(
    (acc, row) => {
      if (!acc.includes(row.program)) {
        acc.push(row.program);
      }
      return acc;
    },
    [],
  );

  const columns = [
    {
      field: 'unicefId',
      headerName: t('Payment Plan ID'),
      width: 200,
      renderCell: (params) => (
        <BlackLink
          to={`/${businessArea}/programs/${params.row.programCode}/payment-module/payment-plans/${params.row.id}`}
          newTab={true}
        >
          {params.value}
        </BlackLink>
      ),
    },
    { field: 'name', headerName: t('Name'), width: 200 },
    { field: 'program', headerName: t('Programme Name'), width: 200 },
    {
      field: 'lastApprovalProcessDate',
      headerName: t('Last Modified Date'),
      width: 200,
      renderCell: (params) => <UniversalMoment>{params.value}</UniversalMoment>,
    },
    {
      field: 'lastApprovalProcessBy',
      headerName: t('Approved by'),
      width: 200,
    },
  ];

  const filteredRows = filterRows(
    inAuthorizationData?.results || [],
    'lastApprovalProcessDate',
    searchText,
    columns,
  );
  const sortedRows = sortRows(filteredRows);

  const {
    visibleIds,
    visibleSelectedIds,
    selectedPlansUnicefIds,
    allSelected,
  } = getVisibleSelection(sortedRows, selectedAuthorized);

  const handleSelectAllAuthorized = () => {
    handleSelectAll(visibleIds, visibleSelectedIds, setSelectedAuthorized);
  };

  // Drop the selection so plans hidden by the filter do not come back selected.
  const handleProgramChange = (program: string) => {
    setSelectedProgram(program);
    setSelectedAuthorized([]);
  };

  const handleSearchChange = (text: string) => {
    setSearchText(text);
    setSelectedAuthorized([]);
  };

  const title = t('Payment Plans pending for Authorization');

  const buttons = (
    <>
      {enableSearch && (
        <TextField
          label="Search"
          value={searchText}
          size="small"
          data-cy="search-authorization"
          onChange={(e) => handleSearchChange(e.target.value)}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            },
          }}
        />
      )}
      <AuthorizePaymentPlansModal
        selectedPlansIds={visibleSelectedIds}
        selectedPlansUnicefIds={selectedPlansUnicefIds}
        onAuthorize={async (_, comment) => {
          try {
            await bulkAction.mutateAsync({
              ids: visibleSelectedIds,
              action: 'AUTHORIZE',
              comment: comment,
            });
            showMessage(t('Payment Plan(s) Authorized'));
            setSelectedAuthorized([]);
          } catch (e) {
            showApiErrorMessages(e, showMessage);
          }
        }}
      />
    </>
  );

  return (
    <BaseSection title={title} buttons={buttons}>
      <TableContainer>
        <Table sx={{ minWidth: responsiveValue<number | string>(700, 'auto') }}>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox" style={{ width: '10%' }}>
                <Box sx={{ flex: 1 }}>
                  <Checkbox
                    checked={allSelected}
                    onClick={handleSelectAllAuthorized}
                    data-cy="select-all-authorization"
                  />
                </Box>
              </TableCell>
              {columns.map((column) => (
                <TableCell key={column.field}>
                  {column.field === 'program' ? (
                    <ProgramSelect
                      selectedProgram={selectedProgram}
                      setSelectedProgram={handleProgramChange}
                      programs={programs}
                      dataCy="program-select-authorization"
                    />
                  ) : (
                    <TableSortLabel
                      active={sortField === column.field}
                      direction={sortDirection}
                      onClick={() => handleSort(column.field)}
                    >
                      {column.headerName}
                    </TableSortLabel>
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRows.map((row) => (
              <TableRow key={row.id}>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={visibleSelectedIds.includes(row.id)}
                    onChange={() =>
                      handleSelect(
                        visibleSelectedIds,
                        setSelectedAuthorized,
                        row.id,
                      )
                    }
                    data-cy="select-authorization"
                  />
                </TableCell>
                {columns.map((column) => (
                  <TableCell
                    key={column.field}
                    align="left"
                    data-cy="column-field-authorization"
                  >
                    {column.renderCell
                      ? column.renderCell({ value: row[column.field], row })
                      : row[column.field]}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </BaseSection>
  );
};

import type { Dispatch, FC, SetStateAction } from 'react';
import { useState } from 'react';
import { BaseSection } from '@components/core/BaseSection';
import type { PaginatedPaymentPlanList } from '@restgenerated/models/PaginatedPaymentPlanList';
import type {
  BulkActionMutation,
  SelectAllHandler,
  SelectHandler,
} from './types';
import {
  Table,
  TableContainer,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Box,
  InputAdornment,
  TextField,
  TableSortLabel,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { useTranslation } from 'react-i18next';
import { ReleasePaymentPlansModal } from '@components/managerialConsole/ReleasePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ProgramSelect, useSortAndFilter } from './useSortAndFilter';
import { getVisibleSelection } from './visibleSelection';
import { showApiErrorMessages } from '@utils/utils';
import { responsiveValue } from 'src/responsive';

interface PendingForReleaseSectionProps {
  selectedInReview: string[];
  setSelectedInReview: Dispatch<SetStateAction<string[]>>;
  handleSelect: SelectHandler;
  handleSelectAll: SelectAllHandler;
  inReviewData: PaginatedPaymentPlanList;
  bulkAction: BulkActionMutation;
  enableSearch?: boolean;
}

export const PendingForReleaseSection: FC<PendingForReleaseSectionProps> = ({
  selectedInReview,
  setSelectedInReview,
  handleSelect,
  handleSelectAll,
  inReviewData,
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

  const programs = inReviewData?.results?.reduce<string[]>((acc, row) => {
    if (!acc.includes(row.program)) {
      acc.push(row.program);
    }
    return acc;
  }, []);

  const columns = [
    {
      field: 'unicefId',
      headerName: t('Payment Plan ID'),
      width: 200,
      renderCell: (params) => (
        <BlackLink
          to={`/${businessArea}/programs/${params.row.programCode}/payment-module/${params.row.planType === 'FOLLOW_UP' ? 'followup-payment-plans' : 'payment-plans'}/${params.row.id}`}
          newTab={true}
        >
          {params.value}
        </BlackLink>
      ),
    },
    { field: 'program', headerName: t('Programme Name'), width: 200 },
    {
      field: 'lastApprovalProcessDate',
      headerName: t('Last Modified Date'),
      width: 200,
      renderCell: (params) => <UniversalMoment>{params.value}</UniversalMoment>,
    },
    {
      field: 'lastApprovalProcessBy',
      headerName: t('Authorized by'),
      width: 200,
    },
  ];

  const filteredRows = filterRows(
    inReviewData?.results || [],
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
  } = getVisibleSelection(sortedRows, selectedInReview);

  const handleSelectAllReviewed = () => {
    handleSelectAll(visibleIds, visibleSelectedIds, setSelectedInReview);
  };

  // Drop the selection so plans hidden by the filter do not come back selected.
  const handleProgramChange = (program: string) => {
    setSelectedProgram(program);
    setSelectedInReview([]);
  };

  const handleSearchChange = (text: string) => {
    setSearchText(text);
    setSelectedInReview([]);
  };

  const title = t('Payment Plans pending for Release');

  const buttons = (
    <>
      {enableSearch && (
        <TextField
          label="Search"
          value={searchText}
          size="small"
          onChange={(e) => handleSearchChange(e.target.value)}
          data-cy="search-release"
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
      <ReleasePaymentPlansModal
        selectedPlansIds={visibleSelectedIds}
        selectedPlansUnicefIds={selectedPlansUnicefIds}
        onRelease={async (_, comment) => {
          try {
            await bulkAction.mutateAsync({
              ids: visibleSelectedIds,
              action: 'REVIEW',
              comment: comment,
            });
            showMessage(t('Payment Plan(s) Released'));
            setSelectedInReview([]);
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
                    onClick={handleSelectAllReviewed}
                    data-cy="select-all-release"
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
                      dataCy="program-select-release"
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
                        setSelectedInReview,
                        row.id,
                      )
                    }
                    data-cy="select-release"
                  />
                </TableCell>
                {columns.map((column) => (
                  <TableCell
                    key={column.field}
                    align="left"
                    data-cy="column-field-release"
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

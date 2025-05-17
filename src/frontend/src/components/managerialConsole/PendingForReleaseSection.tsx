import React, { FC, SetStateAction, useState } from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
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

interface PendingForReleaseSectionProps {
  selectedInReview: any[];
  setSelectedInReview: (value: SetStateAction<any[]>) => void;
  handleSelect: (
    selected: any[],
    setSelected: (value: SetStateAction<any[]>) => void,
    id: any,
  ) => void;
  handleSelectAll: (
    ids: any[],
    selected: any[],
    setSelected: {
      (value: SetStateAction<any[]>): void;
      (arg0: any[]): void;
    },
  ) => void;
  inReviewData: any;
  bulkAction: any;
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

  const handleSelectAllReviewed = () => {
    const ids = inReviewData?.results?.map((plan) => plan.id);
    handleSelectAll(ids, selectedInReview, setSelectedInReview);
  };

  const programs = inReviewData?.results?.reduce((acc, row) => {
    if (!acc.includes(row.program)) {
      acc.push(row.program);
    }
    return acc;
  }, []);

  const allSelected = inReviewData?.results?.every((plan) =>
    selectedInReview.includes(plan.id),
  );

  const selectedPlansUnicefIds = inReviewData?.results
    .filter((plan) => selectedInReview.includes(plan.id))
    .map((plan) => plan.unicefId);

  const columns = [
    {
      field: 'unicef_id',
      headerName: t('Payment Plan ID'),
      width: 200,
      renderCell: (params) => (
        <BlackLink
          to={`/${businessArea}/programs/${params.row.program_id}/payment-module/${params.row.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${params.row.id}`}
          newTab={true}
        >
          {params.value}
        </BlackLink>
      ),
    },
    { field: 'program', headerName: t('Programme Name'), width: 200 },
    {
      field: 'last_approval_process_date',
      headerName: t('Last Modified Date'),
      width: 200,
      renderCell: (params) => <UniversalMoment>{params.value}</UniversalMoment>,
    },
    {
      field: 'last_approval_process_by',
      headerName: t('Authorized by'),
      width: 200,
    },
  ];

  const filteredRows = filterRows(
    inReviewData?.results || [],
    'last_approval_process_date',
    searchText,
    columns,
  );
  const sortedRows = sortRows(filteredRows);

  const title = t('Payment Plans pending for Release');

  const buttons = (
    <>
      {enableSearch && (
        <TextField
          label="Search"
          value={searchText}
          size="small"
          onChange={(e) => setSearchText(e.target.value)}
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
        selectedPlansIds={selectedInReview}
        selectedPlansUnicefIds={selectedPlansUnicefIds}
        onRelease={async (_, comment) => {
          try {
            await bulkAction.mutateAsync({
              ids: selectedInReview,
              action: 'REVIEW',
              comment: comment,
            });
            showMessage(t('Payment Plan(s) Released'));
            setSelectedInReview([]);
          } catch (e) {
            showMessage(e.message);
          }
        }}
      />
    </>
  );

  return (
    <BaseSection title={title} buttons={buttons}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox" style={{ width: '10%' }}>
              <Box sx={{ flex: 1 }}>
                <Checkbox
                  checked={allSelected && selectedInReview.length > 0}
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
                    setSelectedProgram={setSelectedProgram}
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
                  checked={selectedInReview.includes(row.id)}
                  onChange={() =>
                    handleSelect(selectedInReview, setSelectedInReview, row.id)
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
    </BaseSection>
  );
};

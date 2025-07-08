import React, { FC, SetStateAction, useState } from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
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
import { ApprovePaymentPlansModal } from '@components/managerialConsole/ApprovePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ProgramSelect, useSortAndFilter } from './useSortAndFilter';
import { showApiErrorMessages } from '@utils/utils';
import { error } from 'console';

interface ApprovalSectionProps {
  selectedApproved: any[];
  setSelectedApproved: (value: SetStateAction<any[]>) => void;
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
  inApprovalData: any;
  bulkAction: any;
  enableSearch?: boolean;
}

export const ApprovalSection: FC<ApprovalSectionProps> = ({
  selectedApproved,
  setSelectedApproved,
  handleSelect,
  handleSelectAll,
  inApprovalData,
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

  const handleSelectAllApproved = () => {
    const ids = inApprovalData.results.map((plan) => plan.id);
    handleSelectAll(ids, selectedApproved, setSelectedApproved);
  };

  const programs = inApprovalData?.results?.reduce((acc, row) => {
    if (!acc.includes(row.program)) {
      acc.push(row.program);
    }
    return acc;
  }, []);

  const allSelected = inApprovalData?.results?.every((plan) =>
    selectedApproved.includes(plan.id),
  );

  const selectedPlansUnicefIds = inApprovalData?.results
    .filter((plan) => selectedApproved.includes(plan.id))
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
      headerName: t('Sent for Approval by'),
      width: 200,
    },
  ];

  const filteredRows = filterRows(
    inApprovalData?.results || [],
    'last_approval_process_date',
    searchText,
    columns,
  );
  const sortedRows = sortRows(filteredRows);

  const title = t('Payment Plans pending for Approval');

  const buttons = (
    <>
      {enableSearch && (
        <TextField
          label="Search"
          value={searchText}
          data-cy="search-approval"
          size="small"
          onChange={(e) => setSearchText(e.target.value)}
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
      <ApprovePaymentPlansModal
        selectedPlansIds={selectedApproved}
        selectedPlansUnicefIds={selectedPlansUnicefIds}
        onApprove={async (_, comment) => {
          try {
            await bulkAction.mutateAsync({
              ids: selectedApproved,
              action: 'APPROVE',
              comment: comment,
            });
            showMessage(t('Payment Plan(s) Approved'));
            setSelectedApproved([]);
          } catch (e) {
            showApiErrorMessages(error, showMessage);
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
                  data-cy="select-all-approval"
                  checked={allSelected && selectedApproved.length > 0}
                  onClick={handleSelectAllApproved}
                />
              </Box>
            </TableCell>
            {columns.map((column) => (
              <TableCell key={column.field}>
                {column.field === 'program' ? (
                  <ProgramSelect
                    dataCy="program-select-approval"
                    selectedProgram={selectedProgram}
                    setSelectedProgram={setSelectedProgram}
                    programs={programs}
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
                  data-cy="select-approval"
                  checked={selectedApproved.includes(row.id)}
                  onChange={() =>
                    handleSelect(selectedApproved, setSelectedApproved, row.id)
                  }
                />
              </TableCell>
              {columns.map((column) => (
                <TableCell
                  data-cy="column-field"
                  key={column.field}
                  align="left"
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

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
import { AuthorizePaymentPlansModal } from '@components/managerialConsole/AuthorizePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ProgramSelect, useSortAndFilter } from './useSortAndFilter';
import { showApiErrorMessages } from '@utils/utils';

interface AuthorizationSectionProps {
  selectedAuthorized: any[];
  setSelectedAuthorized: (value: SetStateAction<any[]>) => void;
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
  inAuthorizationData: any;
  bulkAction: any;
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

  const handleSelectAllAuthorized = () => {
    const ids = inAuthorizationData.results.map((plan) => plan.id);
    handleSelectAll(ids, selectedAuthorized, setSelectedAuthorized);
  };

  const programs = inAuthorizationData?.results?.reduce((acc, row) => {
    if (!acc.includes(row.program)) {
      acc.push(row.program);
    }
    return acc;
  }, []);

  const allSelected = inAuthorizationData?.results?.every((plan) =>
    selectedAuthorized.includes(plan.id),
  );

  const selectedPlansUnicefIds = inAuthorizationData?.results
    .filter((plan) => selectedAuthorized.includes(plan.id))
    .map((plan) => plan.unicefId);

  const columns = [
    {
      field: 'unicefId',
      headerName: t('Payment Plan ID'),
      width: 200,
      renderCell: (params) => (
        <BlackLink
          to={`/${businessArea}/programs/${params.row.programId}/payment-module/${params.row.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${params.row.id}`}
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

  const title = t('Payment Plans pending for Authorization');

  const buttons = (
    <>
      {enableSearch && (
        <TextField
          label="Search"
          value={searchText}
          size="small"
          data-cy="search-authorization"
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
      <AuthorizePaymentPlansModal
        selectedPlansIds={selectedAuthorized}
        selectedPlansUnicefIds={selectedPlansUnicefIds}
        onAuthorize={async (_, comment) => {
          try {
            await bulkAction.mutateAsync({
              ids: selectedAuthorized,
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
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox" style={{ width: '10%' }}>
              <Box sx={{ flex: 1 }}>
                <Checkbox
                  checked={allSelected && selectedAuthorized.length > 0}
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
                    setSelectedProgram={setSelectedProgram}
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
                  checked={selectedAuthorized.includes(row.id)}
                  onChange={() =>
                    handleSelect(
                      selectedAuthorized,
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
    </BaseSection>
  );
};

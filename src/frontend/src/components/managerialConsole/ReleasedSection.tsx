import { BaseSection } from '@components/core/BaseSection';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import SearchIcon from '@mui/icons-material/Search';
import {
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TextField,
} from '@mui/material';
import React, { FC, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramSelect, useSortAndFilter } from './useSortAndFilter';

interface ReleasedSectionProps {
  releasedData: any;
}

export const ReleasedSection: FC<ReleasedSectionProps> = ({ releasedData }) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
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

  const programs = releasedData?.results?.reduce((acc, row) => {
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
          to={`/${businessArea}/programs/${params.row.programId}/payment-module/${params.row.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${params.row.id}`}
          newTab={true}
        >
          {params.value}
        </BlackLink>
      ),
    },
    { field: 'program', headerName: t('Programme Name'), width: 200 },
    {
      field: 'totalEntitledQuantityUsd',
      headerName: t('Total Entitled Quantity (USD)'),
      width: 200,
      renderCell: (params) => <>{params.value || '-'}</>,
    },
    {
      field: 'lastApprovalProcessDate',
      headerName: t('Released on'),
      width: 200,
      renderCell: (params) => <UniversalMoment>{params.value}</UniversalMoment>,
    },
    {
      field: 'lastApprovalProcessBy',
      headerName: t('Released by'),
      width: 200,
    },
  ];

  const filteredRows = filterRows(
    releasedData?.results || [],
    'lastApprovalProcessDate',
    searchText,
    columns,
  );
  const sortedRows = sortRows(filteredRows);

  const title = t('Released Payment Plans');

  const buttons = (
    <TextField
      label="Search"
      value={searchText}
      size="small"
      onChange={(e) => setSearchText(e.target.value)}
      data-cy="search-released"
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
  );

  return (
    <BaseSection title={title} buttons={buttons}>
      <>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column.field}>
                    {column.field === 'program' ? (
                      <ProgramSelect
                        selectedProgram={selectedProgram}
                        setSelectedProgram={setSelectedProgram}
                        programs={programs}
                        dataCy="program-select-released"
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
                  {columns.map((column) => (
                    <TableCell
                      key={column.field}
                      data-cy="column-field-released"
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
      </>
    </BaseSection>
  );
};

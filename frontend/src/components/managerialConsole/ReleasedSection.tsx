import React, { useState } from 'react';
import { BaseSection } from '@components/core/BaseSection';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';
import {
  TextField,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface ReleasedSectionProps {
  releasedData: any;
}

export const ReleasedSection: React.FC<ReleasedSectionProps> = ({
  releasedData,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [searchText, setSearchText] = useState('');
  const [sortField, setSortField] = useState(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const handleSort = (field) => {
    const newSortDirection =
      sortField === field && sortDirection === 'asc' ? 'desc' : 'asc';
    setSortField(field);
    setSortDirection(newSortDirection);
  };

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
      headerName: t('Released on'),
      width: 200,
      renderCell: (params) => <UniversalMoment>{params.value}</UniversalMoment>,
    },
    {
      field: 'last_approval_process_by',
      headerName: t('Released by'),
      width: 200,
    },
  ];

  const filteredRows =
    releasedData?.results?.filter((row: any) =>
      columns.some((column) => {
        if (column.field === 'last_approval_process_date') {
          const date = moment(row[column.field]).format('D MMMM YYYY');
          return date.toLowerCase().includes(searchText.toLowerCase());
        }
        return row[column.field]
          ?.toString()
          .toLowerCase()
          .includes(searchText.toLowerCase());
      }),
    ) || [];

  const sortedRows = [...filteredRows].sort((a, b) => {
    if (a[sortField] < b[sortField]) {
      return sortDirection === 'asc' ? -1 : 1;
    }
    if (a[sortField] > b[sortField]) {
      return sortDirection === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const title = t('Released Payment Plans');

  const buttons = (
    <TextField
      label="Search"
      value={searchText}
      size="small"
      onChange={(e) => setSearchText(e.target.value)}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <SearchIcon />
          </InputAdornment>
        ),
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
                    <TableSortLabel
                      active={sortField === column.field}
                      direction={sortDirection}
                      onClick={() => handleSort(column.field)}
                    >
                      {column.headerName}
                    </TableSortLabel>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedRows.map((row) => (
                <TableRow key={row.id}>
                  {columns.map((column) => (
                    <TableCell key={column.field}>
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

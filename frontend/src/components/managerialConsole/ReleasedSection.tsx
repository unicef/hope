import React, { useState } from 'react';
import { BaseSection } from '@components/core/BaseSection';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { DataGrid } from '@mui/x-data-grid';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { TextField, InputAdornment } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface ReleasedSectionProps {
  ReleasedData: any;
}

export const ReleasedSection: React.FC<ReleasedSectionProps> = ({
  ReleasedData,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [searchText, setSearchText] = useState('');

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
      field: 'released_on_date',
      headerName: t('Released on'),
      width: 200,
      renderCell: (params) => <UniversalMoment>{params.value}</UniversalMoment>,
    },
    { field: 'released_by', headerName: t('Released by'), width: 200 },
  ];

  const filteredRows =
    ReleasedData?.results?.filter((row: any) =>
      columns.some((column) =>
        row[column.field]
          ?.toString()
          .toLowerCase()
          .includes(searchText.toLowerCase()),
      ),
    ) || [];

  return (
    <BaseSection title={t('Released Payment Plans')}>
      <>
        <TextField
          label="Search"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <DataGrid
          rows={filteredRows}
          columns={columns}
          pageSize={5}
          rowsPerPageOptions={[5]}
          checkboxSelection={false}
          disableSelectionOnClick
        />
      </>
    </BaseSection>
  );
};

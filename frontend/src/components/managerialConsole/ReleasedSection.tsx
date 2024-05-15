import React from 'react';
import { BaseSection } from '@components/core/BaseSection';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { DataGrid } from '@mui/x-data-grid';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';

interface ReleasedSectionProps {
  ReleasedData: any;
}

export const ReleasedSection: React.FC<ReleasedSectionProps> = ({
  ReleasedData,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();

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

  return (
    <BaseSection title={t('Released Payment Plans')}>
      <DataGrid
        rows={ReleasedData?.results || []}
        columns={columns}
        pageSize={5}
        rowsPerPageOptions={[5]}
        checkboxSelection={false}
        disableSelectionOnClick
      />
    </BaseSection>
  );
};

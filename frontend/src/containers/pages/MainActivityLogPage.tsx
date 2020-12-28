import React from 'react';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { MainActivityLogTable } from '../tables/MainActivityLogTable/MainActivityLogTable';

export const ActivityLogPage = () => {
  const businessArea = useBusinessArea();
  return (
    <div>
      <PageHeader title='Activity Log' />
      <MainActivityLogTable businessArea={businessArea} />
    </div>
  );
};

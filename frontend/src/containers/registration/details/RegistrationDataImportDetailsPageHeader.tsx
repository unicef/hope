import React from 'react';
import { RegistrationDetailedFragment } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
}

export function RegistrationDataImportDetailsPageHeader({
  registration,
}: RegistrationDataImportDetailsPageHeaderPropTypes): React.ReactElement {
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
  ];
  return (
    <PageHeader title={registration.name} breadCrumbs={breadCrumbsItems} />
  );
}

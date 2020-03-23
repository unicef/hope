import React from 'react';
import {
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
} from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ApproveRegistrationDataImportDialog } from './ApproveRegistrationDataImportDialog';
import { UnapproveRegistrationDataImportDialog } from './UnapproveRegistrationDataImportDialog';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
}

export function RegistrationDataImportDetailsPageHeader({
  registration,
}: RegistrationDataImportDetailsPageHeaderPropTypes): React.ReactElement {
  let buttons = null;
  // eslint-disable-next-line default-case
  switch (registration.status) {
    case RegistrationDataImportStatus.InReview:
      buttons = (
        <ApproveRegistrationDataImportDialog registration={registration} />
      );
      break;
    case RegistrationDataImportStatus.Approved:
      buttons = (
        <UnapproveRegistrationDataImportDialog registration={registration} />
      );
      break;
  }

  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
  ];
  return (
    <PageHeader title={registration.name} breadCrumbs={breadCrumbsItems}>
      {buttons}
    </PageHeader>
  );
}

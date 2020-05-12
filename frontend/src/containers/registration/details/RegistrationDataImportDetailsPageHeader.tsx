import React from 'react';
import styled from 'styled-components';
import {
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
} from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { ApproveRegistrationDataImportDialog } from './ApproveRegistrationDataImportDialog';
import { UnapproveRegistrationDataImportDialog } from './UnapproveRegistrationDataImportDialog';
import { MergeRegistrationDataImportDialog } from './MergeRegistrationDataImportDialog';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
}

const MergeButtonContainer = styled.span`
  margin-left: ${({ theme }) => theme.spacing(4)}px;
`;

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
        <div>
          <UnapproveRegistrationDataImportDialog registration={registration} />
          <MergeButtonContainer>
            <MergeRegistrationDataImportDialog registration={registration} />
          </MergeButtonContainer>
        </div>
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

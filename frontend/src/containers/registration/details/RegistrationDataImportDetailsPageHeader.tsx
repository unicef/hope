import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { Link } from 'react-router-dom';
import ListItem from '@material-ui/core/ListItem';
import {
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
} from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { MergeRegistrationDataImportDialog } from './MergeRegistrationDataImportDialog';
import { RerunDedupe } from './RerunDedupe';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
  canMerge: boolean;
  canRerunDedupe: boolean;
  canViewList: boolean;
}

const MergeButtonContainer = styled.span`
  margin-left: ${({ theme }) => theme.spacing(4)}px;
`;

export function RegistrationDataImportDetailsPageHeader({
  registration,
  canMerge,
  canRerunDedupe,
  canViewList,
}: RegistrationDataImportDetailsPageHeaderPropTypes): React.ReactElement {
  const businessArea = useBusinessArea();
  let buttons = null;
  // eslint-disable-next-line default-case
  switch (registration?.status) {
    case RegistrationDataImportStatus.InReview:
      buttons = (
        <div>
          {canMerge && (
            <MergeButtonContainer>
              <MergeRegistrationDataImportDialog registration={registration} />
            </MergeButtonContainer>
          )}
        </div>
      );
      break;
    case RegistrationDataImportStatus.DeduplicationFailed:
      buttons = (
        <div>
          {canRerunDedupe && (
            <MergeButtonContainer>
              <RerunDedupe registration={registration} />
            </MergeButtonContainer>
          )}
        </div>
      );
      break;
    case RegistrationDataImportStatus.Merged:
      buttons = (
        <div>
          {canRerunDedupe && (
            <MergeButtonContainer>
              <Button
                variant='contained'
                color='primary'
                component={Link}
                to={`/${businessArea}/grievance-and-feedback/rdi/${registration.id}`}
              >
                View Tickets
              </Button>
            </MergeButtonContainer>
          )}
        </div>
      );
      break;
  }

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
  ];
  return (
    <PageHeader
      title={registration.name}
      breadCrumbs={canViewList ? breadCrumbsItems : null}
    >
      {buttons}
    </PageHeader>
  );
}

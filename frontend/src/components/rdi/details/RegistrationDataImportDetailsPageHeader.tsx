import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import {
  ProgramStatus,
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
  useEraseRdiMutation,
  useRefuseRdiMutation,
} from '../../../__generated__/graphql';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { BreadCrumbsItem } from '../../core/BreadCrumbs';
import { useConfirmation } from '../../core/ConfirmationDialog';
import { LoadingButton } from '../../core/LoadingButton';
import { PageHeader } from '../../core/PageHeader';
import { useProgramContext } from "../../../programContext";
import { MergeRegistrationDataImportDialog } from './MergeRegistrationDataImportDialog';
import { RerunDedupe } from './RerunDedupe';
import { RefuseRdiForm } from './refuseRdiForm';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
  canMerge: boolean;
  canRerunDedupe: boolean;
  canViewList: boolean;
  canRefuse: boolean;
}

const MergeButtonContainer = styled.span`
  margin-left: ${({ theme }) => theme.spacing(4)}px;
`;

export const RegistrationDataImportDetailsPageHeader = ({
  registration,
  canMerge,
  canRerunDedupe,
  canViewList,
  canRefuse,
}: RegistrationDataImportDetailsPageHeaderPropTypes): React.ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const confirm = useConfirmation();
  const { selectedProgram } = useProgramContext();
  const [refuseMutate, { loading: refuseLoading }] = useRefuseRdiMutation();
  const [eraseRdiMutate, { loading: eraseLoading }] = useEraseRdiMutation();
  const [showRefuseRdiForm, setShowRefuseRdiForm] = useState(false);

  let buttons = null;

  const eraseButton = (
    <LoadingButton
      loading={eraseLoading}
      onClick={() =>
        confirm({
          title: t('Warning'),
          content: t(
            'Are you sure you want to erase RDI? Erasing RDI causes deletion of all related datahub RDI data',
          ),
        }).then(async () => {
          await eraseRdiMutate({
            variables: { id: registration.id },
          });
        })
      }
      variant='contained'
      color='primary'
      disabled={selectedProgram?.status !== ProgramStatus.Active}
    >
      {t('Erase import')}
    </LoadingButton>
  );
  // eslint-disable-next-line default-case
  switch (registration?.status) {
    case RegistrationDataImportStatus.ImportError:
    case RegistrationDataImportStatus.MergeError:
      buttons = <div>{canRefuse && eraseButton}</div>;
      break;
    case RegistrationDataImportStatus.InReview:
      buttons = (
        <div>
          {canMerge && canRefuse && (
            <LoadingButton
              loading={refuseLoading}
              onClick={() => setShowRefuseRdiForm(true)}
              variant='contained'
              color='primary'
              disabled={selectedProgram?.status !== ProgramStatus.Active}
            >
              {t('Refuse Import')}
            </LoadingButton>
          )}
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
          {canRefuse && eraseButton}
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
        <MergeButtonContainer>
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${baseUrl}/grievance/rdi/${registration.id}`}
            >
              {t('View Tickets')}
            </Button>
        </MergeButtonContainer>
      );
      break;
  }

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Registration Data import'),
      to: `/${baseUrl}/registration-data-import/`,
    },
  ];

  return (
    <>
      <PageHeader
        title={registration.name}
        breadCrumbs={canViewList ? breadCrumbsItems : null}
      >
        {registration.erased ? null : buttons}
      </PageHeader>
      <RefuseRdiForm
        open={showRefuseRdiForm}
        refuseMutate={refuseMutate}
        onClose={() => setShowRefuseRdiForm(false)}
        registration={registration}
      />
    </>
  );
};

import { Button } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
  RegistrationDataImportStatus,
  RegistrationDetailedFragment,
  useEraseRdiMutation,
  useRefuseRdiMutation,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { useConfirmation } from '@core/ConfirmationDialog';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';
import { useProgramContext } from '../../../programContext';
import MergeRegistrationDataImportDialog from './MergeRegistrationDataImportDialog';
import { RerunDedupe } from './RerunDedupe';
import { RefuseRdiForm } from './refuseRdiForm';
import { AdminButton } from '@core/AdminButton';
import withErrorBoundary from '@components/core/withErrorBoundary';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDetailedFragment;
  canMerge: boolean;
  canRerunDedupe: boolean;
  canViewList: boolean;
  canRefuse: boolean;
}

const MergeButtonContainer = styled.span`
  margin-left: ${({ theme }) => theme.spacing(4)};
`;

const RegistrationDataImportDetailsPageHeader = ({
  registration,
  canMerge,
  canRerunDedupe,
  canViewList,
  canRefuse,
}: RegistrationDataImportDetailsPageHeaderPropTypes): ReactElement => {
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  const confirm = useConfirmation();
  const navigate = useNavigate();
  const { isActiveProgram } = useProgramContext();
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
      variant="contained"
      color="primary"
      disabled={!isActiveProgram}
      data-cy="button-erase-rdi"
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
              variant="contained"
              color="primary"
              disabled={!isActiveProgram}
              data-cy="button-refuse-rdi"
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
            variant="contained"
            color="primary"
            component={Link}
            data-cy="button-view-tickets"
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
      to: '..',
    },
  ];

  return (
    <>
      <PageHeader
        title={registration.name}
        breadCrumbs={canViewList ? breadCrumbsItems : null}
        handleBack={() => navigate('..')}
        flags={<AdminButton adminUrl={registration.adminUrl} />}
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

export default withErrorBoundary(
  RegistrationDataImportDetailsPageHeader,
  'RegistrationDataImportDetailsPageHeader',
);

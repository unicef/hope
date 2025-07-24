import { Button } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
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
import { RegistrationDataImportStatusEnum } from '@restgenerated/models/RegistrationDataImportStatusEnum';
import { RegistrationDataImportDetail } from '@restgenerated/models/RegistrationDataImportDetail';
import { useActionMutation } from '@hooks/useActionMutation';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { RefuseRdi } from '@restgenerated/models/RefuseRdi';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationDataImportDetail;
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
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const confirm = useConfirmation();
  const navigate = useNavigate();
  const client = useQueryClient();
  const { isActiveProgram } = useProgramContext();
  const { mutateAsync: refuseMutate, isPending: refuseLoading } = useMutation({
    mutationFn: async (data: RefuseRdi) => {
      return RestService.restBusinessAreasProgramsRegistrationDataImportsRefuseCreate(
        {
          id: registration.id,
          businessAreaSlug,
          programSlug,
          requestBody: data,
        },
      );
    },
    onSuccess: () => {
      client.invalidateQueries({
        queryKey: [
          RestService.restBusinessAreasProgramsRegistrationDataImportsRetrieve
            .name,
        ],
      });
    },
  });
  const { mutateAsync: eraseRdiMutate, isPending: eraseLoading } =
    useActionMutation(
      registration.id,
      RestService.restBusinessAreasProgramsRegistrationDataImportsEraseCreate,
      [
        RestService.restBusinessAreasProgramsRegistrationDataImportsRetrieve
          .name,
      ],
    );
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
          await eraseRdiMutate();
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
    case RegistrationDataImportStatusEnum.IMPORT_ERROR:
    case RegistrationDataImportStatusEnum.MERGE_ERROR:
      buttons = <div>{canRefuse && eraseButton}</div>;
      break;
    case RegistrationDataImportStatusEnum.IN_REVIEW:
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
    case RegistrationDataImportStatusEnum.DEDUPLICATION_FAILED:
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
    case RegistrationDataImportStatusEnum.MERGED:
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

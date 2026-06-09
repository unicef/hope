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
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { RefuseRdi } from '@restgenerated/models/RefuseRdi';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { IngestSourceEnum } from '@restgenerated/models/IngestSourceEnum';

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
  const { businessAreaSlug, programCode } = useBaseUrl();
  const confirm = useConfirmation();
  const navigate = useNavigate();
  const client = useQueryClient();
  const { isActiveProgram } = useProgramContext();
  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({ slug: businessAreaSlug }),
  });
  const isManualIngest =
    businessAreaData?.ingestSource !== IngestSourceEnum.COUNTRY_WORKSPACE_ONLY;
  const { mutateAsync: refuseMutate, isPending: refuseLoading } = useMutation({
    mutationFn: async (data: RefuseRdi) => {
      return RestService.restBusinessAreasProgramsRegistrationDataImportsRefuseCreate(
        {
          id: registration.id,
          businessAreaSlug,
          programCode,
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

  switch (registration?.status) {
    case RegistrationDataImportStatusEnum.IMPORT_ERROR:
    case RegistrationDataImportStatusEnum.MERGE_ERROR:
      buttons = <div>{isManualIngest && canRefuse && eraseButton}</div>;
      break;
    case RegistrationDataImportStatusEnum.IN_REVIEW:
      buttons = (
        <div>
          {isManualIngest &&
            !registration.countryWorkspaceId &&
            canMerge &&
            canRefuse && (
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
          {isManualIngest && !registration.countryWorkspaceId && canMerge && (
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
          {isManualIngest && canRefuse && eraseButton}
          {isManualIngest && !registration.countryWorkspaceId && canRerunDedupe && (
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

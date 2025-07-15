import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { IndividualAccounts } from '@components/population/IndividualAccounts';
import { IndividualAdditionalRegistrationInformation } from '@components/population/IndividualAdditionalRegistrationInformation/IndividualAdditionalRegistrationInformation';
import { IndividualBioData } from '@components/population/IndividualBioData/IndividualBioData';
import { ProgrammeTimeSeriesFields } from '@components/population/ProgrammeTimeSeriesFields';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';
import { AdminButton } from '@components/core/AdminButton';
import { IndividualFlags } from '@components/population/IndividualFlags';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const PopulationIndividualsDetailsPage = (): ReactElement => {
  const { id } = useParams();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const { t } = useTranslation();

  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();

  const {
    data: individual,
    isLoading: loadingIndividual,
    error,
  } = useHopeDetailsQuery<IndividualDetail>(
    id,
    RestService.restBusinessAreasProgramsIndividualsRetrieve,
    {},
  );

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<IndividualChoices>({
      queryKey: ['individualChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: flexFieldsData, isLoading: flexFieldsDataLoading } = useQuery({
    queryKey: ['fieldsAttributes', businessArea, programId],
    queryFn: async () => {
      const data =
        await RestService.restBusinessAreasProgramsIndividualsAllFlexFieldsAttributesList(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
          },
        );
      return { allIndividualsFlexFieldsAttributes: data.results };
    },
  });

  const { data: grievancesChoices, isLoading: grievancesChoicesLoading } =
    useQuery({
      queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: periodicFieldsData, isLoading: periodicFieldsLoading } =
    useQuery({
      queryKey: ['periodicFields', businessArea, programId],
      queryFn: () =>
        RestService.restBusinessAreasProgramsPeriodicFieldsList({
          businessAreaSlug: businessArea,
          programSlug: programId,
          limit: 1000,
        }),
    });

  if (
    loadingIndividual ||
    choicesLoading ||
    flexFieldsDataLoading ||
    grievancesChoicesLoading ||
    periodicFieldsLoading
  )
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !individual ||
    !choicesData ||
    !flexFieldsData ||
    !grievancesChoices ||
    !periodicFieldsData ||
    permissions === null
  )
    return null;

  let breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: `${beneficiaryGroup?.memberLabelPlural}`,
      to: `/${baseUrl}/population/individuals`,
    },
  ];

  const breadcrumbTitle = location?.state?.breadcrumbTitle;
  const breadcrumbUrl = location?.state?.breadcrumbUrl;

  if (breadcrumbTitle && breadcrumbUrl) {
    breadCrumbsItems = [
      {
        title: breadcrumbTitle,
        to: breadcrumbUrl,
      },
    ];
  }

  return (
    <>
      <PageHeader
        title={`${t(`${beneficiaryGroup?.memberLabel} ID`)}: ${individual?.unicefId}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        flags={
          <>
            <IndividualFlags individual={individual} />
            <AdminButton adminUrl={individual?.adminUrl} />
          </>
        }
      >
        <Box mr={2}>
          {individual?.photo ? (
            <IndividualPhotoModal individual={individual} />
          ) : null}
        </Box>
      </PageHeader>
      <Container>
        <IndividualBioData
          baseUrl={baseUrl}
          businessArea={businessArea}
          individual={individual}
          choicesData={choicesData}
          grievancesChoices={grievancesChoices}
        />
        <IndividualAccounts individual={individual} />
        <IndividualAdditionalRegistrationInformation
          flexFieldsData={flexFieldsData}
          individual={individual}
        />
        <ProgrammeTimeSeriesFields
          individual={individual}
          periodicFieldsData={periodicFieldsData}
        />
        {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
          <UniversalActivityLogTable objectId={individual?.id} />
        )}
      </Container>
    </>
  );
};
export default withErrorBoundary(
  PopulationIndividualsDetailsPage,
  'PopulationIndividualsDetailsPage',
);

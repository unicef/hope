import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { IndividualAdditionalRegistrationInformation } from '@components/population/IndividualAdditionalRegistrationInformation/IndividualAdditionalRegistrationInformation';
import { IndividualBioData } from '@components/population/IndividualBioData/IndividualBioData';
import { IndividualAccounts } from '@components/population/IndividualAccounts';
import { ProgrammeTimeSeriesFields } from '@components/population/ProgrammeTimeSeriesFields';
import { useAllIndividualsFlexFieldsAttributesQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { RestService } from '@restgenerated/services/RestService';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';

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
  } = useQuery<IndividualDetail>({
    queryKey: ['businessAreaProgramIndividual', businessArea, programId, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsIndividualsRetrieve({
        businessAreaSlug: businessArea,
        programSlug: programId,
        id: id,
      }),
  });

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: flexFieldsData, loading: flexFieldsDataLoading } =
    useAllIndividualsFlexFieldsAttributesQuery();

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
      title: `${beneficiaryGroup?.groupLabelPlural}`,
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
            {/*<IndividualFlags individual={individual} />  TODO REST refactor*/}
            {/* //TODO: Rest refactor */}
            {/* <AdminButton adminUrl={individual?.adminUrl} /> */}
          </>
        }
      >
        <Box mr={2}>
          {/* //TODO: Rest refactor */}
          {/* {individual?.photo ? (
            <IndividualPhotoModal individual={individual} />
          ) : null} */}
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

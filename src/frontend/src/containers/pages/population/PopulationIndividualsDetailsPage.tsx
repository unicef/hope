import { fetchPeriodicFields } from '@api/periodicDataUpdateApi';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { IndividualAdditionalRegistrationInformation } from '@components/population/IndividualAdditionalRegistrationInformation/IndividualAdditionalRegistrationInformation';
import { IndividualBioData } from '@components/population/IndividualBioData/IndividualBioData';
import { IndividualAccounts } from '@components/population/IndividualAccounts';
import { IndividualFlags } from '@components/population/IndividualFlags';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';
import { ProgrammeTimeSeriesFields } from '@components/population/ProgrammeTimeSeriesFields';
import { AdminButton } from '@core/AdminButton';
import {
  IndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
  useHouseholdChoiceDataQuery,
  useIndividualQuery,
} from '@generated/graphql';
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

  const { data, loading, error } = useIndividualQuery({
    variables: {
      id,
    },
    fetchPolicy: 'cache-and-network',
  });

  const { data: choicesData, loading: choicesLoading } =
    useHouseholdChoiceDataQuery();

  const { data: flexFieldsData, loading: flexFieldsDataLoading } =
    useAllIndividualsFlexFieldsAttributesQuery();

  const { data: grievancesChoices, loading: grievancesChoicesLoading } =
    useGrievancesChoiceDataQuery();

  const { data: periodicFieldsData, isLoading: periodicFieldsLoading } =
    useQuery({
      queryKey: ['periodicFields', businessArea, programId],
      queryFn: () =>
        fetchPeriodicFields(businessArea, programId, { limit: 1000 }),
    });

  if (
    loading ||
    choicesLoading ||
    flexFieldsDataLoading ||
    grievancesChoicesLoading ||
    periodicFieldsLoading
  )
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !data ||
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

  const { individual } = data;

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
            <IndividualPhotoModal individual={individual as IndividualNode} />
          ) : null}
        </Box>
      </PageHeader>
      <Container>
        <IndividualBioData
          baseUrl={baseUrl}
          businessArea={businessArea}
          individual={individual as IndividualNode}
          choicesData={choicesData}
          grievancesChoices={grievancesChoices}
        />
        <IndividualAccounts individual={individual as IndividualNode} />
        <IndividualAdditionalRegistrationInformation
          flexFieldsData={flexFieldsData}
          individual={individual as IndividualNode}
        />
        <ProgrammeTimeSeriesFields
          individual={individual as IndividualNode}
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

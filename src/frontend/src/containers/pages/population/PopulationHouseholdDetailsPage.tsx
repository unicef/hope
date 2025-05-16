import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { FlagTooltip } from '@components/core/FlagTooltip';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { Missing } from '@components/core/Missing';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { Title } from '@components/core/Title';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { WarningTooltip } from '@components/core/WarningTooltip';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { HouseholdAdditionalRegistrationInformation } from '@components/population/HouseholdAdditionalRegistrationInformation/HouseholdAdditionalRegistrationInformation';
import { HouseholdDetails } from '@components/population/HouseholdDetails';
import PaymentsHouseholdTable from '@containers/tables/payments/PaymentsHouseholdTable/PaymentsHouseholdTable';
import { AdminButton } from '@core/AdminButton';
import {
  useAllHouseholdsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box, Grid2 as Grid, Typography } from '@mui/material';
import Paper from '@mui/material/Paper';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError, renderSomethingOrDash } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { HouseholdCompositionTable } from '../../tables/population/HouseholdCompositionTable/HouseholdCompositionTable';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { Theme } from '@mui/material/styles';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Overview = styled(Paper)<{ theme?: Theme }>`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: 20px;
  &:first-child {
    margin-top: 0;
  }
`;

const SubTitle = styled(Typography)`
  && {
    font-size: 16px;
  }
`;

const PopulationHouseholdDetailsPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { baseUrl, businessArea } = useBaseUrl();

  const location = useLocation();
  const permissions = usePermissions();
  const { programId } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const {
    data: household,
    isLoading: householdLoading,
    error,
  } = useQuery<HouseholdDetail>({
    queryKey: ['household', businessArea, id, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsHouseholdsRetrieve({
        businessAreaSlug: businessArea,
        id,
        programSlug: programId,
      }),
  });

  const { data: flexFieldsData, loading: flexFieldsDataLoading } =
    useAllHouseholdsFlexFieldsAttributesQuery();

  const { data: householdChoicesData, isLoading: householdChoicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: grievancesChoices, loading: grievancesChoicesLoading } =
    useGrievancesChoiceDataQuery();

  if (
    householdChoicesLoading ||
    flexFieldsDataLoading ||
    grievancesChoicesLoading ||
    householdLoading
  )
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !householdChoicesData ||
    !grievancesChoices ||
    !flexFieldsData ||
    permissions === null ||
    !household
  )
    return null;

  let breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: beneficiaryGroup?.groupLabelPlural,
      to: `/${baseUrl}/population/household`,
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
        title={`${beneficiaryGroup?.groupLabel}: ${renderSomethingOrDash(
          household?.unicefId,
        )}`}
        breadCrumbs={
          hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST,
            permissions,
          )
            ? breadCrumbsItems
            : null
        }
        flags={
          <>
            <Box mr={2}>
              {household?.hasDuplicates && (
                <WarningTooltip
                  confirmed
                  message={`${beneficiaryGroup?.groupLabel} has Duplicates`}
                />
              )}
            </Box>
            <Box mr={2}>
              {household?.sanctionListPossibleMatch && (
                <FlagTooltip message={t('Sanction List Possible Match')} />
              )}
            </Box>
            <Box mr={2}>
              {household?.sanctionListConfirmedMatch && (
                <FlagTooltip
                  message={t('Sanction List Confirmed Match')}
                  confirmed
                />
              )}
            </Box>
            <AdminButton adminUrl={household?.adminUrl} />
          </>
        }
      />
      <HouseholdDetails
        household={household}
        baseUrl={baseUrl}
        businessArea={businessArea}
        grievancesChoices={grievancesChoices}
      />
      <HouseholdCompositionTable household={household} />
      <Container>
        <Missing />
        {/* //TODO: */}
        {/* {household?.individuals?.edges?.length ? (
          <>
            <HouseholdMembersTable
              choicesData={choicesData}
              household={household}
            />
            <CollectorsTable choicesData={choicesData} household={household} />
          </>
        ) : null} */}
        {hasPermissions(
          PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
          permissions,
        ) && (
          <PaymentsHouseholdTable
            openInNewTab
            household={household}
            businessArea={businessArea}
            canViewPaymentRecordDetails={hasPermissions(
              PERMISSIONS.PM_VIEW_PAYMENT_LIST,
              permissions,
            )}
          />
        )}
        <HouseholdAdditionalRegistrationInformation
          household={household}
          flexFieldsData={flexFieldsData}
        />
        <Overview>
          <Title>
            <Typography variant="h6">{t('Registration Details')}</Typography>
          </Title>
          <Grid container spacing={6}>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Source')}>
                <div>{household?.registrationDataImport?.dataSource}</div>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Import name')}>
                <div>{household?.registrationDataImport?.name}</div>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Registration Date')}>
                <div>
                  <UniversalMoment>
                    {household?.lastRegistrationDate}
                  </UniversalMoment>
                </div>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('User name')}>
                {<Missing />}
                {household?.registrationDataImport.importedBy.email}
              </LabelizedField>
            </Grid>
            {/* {household?.programRegistrationId && (
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Programme registration id')}>
                  {household.programRegistrationId}
                </LabelizedField>
              </Grid>
            )} */}
          </Grid>
          {household?.registrationDataImport?.dataSource === 'XLS' ? null : (
            <>
              <hr />
              <SubTitle variant="h6">{t('Data Collection')}</SubTitle>
              <Grid container spacing={6}>
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('Start time')}>
                    <UniversalMoment>{household?.start}</UniversalMoment>
                  </LabelizedField>
                </Grid>
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('End time')}>
                    <UniversalMoment>
                      {household?.firstRegistrationDate}
                    </UniversalMoment>
                  </LabelizedField>
                </Grid>
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('Device ID')}>
                    {household?.deviceid}
                  </LabelizedField>
                </Grid>
              </Grid>
            </>
          )}
        </Overview>
      </Container>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={household?.id} />
      )}
    </>
  );
};

export default withErrorBoundary(
  PopulationHouseholdDetailsPage,
  'PopulationHouseholdDetailsPage',
);

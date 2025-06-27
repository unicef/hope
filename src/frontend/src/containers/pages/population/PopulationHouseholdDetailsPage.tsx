import { Box, Grid2 as Grid, Typography } from '@mui/material';
import Paper from '@mui/material/Paper';
import { useTranslation } from 'react-i18next';
import { useLocation, useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  HouseholdNode,
  useAllHouseholdsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
  useHouseholdChoiceDataQuery,
  useHouseholdQuery,
} from '@generated/graphql';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { FlagTooltip } from '@components/core/FlagTooltip';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { Title } from '@components/core/Title';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { WarningTooltip } from '@components/core/WarningTooltip';
import { HouseholdDetails } from '@components/population/HouseholdDetails';
import { HouseholdAdditionalRegistrationInformation } from '@components/population/HouseholdAdditionalRegistrationInformation/HouseholdAdditionalRegistrationInformation';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError, renderSomethingOrDash } from '@utils/utils';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { HouseholdCompositionTable } from '../../tables/population/HouseholdCompositionTable/HouseholdCompositionTable';
import { AdminButton } from '@core/AdminButton';
import { CollectorsTable } from '@containers/tables/population/CollectorsTable';
import { HouseholdMembersTable } from '@containers/tables/population/HouseholdMembersTable';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import PaymentsHouseholdTable from '@containers/tables/payments/PaymentsHouseholdTable/PaymentsHouseholdTable';

const Container = styled.div`
  padding: 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;

const Overview = styled(Paper)`
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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const { data, loading, error } = useHouseholdQuery({
    variables: { id },
    fetchPolicy: 'cache-and-network',
  });
  const { data: flexFieldsData, loading: flexFieldsDataLoading } =
    useAllHouseholdsFlexFieldsAttributesQuery();
  const { data: choicesData, loading: choicesLoading } =
    useHouseholdChoiceDataQuery();
  const { data: grievancesChoices, loading: grievancesChoicesLoading } =
    useGrievancesChoiceDataQuery();

  if (
    loading ||
    choicesLoading ||
    flexFieldsDataLoading ||
    grievancesChoicesLoading
  )
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !data ||
    !choicesData ||
    !grievancesChoices ||
    !flexFieldsData ||
    permissions === null
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

  const { household } = data;

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
        choicesData={choicesData}
        household={household as HouseholdNode}
        baseUrl={baseUrl}
        businessArea={businessArea}
        grievancesChoices={grievancesChoices}
      />
      <HouseholdCompositionTable household={household as HouseholdNode} />
      <Container>
        {household?.individuals?.edges?.length ? (
          <>
            <HouseholdMembersTable
              choicesData={choicesData}
              household={household as HouseholdNode}
            />
            <CollectorsTable
              choicesData={choicesData}
              household={household as HouseholdNode}
            />
          </>
        ) : null}
        {hasPermissions(
          PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
          permissions,
        ) && (
          <PaymentsHouseholdTable
            openInNewTab
            household={household as HouseholdNode}
            businessArea={businessArea}
            canViewPaymentRecordDetails={hasPermissions(
              PERMISSIONS.PM_VIEW_PAYMENT_LIST,
              permissions,
            )}
          />
        )}
        <HouseholdAdditionalRegistrationInformation
          household={household as HouseholdNode}
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
                {household?.registrationDataImport?.importedBy?.email}
              </LabelizedField>
            </Grid>
            {household?.programRegistrationId && (
              <Grid size={{ xs: 3 }}>
                <LabelizedField label={t('Programme registration id')}>
                  {household.programRegistrationId}
                </LabelizedField>
              </Grid>
            )}
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
        <UniversalActivityLogTable objectId={data.household?.id} />
      )}
    </>
  );
};

export default withErrorBoundary(
  PopulationHouseholdDetailsPage,
  'PopulationHouseholdDetailsPage',
);

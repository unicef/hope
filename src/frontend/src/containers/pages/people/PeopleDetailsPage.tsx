import { fetchPeriodicFields } from '@api/periodicDataUpdateApi';
import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { PeopleBioData } from '@components/people/PeopleBioData/PeopleBioData';
import { IndividualAdditionalRegistrationInformation } from '@components/population/IndividualAdditionalRegistrationInformation/IndividualAdditionalRegistrationInformation';
import { IndividualFlags } from '@components/population/IndividualFlags';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';
import { ProgrammeTimeSeriesFields } from '@components/population/ProgrammeTimeSeriesFields';
import {
  BigValue,
  BigValueContainer,
} from '@components/rdi/details/RegistrationDetails/RegistrationDetails';
import { AdminButton } from '@core/AdminButton';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import {
  HouseholdNode,
  IndividualNode,
  useAllIndividualsFlexFieldsAttributesQuery,
  useGrievancesChoiceDataQuery,
  useHouseholdChoiceDataQuery,
  useIndividualQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box, Grid2 as Grid, Paper, Typography } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import {
  formatCurrencyWithSymbol,
  isPermissionDeniedError,
} from '@utils/utils';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { ReactElement } from 'react';
import { IndividualAccounts } from '@components/population/IndividualAccounts';
import withErrorBoundary from '@components/core/withErrorBoundary';
import PaymentsPeopleTable from '@containers/tables/payments/PaymentsPeopleTable/PaymentsPeopleTable';

const Container = styled.div`
  padding: 20px 20px 00px 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;
const OverviewPaper = styled(Paper)`
  margin: 0px 0px 20px 0px;
  padding: 20px ${({ theme }) => theme.spacing(11)};
`;
const Overview = styled(Paper)`
  margin: 15px 0px 20px 0px;
  padding: 20px ${({ theme }) => theme.spacing(11)};
`;
const SubTitle = styled(Typography)`
  && {
    font-size: 16px;
  }
`;

const PeopleDetailsPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
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
    permissions === null
  )
    return null;

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'People',
      to: `/${baseUrl}/population/people`,
    },
  ];

  const { individual } = data;
  const household = individual?.household;

  return (
    <>
      <PageHeader
        title={`${t('Individual ID')}: ${individual?.unicefId}`}
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
        <PeopleBioData
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
        <Box mb={4}>
          <ProgrammeTimeSeriesFields
            individual={individual as IndividualNode}
            periodicFieldsData={periodicFieldsData}
          />
        </Box>
        <OverviewPaper>
          <Title>
            <Typography variant="h6">{t('Benefits')}</Typography>
          </Title>
          <Grid container>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Cash received')}>
                {household?.deliveredQuantities?.length ? (
                  <Box mb={2}>
                    <Grid container>
                      <Grid size={{ xs: 6 }}>
                        <Box display="flex" flexDirection="column">
                          {household?.deliveredQuantities?.map((item) => (
                            <Box
                              key={`${item.currency}-${item.totalDeliveredQuantity}`}
                            >
                              {item.currency === 'USD'
                                ? formatCurrencyWithSymbol(
                                    item.totalDeliveredQuantity,
                                    item.currency,
                                  )
                                : `(${formatCurrencyWithSymbol(
                                    item.totalDeliveredQuantity,
                                    item.currency,
                                  )})`}
                            </Box>
                          ))}
                        </Box>
                      </Grid>
                    </Grid>
                  </Box>
                ) : (
                  <>-</>
                )}
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <BigValueContainer>
                <LabelizedField label={t('Total Cash Received')}>
                  <BigValue>
                    {formatCurrencyWithSymbol(
                      household?.totalCashReceivedUsd,
                      'USD',
                    )}
                  </BigValue>
                </LabelizedField>
              </BigValueContainer>
            </Grid>
          </Grid>
        </OverviewPaper>
        {hasPermissions(PERMISSIONS.PM_VIEW_PAYMENT_LIST, permissions) && (
          <PaymentsPeopleTable
            openInNewTab
            household={household as HouseholdNode}
            businessArea={businessArea}
            canViewPaymentRecordDetails={hasPermissions(
              PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
              permissions,
            )}
          />
        )}

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
                    {/* //TODO: Figure it out. deviceId removed from the model? */}
                    {/* {household?.deviceid} */} -
                  </LabelizedField>
                </Grid>
              </Grid>
            </>
          )}
        </Overview>
      </Container>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={individual?.id} />
      )}
    </>
  );
};

export default withErrorBoundary(PeopleDetailsPage, 'PeopleDetailsPage');

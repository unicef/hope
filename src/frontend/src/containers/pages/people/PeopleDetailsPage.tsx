import { BreadCrumbsItem } from '@components/core/BreadCrumbs';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PeopleBioData } from '@components/people/PeopleBioData/PeopleBioData';
import { IndividualAdditionalRegistrationInformation } from '@components/population/IndividualAdditionalRegistrationInformation/IndividualAdditionalRegistrationInformation';
import { IndividualAccounts } from '@components/population/IndividualAccounts';
import { ProgrammeTimeSeriesFields } from '@components/population/ProgrammeTimeSeriesFields';
import {
  BigValue,
  BigValueContainer,
} from '@components/rdi/details/RegistrationDetails/RegistrationDetails';
import PaymentsPeopleTable from '@containers/tables/payments/PaymentsPeopleTable/PaymentsPeopleTable';
import { LabelizedField } from '@core/LabelizedField';
import { Title } from '@core/Title';
import { FieldsAttributesService } from '@restgenerated/services/FieldsAttributesService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box, Grid2 as Grid, Paper, Theme, Typography } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import {
  formatCurrencyWithSymbol,
  isPermissionDeniedError,
} from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../tables/UniversalActivityLogTable';
import { IndividualChoices } from '@restgenerated/models/IndividualChoices';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';
import { IndividualFlags } from '@components/population/IndividualFlags';
import { AdminButton } from '@components/core/AdminButton';
import { IndividualPhotoModal } from '@components/population/IndividualPhotoModal';
import { UniversalMoment } from '@components/core/UniversalMoment';

const Container = styled.div`
  padding: 20px 20px 00px 20px;
  && {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
`;
const OverviewPaper = styled(Paper)<{ theme?: Theme }>`
  margin: 0px 0px 20px 0px;
  padding: 20px ${({ theme }) => theme.spacing(11)};
`;
const Overview = styled(Paper)<{ theme?: Theme }>`
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

  const {
    data: individual,
    isLoading: loadingIndividual,
    error,
  } = useHopeDetailsQuery<IndividualDetail>(
    id,
    RestService.restBusinessAreasProgramsIndividualsRetrieve,
    {},
  );

  const { data: individualChoicesData, isLoading: individualChoicesLoading } =
    useQuery<IndividualChoices>({
      queryKey: ['individualChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasIndividualsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const { data: flexFieldsData, isLoading: flexFieldsDataLoading } = useQuery({
    queryKey: ['fieldsAttributes'],
    queryFn: async () => {
      const data = await FieldsAttributesService.fieldsAttributesRetrieve();
      return { allIndividualsFlexFieldsAttributes: data };
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
    individualChoicesLoading ||
    flexFieldsDataLoading ||
    grievancesChoicesLoading ||
    periodicFieldsLoading
  )
    return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !individual ||
    !individualChoicesLoading ||
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
            <IndividualPhotoModal individual={individual} />
          ) : null}
        </Box>
      </PageHeader>

      <Container>
        <PeopleBioData
          baseUrl={baseUrl}
          businessArea={businessArea}
          individual={individual}
          choicesData={individualChoicesData}
          grievancesChoices={grievancesChoices}
        />
        <IndividualAccounts individual={individual} />
        <IndividualAdditionalRegistrationInformation
          flexFieldsData={flexFieldsData}
          individual={individual}
        />
        <Box mb={4}>
          <ProgrammeTimeSeriesFields
            individual={individual}
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
            household={household}
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
                <div>{individual?.registrationDataImport?.dataSource}</div>
              </LabelizedField>
            </Grid>
            <Grid size={{ xs: 3 }}>
              <LabelizedField label={t('Import name')}>
                <div>{individual?.registrationDataImport?.name}</div>
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
                {individual?.registrationDataImport?.importedBy?.email}
              </LabelizedField>
            </Grid>
          </Grid>
          {individual?.registrationDataImport?.dataSource === 'XLS' ? null : (
            <>
              <hr />
              <SubTitle variant="h6">{t('Data Collection')}</SubTitle>
              <Grid container spacing={6}>
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('Start time')}>
                    <UniversalMoment>{household?.startTime}</UniversalMoment>
                  </LabelizedField>
                </Grid>
                <Grid size={{ xs: 3 }}>
                  <LabelizedField label={t('End time')}>
                    {household?.firstRegistrationDate}
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

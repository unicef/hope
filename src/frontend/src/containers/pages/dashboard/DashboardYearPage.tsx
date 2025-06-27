import { Box, Grid2 as Grid } from '@mui/material';
import { ReactElement, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllChartsQueryVariables,
  useAllChartsQuery,
  useGlobalAreaChartsLazyQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { DashboardPaper } from '@components/dashboard/DashboardPaper';
import { PaymentsChart } from '@components/dashboard/charts/PaymentsChart';
import { ProgrammesBySector } from '@components/dashboard/charts/ProgrammesBySector';
import { TotalTransferredByMonth } from '@components/dashboard/charts/TotalTransferredByMonth';
import { VolumeByDeliveryMechanism } from '@components/dashboard/charts/VolumeByDeliveryMechanism';
import { GrievancesSection } from '@components/dashboard/sections/GrievancesSection/GrievancesSection';
import { PaymentVerificationSection } from '@components/dashboard/sections/PaymentVerificationSection/PaymentVerificationSection';
import { TotalAmountTransferredSectionByAdminAreaSection } from '@components/dashboard/sections/TotalAmountTransferredByAdminAreaSection/TotalAmountTransferredByAdminAreaSection';
import { TotalAmountTransferredByCountrySection } from '@components/dashboard/sections/TotalAmountTransferredByCountrySection';
import { TotalAmountTransferredSection } from '@components/dashboard/sections/TotalAmountTransferredSection/TotalAmountTransferredSection';
import { TotalNumberOfChildrenReachedSection } from '@components/dashboard/sections/TotalNumberOfChildrenReachedSection/TotalNumberOfChildrenReachedSection';
import { TotalNumberOfHouseholdsReachedSection } from '@components/dashboard/sections/TotalNumberOfHouseholdsReachedSection/TotalNumberOfHouseholdsReachedSection';
import { TotalNumberOfIndividualsReachedSection } from '@components/dashboard/sections/TotalNumberOfIndividualsReachedSection/TotalNumberOfIndividualsReachedSection';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from '../../../programContext';
import { TotalNumberOfPeopleReachedSection } from '@components/dashboard/sections/TotalNumberOfPeopleReachedSection';
import { TotalAmountTransferredSectionByAdminAreaForPeopleSection } from '@components/dashboard/sections/TotalAmountTransferredByAdminAreaForPeopleSection';
import { PaymentVerificationSectionForPeople } from '@components/dashboard/sections/PaymentVerificationSectionForPeople';

const PaddingContainer = styled.div`
  padding: 20px;
`;

interface ChartWrapperProps {
  numberOfProgrammes: number;
}

const ChartWrapper = styled.div<ChartWrapperProps>`
  height: ${(props) => (props.numberOfProgrammes <= 3 ? '200px' : '400px')};
`;

interface PaddingLeftContainerProps {
  paddingLeft?: string;
}

const PaddingLeftContainer = styled.div<PaddingLeftContainerProps>`
  padding-left: ${(props) => props.paddingLeft || '20px'};
`;

interface CardTextLightProps {
  large?: boolean;
}

const CardTextLight = styled.div<CardTextLightProps>`
  text-transform: capitalize;
  color: #a4a4a4;
  font-weight: 500;
  font-size: ${(props) => (props.large ? '16px' : '12px')};
`;

interface DashboardYearPageProps {
  year: string;
  filter;
}

export const DashboardYearPage = ({
  year,
  filter,
}: DashboardYearPageProps): ReactElement => {
  const { t } = useTranslation();
  const { businessArea, isGlobal, isAllPrograms, programId } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();

  const variables: AllChartsQueryVariables = {
    year: parseInt(year, 10),
    businessAreaSlug: businessArea,
  };

  if (!isGlobal) {
    variables.program = filter.program;
    variables.administrativeArea = filter.administrativeArea;
  }

  if (!isAllPrograms) {
    variables.program = programId;
  }

  const { data, loading } = useAllChartsQuery({
    variables,
    fetchPolicy: 'cache-and-network',
  });

  const [loadGlobal, { data: globalData, loading: globalLoading }] =
    useGlobalAreaChartsLazyQuery({
      variables: {
        year: parseInt(year, 10),
      },
    });

  useEffect(() => {
    if (isGlobal) {
      void loadGlobal();
    }
  }, [isGlobal, loadGlobal]);

  if (isGlobal) {
    if (loading || globalLoading) return <LoadingComponent />;
    if (!data || !globalData) return null;
  } else {
    if (loading) return <LoadingComponent />;
    if (!data) return null;
  }

  return (
    <PaddingContainer>
      <Grid container spacing={3}>
        <Grid size={{ xs:8 }}>
          <Box mb={6}>
            <TotalAmountTransferredSection
              data={data.sectionTotalTransferred}
            />
          </Box>
          {isGlobal && (
            <Box mb={6}>
              <TotalAmountTransferredByCountrySection
                data={globalData?.chartTotalTransferredCashByCountry}
              />
            </Box>
          )}
          {isAllPrograms && (
            <Box mb={6}>
              <DashboardPaper title={t('Number of Programmes by Sector')}>
                <ChartWrapper
                  numberOfProgrammes={
                    data.chartProgrammesBySector?.labels.length || 0
                  }
                >
                  <ProgrammesBySector data={data.chartProgrammesBySector} />
                </ChartWrapper>
              </DashboardPaper>
            </Box>
          )}
          <Box mb={6}>
            <DashboardPaper title={t('Total Transferred by Month')}>
              <TotalTransferredByMonth
                data={data.chartTotalTransferredByMonth}
              />
            </DashboardPaper>
          </Box>
          {!isGlobal && (
            <>
              {(isAllPrograms || !isSocialDctType) && (
                <Box mb={6}>
                  <TotalAmountTransferredSectionByAdminAreaSection
                    year={year}
                    filter={filter}
                  />
                </Box>
              )}
              {(isAllPrograms || isSocialDctType) && (
                <Box mb={6}>
                  <TotalAmountTransferredSectionByAdminAreaForPeopleSection
                    year={year}
                    filter={filter}
                  />
                </Box>
              )}
            </>
          )}
          {(isAllPrograms || !isSocialDctType) && (
            <Box mb={6}>
              <PaymentVerificationSection
                data={data.chartPaymentVerification}
              />
            </Box>
          )}
          {(isAllPrograms || isSocialDctType) && (
            <Box mb={6}>
              <PaymentVerificationSectionForPeople
                data={data.chartPaymentVerificationForPeople}
              />
            </Box>
          )}
        </Grid>
        <Grid size={{ xs: 4 }}>
          <PaddingLeftContainer>
            <Grid container spacing={6}>
              {(isAllPrograms || !isSocialDctType) && (
                <>
                  <Grid size={{ xs: 12 }}>
                    <TotalNumberOfHouseholdsReachedSection
                      data={data.sectionHouseholdsReached}
                    />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TotalNumberOfIndividualsReachedSection
                      data={data.sectionIndividualsReached}
                      chartDataIndividuals={
                        data.chartIndividualsReachedByAgeAndGender
                      }
                      chartDataIndividualsDisability={
                        data.chartIndividualsWithDisabilityReachedByAge
                      }
                    />
                  </Grid>
                </>
              )}
              {(isAllPrograms || isSocialDctType) && (
                <Grid size={{ xs: 12 }}>
                  <TotalNumberOfPeopleReachedSection
                    data={data.sectionPeopleReached}
                    chartDataPeople={data.chartPeopleReachedByAgeAndGender}
                    chartDataPeopleDisability={
                      data.chartPeopleWithDisabilityReachedByAge
                    }
                  />
                </Grid>
              )}
              {data.sectionChildReached && (
                <Grid size={{ xs: 12 }}>
                  <TotalNumberOfChildrenReachedSection
                    data={data.sectionChildReached}
                  />
                </Grid>
              )}
              <Grid size={{ xs: 12 }}>
                <Box mb={6}>
                  <DashboardPaper
                    title={t('Volume by Delivery Mechanism in USD')}
                    noMarginTop
                    extraPaddingTitle={false}
                  >
                    <CardTextLight large>{t('Delivery Type')}</CardTextLight>
                    <VolumeByDeliveryMechanism
                      data={data.chartVolumeByDeliveryMechanism}
                    />
                  </DashboardPaper>
                </Box>
                <Box mb={6}>
                  <GrievancesSection data={data.chartGrievances} />
                </Box>
                <Box mb={6}>
                  <DashboardPaper title="Payments">
                    <PaymentsChart data={data.chartPayment} />
                  </DashboardPaper>
                </Box>
              </Grid>
            </Grid>
          </PaddingLeftContainer>
        </Grid>
      </Grid>
    </PaddingContainer>
  );
};

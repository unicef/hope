import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { Title } from '@components/core/Title';
import withErrorBoundary from '@components/core/withErrorBoundary';
import RegistrationDataImportDetailsPageHeader from '@components/rdi/details/RegistrationDataImportDetailsPageHeader';
import RegistrationDetails from '@components/rdi/details/RegistrationDetails/RegistrationDetails';
import { ImportedPeopleTable } from '@containers/tables/rdi/ImportedPeopleTable';
import { Tab, Tabs } from '@core/Tabs';
import { RegistrationDataImportStatusEnum } from '@restgenerated/models/RegistrationDataImportStatusEnum';
import { RegistrationDataImportDetail } from '@restgenerated/models/RegistrationDataImportDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Typography } from '@mui/material';
import { HouseholdChoices } from '@restgenerated/models/HouseholdChoices';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement, ReactNode, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;
const TabsContainer = styled.div`
  border-bottom: 1px solid #e8e8e8;
`;

interface TabPanelProps {
  children: ReactNode;
  index: number;
  value: number;
}
const TabPanel = ({ children, index, value }: TabPanelProps): ReactElement => {
  return (
    <div style={{ display: index !== value ? 'none' : 'block' }}>
      {children}
    </div>
  );
};

export const PeopleRegistrationDataImportDetailsPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { businessArea, programSlug } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();

  const { data, isLoading: loading, error } = useQuery<RegistrationDataImportDetail>({
    queryKey: ['registrationDataImport', businessArea, programSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRegistrationDataImportsRetrieve({
        businessAreaSlug: businessArea,
        programSlug,
        id,
      }),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (
        [
          RegistrationDataImportStatusEnum.LOADING,
          RegistrationDataImportStatusEnum.DEDUPLICATION,
          RegistrationDataImportStatusEnum.IMPORT_SCHEDULED,
          RegistrationDataImportStatusEnum.IMPORTING,
          RegistrationDataImportStatusEnum.MERGE_SCHEDULED,
          RegistrationDataImportStatusEnum.MERGING,
        ].includes(status as RegistrationDataImportStatusEnum)
      ) {
        return 30000;
      }
      return false;
    },
    refetchIntervalInBackground: true,
  });

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<HouseholdChoices>({
      queryKey: ['householdChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasHouseholdsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

  const [selectedTab, setSelectedTab] = useState(0);

  const status = data?.status;
  const isMerged = RegistrationDataImportStatusEnum.MERGED === data?.status;

  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || !choicesData || permissions === null) {
    return null;
  }

  const canMerge = hasPermissions(PERMISSIONS.RDI_MERGE_IMPORT, permissions);

  function RegistrationContainer({
    isErased,
  }: {
    isErased: boolean;
  }): ReactElement {
    return (
      <Container>
        <RegistrationDetails
          registration={data}
          isSocialWorkerProgram={isSocialDctType}
        />
        {isErased ? null : (
          <TableWrapper>
            <ContainerColumnWithBorder>
              <Title>
                <Typography variant="h6">
                  {isMerged ? t('Population Preview') : t('Import Preview')}
                </Typography>
              </Title>
              <TabsContainer>
                <StyledTabs
                  value={selectedTab}
                  onChange={(_, newValue: number) => setSelectedTab(newValue)}
                  indicatorColor="primary"
                  textColor="primary"
                  variant="fullWidth"
                  aria-label="full width tabs example"
                >
                  <Tab data-cy="tab-Individuals" label={t('People')} />
                </StyledTabs>
              </TabsContainer>
              <TabPanel value={selectedTab} index={0}>
                <ImportedPeopleTable
                  showCheckbox
                  isOnPaper={false}
                  rdiId={id}
                  rdi={data}
                  isMerged={isMerged}
                  businessArea={businessArea}
                  key={`${data.status}-individual`}
                  choicesData={choicesData}
                />
              </TabPanel>
            </ContainerColumnWithBorder>
          </TableWrapper>
        )}
      </Container>
    );
  }

  return (
    <>
      <RegistrationDataImportDetailsPageHeader
        registration={data}
        canMerge={canMerge}
        canRerunDedupe={hasPermissions(
          PERMISSIONS.RDI_RERUN_DEDUPE,
          permissions,
        )}
        canViewList={hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions)}
        canRefuse={hasPermissions(PERMISSIONS.RDI_REFUSE_IMPORT, permissions)}
      />
      <RegistrationContainer isErased={data.erased} />
    </>
  );
};

export default withErrorBoundary(
  PeopleRegistrationDataImportDetailsPage,
  'PeopleRegistrationDataImportDetailsPage',
);

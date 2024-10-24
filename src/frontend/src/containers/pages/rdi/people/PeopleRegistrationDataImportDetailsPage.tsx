import { Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  RegistrationDataImportStatus,
  useHouseholdChoiceDataQuery,
  useProgramQuery,
  useRegistrationDataImportQuery,
} from '@generated/graphql';
import { Tabs, Tab } from '@core/Tabs';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { Title } from '@components/core/Title';
import { RegistrationDataImportDetailsPageHeader } from '@components/rdi/details/RegistrationDataImportDetailsPageHeader';
import { RegistrationDetails } from '@components/rdi/details/RegistrationDetails/RegistrationDetails';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { ImportedPeopleTable } from '@containers/tables/rdi/ImportedPeopleTable';

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
  children: React.ReactNode;
  index: number;
  value: number;
}
const TabPanel = ({
  children,
  index,
  value,
}: TabPanelProps): React.ReactElement => {
  return (
    <div style={{ display: index !== value ? 'none' : 'block' }}>
      {children}
    </div>
  );
};

export const PeopleRegistrationDataImportDetailsPage =
  (): React.ReactElement => {
    const { t } = useTranslation();
    const { id } = useParams();
    const permissions = usePermissions();
    const { businessArea, programId } = useBaseUrl();
    const { data: programData } = useProgramQuery({
      variables: { id: programId },
    });
    const { data, loading, error, stopPolling, startPolling } =
      useRegistrationDataImportQuery({
        variables: { id },
        fetchPolicy: 'cache-and-network',
      });
    const { data: choicesData, loading: choicesLoading } =
      useHouseholdChoiceDataQuery();

    const [selectedTab, setSelectedTab] = useState(0);

    const status = data?.registrationDataImport?.status;
    useEffect(() => {
      if (
        [
          RegistrationDataImportStatus.Loading,
          RegistrationDataImportStatus.Deduplication,
          RegistrationDataImportStatus.ImportScheduled,
          RegistrationDataImportStatus.Importing,
          RegistrationDataImportStatus.MergeScheduled,
          RegistrationDataImportStatus.Merging,
        ].includes(status)
      ) {
        startPolling(30000);
      } else {
        stopPolling();
      }
      return stopPolling;
    }, [status, startPolling, stopPolling]);

    if (loading || choicesLoading) return <LoadingComponent />;
    if (isPermissionDeniedError(error)) return <PermissionDenied />;
    if (!data?.registrationDataImport || !choicesData || permissions === null) {
      return null;
    }

    const isMerged =
      RegistrationDataImportStatus.Merged ===
      data.registrationDataImport.status;

    const canMerge = hasPermissions(PERMISSIONS.RDI_MERGE_IMPORT, permissions);

    function RegistrationContainer({
      isErased,
    }: {
      isErased: boolean;
    }): React.ReactElement {
      return (
        <Container>
          <RegistrationDetails
            registration={data.registrationDataImport}
            isSocialWorkerProgram={programData.program.isSocialWorkerProgram}
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
                    rdiId={id}
                    isMerged={isMerged}
                    businessArea={businessArea}
                    key={`${data.registrationDataImport.status}-individual`}
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
      <div>
        <RegistrationDataImportDetailsPageHeader
          registration={data.registrationDataImport}
          canMerge={canMerge}
          canRerunDedupe={hasPermissions(
            PERMISSIONS.RDI_RERUN_DEDUPE,
            permissions,
          )}
          canViewList={hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions)}
          canRefuse={hasPermissions(PERMISSIONS.RDI_REFUSE_IMPORT, permissions)}
        />
        <RegistrationContainer isErased={data.registrationDataImport.erased} />
      </div>
    );
  };

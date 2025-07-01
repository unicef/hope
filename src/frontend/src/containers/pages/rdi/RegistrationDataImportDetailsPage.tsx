import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { TableWrapper } from '@components/core/TableWrapper';
import { Title } from '@components/core/Title';
import withErrorBoundary from '@components/core/withErrorBoundary';
import RegistrationDataImportDetailsPageHeader from '@components/rdi/details/RegistrationDataImportDetailsPageHeader';
import { Tab, Tabs } from '@core/Tabs';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Typography } from '@mui/material';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement, ReactNode, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { ImportedHouseholdTable } from '../../tables/rdi/ImportedHouseholdsTable';
import { ImportedIndividualsTable } from '../../tables/rdi/ImportedIndividualsTable';
import RegistrationDetails from '@components/rdi/details/RegistrationDetails/RegistrationDetails';
import { useHopeDetailsQuery } from '@hooks/useHopeDetailsQuery';
import { RestService } from '@restgenerated/services/RestService';

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

const RegistrationDataImportDetailsPage = (): ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const { selectedProgram } = useProgramContext();
  const { businessArea } = useBaseUrl();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const refetchInterval = (result) => {
    if (
      [
        'Loading',
        'Deduplication',
        'Import  Scheduled',
        'Importing',
        'Merge Scheduled',
        'Merging',
      ].includes(result?.state?.data?.status)
    ) {
      return 30000;
    }
    return undefined;
  };
  const {
    data,
    isLoading: loading,
    error,
  } = useHopeDetailsQuery(
    id,
    RestService.restBusinessAreasProgramsRegistrationDataImportsRetrieve,
    { refetchInterval },
  );

  const [selectedTab, setSelectedTab] = useState(0);

  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data || permissions === null) {
    return null;
  }

  const isMerged = 'MERGED' === data.status;

  function RegistrationContainer({
    isErased,
  }: {
    isErased: boolean;
  }): ReactElement {
    return (
      <Container>
        <RegistrationDetails registration={data} />
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
                  <Tab
                    data-cy="tab-Households"
                    label={beneficiaryGroup?.groupLabelPlural}
                  />
                  <Tab
                    data-cy="tab-Individuals"
                    label={beneficiaryGroup?.memberLabelPlural}
                  />
                </StyledTabs>
              </TabsContainer>
              <TabPanel value={selectedTab} index={0}>
                <ImportedHouseholdTable
                  key={`${data.status}-household`}
                  isMerged={isMerged}
                  rdi={data}
                  businessArea={businessArea}
                />
              </TabPanel>
              <TabPanel value={selectedTab} index={1}>
                <ImportedIndividualsTable
                  isOnPaper={false}
                  showCheckbox
                  rdiId={id}
                  isMerged={isMerged}
                  businessArea={businessArea}
                  key={`${data.status}-individual`}
                  rdi={data}
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
        canMerge={hasPermissions(PERMISSIONS.RDI_MERGE_IMPORT, permissions)}
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
  RegistrationDataImportDetailsPage,
  'RegistrationDataImportDetailsPage',
);

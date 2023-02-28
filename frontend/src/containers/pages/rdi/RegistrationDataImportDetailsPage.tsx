import { Tab, Typography } from '@material-ui/core';
import Tabs from '@material-ui/core/Tabs';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { TableWrapper } from '../../../components/core/TableWrapper';
import { Title } from '../../../components/core/Title';
import { RegistrationDataImportDetailsPageHeader } from '../../../components/rdi/details/RegistrationDataImportDetailsPageHeader';
import { RegistrationDetails } from '../../../components/rdi/details/RegistrationDetails/RegistrationDetails';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import {
  useHouseholdChoiceDataQuery,
  useRegistrationDataImportQuery,
} from '../../../__generated__/graphql';
import { ImportedHouseholdTable } from '../../tables/rdi/ImportedHouseholdsTable';
import { ImportedIndividualsTable } from '../../tables/rdi/ImportedIndividualsTable';

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
function TabPanel({
  children,
  index,
  value,
}: TabPanelProps): React.ReactElement {
  const style = {};
  if (index !== value) {
    // eslint-disable-next-line dot-notation
    style['display'] = 'none';
  }
  return <div style={style}>{children}</div>;
}
export function RegistrationDataImportDetailsPage(): React.ReactElement {
  const { t } = useTranslation();
  const { id } = useParams();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const { data, loading, error, stopPolling } = useRegistrationDataImportQuery({
    variables: { id },
    pollInterval: 30000,
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery();

  const [selectedTab, setSelectedTab] = useState(0);

  if (loading || choicesLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;
  if (!data?.registrationDataImport || !choicesData || permissions === null) {
    return null;
  }
  if (data.registrationDataImport.status !== 'IMPORTING') {
    stopPolling();
  }

  return (
    <div>
      <RegistrationDataImportDetailsPageHeader
        registration={data.registrationDataImport}
        canMerge={hasPermissions(PERMISSIONS.RDI_MERGE_IMPORT, permissions)}
        canRerunDedupe={hasPermissions(
          PERMISSIONS.RDI_RERUN_DEDUPE,
          permissions,
        )}
        canViewList={hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions)}
        canRefuse={hasPermissions(PERMISSIONS.RDI_REFUSE_IMPORT, permissions)}
      />
      <Container>
        <RegistrationDetails registration={data.registrationDataImport} />
        <TableWrapper>
          <ContainerColumnWithBorder>
            <Title>
              <Typography variant='h6'>{t('Import Preview')}</Typography>
            </Title>
            <TabsContainer>
              <StyledTabs
                value={selectedTab}
                onChange={(event: React.ChangeEvent<{}>, newValue: number) =>
                  setSelectedTab(newValue)
                }
                indicatorColor='primary'
                textColor='primary'
                variant='fullWidth'
                aria-label='full width tabs example'
              >
                <Tab label={t('Households')} />
                <Tab label={t('Individuals')} />
              </StyledTabs>
            </TabsContainer>
            <TabPanel value={selectedTab} index={0}>
              <ImportedHouseholdTable
                key={`${data.registrationDataImport.status}-household`}
                rdiId={id}
                businessArea={businessArea}
              />
            </TabPanel>
            <TabPanel value={selectedTab} index={1}>
              <ImportedIndividualsTable
                showCheckbox
                rdiId={id}
                businessArea={businessArea}
                key={`${data.registrationDataImport.status}-individual`}
                choicesData={choicesData}
              />
            </TabPanel>
          </ContainerColumnWithBorder>
        </TableWrapper>
      </Container>
    </div>
  );
}

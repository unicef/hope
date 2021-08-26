import { Paper, Tab } from '@material-ui/core';
import Tabs from '@material-ui/core/Tabs';
import Typography from '@material-ui/core/Typography';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { LoadingComponent } from '../../../components/LoadingComponent';
import { PermissionDenied } from '../../../components/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../utils/utils';
import { useRegistrationDataImportQuery } from '../../../__generated__/graphql';
import { ImportedHouseholdTable } from '../tables/ImportedHouseholdsTable';
import { ImportedIndividualsTable } from '../tables/ImportedIndividualsTable';
import { RegistrationDataImportDetailsPageHeader } from './RegistrationDataImportDetailsPageHeader';
import { RegistrationDetails } from './RegistrationDetails';

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

const TableWrapper = styled.div`
  padding: ${({ theme }) => theme.spacing(4)}px;
`;
const Title = styled(Typography)`
  padding: ${({ theme }) => theme.spacing(6)}px;
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
  const { data, loading, error } = useRegistrationDataImportQuery({
    variables: { id },
  });
  const [selectedTab, setSelectedTab] = useState(0);

  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

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
      />
      <Container>
        <RegistrationDetails registration={data.registrationDataImport} />
        <TableWrapper>
          <Paper>
            <Title variant='h6'>{t('Import Preview')}</Title>
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
              <ImportedHouseholdTable rdiId={id} businessArea={businessArea} />
            </TabPanel>
            <TabPanel value={selectedTab} index={1}>
              <ImportedIndividualsTable
                showCheckbox
                rdiId={id}
                businessArea={businessArea}
              />
            </TabPanel>
          </Paper>
        </TableWrapper>
      </Container>
    </div>
  );
}

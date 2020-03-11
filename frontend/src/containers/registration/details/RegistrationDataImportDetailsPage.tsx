import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import { Paper, Snackbar, SnackbarContent, Tab } from '@material-ui/core';
import {
  useProgrammeChoiceDataQuery,
  useRegistrationDataImportQuery,
} from '../../../__generated__/graphql';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import { LoadingComponent } from '../../../components/LoadingComponent';
import { useSnackbarHelper } from '../../../hooks/useBreadcrumbHelper';
import { ImportedHouseholdTable } from '../tables/ImportedHouseholdsTable';
import { RegistrationDetails } from './RegistrationDetails';
import { RegistrationDataImportDetailsPageHeader } from './RegistrationDataImportDetailsPageHeader';
import Typography from '@material-ui/core/Typography';
import Toolbar from '@material-ui/core/Toolbar';
import { ImportedIndividualsTable } from '../tables/ImportedIndividualsTable';

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
  padding: 20px;
`;
const Title = styled(Typography)`
  padding: 24px;
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
  const { id } = useParams();
  const { data, loading } = useRegistrationDataImportQuery({
    variables: { id },
  });
  const [selectedTab, setSelectedTab] = useState(0);
  const {
    data: choices,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const snackBar = useSnackbarHelper();
  if (loading || choicesLoading) {
    return <LoadingComponent />;
  }

  if (!data || !choices) {
    return null;
  }
  return (
    <div>
      <RegistrationDataImportDetailsPageHeader
        registration={data.registrationDataImport}
      />
      <Container>
        <RegistrationDetails registration={data.registrationDataImport} />
        <TableWrapper>
          <Paper>
            <Title variant='h6'>
              Import Preview
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
                <Tab label='Households' />
                <Tab label='Individuals' />
              </StyledTabs>
            </TabsContainer>
            <TabPanel value={selectedTab} index={0}>
              <ImportedHouseholdTable rdiId={id} />
            </TabPanel>
            <TabPanel value={selectedTab} index={1}>
              <ImportedIndividualsTable rdiId={id} />
            </TabPanel>
          </Paper>
        </TableWrapper>
      </Container>
      {snackBar.show && (
        <Snackbar
          open={snackBar.show}
          autoHideDuration={5000}
          onClose={() => snackBar.setShow(false)}
        >
          <SnackbarContent message={snackBar.message} />
        </Snackbar>
      )}
    </div>
  );
}

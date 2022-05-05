import { Box, Button, Paper, Tab, Tabs } from '@material-ui/core';
import { Link } from 'react-router-dom';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { PaymentPlansTable } from '../../tables/paymentmodule/PaymentPlansTable';
import { PaymentPlansFilters } from '../../tables/paymentmodule/PaymentPlansTable/PaymentPlansFilters';
import { TabPanel } from '../../../components/core/TabPanel';
import { FspTable } from '../../tables/paymentmodule/FspTable';
import { FspFilters } from '../../tables/paymentmodule/FspTable/FspFilters';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;

const TableWrapper = styled.div`
  padding: 20px;
`;

export function PaymentModulePage(): React.ReactElement {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const [selectedTab, setSelectedTab] = useState(0);
  const [planfilter, setPlanFilter] = useState({
    search: '',
    dispersionDate: '',
    status: '',
    entitlement: { min: null, max: null },
  });
  const [fspFilter, setFspFilter] = useState({
    search: '',
    paymentChannel: '',
  });
  const debouncedPlanFilter = useDebounce(planfilter, 500);
  const debouncedFspFilter = useDebounce(fspFilter, 500);

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PAYMENT_MODULE_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <Paper>
        <PageHeader title={t('Payment Module')} />
        <Box>
          <Tabs
            value={selectedTab}
            onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
              setSelectedTab(newValue);
            }}
            variant='fullWidth'
            indicatorColor='primary'
            textColor='primary'
          >
            <Tab label={t('Payment Plans')} />
            <Tab label={t('FSP')} />
          </Tabs>
        </Box>
      </Paper>
      <TabPanel value={selectedTab} index={0}>
        <PaymentPlansFilters
          filter={planfilter}
          onFilterChange={setPlanFilter}
        />
        <Box p={6} width='100%' display='flex' justifyContent='flex-end'>
          {hasPermissions(PERMISSIONS.PAYMENT_MODULE_CREATE, permissions) && (
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${businessArea}/payment-module/new-plan`}
            >
              {t('NEW PAYMENT PLAN')}
            </Button>
          )}
        </Box>
        <Container>
          <TableWrapper>
            <PaymentPlansTable
              filter={debouncedPlanFilter}
              businessArea={businessArea}
              canViewDetails={hasPermissions(
                PERMISSIONS.PAYMENT_MODULE_VIEW_DETAILS,
                permissions,
              )}
            />
          </TableWrapper>
        </Container>
      </TabPanel>
      <TabPanel value={selectedTab} index={1}>
        <FspFilters filter={fspFilter} onFilterChange={setFspFilter} />
        <Box p={6} width='100%' display='flex' justifyContent='flex-end'>
          {hasPermissions(PERMISSIONS.PAYMENT_MODULE_CREATE, permissions) && (
            <Button
              variant='contained'
              color='primary'
              component={Link}
              to={`/${businessArea}/payment-module/new-fsp`}
            >
              {t('NEW FSP')}
            </Button>
          )}
        </Box>
        <Container>
          <TableWrapper>
            <FspTable
              filter={debouncedFspFilter}
              businessArea={businessArea}
              canViewDetails={hasPermissions(
                PERMISSIONS.PAYMENT_MODULE_VIEW_DETAILS,
                permissions,
              )}
            />
          </TableWrapper>
        </Container>
      </TabPanel>
    </>
  );
}

import {
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@mui/material';
import { GetApp } from '@mui/icons-material';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  PaymentPlanBackgroundActionStatus,
  PaymentPlanDocument,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useAllSteficonRulesQuery,
  useExportXlsxPpListMutation,
  useSetSteficonRuleOnPpListMutation,
} from '@generated/graphql';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { BigValue } from '../../../rdi/details/RegistrationDetails/RegistrationDetails';
import { ImportXlsxPaymentPlanPaymentList } from '../ImportXlsxPaymentPlanPaymentList/ImportXlsxPaymentPlanPaymentList';
import { useProgramContext } from '../../../../programContext';

const GreyText = styled.p`
  color: #9e9e9e;
  font-size: 16px;
`;

const GreyTextSmall = styled.p`
  color: #9e9e9e;
  font-size: 14px;
`;

const OrDivider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 2px;
  width: 50%;
  margin-top: 20px;
`;

const Divider = styled.div`
  border-top: 1px solid #b1b1b5;
  height: 20px;
`;

const DividerLabel = styled.div`
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
  margin-top: 20px;
`;

const DownloadIcon = styled(GetApp)`
  color: #043f91;
`;

const SpinaczIconContainer = styled(Box)`
  position: relative;
  top: 4px;
  font-size: 16px;
  color: #666666;
`;

const BoxWithBorderRight = styled(Box)`
  border-right: 1px solid #b1b1b5;
`;

interface EntitlementProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  permissions: string[];
}

export function Entitlement({
  paymentPlan,
  permissions,
}: EntitlementProps): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();

  const [steficonRuleValue, setSteficonRuleValue] = useState<string>(
    paymentPlan.steficonRule?.rule.id || '',
  );
  const options = {
    refetchQueries: () => [
      {
        query: PaymentPlanDocument,
        variables: {
          id: paymentPlan.id,
        },
      },
    ],
  };

  const [setSteficonRule, { loading: loadingSetSteficonRule }] =
    useSetSteficonRuleOnPpListMutation(options);

  const { data: steficonData, loading } = useAllSteficonRulesQuery({
    variables: { enabled: true, deprecated: false, type: 'PAYMENT_PLAN' },
    fetchPolicy: 'network-only',
  });
  const [mutateExport, { loading: loadingExport }] =
    useExportXlsxPpListMutation();

  if (!steficonData) {
    return null;
  }
  if (loading) {
    return <LoadingComponent />;
  }

  const canApplySteficonRule = hasPermissions(
    PERMISSIONS.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
    permissions,
  );

  const shouldDisableEntitlementSelect =
    !canApplySteficonRule ||
    paymentPlan.status !== PaymentPlanStatus.Locked ||
    !isActiveProgram;

  const shouldDisableDownloadTemplate =
    paymentPlan.status !== PaymentPlanStatus.Locked || !isActiveProgram;

  const shouldDisableExportXlsx =
    loadingExport ||
    paymentPlan.status !== PaymentPlanStatus.Locked ||
    paymentPlan?.backgroundActionStatus ===
      PaymentPlanBackgroundActionStatus.XlsxExporting ||
    !isActiveProgram;

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant="h6">{t('Entitlement')}</Typography>
          </Title>
          <GreyText>{t('Select Entitlement Formula')}</GreyText>
          <Grid alignItems="center" container>
            <Grid item xs={11}>
              <FormControl size="small" variant="outlined" fullWidth>
                <Box mb={1}>
                  <InputLabel>{t('Entitlement Formula')}</InputLabel>
                </Box>
                <Select
                  size="small"
                  disabled={shouldDisableEntitlementSelect}
                  MenuProps={{
                    anchorOrigin: {
                      vertical: 'bottom',
                      horizontal: 'left',
                    },
                    transformOrigin: {
                      vertical: 'top',
                      horizontal: 'left',
                    },
                  }}
                  value={steficonRuleValue}
                  data-cy="input-entitlement-formula"
                  onChange={(event) => setSteficonRuleValue(event.target.value)}
                >
                  {steficonData.allSteficonRules?.edges?.map((each, index) => (
                    <MenuItem
                      data-cy={`select-option-${index}`}
                      key={each.node.id}
                      value={each.node.id}
                    >
                      {each.node.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item>
              <Box ml={2}>
                <Button
                  variant="contained"
                  color="primary"
                  disabled={
                    loadingSetSteficonRule ||
                    !steficonRuleValue ||
                    paymentPlan.status !== PaymentPlanStatus.Locked ||
                    paymentPlan.backgroundActionStatus ===
                      PaymentPlanBackgroundActionStatus.RuleEngineRun ||
                    !isActiveProgram
                  }
                  data-cy="button-apply-steficon"
                  onClick={async () => {
                    try {
                      await setSteficonRule({
                        variables: {
                          paymentPlanId: paymentPlan.id,
                          steficonRuleId: steficonRuleValue,
                        },
                      });
                      showMessage(
                        t('Formula is executing, please wait until completed'),
                      );
                    } catch (e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
                  }}
                >
                  {t('Apply')}
                </Button>
              </Box>
            </Grid>
          </Grid>
          <Box display="flex" alignItems="center">
            <OrDivider />
            <DividerLabel>Or</DividerLabel>
            <OrDivider />
          </Box>
        </Box>
        <Box display="flex">
          <Box width="50%">
            <BoxWithBorderRight
              display="flex"
              justifyContent="center"
              alignItems="center"
              flexDirection="column"
            >
              {paymentPlan.hasPaymentListExportFile ? (
                <Button
                  color="primary"
                  startIcon={<DownloadIcon />}
                  component="a"
                  download
                  data-cy="button-download-template"
                  href={`/api/download-payment-plan-payment-list/${paymentPlan.id}`}
                  disabled={shouldDisableDownloadTemplate}
                >
                  {t('DOWNLOAD TEMPLATE')}
                </Button>
              ) : (
                <LoadingButton
                  loading={loadingExport}
                  disabled={shouldDisableExportXlsx}
                  color="primary"
                  startIcon={<GetApp />}
                  data-cy="button-export-xlsx"
                  onClick={async () => {
                    try {
                      await mutateExport({
                        variables: {
                          paymentPlanId: paymentPlan.id,
                        },
                      });
                      showMessage(
                        t('Exporting XLSX started. Please check your email.'),
                      );
                    } catch (e) {
                      e.graphQLErrors.map((x) => showMessage(x.message));
                    }
                  }}
                >
                  {t('Export Xlsx')}
                </LoadingButton>
              )}

              <GreyTextSmall>
                {t(
                  'Template contains payment list with all targeted households',
                )}
              </GreyTextSmall>
            </BoxWithBorderRight>
          </Box>
          <Box width="50%">
            <Box
              display="flex"
              justifyContent="center"
              alignItems="center"
              flexDirection="column"
            >
              <Box>
                <ImportXlsxPaymentPlanPaymentList
                  permissions={permissions}
                  paymentPlan={paymentPlan}
                />
              </Box>
              {paymentPlan?.importedFileName ? (
                <Box alignItems="center" display="flex">
                  <SpinaczIconContainer>
                    <AttachFileIcon fontSize="inherit" />
                  </SpinaczIconContainer>
                  <Box mr={1}>
                    <GreyTextSmall data-cy="imported-file-name">
                      {paymentPlan?.importedFileName}
                    </GreyTextSmall>
                  </Box>
                  <GreyTextSmall>
                    {paymentPlan?.importedFileDate ? (
                      <UniversalMoment>
                        {paymentPlan?.importedFileDate}
                      </UniversalMoment>
                    ) : null}
                  </GreyTextSmall>
                </Box>
              ) : (
                <GreyTextSmall>
                  {t(
                    'Uploaded file should contain entitlement for each household',
                  )}
                </GreyTextSmall>
              )}
            </Box>
          </Box>
        </Box>
        {paymentPlan.totalEntitledQuantityUsd ? (
          <>
            <Divider />
            <LabelizedField label={t('Total Entitled Quantity')}>
              <BigValue data-cy="total-entitled-quantity-usd">
                {`${paymentPlan.totalEntitledQuantity} ${paymentPlan.currency} (${paymentPlan.totalEntitledQuantityUsd} USD)`}
              </BigValue>
            </LabelizedField>
          </>
        ) : null}
      </ContainerColumnWithBorder>
    </Box>
  );
}

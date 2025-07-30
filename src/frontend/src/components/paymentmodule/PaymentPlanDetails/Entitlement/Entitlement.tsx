import withErrorBoundary from '@components/core/withErrorBoundary';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { LoadingComponent } from '@core/LoadingComponent';
import { Title } from '@core/Title';
import { UniversalMoment } from '@core/UniversalMoment';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import {
  Box,
  Button,
  FormControl,
  Grid2 as Grid,
  InputLabel,
  MenuItem,
  Select,
  Typography,
} from '@mui/material';
import { ApplyEngineFormula } from '@restgenerated/models/ApplyEngineFormula';
import { PaginatedRuleList } from '@restgenerated/models/PaginatedRuleList';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';
import { BigValue } from '../../../rdi/details/RegistrationDetails/RegistrationDetails';
import { ImportXlsxPaymentPlanPaymentList } from '../ImportXlsxPaymentPlanPaymentList/ImportXlsxPaymentPlanPaymentList';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { BackgroundActionStatusEnum } from '@restgenerated/models/BackgroundActionStatusEnum';
import { showApiErrorMessages } from '@utils/utils';

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
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
}

function Entitlement({
  paymentPlan,
  permissions,
}: EntitlementProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const [steficonRuleValue, setSteficonRuleValue] = useState<string>(
    paymentPlan.steficonRule?.id ? String(paymentPlan.steficonRule.id) : '',
  );

  const { mutateAsync: setSteficonRule, isPending: loadingSetSteficonRule } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
      }: {
        businessAreaSlug: string;
        id: string;
        programSlug: string;
        requestBody: ApplyEngineFormula;
      }) =>
        RestService.restBusinessAreasProgramsPaymentPlansApplyEngineFormulaCreate(
          {
            businessAreaSlug,
            id,
            programSlug,
            requestBody,
          },
        ),
      onSuccess: () => {
        showMessage(t('Formula is executing, please wait until completed'));
        queryClient.invalidateQueries({
          queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
        });
      },
      onError: (e) => {
        showMessage(e.message);
      },
    });

  const { data: steficonData, isLoading: loading } =
    useQuery<PaginatedRuleList>({
      queryKey: ['engineRules'],
      queryFn: () =>
        RestService.restEngineRulesList({
          type: 'PAYMENT_PLAN',
          deprecated: false,
          enabled: true,
        }),
    });

  const { mutateAsync: mutateExport, isPending: loadingExport } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansReconciliationExportXlsxRetrieve(
        {
          businessAreaSlug,
          id,
          programSlug,
        },
      ),
    onSuccess: () => {
      showMessage(t('Exporting XLSX started. Please check your email.'));
    },
    onError: (e) => {
      showMessage(e.message);
    },
  });

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
    paymentPlan.status !== PaymentPlanStatusEnum.LOCKED ||
    !isActiveProgram;

  const shouldDisableDownloadTemplate =
    paymentPlan.status !== PaymentPlanStatusEnum.LOCKED || !isActiveProgram;

  const shouldDisableExportXlsx =
    loadingExport ||
    paymentPlan.status !== PaymentPlanStatusEnum.LOCKED ||
    paymentPlan?.backgroundActionStatus ===
    BackgroundActionStatusEnum.XLSX_EXPORTING ||
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
            <Grid size={{ xs: 11 }}>
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
                  {steficonData?.results?.map((each, index) => (
                    <MenuItem
                      data-cy={`select-option-${index}`}
                      key={each.id}
                      value={each.id}
                    >
                      {each.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid>
              <Box ml={2}>
                <Button
                  variant="contained"
                  color="primary"
                  disabled={
                    loadingSetSteficonRule ||
                    !steficonRuleValue ||
                    paymentPlan.status !== PaymentPlanStatusEnum.LOCKED ||
                    paymentPlan.backgroundActionStatus ===
                    BackgroundActionStatusEnum.RULE_ENGINE_RUN ||
                    !isActiveProgram
                  }
                  data-cy="button-apply-steficon"
                  onClick={async () => {
                    try {
                      await setSteficonRule({
                        programSlug: programId,
                        businessAreaSlug: businessArea,
                        id: paymentPlan.id,
                        requestBody: {
                          engineFormulaRuleId: steficonRuleValue,
                          version: paymentPlan.version,
                        },
                      });
                      showMessage(
                        t('Formula is executing, please wait until completed'),
                      );
                    } catch (e) {
                      showApiErrorMessages(e, showMessage);
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
                  onClick={() =>
                    mutateExport({
                      businessAreaSlug: businessArea,
                      programSlug: programId,
                      id: paymentPlan.id,
                    })
                  }
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

export default withErrorBoundary(Entitlement, 'Entitlement');

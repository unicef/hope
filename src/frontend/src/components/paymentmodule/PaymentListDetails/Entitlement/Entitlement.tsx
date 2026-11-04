import withErrorBoundary from '@components/core/withErrorBoundary';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { LoadingComponent } from '@core/LoadingComponent';
import { RuleNameWithDescription } from '@core/RuleNameWithDescription';
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
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from '@mui/material';
import type { ApplyEngineFormula } from '@restgenerated/models/ApplyEngineFormula';
import { PaymentListDetailBackgroundActionStatusEnum } from '@restgenerated/models/PaymentListDetailBackgroundActionStatusEnum';
import type { PaginatedRuleList } from '@restgenerated/models/PaginatedRuleList';
import type { PaymentListDetail } from '@restgenerated/models/PaymentListDetail';
import { PaymentListStatusEnum } from '@restgenerated/models/PaymentListStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import {
  formatCurrencyCode,
  formatFigure,
  showApiErrorMessages,
} from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';
import { BigValue } from '../../../rdi/details/RegistrationDetails/RegistrationDetails';
import { ImportXlsxPaymentList } from '../ImportXlsxPaymentList/ImportXlsxPaymentList';
import { responsiveValue, Row } from 'src/responsive';

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

interface EntitlementProps {
  paymentList: PaymentListDetail;
  permissions: string[];
}

function Entitlement({
  paymentList,
  permissions,
}: EntitlementProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();

  const [steficonRuleValue, setSteficonRuleValue] = useState<string>(
    paymentList.steficonRule?.rule?.id
      ? String(paymentList.steficonRule.rule.id)
      : '',
  );
  const [flatAmount, setFlatAmount] = useState<string>(
    paymentList.flatAmountValue ? paymentList.flatAmountValue : '',
  );

  const { mutateAsync: setSteficonRule, isPending: loadingSetSteficonRule } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programCode,
        requestBody,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
        requestBody: ApplyEngineFormula;
      }) =>
        RestService.restBusinessAreasProgramsPaymentListsApplyEngineFormulaCreate(
          {
            businessAreaSlug,
            id,
            programCode,
            requestBody,
          },
        ),
      onSuccess: () => {
        showMessage(t('Formula is executing, please wait until completed'));
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentListsRetrieve,
          ),
        });
      },
      onError: (error: any) => {
        showApiErrorMessages(error, showMessage);
      },
    });

  const { mutateAsync: applyFlatAmount, isPending: loadingSetFlatAmount } =
    useMutation({
      mutationFn: ({
        businessAreaSlug,
        id,
        programCode,
        requestBody,
      }: {
        businessAreaSlug: string;
        id: string;
        programCode: string;
        requestBody: any;
      }) =>
        RestService.restBusinessAreasProgramsPaymentListsEntitlementFlatAmountCreate(
          {
            businessAreaSlug,
            id,
            programCode,
            requestBody,
          },
        ),
      onSuccess: () => {
        showMessage(
          t('Flat amount is being applied, please wait until completed'),
        );
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentListsRetrieve,
          ),
        });
      },
      onError: (error: any) => {
        showApiErrorMessages(error, showMessage);
      },
    });

  const engineRulesParams = {
    type: 'PAYMENT_PLAN' as const,
    deprecated: false,
    enabled: true,
    businessArea: businessArea,
  };
  const { data: steficonData, isLoading: loading } =
    useQuery<PaginatedRuleList>({
      queryKey: restQueryKey(
        RestService.restEngineRulesList,
        engineRulesParams,
      ),
      queryFn: () => RestService.restEngineRulesList(engineRulesParams),
    });

  const { mutate: mutateExport, isPending: loadingExport } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programCode,
    }: {
      businessAreaSlug: string;
      id: string;
      programCode: string;
    }) =>
      RestService.restBusinessAreasProgramsPaymentListsEntitlementExportXlsxRetrieve(
        {
          businessAreaSlug,
          id,
          programCode,
        },
      ),
    onSuccess: async () => {
      showMessage(t('Exporting XLSX started. Please check your email.'));
      await queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentListsRetrieve,
        ),
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
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
    paymentList.status !== PaymentListStatusEnum.LOCKED ||
    !isActiveProgram;

  const shouldDisableDownloadTemplate =
    paymentList.status !== PaymentListStatusEnum.LOCKED || !isActiveProgram;

  const shouldDisableExportXlsx =
    loadingExport ||
    paymentList.status !== PaymentListStatusEnum.LOCKED ||
    paymentList?.backgroundActionStatus ===
      PaymentListDetailBackgroundActionStatusEnum.XLSX_EXPORTING ||
    paymentList?.backgroundActionStatus ===
      PaymentListDetailBackgroundActionStatusEnum.RULE_ENGINE_RUN ||
    !isActiveProgram;

  return (
    <Box
      sx={{
        m: responsiveValue(2, 5),
      }}
    >
      <ContainerColumnWithBorder>
        <Box
          sx={{
            mt: 4,
          }}
        >
          <Title>
            <Typography variant="h6">{t('Entitlement')}</Typography>
          </Title>
          <GreyText>{t('Select Entitlement Formula')}</GreyText>
          <Grid
            container
            spacing={2}
            sx={{
              alignItems: 'center',
            }}
          >
            <Grid size={responsiveValue(12, 10)}>
              <FormControl size="small" variant="outlined" fullWidth>
                <Box>
                  <InputLabel size="small" htmlFor="entitlement-formula">
                    {t('Entitlement Formula')}
                  </InputLabel>
                </Box>
                <Select
                  id="entitlement-formula"
                  size="small"
                  disabled={shouldDisableEntitlementSelect}
                  label={t('Entitlement Formula')}
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
                  renderValue={(value) => {
                    const appliedRule = paymentList.steficonRule?.rule;
                    const rule =
                      steficonData?.results?.find(
                        (each) => String(each.id) === String(value),
                      ) ??
                      (String(appliedRule?.id) === String(value)
                        ? appliedRule
                        : undefined);
                    return rule ? (
                      <RuleNameWithDescription
                        name={rule.name}
                        description={rule.description}
                      />
                    ) : (
                      ''
                    );
                  }}
                >
                  {steficonData?.results?.map((each, index) => (
                    <MenuItem
                      data-cy={`select-option-${index}`}
                      key={each.id}
                      value={each.id}
                    >
                      <RuleNameWithDescription
                        name={each.name}
                        description={each.description}
                      />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={responsiveValue(12, 2)}>
              <Button
                variant="contained"
                color="primary"
                sx={{ ml: responsiveValue(0, 1) }}
                disabled={
                  loadingSetSteficonRule ||
                  !steficonRuleValue ||
                  paymentList.status !== PaymentListStatusEnum.LOCKED ||
                  paymentList.backgroundActionStatus ===
                    PaymentListDetailBackgroundActionStatusEnum.RULE_ENGINE_RUN ||
                  !isActiveProgram
                }
                data-cy="button-apply-steficon"
                data-perm={
                  PERMISSIONS.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS
                }
                onClick={async () => {
                  try {
                    await setSteficonRule({
                      programCode: programId,
                      businessAreaSlug: businessArea,
                      id: paymentList.id,
                      requestBody: {
                        engineFormulaRuleId: steficonRuleValue,
                        version: paymentList.version,
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
            </Grid>
          </Grid>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <OrDivider />
            <DividerLabel>Or</DividerLabel>
            <OrDivider />
          </Box>
          <Box
            sx={{
              mt: 3,
              mb: 3,
            }}
          >
            <Typography variant="h6" gutterBottom>
              {t('Fixed Amount')}
            </Typography>
            <GreyText>{t('Entitlement Quantity')}</GreyText>
            <Grid
              container
              spacing={2}
              sx={{
                alignItems: 'center',
              }}
            >
              <Grid size={responsiveValue(12, 10)}>
                <TextField
                  size="small"
                  variant="outlined"
                  fullWidth
                  type="number"
                  label={t('Enter amount')}
                  disabled={shouldDisableEntitlementSelect}
                  value={flatAmount}
                  onChange={(e) => setFlatAmount(e.target.value)}
                  placeholder={t('Enter amount')}
                  data-cy="input-flat-amount"
                />
              </Grid>
              <Grid size={responsiveValue(12, 2)}>
                <LoadingButton
                  variant="contained"
                  color="primary"
                  loading={loadingSetFlatAmount}
                  sx={{ ml: responsiveValue(0, 1) }}
                  disabled={
                    loadingSetFlatAmount ||
                    !flatAmount ||
                    paymentList.status !== PaymentListStatusEnum.LOCKED ||
                    paymentList.backgroundActionStatus ===
                      PaymentListDetailBackgroundActionStatusEnum.RULE_ENGINE_RUN ||
                    !isActiveProgram
                  }
                  data-cy="button-apply-flat-amount"
                  onClick={async () => {
                    try {
                      await applyFlatAmount({
                        programCode: programId,
                        businessAreaSlug: businessArea,
                        id: paymentList.id,
                        requestBody: {
                          flatAmountValue: flatAmount,
                          version: paymentList.version,
                        },
                      });
                    } catch (e) {
                      showApiErrorMessages(e, showMessage);
                    }
                  }}
                >
                  {t('Apply')}
                </LoadingButton>
              </Grid>
            </Grid>
            <GreyTextSmall>
              {t('Set the same amount for all payment records')}
            </GreyTextSmall>
          </Box>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <OrDivider />
            <DividerLabel>Or</DividerLabel>
            <OrDivider />
          </Box>
        </Box>
        <Row sx={{ gap: responsiveValue(4, 0) }}>
          <Box
            sx={{
              width: responsiveValue('100%', '50%'),
            }}
          >
            <Box
              sx={{
                borderRight: responsiveValue('none', '1px solid #b1b1b5'),
                borderBottom: responsiveValue('1px solid #b1b1b5', 'none'),
                pb: responsiveValue(4, 0),
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                flexDirection: 'column',
              }}
            >
              {paymentList.hasPaymentListExportFile ? (
                <Button
                  color="primary"
                  startIcon={<DownloadIcon />}
                  component="a"
                  download
                  data-cy="button-download-template"
                  href={`/api/download-payment-list/${paymentList.id}`}
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
                      programCode: programId,
                      id: paymentList.id,
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
            </Box>
          </Box>
          <Box
            sx={{
              width: responsiveValue('100%', '50%'),
            }}
          >
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                flexDirection: 'column',
              }}
            >
              <Box>
                <ImportXlsxPaymentList
                  permissions={permissions}
                  paymentList={paymentList}
                />
              </Box>
              {paymentList?.importedFileName ? (
                <Box
                  sx={{
                    alignItems: 'center',
                    display: 'flex',
                  }}
                >
                  <SpinaczIconContainer>
                    <AttachFileIcon fontSize="inherit" />
                  </SpinaczIconContainer>
                  <Box
                    sx={{
                      mr: 1,
                    }}
                  >
                    <GreyTextSmall data-cy="imported-file-name">
                      {paymentList?.importedFileName}
                    </GreyTextSmall>
                  </Box>
                  <GreyTextSmall>
                    {paymentList?.importedFileDate ? (
                      <UniversalMoment>
                        {paymentList?.importedFileDate}
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
        </Row>
        {paymentList.totalEntitledQuantityUsd ? (
          <>
            <Divider />
            <LabelizedField label={t('Total Entitled Quantity')}>
              <BigValue data-cy="total-entitled-quantity-usd">
                {`${formatFigure(paymentList.totalEntitledQuantity)} ${formatCurrencyCode(paymentList.currency, paymentList.currencyVisionCode)} (${formatFigure(paymentList.totalEntitledQuantityUsd)} USD)`}
              </BigValue>
            </LabelizedField>
          </>
        ) : null}
      </ContainerColumnWithBorder>
    </Box>
  );
}

export default withErrorBoundary(Entitlement, 'Entitlement');

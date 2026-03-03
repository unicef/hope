import withErrorBoundary from '@components/core/withErrorBoundary';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  TextField,
  Typography,
} from '@mui/material';
import { ApplyCustomExchangeRate } from '@restgenerated/models/ApplyCustomExchangeRate';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';


const OptionDetails = styled(Box)`
  margin-left: 32px;
  margin-bottom: 16px;
`;

type ExchangeRateOption = 'unore' | 'custom';

interface ConversionToUsdProps {
  paymentPlan: PaymentPlanDetail;
  permissions: string[];
}

function ConversionToUsd({
  paymentPlan,
  permissions,
}: ConversionToUsdProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();
  const unoreExchangeRate =
    paymentPlan.unoreExchangeRate != null
      ? String(paymentPlan.unoreExchangeRate)
      : paymentPlan.exchangeRate;
  const [selectedOption, setSelectedOption] = useState<ExchangeRateOption>(
    paymentPlan.customExchangeRate ? 'custom' : 'unore',
  );
  const [customExchangeRate, setCustomExchangeRate] = useState<string>(
    paymentPlan.customExchangeRate ? paymentPlan.exchangeRate ?? '' : '',
  );

  useEffect(() => {
    setSelectedOption(paymentPlan.customExchangeRate ? 'custom' : 'unore');
    setCustomExchangeRate(
      paymentPlan.customExchangeRate ? paymentPlan.exchangeRate ?? '' : '',
    );
  }, [paymentPlan.customExchangeRate, paymentPlan.exchangeRate, paymentPlan.id]);

  const { mutateAsync: applyExchangeRate, isPending } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
      requestBody: ApplyCustomExchangeRate;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansCustomExchangeRateCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
      }),
    onSuccess: () => {
      showMessage(t('Exchange rate is being applied, please wait until completed'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlan', businessArea, paymentPlan.id, programId],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const canApplyCustomExchangeRate = hasPermissions(
    PERMISSIONS.PM_CUSTOM_EXCHANGE_RATE,
    permissions,
  );
  const isSupportedStatus =
    paymentPlan.status === PaymentPlanStatusEnum.OPEN ||
    paymentPlan.status === PaymentPlanStatusEnum.IN_REVIEW;
  const isCustomExchangeRateReadOnly =
    !canApplyCustomExchangeRate || !isActiveProgram || !isSupportedStatus;
  const exchangeRateToApply =
    (selectedOption === 'custom' ? customExchangeRate : unoreExchangeRate) ??
    '';
  const requestBody: ApplyCustomExchangeRate =
    selectedOption === 'custom'
      ? {
          customExchangeRate: exchangeRateToApply,
          version: paymentPlan.version,
        }
      : {
          unoreExchangeRate: exchangeRateToApply,
          version: paymentPlan.version,
        };
  const isApplyDisabled =
    !canApplyCustomExchangeRate ||
    !isActiveProgram ||
    !isSupportedStatus ||
    !exchangeRateToApply;
  const areOptionsDisabled =
    !canApplyCustomExchangeRate || !isActiveProgram || !isSupportedStatus;

  const renderExchangeRateInfo = (exchangeRate: string | null | undefined) =>
    exchangeRate
      ? t('1 USD = {{rate}} {{currency}}', {
          rate: exchangeRate,
          currency: paymentPlan.currency,
        })
      : t('Exchange rate is unavailable');

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Box display="flex" justifyContent="space-between" alignItems="flex-start" gap={2}>
              <Typography variant="h6">{t('Conversion to USD')}</Typography>
              <LoadingButton
                variant="contained"
                color="primary"
                loading={isPending}
                disabled={isApplyDisabled}
                onClick={async () => {
                  await applyExchangeRate({
                    businessAreaSlug: businessArea,
                    id: paymentPlan.id,
                    programSlug: programId,
                    requestBody,
                  });
                }}
              >
                {t('Apply')}
              </LoadingButton>
            </Box>
          </Title>
          <RadioGroup
            value={selectedOption}
            onChange={(event) =>
              setSelectedOption(event.target.value as ExchangeRateOption)
            }
          >
            <FormControlLabel
              value="unore"
              control={<Radio />}
              disabled={areOptionsDisabled}
              label={t('Use UNORE exchange rate')}
            />
            <OptionDetails>
              <Typography variant="body2">
                {renderExchangeRateInfo(unoreExchangeRate)}
              </Typography>
            </OptionDetails>
            <FormControlLabel
              value="custom"
              control={<Radio />}
              disabled={areOptionsDisabled}
              label={t('Custom exchange rate')}
            />
            <OptionDetails>
              <TextField
                size="small"
                type="number"
                helperText={t('Enter the amount of local currency against 1 USD')}
                value={customExchangeRate}
                disabled={selectedOption !== 'custom' || !isSupportedStatus}
                onChange={(event) => setCustomExchangeRate(event.target.value)}
                sx={{ width: { xs: '100%', sm: 280 } }}
                inputProps={{
                  step: '0.00000001',
                  min: '0',
                  readOnly: isCustomExchangeRateReadOnly,
                }}
              />
            </OptionDetails>
          </RadioGroup>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
}

export default withErrorBoundary(ConversionToUsd, 'ConversionToUsd');

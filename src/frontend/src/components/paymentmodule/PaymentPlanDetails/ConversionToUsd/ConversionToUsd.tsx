import withErrorBoundary from '@components/core/withErrorBoundary';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LoadingButton } from '@core/LoadingButton';
import { Title } from '@core/Title';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import {
  Alert,
  Box,
  FormControlLabel,
  Radio,
  RadioGroup,
  TextField,
  Typography,
} from '@mui/material';
import type { ApplyCustomExchangeRate } from '@restgenerated/models/ApplyCustomExchangeRate';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import type { PaymentPlanGroupDetail } from '@restgenerated/models/PaymentPlanGroupDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { formatCurrencyCode, showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import { responsiveValue } from 'src/responsive';

const OptionDetails = styled(Box)`
  margin-left: 32px;
  margin-bottom: 16px;
`;

type ExchangeRateOption = 'unore' | 'custom';

interface ConversionToUsdProps {
  owner: PaymentPlanGroupDetail | FollowUpInstructionDetail;
  ownerType: 'group' | 'instruction';
  permissions: string[];
}

function ConversionToUsd({
  owner,
  ownerType,
  permissions,
}: ConversionToUsdProps): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const { isActiveProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();
  const unoreExchangeRate =
    owner.unoreExchangeRate != null ? String(owner.unoreExchangeRate) : '';
  const [selectedOption, setSelectedOption] = useState<ExchangeRateOption>(
    owner.customExchangeRate ? 'custom' : 'unore',
  );
  const [customExchangeRate, setCustomExchangeRate] = useState<string>(
    owner.customExchangeRate ? (owner.exchangeRate ?? '') : '',
  );

  useEffect(() => {
    setSelectedOption(owner.customExchangeRate ? 'custom' : 'unore');
    setCustomExchangeRate(
      owner.customExchangeRate ? (owner.exchangeRate ?? '') : '',
    );
  }, [owner.customExchangeRate, owner.exchangeRate, owner.id]);

  const { mutate: applyExchangeRate, isPending } = useMutation({
    mutationFn: async ({
      businessAreaSlug,
      id,
      ownerType,
      programCode,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      ownerType: 'group' | 'instruction';
      programCode: string;
      requestBody: ApplyCustomExchangeRate;
    }) => {
      const params = { businessAreaSlug, id, programCode, requestBody };
      await (ownerType === 'group'
        ? RestService.restBusinessAreasProgramsPaymentPlanGroupsCustomExchangeRateCreate(
            params,
          )
        : RestService.restBusinessAreasProgramsFollowUpInstructionsCustomExchangeRateCreate(
            params,
          ));
    },
    onSuccess: () => {
      showMessage(
        t('Exchange rate is being applied, please wait until completed'),
      );
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          ownerType === 'group'
            ? RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve
            : RestService.restBusinessAreasProgramsFollowUpInstructionsRetrieve,
        ),
      });
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
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
    owner.status === 'OPEN' || owner.status === 'IN_REVIEW';
  const isCustomExchangeRateReadOnly =
    !canApplyCustomExchangeRate || !isActiveProgram || !isSupportedStatus;
  const exchangeRateToApply =
    (selectedOption === 'custom' ? customExchangeRate : unoreExchangeRate) ??
    '';
  const requestBody: ApplyCustomExchangeRate =
    selectedOption === 'custom'
      ? {
          customExchangeRate: exchangeRateToApply,
          updatedAt: owner.updatedAt,
        }
      : {
          unoreExchangeRate: exchangeRateToApply,
          updatedAt: owner.updatedAt,
        };
  const isApplyDisabled =
    !canApplyCustomExchangeRate ||
    !isActiveProgram ||
    !isSupportedStatus ||
    owner.backgroundActionStatus === 'RECALCULATING' ||
    !exchangeRateToApply ||
    Number(exchangeRateToApply) <= 0;
  const areOptionsDisabled =
    !canApplyCustomExchangeRate || !isActiveProgram || !isSupportedStatus;

  const renderExchangeRateInfo = (exchangeRate: string | null | undefined) =>
    exchangeRate
      ? t('1 USD = {{rate}} {{currency}}', {
          rate: exchangeRate,
          currency: formatCurrencyCode(
            owner.currency,
            owner.currencyVisionCode,
          ),
        })
      : t('Exchange rate is unavailable');

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
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                gap: 2,
              }}
            >
              <Typography variant="h6">{t('Conversion to USD')}</Typography>
              <LoadingButton
                variant="contained"
                color="primary"
                loading={isPending}
                disabled={isApplyDisabled}
                data-cy="button-apply-exchange-rate"
                onClick={() => {
                  applyExchangeRate({
                    businessAreaSlug: businessArea,
                    id: owner.id,
                    ownerType,
                    programCode: programId,
                    requestBody,
                  });
                }}
              >
                {t('Apply')}
              </LoadingButton>
            </Box>
          </Title>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {ownerType === 'instruction'
              ? t(
                  'This exchange rate applies to all plans in this Follow-Up Instruction.',
                )
              : t(
                  'This exchange rate applies to all plans in this Payment Plan Group.',
                )}
          </Typography>
          {owner.unoreExchangeRateUnavailable && (
            <Box
              sx={{
                mb: 3,
              }}
            >
              <Alert severity="warning">
                {t(
                  'The UNORE exchange rate service is currently unavailable. The latest rate could not be retrieved - please try again later or apply a custom exchange rate.',
                )}
              </Alert>
            </Box>
          )}
          {owner.backgroundActionStatus === 'RECALCULATING_ERROR' && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {t('Exchange rate recalculation failed. Please try again.')}
            </Alert>
          )}
          <RadioGroup
            value={selectedOption}
            onChange={(event) =>
              setSelectedOption(event.target.value as ExchangeRateOption)
            }
          >
            <FormControlLabel
              value="unore"
              control={<Radio />}
              data-cy="radio-unore-exchange-rate"
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
              data-cy="radio-custom-exchange-rate"
              disabled={areOptionsDisabled}
              label={t('Custom exchange rate')}
            />
            <OptionDetails>
              <TextField
                size="small"
                type="number"
                helperText={t(
                  'Enter the amount of local currency against 1 USD',
                )}
                value={customExchangeRate}
                data-cy="input-custom-exchange-rate"
                disabled={selectedOption !== 'custom' || !isSupportedStatus}
                onChange={(event) => setCustomExchangeRate(event.target.value)}
                sx={{ width: { xs: '100%', sm: 280 } }}
                slotProps={{
                  htmlInput: {
                    step: '0.00000001',
                    min: '0.00000001',
                    readOnly: isCustomExchangeRateReadOnly,
                  },
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

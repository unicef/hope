import { useAvailableFsps } from '@hooks/useAvailableFsps';
import { Autocomplete, Grid, TextField } from '@mui/material';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
import type { CurrencyChoice } from '@restgenerated/models/CurrencyChoice';
import type { FspChoice } from '@restgenerated/models/FspChoice';
import { RestService } from '@restgenerated/services/RestService';
import { getCurrencyLabel } from '@shared/Formik/FormikCurrencyAutocomplete/FormikCurrencyAutocomplete';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { format, isValid, parseISO } from 'date-fns';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';

export interface PaymentPlanGroupSettings {
  financialServiceProvider: string | null;
  currency: string | null;
  dispersionStartDate: string | null;
  dispersionEndDate: string | null;
}

const toDate = (value: string | null): Date | null =>
  value ? parseISO(value) : null;

const toIsoDate = (date: unknown): string | null =>
  date instanceof Date && isValid(date) ? format(date, 'yyyy-MM-dd') : null;

interface PaymentPlanGroupSettingsFieldsProps {
  value: PaymentPlanGroupSettings;
  onChange: (value: PaymentPlanGroupSettings) => void;
  disabled?: boolean;
}

export const PaymentPlanGroupSettingsFields = ({
  value,
  onChange,
  disabled,
}: PaymentPlanGroupSettingsFieldsProps): ReactElement => {
  const { t } = useTranslation();
  const fsps = useAvailableFsps();
  const { data: currencies } = useQuery<CurrencyChoice[]>({
    queryKey: restQueryKey(RestService.restChoicesCurrenciesList),
    queryFn: () => RestService.restChoicesCurrenciesList(),
  });

  return (
    <Grid container spacing={2}>
      <Grid size={{ xs: 12 }}>
        <Autocomplete<FspChoice>
          options={fsps}
          value={
            fsps.find((fsp) => fsp.id === value.financialServiceProvider) ??
            null
          }
          getOptionLabel={(option) => option.name}
          isOptionEqualToValue={(option, selected) => option.id === selected.id}
          onChange={(_e, option) =>
            onChange({ ...value, financialServiceProvider: option?.id ?? null })
          }
          disabled={disabled}
          renderInput={(params) => (
            <TextField
              {...params}
              label={t('FSP')}
              variant="outlined"
              size="small"
            />
          )}
          data-cy="input-group-fsp"
        />
      </Grid>
      <Grid size={{ xs: 12 }}>
        <Autocomplete<CurrencyChoice>
          options={currencies ?? []}
          value={
            (currencies ?? []).find((c) => c.value === value.currency) ?? null
          }
          getOptionLabel={getCurrencyLabel}
          isOptionEqualToValue={(option, selected) =>
            option.value === selected.value
          }
          onChange={(_e, option) =>
            onChange({ ...value, currency: option?.value ?? null })
          }
          disabled={disabled}
          renderInput={(params) => (
            <TextField
              {...params}
              label={t('Currency')}
              variant="outlined"
              size="small"
            />
          )}
          data-cy="input-group-currency"
        />
      </Grid>
      <Grid size={{ xs: 6 }}>
        <DesktopDatePicker
          label={t('Dispersion Start Date')}
          format="yyyy-MM-dd"
          value={toDate(value.dispersionStartDate)}
          onChange={(date) =>
            onChange({ ...value, dispersionStartDate: toIsoDate(date) })
          }
          disabled={disabled}
          slotProps={{
            textField: {
              size: 'small',
              fullWidth: true,
              name: 'dispersionStartDate',
            },
          }}
        />
      </Grid>
      <Grid size={{ xs: 6 }}>
        <DesktopDatePicker
          label={t('Dispersion End Date')}
          format="yyyy-MM-dd"
          value={toDate(value.dispersionEndDate)}
          minDate={toDate(value.dispersionStartDate) ?? undefined}
          onChange={(date) =>
            onChange({ ...value, dispersionEndDate: toIsoDate(date) })
          }
          disabled={disabled}
          slotProps={{
            textField: {
              size: 'small',
              fullWidth: true,
              name: 'dispersionEndDate',
            },
          }}
        />
      </Grid>
    </Grid>
  );
};

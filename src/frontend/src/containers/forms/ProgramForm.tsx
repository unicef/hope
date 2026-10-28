import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { TextField, Tooltip } from '@mui/material';
import type { PaginatedPayeeLabelList } from '@restgenerated/models/PaginatedPayeeLabelList';
import type { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { PaymentPlanPurposesAutocomplete } from '@shared/autocompletes/rest/PaymentPlanPurposesAutocomplete';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { Field, Form, useFormikContext } from 'formik';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';

interface ProgramFormPropTypes {
  values;
  programHasRdi?: boolean;
  errors;
  lockedPurposeIds?: string[];
  program?: ProgramDetail;
}

const ProgramForm = ({
  values,
  programHasRdi,
  lockedPurposeIds,
  program,
}: ProgramFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const isEditProgram = location.pathname.indexOf('edit') !== -1;

  const { data } = useQuery<ProgramChoices>({
    queryKey: restQueryKey(RestService.restChoicesProgramsRetrieve),
    queryFn: () => RestService.restChoicesProgramsRetrieve(),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });

  const { data: dataCollectingTypeChoices } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasDataCollectingTypesChoicesList,
      { businessAreaSlug: businessArea },
    ),
    queryFn: () =>
      RestService.restBusinessAreasDataCollectingTypesChoicesList({
        businessAreaSlug: businessArea,
      }),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });

  const { data: payeeTypeChoices } = useQuery({
    queryKey: restQueryKey(RestService.restBusinessAreasPayeeTypesChoicesList, {
      businessAreaSlug: businessArea,
    }),
    queryFn: () =>
      RestService.restBusinessAreasPayeeTypesChoicesList({
        businessAreaSlug: businessArea,
      }),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });

  const { data: beneficiaryGroupsData } = useQuery<PaginatedPayeeLabelList>({
    queryKey: restQueryKey(RestService.restBeneficiaryGroupsList, {
      active: true,
    }),
    queryFn: () => RestService.restBeneficiaryGroupsList({ active: true }),
  });

  const { setFieldValue, setValues } = useFormikContext();

  const isCopyProgramPage = location.pathname.includes('duplicate');

  const currentPayeeType = program?.payeeType;
  const selectedPayeeType =
    payeeTypeChoices?.find((payeeType) => payeeType.id === values.payeeType) ??
    (currentPayeeType && values.payeeType === currentPayeeType.id
      ? currentPayeeType
      : undefined);

  const payeeTypeOptions = useMemo(() => {
    const choices = (payeeTypeChoices ?? []).map((choice) => ({
      name: choice.name,
      value: choice.id,
    }));
    // A program may keep a Payee Type that the choices no longer list.
    if (
      currentPayeeType &&
      values.payeeType === currentPayeeType.id &&
      !choices.some((choice) => choice.value === currentPayeeType.id)
    ) {
      choices.push({ name: currentPayeeType.name, value: currentPayeeType.id });
    }
    return choices;
  }, [payeeTypeChoices, currentPayeeType, values.payeeType]);

  const filteredDataCollectionTypeChoicesData = useMemo(() => {
    const payeeTypeId = isCopyProgramPage
      ? program?.payeeType?.id
      : values.payeeType;
    const choices = (dataCollectingTypeChoices ?? []).filter(
      (dct) => dct.name !== '' && dct.payeeType === payeeTypeId,
    );
    // A program may keep a DCT that no longer matches its payee type.
    const currentCode = program?.dataCollectingType?.code;
    if (
      currentCode &&
      values.dataCollectingTypeCode === currentCode &&
      !choices.some((dct) => dct.value === currentCode)
    ) {
      choices.push({
        name: program.dataCollectingType.label,
        value: currentCode,
      });
    }
    return choices;
  }, [
    dataCollectingTypeChoices,
    isCopyProgramPage,
    program,
    values.payeeType,
    values.dataCollectingTypeCode,
  ]);

  const mappedBeneficiaryGroupsData = useMemo(() => {
    const choices = (beneficiaryGroupsData?.results ?? [])
      .filter(
        (label) =>
          label.active &&
          label.payeeType === values.payeeType &&
          (label.dataCollectingTypes.length === 0 ||
            label.dataCollectingTypes.includes(values.dataCollectingTypeCode)),
      )
      .map((label) => ({ name: label.name, value: label.id }));
    // A program may keep a Payee Label that was deactivated since.
    const currentLabel = program?.beneficiaryGroup;
    if (
      currentLabel &&
      values.beneficiaryGroup === currentLabel.id &&
      !choices.some((choice) => choice.value === currentLabel.id)
    ) {
      choices.push({ name: currentLabel.name, value: currentLabel.id });
    }
    return choices;
  }, [
    beneficiaryGroupsData,
    program,
    values.payeeType,
    values.dataCollectingTypeCode,
    values.beneficiaryGroup,
  ]);

  if (
    !data ||
    !beneficiaryGroupsData ||
    !dataCollectingTypeChoices ||
    !payeeTypeChoices
  )
    return null;

  return (
    <Form>
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="half">
          <Field
            name="name"
            label={t('Programme Name')}
            type="text"
            fullWidth
            required
            variant="outlined"
            component={FormikTextField}
            data-cy="input-programme-name"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="code"
            label={t('Programme Code')}
            type="text"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            maxLength={4}
            disabled={isEditProgram}
            data-cy="input-programme-code"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="startDate"
            label={t('Start Date')}
            component={FormikDateField}
            required
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
            data-cy="input-start-date"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="endDate"
            label={t('End Date')}
            component={FormikDateField}
            disabled={!values.startDate}
            initialFocusedDate={values.startDate}
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
            minDate={values.startDate}
            data-cy="input-end-date"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="sector"
            label={t('Sector')}
            fullWidth
            required
            variant="outlined"
            choices={data.sectorChoices}
            component={FormikSelectField}
            data-cy="input-sector"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Tooltip
            title={
              values.isActive
                ? 'Cannot update Payee Type when program is Active'
                : programHasRdi
                  ? 'Field disabled because Programme has RDI'
                  : isCopyProgramPage
                    ? 'Payee Type is fixed when copying programs'
                    : ''
            }
            placement="top"
          >
            <span>
              <Field
                name="payeeType"
                label={t('Payee Type')}
                fullWidth
                variant="outlined"
                required
                disabled={programHasRdi || isCopyProgramPage || values.isActive}
                onChange={(e) => {
                  const payeeType = payeeTypeChoices.find(
                    (choice) => choice.id === e.target.value,
                  );
                  setValues({
                    ...values,
                    payeeType: e.target.value,
                    dataCollectingTypeCode:
                      payeeType?.defaultDataCollectingType ?? '',
                    beneficiaryGroup: '',
                  });
                }}
                choices={payeeTypeOptions}
                component={FormikSelectField}
                data-cy="input-payee-type"
              />
            </span>
          </Tooltip>
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <TextField
            label={t('GL Code')}
            value={selectedPayeeType?.glCode ?? ''}
            fullWidth
            variant="outlined"
            size="small"
            disabled
            slotProps={{ htmlInput: { readOnly: true } }}
            data-cy="input-gl-code"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Tooltip
            title={
              values.isActive
                ? 'Cannot update Data Collecting Type when program is Active'
                : programHasRdi
                  ? 'Field disabled because Programme has RDI'
                  : isCopyProgramPage
                    ? 'Field disabled on Copy Programme page'
                    : !values.payeeType
                      ? 'Select Payee Type first'
                      : ''
            }
            placement="top"
          >
            <span>
              <Field
                name="dataCollectingTypeCode"
                label={t('Data Collecting Type')}
                fullWidth
                variant="outlined"
                required
                disabled={
                  programHasRdi ||
                  isCopyProgramPage ||
                  values.isActive ||
                  !values.payeeType
                }
                onChange={(e) => {
                  // Only clear Payee Label if NOT copying a program
                  if (!isCopyProgramPage) {
                    setFieldValue('beneficiaryGroup', '');
                  }
                  setFieldValue('dataCollectingTypeCode', e.target.value);
                }}
                choices={filteredDataCollectionTypeChoicesData || []}
                component={FormikSelectField}
                data-cy="input-data-collecting-type"
              />
            </span>
          </Tooltip>
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Tooltip
            title={
              isCopyProgramPage
                ? 'Payee Label is fixed when copying programs'
                : !values.payeeType
                  ? 'Select Payee Type first'
                  : !values.dataCollectingTypeCode
                    ? 'Select Data Collecting Type first'
                    : programHasRdi
                      ? 'Field disabled because program has RDI'
                      : ''
            }
            placement="top"
          >
            <span>
              <Field
                name="beneficiaryGroup"
                label={t('Payee Label')}
                fullWidth
                variant="outlined"
                required={
                  !!values.dataCollectingTypeCode &&
                  !programHasRdi &&
                  !isCopyProgramPage
                }
                choices={mappedBeneficiaryGroupsData}
                component={FormikSelectField}
                data-cy="input-beneficiary-group"
                disabled={
                  (isCopyProgramPage && !!values.beneficiaryGroup) ||
                  (!values.dataCollectingTypeCode && !isCopyProgramPage) ||
                  (!values.payeeType && !isCopyProgramPage) ||
                  programHasRdi
                }
              />
            </span>
          </Tooltip>
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
          <Field
            name="description"
            label={t('Description')}
            type="text"
            fullWidth
            multiline
            variant="outlined"
            component={FormikTextField}
            data-cy="input-description"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
          <Field
            name="paymentPlanPurposes"
            required
            component={PaymentPlanPurposesAutocomplete}
            lockedValues={lockedPurposeIds ?? []}
            disabled={(values.paymentPlanPurposes?.length ?? 0) >= 10}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="budget"
            label={t('Budget (USD)')}
            type="number"
            fullWidth
            precision={2}
            variant="outlined"
            component={FormikTextField}
            data-cy="input-budget"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="administrativeAreasOfImplementation"
            label={t('Administrative Areas of Implementation')}
            type="text"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="input-admin-area"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="populationGoal"
            label={t('Population Goal (# of Individuals)')}
            type="number"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="input-population-goal"
          />
        </ResponsiveGrid>
        <ResponsiveGrid
          size="half"
          sx={{ display: responsiveValue('none', 'block') }}
        />
        <ResponsiveGrid size="half">
          <Field
            name="cashPlus"
            label={t('Cash+')}
            color="primary"
            component={FormikCheckboxField}
            data-cy="input-cash-plus"
          />
        </ResponsiveGrid>
        <ResponsiveGrid
          size="half"
          sx={{ display: responsiveValue('none', 'block') }}
        />
        <ResponsiveGrid size="full">
          <Field
            name="frequencyOfPayments"
            label={t('Frequency of Payment')}
            choices={data.frequencyOfPaymentsChoices}
            component={FormikRadioGroup}
            data-cy="input-frequency-of-payment"
            alignItems="center"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="reconciliationWindowInDays"
            label={t('Reconciliation window (in days)')}
            type="number"
            fullWidth
            integer
            variant="outlined"
            component={FormikTextField}
            data-cy="input-reconciliation-window"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="sendReconciliationWindowExpiryNotifications"
            label={t('Send reconciliation window expiry notifications')}
            color="primary"
            component={FormikCheckboxField}
            data-cy="input-reconciliation-window-notifications"
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </Form>
  );
};

export default withErrorBoundary(ProgramForm, 'ProgramForm');

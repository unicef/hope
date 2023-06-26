import {
  Button,
  DialogContent,
  DialogTitle,
  Grid,
  Paper,
  Typography,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik, FormikValues } from 'formik';
import moment from 'moment';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  CreateReportMutationVariables,
  useCreateReportMutation,
  useReportChoiceDataQuery,
} from '../../__generated__/graphql';
import { ALL_REPORTS_QUERY } from '../../apollo/queries/reporting/AllReports';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '../../hooks/useBaseUrl';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikAdminAreaAutocomplete } from '../../shared/Formik/FormikAdminAreaAutocomplete';
import { FormikAdminAreaAutocompleteMultiple } from '../../shared/Formik/FormikAdminAreaAutocomplete/FormikAdminAreaAutocompleteMultiple';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { REPORT_TYPES } from '../../utils/constants';
import { AutoSubmitFormOnEnter } from '../core/AutoSubmitFormOnEnter';
import { FieldLabel } from '../core/FieldLabel';
import { LoadingButton } from '../core/LoadingButton';
import { LoadingComponent } from '../core/LoadingComponent';

export const NewReportForm = (): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea, programId } = useBaseUrl();

  const validationSchema = Yup.object().shape({
    reportType: Yup.string().required(t('Report type is required')),
    dateFrom: Yup.date().required(t('Date From is required')),
    dateTo: Yup.date()
      .when(
        'dateFrom',
        (dateFrom, schema) =>
          dateFrom &&
          schema.min(
            dateFrom,
            `${t('End date have to be greater than')}
            ${moment(dateFrom).format('YYYY-MM-DD')}`,
          ),
        '',
      )
      .required(t('Date To is required')),
  });

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();
  const [mutate, { loading }] = useCreateReportMutation();

  if (choicesLoading) return <LoadingComponent />;

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const initialValue: { [key: string]: any } = {
    reportType: '',
    dateFrom: '',
    dateTo: '',
    adminArea1: '',
    adminArea2: [],
  };

  const prepareVariables = (
    values: FormikValues,
  ): CreateReportMutationVariables['reportData'] => {
    const shouldSendAdmin2Field =
      values.reportType === REPORT_TYPES.INDIVIDUALS ||
      values.reportType === REPORT_TYPES.HOUSEHOLD_DEMOGRAPHICS ||
      values.reportType === REPORT_TYPES.PAYMENTS ||
      values.reportType === REPORT_TYPES.INDIVIDUALS_AND_PAYMENT;

    const shouldSendAdmin1Field =
      values.reportType === REPORT_TYPES.INDIVIDUALS_AND_PAYMENT;

    let variables: CreateReportMutationVariables['reportData'] = {
      businessAreaSlug: businessArea,
      program: programId,
      reportType: values.reportType,
      dateFrom: values.dateFrom,
      dateTo: values.dateTo,
    };

    if (shouldSendAdmin2Field) {
      variables = {
        ...variables,
        adminArea2: values.adminArea2.map((el) => el.node.id),
      };
    }
    if (shouldSendAdmin1Field) {
      variables = {
        ...variables,
        adminArea1: values.adminArea1?.node?.id,
      };
    }
    return variables;
  };

  const submitFormHandler = async (values: FormikValues): Promise<void> => {
    const response = await mutate({
      variables: {
        reportData: prepareVariables(values),
      },
      refetchQueries: () => [
        { query: ALL_REPORTS_QUERY, variables: { businessArea } },
      ],
    });
    if (!response.errors && response.data.createReport) {
      showMessage('Report created.', {
        pathname: `/${baseUrl}/reporting/${response.data.createReport.report.id}`,
        historyMethod: 'push',
      });
    } else {
      showMessage('Report create action failed.');
    }
  };

  const renderConditionalFields = (
    values: FormikValues,
    setFieldValue,
  ): React.ReactElement[] => {
    const fields: React.ReactElement[] = [];

    switch (values.reportType) {
      case REPORT_TYPES.INDIVIDUALS:
      case REPORT_TYPES.HOUSEHOLD_DEMOGRAPHICS:
      case REPORT_TYPES.PAYMENTS:
        fields.push(
          <Grid item xs={12}>
            <Field
              name='adminArea2'
              label={t('Administrative Level 2')}
              variant='outlined'
              component={FormikAdminAreaAutocompleteMultiple}
              parentId={values.adminArea1?.node?.id}
            />
          </Grid>,
        );
        break;
      case REPORT_TYPES.INDIVIDUALS_AND_PAYMENT:
        fields.push(
          <Grid item xs={12}>
            <Field
              name='adminArea1'
              label={t('Administrative Level 1')}
              variant='outlined'
              level={1}
              component={FormikAdminAreaAutocomplete}
              onClear={() => setFieldValue('adminArea2', [])}
              additionalOnChange={() => setFieldValue('adminArea2', [])}
            />
          </Grid>,
        );
        fields.push(
          <Grid item xs={12}>
            <Field
              name='adminArea2'
              label={t('Administrative Level 2')}
              variant='outlined'
              component={FormikAdminAreaAutocompleteMultiple}
              parentId={values.adminArea1?.node?.id}
            />
          </Grid>,
        );
        break;
      default:
        break;
    }

    return fields;
  };
  const renderTimeframeLabel = (reportType: string): string => {
    switch (reportType) {
      case REPORT_TYPES.INDIVIDUALS:
      case REPORT_TYPES.HOUSEHOLD_DEMOGRAPHICS:
        return t('Last Registration Date');
      case REPORT_TYPES.CASH_PLAN_VERIFICATION:
      case REPORT_TYPES.PAYMENT_VERIFICATION:
        return t('Completion Date');
      case REPORT_TYPES.PAYMENTS:
      case REPORT_TYPES.INDIVIDUALS_AND_PAYMENT:
        return t('Delivery Date');
      case REPORT_TYPES.CASH_PLAN:
        return t('End Date');
      default:
        return '';
    }
  };

  const renderDataFields = (values: FormikValues): React.ReactElement => {
    return (
      <Grid container spacing={3}>
        <Grid item xs={6}>
          <Field
            name='dateFrom'
            label={t('From Date')}
            component={FormikDateField}
            required
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
          />
        </Grid>
        <Grid item xs={6}>
          <Field
            name='dateTo'
            label={t('To Date')}
            component={FormikDateField}
            required
            disabled={!values.dateFrom}
            initialFocusedDate={values.dateFrom}
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
            minDate={values.dateFrom}
          />
        </Grid>
      </Grid>
    );
  };

  return (
    <>
      <Button
        color='primary'
        variant='contained'
        onClick={() => setDialogOpen(true)}
      >
        {t('NEW REPORT')}
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        PaperComponent={React.forwardRef((props, ref) => (
          <Paper
            {...{
              ...props,
              ref,
            }}
            data-cy='dialog-setup-new-report'
          />
        ))}
        aria-labelledby='form-dialog-title'
      >
        <Formik
          initialValues={initialValue}
          onSubmit={submitFormHandler}
          validationSchema={validationSchema}
        >
          {({ submitForm, values, setFieldValue }) => (
            <>
              {dialogOpen && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle disableTypography>
                  <Typography variant='h6'>
                    {t('Generate New Report')}
                  </Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Form>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Field
                        name='reportType'
                        label={t('Report Type')}
                        fullWidth
                        variant='outlined'
                        required
                        choices={choicesData.reportTypesChoices}
                        component={FormikSelectField}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <FieldLabel>
                        {renderTimeframeLabel(values.reportType)}
                      </FieldLabel>

                      {renderDataFields(values)}
                    </Grid>
                    {renderConditionalFields(values, setFieldValue)}
                  </Grid>
                </Form>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setDialogOpen(false)}>
                    {t('CANCEL')}
                  </Button>
                  <LoadingButton
                    loading={loading}
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    {t('GENERATE')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
};

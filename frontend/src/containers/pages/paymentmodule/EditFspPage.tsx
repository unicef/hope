import { Box } from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { EditFspHeader } from '../../../components/paymentmodule/EditFsp/EditFspHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikCheckboxGroup } from '../../../shared/Formik/FormikCheckboxGroup';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { handleValidationErrors } from '../../../utils/utils';
import { useCreateTpMutation } from '../../../__generated__/graphql';

export const EditFspPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    name: '',
    visionVendorNumber: '',
    paymentChannels: null,
  };
  const [mutate] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({});

  const handleSubmit = async (values, { setFieldError }): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            programId: values.program,
            name: values.name,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            businessAreaSlug: businessArea,
            ...getTargetingCriteriaVariables(values),
          },
        },
      });
      showMessage(t('Target Population Created'), {
        pathname: `/${businessArea}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'createTargetPopulation',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while creating Target Population'));
      }
    }
  };

  const paymentChannelChoices = [
    { name: t('Transfer'), value: 'transfer' },
    { name: t('Mobile Money'), value: 'mobileMoney' },
    { name: t('Deposit to Card'), value: 'depositToCard' },
    { name: t('Cash'), value: 'cash' },
    { name: t('Wallet'), value: 'wallet' },
  ];

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values }) => {
        return (
          <Form>
            <EditFspHeader
              handleSubmit={submitForm}
              businessArea={businessArea}
              permissions={permissions}
            />
            <Box m={5}>
              <ContainerColumnWithBorder>
                <Box mt={4}>
                  <Field
                    name='name'
                    label={t('Name')}
                    color='primary'
                    variant='outlined'
                    fullWidth
                    component={FormikTextField}
                  />
                </Box>
                <Box mt={4}>
                  <Field
                    name='visionVendorNumber'
                    label={t('Vision Vendor Number')}
                    color='primary'
                    variant='outlined'
                    fullWidth
                    component={FormikTextField}
                  />
                </Box>
                <Box mt={4}>
                  <Field
                    name='paymentChannels'
                    label={t('Payment Channels')}
                    component={FormikCheckboxGroup}
                    choices={paymentChannelChoices}
                    values={values}
                  />
                </Box>
              </ContainerColumnWithBorder>
            </Box>
          </Form>
        );
      }}
    </Formik>
  );
};

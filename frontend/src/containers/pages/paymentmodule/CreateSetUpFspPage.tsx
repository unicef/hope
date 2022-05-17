import { Box, Divider } from '@material-ui/core';
import { Form, Formik } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { CreateSetUpFspHeader } from '../../../components/paymentmodule/CreateSetUpFspPlan/CreateSetUpFspHeader';
import { FspArray } from '../../../components/paymentmodule/CreateSetUpFspPlan/FspArray';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { handleValidationErrors } from '../../../utils/utils';
import { useCreateTpMutation } from '../../../__generated__/graphql';

export const CreateSetUpFspPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    mobileMoney: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
    transfer: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
    cash: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
    wallet: [
      {
        fsp: '',
        maximumAmount: '',
      },
    ],
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

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values }) => {
        return (
          <Form>
            <CreateSetUpFspHeader
              handleSubmit={submitForm}
              businessArea={businessArea}
              permissions={permissions}
            />
            <Box m={5}>
              <ContainerColumnWithBorder>
                <FspArray
                  baseName='mobileMoney'
                  label={t('Mobile Money')}
                  values={values}
                  permissions={permissions}
                />
                <Divider />
                <FspArray
                  baseName='transfer'
                  label={t('Transfer')}
                  values={values}
                  permissions={permissions}
                />
                <Divider />
                <FspArray
                  baseName='cash'
                  label={t('Cash')}
                  values={values}
                  permissions={permissions}
                />
                <Divider />
                <FspArray
                  baseName='wallet'
                  label={t('Wallet')}
                  values={values}
                  permissions={permissions}
                />
              </ContainerColumnWithBorder>
            </Box>
          </Form>
        );
      }}
    </Formik>
  );
};

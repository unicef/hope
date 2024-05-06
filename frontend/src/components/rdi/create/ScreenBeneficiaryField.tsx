import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Field } from 'formik';
import { useBusinessAreaDataQuery } from '@generated/graphql';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { useBaseUrl } from '@hooks/useBaseUrl';

export function ScreenBeneficiaryField(): React.ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { data: businessAreaData } = useBusinessAreaDataQuery({
    variables: { businessAreaSlug: businessArea },
  });
  if (!businessAreaData?.businessArea?.screenBeneficiary) {
    return null;
  }
  return (
    <Field
      name="screenBeneficiary"
      label={t('Screen Beneficiary')}
      color="primary"
      component={FormikCheckboxField}
    />
  );
}

import { useTranslation } from 'react-i18next';
import { Field } from 'formik';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

export function ScreenBeneficiaryField(): ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({
        slug: businessArea,
      }),
  });
  if (!businessAreaData?.screenBeneficiary) {
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

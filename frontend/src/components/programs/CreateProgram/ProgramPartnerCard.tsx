import { Box, Button, Grid, IconButton } from '@material-ui/core';
import { Field, Form, Formik } from 'formik';
import EditIcon from '@material-ui/icons/Edit';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikRadioGroup } from '../../../shared/Formik/FormikRadioGroup';
import { BaseSection } from '../../core/BaseSection';
import { DeleteProgramPartner } from './DeleteProgramPartner';
import { DividerLine } from '../../core/DividerLine';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';

interface ProgramPartnerCardProps {
  partner;
  handleDeleteProgramPartner: (id: string) => void;
  index: number;
  total: number;
  arrayHelpers;
}

const BiggestText = styled(Box)`
  font-size: 18px;
  font-weight: 400;
`;

const BigText = styled(Box)`
  font-size: 16px;
  font-weight: 400;
`;

const SmallText = styled(Box)`
  font-size: 14px;
  font-weight: 400;
  color: #49454f;
`;

export const ProgramPartnerCard: React.FC<ProgramPartnerCardProps> = ({
  partner,
  handleDeleteProgramPartner,
  index,
  total,
  arrayHelpers,
}): React.ReactElement => {
  const { t } = useTranslation();

  const businessAreaOptionLabel = (
    <Box display='flex' flexDirection='column'>
      <BigText>{t('Business Area')}</BigText>
      <SmallText>
        {t('The partner has access to the entire business area')}
      </SmallText>
    </Box>
  );

  const adminAreaOptionLabel = (
    <Box display='flex' flexDirection='column'>
      <BigText>{t('Admin Area')}</BigText>
      <SmallText>
        {t('The partner has access to selected Admin Areas')}
      </SmallText>
      <SmallText>
        Selected Admin Areas:
        {/* //TODO: add admin areas */}
        {/* {values.adminAreas.length > 0 ? values.adminAreas.length : 0} */}
      </SmallText>
    </Box>
  );

  return (
    <Grid container direction='column'>
      <Box display='flex' justifyContent='space-between'>
        <Grid item xs={6}>
          <Field
            name='partner'
            label={t('Partner')}
            color='primary'
            required
            choices={[
              {
                value: 'examplePartner1',
                name: t('Example Partner 1'),
              },
              {
                value: 'examplePartner2',
                name: t('Example Partner 2'),
              },
            ]}
            component={FormikSelectField}
          />
        </Grid>
        <DeleteProgramPartner
          partner={partner}
          //TODO: add permission
          canDeleteProgramPartner
          handleDeleteProgramPartner={handleDeleteProgramPartner}
        />
      </Box>
      <Box mt={2} mb={2}>
        <BiggestText>{t('Area Access')}</BiggestText>
      </Box>
      <Grid item xs={6}>
        <Field
          name='areaAccess'
          choices={[
            {
              value: 'BUSINESS_AREA',
              name: t('Business Area'),
              optionLabel: businessAreaOptionLabel,
            },
            {
              value: 'ADMIN_AREA',
              name: t('Admin Area'),
              optionLabel: adminAreaOptionLabel,
            },
          ]}
          component={FormikRadioGroup}
          withGreyBox
        />
      </Grid>
      {index + 1 < total && <DividerLine />}
    </Grid>
  );
};

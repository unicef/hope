import { Box, Collapse, Grid, IconButton } from '@material-ui/core';
import { TreeView, TreeItem } from '@material-ui/lab';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { Field } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FormikRadioGroup } from '../../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { DividerLine } from '../../core/DividerLine';
import { DeleteProgramPartner } from './DeleteProgramPartner';
import { ArrowDropDown, ArrowRight } from '@material-ui/icons';
import { AllAreasTreeQuery } from '../../../__generated__/graphql';

interface ProgramPartnerCardProps {
  values;
  partner;
  index: number;
  arrayHelpers;
  allAreasTree: AllAreasTreeQuery['allAreasTree'];
  setFieldValue;
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
  values,
  partner,
  index,
  arrayHelpers,
  allAreasTree,
  setFieldValue,
}): React.ReactElement => {
  const { t } = useTranslation();
  const [isAdminAreaExpanded, setIsAdminAreaExpanded] = useState(false);

  const businessAreaOptionLabel = (
    <Box display='flex' flexDirection='column'>
      <BigText>{t('Business Area')}</BigText>
      <SmallText>
        {t('The partner has access to the entire business area')}
      </SmallText>
    </Box>
  );

  const renderTree = (nodes): React.ReactElement => (
    <TreeItem key={nodes.id} nodeId={nodes.id} label={nodes.name}>
      {Array.isArray(nodes.areas)
        ? nodes.areas.map((node) => renderTree(node))
        : null}
    </TreeItem>
  );

  const handleNodeSelect = (_event, nodeId): void => {
    let newSelected = [...(values.partners[index].adminAreas || [])];
    if (newSelected.includes(nodeId)) {
      newSelected = newSelected.filter((id) => id !== nodeId);
    } else {
      newSelected.push(nodeId);
    }
    setFieldValue(`partners[${index}].adminAreas`, newSelected);
  };

  const adminAreaOptionLabel = (
    <Box display='flex' flexDirection='column'>
      <Box display='flex' justifyContent='space-between' alignItems='center'>
        <Box>
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
        <IconButton
          onClick={() => setIsAdminAreaExpanded(!isAdminAreaExpanded)}
        >
          {isAdminAreaExpanded ? <ArrowDropDown /> : <ArrowRight />}
        </IconButton>
      </Box>
      <Collapse in={isAdminAreaExpanded}>
        <TreeView
          defaultCollapseIcon={<ExpandMoreIcon />}
          defaultExpandIcon={<ChevronRightIcon />}
          multiSelect
          selected={(values.partners[index]?.adminAreas || []).map(String)}
          onNodeSelect={handleNodeSelect}
        >
          {allAreasTree.map((tree) => renderTree(tree))}
        </TreeView>
      </Collapse>
    </Box>
  );

  const handleDeleteProgramPartner = (): void => {
    const foundIndex = values.partners.findIndex((p) => p.id === partner.id);
    if (foundIndex !== -1) {
      arrayHelpers.remove(foundIndex);
    }
  };

  return (
    <Grid container direction='column'>
      <Box display='flex' justifyContent='space-between'>
        <Grid item xs={6}>
          <Field
            name={`partners[${index}].partner`}
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
      <Box mt={2}>
        <BiggestText>{t('Area Access')}</BiggestText>
      </Box>
      <Grid item xs={6}>
        <Field
          name={`partners[${index}].areaAccess`}
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
      {index + 1 < values.partners.length && <DividerLine />}
    </Grid>
  );
};

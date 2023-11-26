import { Box, Checkbox, Collapse, Grid, IconButton } from '@material-ui/core';
import { ArrowDropDown, ArrowRight } from '@material-ui/icons';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { TreeItem, TreeView } from '@material-ui/lab';
import { Field } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { AllAreasTreeQuery } from '../../../__generated__/graphql';
import { FormikRadioGroup } from '../../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { DividerLine } from '../../core/DividerLine';
import { DeleteProgramPartner } from './DeleteProgramPartner';

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
  const selectedAdminAreasLength = values.partners[index]?.adminAreas?.length;
  const initialExpanded = selectedAdminAreasLength > 0;
  const [isAdminAreaExpanded, setIsAdminAreaExpanded] = useState(
    initialExpanded,
  );

  const businessAreaOptionLabel = (
    <Box display='flex' flexDirection='column'>
      <BigText>{t('Business Area')}</BigText>
      <SmallText>
        {t('The partner has access to the entire business area')}
      </SmallText>
    </Box>
  );

  const handleNodeSelect = (_event, nodeId): void => {
    let selectedNodeId = nodeId;
    let newSelected = [...(values.partners[index]?.adminAreas || [])].flat();
    selectedNodeId = Array.isArray(selectedNodeId)
      ? selectedNodeId.flat()
      : [selectedNodeId];

    selectedNodeId.forEach((id) => {
      if (newSelected.includes(id)) {
        newSelected = newSelected.filter((newId) => newId !== id);
      } else {
        newSelected.push(id);
      }
    });

    setFieldValue(`partners[${index}].adminAreas`, newSelected);
  };

  const renderTree = (nodes): React.ReactElement => (
    <TreeItem
      key={nodes.id}
      nodeId={nodes.id}
      label={
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Checkbox
            color='primary'
            checked={(values.partners[index]?.adminAreas || [])
              .flat()
              .includes(nodes.id)}
            onChange={(event) => handleNodeSelect(event, nodes.id)}
          />
          {nodes.name}
        </div>
      }
    >
      {Array.isArray(nodes.areas)
        ? nodes.areas.map((node) => renderTree(node))
        : null}
    </TreeItem>
  );

  const adminAreaOptionLabel = (
    <Box display='flex' flexDirection='column'>
      <Box display='flex' justifyContent='space-between' alignItems='center'>
        <Box>
          <BigText>{t('Admin Area')}</BigText>
          <SmallText>
            {t('The partner has access to selected Admin Areas')}
          </SmallText>
          <Box mt={2} mb={2}>
            <SmallText>
              Selected Admin Areas: {selectedAdminAreasLength || 0}
            </SmallText>
          </Box>
        </Box>
        <IconButton
          onClick={() => {
            setIsAdminAreaExpanded(!isAdminAreaExpanded);
          }}
        >
          {isAdminAreaExpanded ? <ArrowDropDown /> : <ArrowRight />}
        </IconButton>
      </Box>
      <Collapse in={isAdminAreaExpanded}>
        <Box style={{ maxHeight: '30vh', overflow: 'auto' }}>
          <TreeView
            defaultCollapseIcon={<ExpandMoreIcon />}
            defaultExpandIcon={<ChevronRightIcon />}
            multiSelect
            selected={(values.partners[index]?.adminAreas || []).map(String)}
            onNodeSelect={handleNodeSelect}
          >
            {allAreasTree.map((tree) => renderTree(tree))}
          </TreeView>
        </Box>
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
          onChange={(event) =>
            setIsAdminAreaExpanded(event.target.value === 'ADMIN_AREA')
          }
        />
      </Grid>
      {index + 1 < values.partners.length && <DividerLine />}
    </Grid>
  );
};

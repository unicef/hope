import { Box, Checkbox, Collapse, Grid, IconButton } from '@mui/material';
import { ArrowDropDown, ArrowRight } from '@mui/icons-material';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { TreeItem, TreeView } from '@mui/lab';
import { Field } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import {
  AllAreasTreeQuery,
  UserPartnerChoicesQuery,
} from '../../../__generated__/graphql';
import { FormikRadioGroup } from '../../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { DividerLine } from '../../core/DividerLine';
import { DeleteProgramPartner } from './DeleteProgramPartner';
import { AreaTreeNode } from './AreaTreeNode';

interface ProgramPartnerCardProps {
  values;
  partner;
  index: number;
  arrayHelpers;
  allAreasTreeData: AllAreasTreeQuery['allAreasTree'];
  partnerChoices: UserPartnerChoicesQuery['userPartnerChoices'];
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
  allAreasTreeData,
  partnerChoices,
  setFieldValue,
}): React.ReactElement => {
  const { t } = useTranslation();
  const selectedAdminAreasLength = values.partners[index]?.adminAreas?.length;
  const initialExpanded = selectedAdminAreasLength > 0;
  const [isAdminAreaExpanded, setIsAdminAreaExpanded] =
    useState(initialExpanded);
  const [allAreasTree, setAllAreasTree] = React.useState<AreaTreeNode[]>(() =>
    AreaTreeNode.buildTree(
      allAreasTreeData,
      values.partners[index]?.adminAreas,
    ),
  );
  const businessAreaOptionLabel = (
    <Box display="flex" flexDirection="column">
      <BigText>{t('Business Area')}</BigText>
      <SmallText>
        {t('The partner has access to the entire business area')}
      </SmallText>
    </Box>
  );

  const handleCheckBoxSelect = (_event, node): void => {
    _event.stopPropagation();
    node.toggleCheck();
    setFieldValue(
      `partners[${index}].adminAreas`,
      AreaTreeNode.getAllSelectedIds(allAreasTree),
    );
    setFieldValue(`partners[${index}].areaAccess`, 'ADMIN_AREA');
    setAllAreasTree([...allAreasTree]);
  };
  let renderTree = null;
  const renderNode = (node: AreaTreeNode): React.ReactElement => {
    return (
      <TreeItem
        key={node.id}
        nodeId={node.id}
        label={
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Checkbox
              id={node.id}
              color="primary"
              checked={Boolean(node.checked)}
              indeterminate={node.checked === 'indeterminate'}
              onChange={(event) => handleCheckBoxSelect(event, node)}
              onClick={(event) => event.stopPropagation()}
            />
            {node.name}
          </div>
        }
      >
        {renderTree(node.children)}
      </TreeItem>
    );
  };
  renderTree = (children: AreaTreeNode[]): React.ReactElement => {
    if (!children.length) {
      return null;
    }
    return <>{children.map((node) => renderNode(node))}</>;
  };

  const adminAreaOptionLabel = (
    <Box display="flex" flexDirection="column">
      <Box display="flex" justifyContent="space-between" alignItems="center">
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
          >
            {renderTree(allAreasTree)}
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
    <Grid container direction="column">
      <Box display="flex" justifyContent="space-between">
        <Grid item xs={6}>
          <Field
            name={`partners[${index}].id`}
            label={t('Partner')}
            color="primary"
            choices={partnerChoices}
            component={FormikSelectField}
          />
        </Grid>
        <DeleteProgramPartner
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
          required={values.partners[index]?.id !== ''}
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
          onChange={(event) => {
            setIsAdminAreaExpanded(event.target.value === 'ADMIN_AREA');
            if (event.target.value === 'BUSINESS_AREA') {
              setFieldValue(`partners[${index}].adminAreas`, []);
            }
          }}
        />
      </Grid>
      {index + 1 < values.partners.length && <DividerLine />}
    </Grid>
  );
};

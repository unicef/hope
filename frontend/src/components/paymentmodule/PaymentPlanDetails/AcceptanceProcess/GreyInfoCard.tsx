import { styled } from 'styled-components';
import { Box, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { ContainerColumnWithBorder } from '../../../core/ContainerColumnWithBorder';
import { Title } from '../../../core/Title';
import { AcceptanceProcessStepper } from './AcceptanceProcessStepper/AcceptanceProcessStepper';

const GreyText = styled.div`
  color: #9e9e9e;
`;
interface AcceptanceProcessProps {
  businessArea: string;
  permissions: string[];
}

export function AcceptanceProcess({
  businessArea,
  permissions,
}: AcceptanceProcessProps): React.ReactElement {
  const { t } = useTranslation();

  return <Box p={3}></Box>;
}
